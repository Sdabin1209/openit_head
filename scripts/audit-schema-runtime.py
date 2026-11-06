"""Replay schema-census runtime-cases.json in the owning repository venv.

Usage: <area>/.venv/bin/python <head>/scripts/audit-schema-runtime.py AREA < runtime-cases-for-area.json
The input must contain cases for AREA only. No services are started.
"""
import json,sys,jsonschema
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from functools import lru_cache
area=sys.argv[1]
if area=='boundary-contracts':
 from boundary_contracts import validator
 def check(name,doc,fragment):return validator(name+fragment).is_valid(doc)
elif area=='survey-service':
 from survey_service.types.validation import errors
 def check(name,doc,fragment):return not errors(name,doc)
elif area=='question-authoring':
 from question_authoring.wiring.schemas import problems
 def check(name,doc,fragment):return not problems(name,doc)
elif area=='ops-feedback':
 from ops_feedback.wiring.validate import validator
 def check(name,doc,fragment):return validator(name).is_valid(doc)
elif area=='model-lab':
 from model_lab.wiring.schemas import validator
 def check(name,doc,fragment):return validator(name).is_valid(doc)
elif area=='release-gate':
 from release_gate.types.validators import validate
 def check(name,doc,fragment):
  from boundary_contracts import BoundaryError
  try:validate(name,doc);return True
  except BoundaryError:return False
elif area=='synthetic-data':
 from synthetic_data.types.schema_registry import codes
 def check(name,doc,fragment):return not codes(name,doc)
elif area=='model-runtime':
 from model_runtime.wiring.schema_gate import violations
 def check(name,doc,fragment):return not violations(name,doc)
elif area=='deploy':
 from openit_deploy.wiring.schema_check import errors
 def check(name,doc,fragment):return not errors(name,doc)
else:raise ValueError(area)
results=[]
for item in json.load(sys.stdin):
 try:
  control=check(item['name'],item['control'],item.get('fragment',''))
  mutated=check(item['name'],item['document'],item.get('fragment',''))
  results.append({k:item[k] for k in ['area','name','fixture','pointer']}|{'control_accepted':control,'invalid_accepted':mutated})
 except Exception as error:
  results.append({k:item[k] for k in ['area','name','fixture','pointer']}|{'unresolved':type(error).__name__})
print(json.dumps({'date_time_registered':'date-time' in jsonschema.FormatChecker.checkers,'uri_registered':'uri' in jsonschema.FormatChecker.checkers,'results':results}))
