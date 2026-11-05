#!/usr/bin/env python3
"""Compare E2E expectations with service-scoped OpenAPI; never accept arbitrary 2xx.

This static check reports unresolved calls separately. Unresolved is not verified.
Use --strict to fail on those as well as definite mismatches. Runtime producers
and service conformance tests enforce the complete request/response contract.
"""
import argparse
import ast
import json
from pathlib import Path
import re
import sys

WS = Path(__file__).resolve().parents[2]
from boundary_contracts.http_contracts import catalog, document


def templates():
    result = []
    for service in catalog()['services']:
        for path, methods in document(service)['paths'].items():
            pattern = re.compile('^' + re.sub(r'\\\{[^}]+\\\}', '[^/]+', re.escape(path)) + '$')
            for method, op in methods.items():
                result.append((service, method.upper(), pattern, {int(c) for c in op['responses']}))
    return result


def check(method, path, statuses, specs):
    path = path.split('?', 1)[0]
    hits = [(s, m, codes) for s, m, regex, codes in specs if regex.fullmatch(path)]
    if not hits:
        return None if statuses <= {404, 405} else 'path is not declared'
    if method is None:
        return 'UNRESOLVED: HTTP method cannot be determined from this statement'
    operations = [(s, codes) for s, m, codes in hits if m == method]
    if not operations:
        return None if statuses <= {404, 405} else 'method is not declared'
    allowed = set.intersection(*(codes for _, codes in operations))
    union = set.union(*(codes for _, codes in operations))
    if statuses <= union and not statuses <= allowed:
        return "UNRESOLVED: service identity is required for different status contracts"
    bad = statuses - allowed
    return 'statuses are not declared: ' + ','.join(map(str, sorted(bad))) if bad else None


def method_specs(source):
    tree = ast.parse(source)
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    specs = {}
    for fn in functions:
        names = [a.arg for a in fn.args.args]
        for parameter in ("method", "meth"):
            if parameter in names:
                idx = names.index(parameter)
                default = None
                offset = len(names) - len(fn.args.defaults)
                if idx >= offset and isinstance(fn.args.defaults[idx - offset], ast.Constant):
                    default = fn.args.defaults[idx - offset].value
                specs[fn.name] = (idx, parameter, default)
    def calls(fn):
        result = list(ast.walk(fn))
        for node in list(result):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and 'call(' in node.value:
                try:
                    result.extend(ast.walk(ast.parse(node.value)))
                except SyntaxError:
                    pass
        return [n for n in result if isinstance(n, ast.Call)]
    for _ in range(len(functions)):
        changed = False
        for fn in functions:
            if fn.name in specs:
                continue
            methods = {resolve_method(c, specs) for c in calls(fn)} - {None}
            if len(methods) == 1:
                specs[fn.name] = (-1, "", next(iter(methods)))
                changed = True
        if not changed:
            break
    # Lambda aliases can forward a method under a different parameter name.
    for assignment in ast.walk(tree):
        if not isinstance(assignment, ast.Assign) or not isinstance(assignment.value, ast.Lambda):
            continue
        names = [a.arg for a in assignment.value.args.args]
        candidates = set()
        for call in ast.walk(assignment.value.body):
            if not isinstance(call, ast.Call):
                continue
            called = call.func.id if isinstance(call.func, ast.Name) else None
            spec = specs.get(called)
            if spec and spec[0] >= 0 and len(call.args) > spec[0]:
                argument = call.args[spec[0]]
                if isinstance(argument, ast.Name) and argument.id in names:
                    candidates.add((names.index(argument.id), argument.id, None))
        if len(candidates) == 1:
            for target in assignment.targets:
                if isinstance(target, ast.Name):
                    specs[target.id] = next(iter(candidates))
    return specs


def resolve_method(call, specs):
    name = call.func.id if isinstance(call.func, ast.Name) else call.func.attr if isinstance(call.func, ast.Attribute) else None
    spec = specs.get(name)
    if spec is None:
        return None
    index, keyword, default = spec
    value = next((x.value for x in call.keywords if x.arg == keyword), None)
    if value is None and index >= 0 and len(call.args) > index:
        value = call.args[index]
    result = value.value if isinstance(value, ast.Constant) else default if value is None else None
    return result if result in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS') else None


def statement_method(line, position, specs):
    text = line.lstrip()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    offset = len(line) - len(text)
    column = len(text[:position - offset].encode('utf-8'))
    candidates = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and n.col_offset <= column < n.end_col_offset]
    candidates.sort(key=lambda n: n.end_col_offset - n.col_offset)
    return next((m for n in candidates if (m := resolve_method(n, specs))), None)


def scan(path):
    specs = templates()
    verified, violations, unresolved = 0, [], []
    source = path.read_text()
    helper = path.with_name("e2e_sandbox.py")
    specs_by_name = method_specs(helper.read_text() + "\n" + source if helper.exists() else source)
    for i, line in enumerate(source.splitlines(), 1):
        codes = {int(c) for c in re.findall(r'(?<!!)==\s*"?(\d{3})\b', line)}
        codes |= {int(c) for group in re.findall(r'in \(([0-9, ]+)\)', line) for c in re.findall(r'\d{3}', group)}
        if not codes:
            continue
        for match in re.finditer(r'f?"(/v1/[^"?]*)', line):
            url = re.sub(r'\{[^}]*\}', 'x', match.group(1))
            if url.endswith('/') and re.match(r'"\s*\+', line[match.end():]):
                url += 'x'
            selected = statement_method(line, match.start(), specs_by_name)
            reason = check(selected, url, codes, specs)
            if reason is None:
                verified += 1
            else:
                record = f'{path.name}:{i}: {selected or "?"} {match.group(1)}: {reason}'
                (unresolved if reason.startswith('UNRESOLVED') else violations).append(record)
    return {'verified': verified, 'violations': violations, 'unresolved': unresolved}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('deploy', nargs='?', type=Path, default=WS / 'deploy')
    p.add_argument('--strict', action='store_true')
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    result = scan(a.deploy / 'scripts/e2e_steps.py')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if a.out:
        a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return int(bool(result['violations'] or (a.strict and result['unresolved'])))


if __name__ == '__main__':
    sys.exit(main())
