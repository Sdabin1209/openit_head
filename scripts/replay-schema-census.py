#!/usr/bin/env python3
"""Replay saved positive/negative controls without starting services."""
import json
import os
from pathlib import Path
import subprocess
import sys

HEAD = Path(__file__).resolve().parents[1]
WORKSPACE = HEAD.parent
EVIDENCE = HEAD / 'docs/reviews/2026-11-06/schema-census'


def invoke(root, command, cases):
    environment = {key: value for key, value in os.environ.items() if key != 'PYTHONPATH'}
    result = subprocess.run(
        [str(root / '.venv/bin/python'), *command], cwd=root,
        input=json.dumps(cases), text=True, capture_output=True,
        env=environment, timeout=120, check=True,
    )
    return json.loads(result.stdout)


cases = json.loads((EVIDENCE / 'runtime-cases.json').read_text())
results = {}
for area in sorted({case['area'] for case in cases}):
    root = WORKSPACE / ('ops-feedback' if area == 'boundary-contracts' else area)
    selected = [case for case in cases if case['area'] == area]
    results[area] = invoke(root, [str(HEAD / 'scripts/audit-schema-runtime.py'), area], selected)

http_worker = '''
import json, sys
from boundary_contracts.http_contracts import HttpContract
results = []
for case in json.load(sys.stdin):
    contract = HttpContract(case['service'])
    row = {key: case[key] for key in ['service', 'method', 'path', 'status', 'fixture', 'pointer']}
    for field, verdict in [('control', 'control_accepted'), ('document', 'invalid_accepted')]:
        try:
            contract.response(case['method'], case['path'], case['status'], case[field], content_type='application/json')
            row[verdict] = True
        except Exception as error:
            row[verdict] = False
            row[verdict + '_error'] = type(error).__name__
    results.append(row)
print(json.dumps(results))
'''
http_cases = json.loads((EVIDENCE / 'openapi-cases.json').read_text())
http_results = invoke(WORKSPACE / 'ops-feedback', ['-c', http_worker], http_cases)
confirmed = {
    (area, row['name'])
    for area, group in results.items() for row in group['results']
    if row.get('control_accepted') and row.get('invalid_accepted')
}
http_confirmed = {
    row['service'] for row in http_results
    if row.get('control_accepted') and row.get('invalid_accepted')
}
json.dump({'runtime': results, 'openapi': http_results}, sys.stdout, ensure_ascii=False, indent=2)
print(file=sys.stdout)
print(f'Confirmed JSON schemas: {len(confirmed)}; OpenAPI documents: {len(http_confirmed)}', file=sys.stderr)
