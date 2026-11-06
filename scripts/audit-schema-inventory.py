#!/usr/bin/env python3
"""Inventory every source schema and retain per-file audit evidence.

This is a census, not a proof of all business semantics. Missing evidence remains
unreviewed. It never starts services or sends a request to a declared endpoint.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,re,subprocess,sys
from pathlib import Path
from urllib.parse import urljoin
import jsonschema
from referencing import Registry,Resource
from referencing.jsonschema import DRAFT202012
import survey_schema

WS=Path(__file__).resolve().parents[2]
AREAS=['survey-service','question-authoring','ops-feedback','release-gate','model-runtime','model-lab','synthetic-data','admin-console','kiosk-frontend']
DEPLOY=WS/'deploy/build/wt-deploy-450-lg'
ROOTS={a:WS/a/'schemas' for a in AREAS}
ROOTS.update({'boundary-contracts':WS/'boundary-contracts/boundary_contracts/schemas','survey-domain':WS/'survey-service/schema/schemas','deploy':DEPLOY/'schemas'})
SCHEMA_MAPS={'properties','patternProperties','dependentSchemas','$defs','definitions'}
SCHEMA_ARRAYS={'allOf','anyOf','oneOf','prefixItems'}
SCHEMA_CHILDREN={'items','contains','additionalProperties','unevaluatedProperties','propertyNames','not','if','then','else','additionalItems','unevaluatedItems','contentSchema'}


def nodes(node):
    if not isinstance(node,dict):return
    yield node
    for key,value in node.items():
        if key in SCHEMA_MAPS and isinstance(value,dict):
            for child in value.values():yield from nodes(child)
        elif key in SCHEMA_ARRAYS and isinstance(value,list):
            for child in value:yield from nodes(child)
        elif key in SCHEMA_CHILDREN:
            if isinstance(value,list):
                for child in value:yield from nodes(child)
            else:yield from nodes(value)


def transform(node):
    if not isinstance(node,dict):return node
    result=copy.deepcopy(node)
    for target in nodes(result):
        refs=[]
        if isinstance(target.get('x-contract'),str):
            name,_,fragment=target['x-contract'].partition('#')
            refs.append((ROOTS['boundary-contracts']/(name+'.schema.json')).as_uri()+('#'+fragment if fragment else ''))
        if isinstance(target.get('x-survey-schema'),str):refs.append('https://openit.example/survey/v1/'+target['x-survey-schema']+'.json')
        if refs:target.setdefault('allOf',[]).extend({'$ref':ref} for ref in refs)
    return result


def owner_resource(uri):
    prefix='https://openit.example/survey/v1/'
    if not uri.startswith(prefix):raise ValueError('unregistered schema owner')
    name=uri[len(prefix):].removesuffix('.json')
    doc=survey_schema.load_schema(name,version=1)
    return Resource.from_contents({**doc,'$id':uri},default_specification=DRAFT202012)


def registry(area,docs):
    result=Registry(retrieve=owner_resource)
    # Canonical resources plus the same filename aliases that area wiring uses.
    source={**docs['boundary-contracts'],**docs[area]}
    for name,(path,raw) in source.items():
        doc={**transform(raw),'$id':path.as_uri()}
        resource=Resource.from_contents(doc,default_specification=DRAFT202012)
        result=result.with_resource(path.as_uri(),resource)
        result=result.with_resource((ROOTS[area]/path.name).as_uri(),resource)
        if name in docs['boundary-contracts']:
            result=result.with_resource((ROOTS[area].parent/'boundary'/path.name).as_uri(),resource)
        if raw.get('$id'):result=result.with_resource(urljoin(ROOTS[area].as_uri()+'/',raw['$id']),resource)
    return result


def reference_errors(raw,base,reg):
    seen=set();errors=[]
    def visit(doc,scope):
        for node in nodes(doc):
            scope2=urljoin(scope,node.get('$id',''))
            if '$ref' not in node:continue
            ref=node['$ref'];absolute=urljoin(scope2,ref)
            if absolute in seen:continue
            seen.add(absolute)
            try:
                resolved=reg.resolver(base_uri=scope2).lookup(ref)
                visit(resolved.contents,absolute.split('#')[0])
            except Exception as error:errors.append({'reference':ref,'error':type(error).__name__})
    visit(raw,base)
    return errors


def fixtures(area,name):
    if area=='boundary-contracts':
        root=WS/'boundary-contracts'
        good=[p for p in (root/'examples').glob(name+'*.json') if p.name.split('.')[0]==name]
        bad=list((root/'conformance/examples_invalid').glob(name+'.*.json'))
    elif area=='survey-domain':
        good=list((ROOTS[area]/'examples').glob(name+'.valid*.json'))
        bad=list((ROOTS[area]/'examples').glob(name+'.invalid*.json'))
    else:
        folder=ROOTS[area]/'examples'
        good=list(folder.glob(name+'.valid*.json'));bad=list(folder.glob(name+'.invalid*.json'))
    return sorted(good),sorted(bad)


def strings(value,path=()):
    if isinstance(value,str):yield path,value
    elif isinstance(value,dict):
        for key,item in value.items():yield from strings(item,path+(key,))
    elif isinstance(value,list):
        for key,item in enumerate(value):yield from strings(item,path+(key,))


def replace(value,path,item):
    result=copy.deepcopy(value)
    if not path:return item
    cursor=result
    for key in path[:-1]:cursor=cursor[key]
    cursor[path[-1]]=item
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--cases',type=Path,required=True)
    args=parser.parse_args();docs={};rows=[];cases=[]
    for area,root in ROOTS.items():
        docs[area]={}
        for path in sorted(root.glob('*.json')):
            name=path.name.removesuffix('.schema.json').removesuffix('.json')
            try:raw=json.loads(path.read_text())
            except Exception:raw=None
            docs[area][name]=(path,raw)
    for area,documents in docs.items():
        reg=registry(area,docs)
        for name,(path,raw) in documents.items():
            row={'area':area,'name':name,'path':str(path.relative_to(WS)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'issues':[],'unreviewed':['business_semantics','complete_rule_test_coverage']}
            rows.append(row)
            try:jsonschema.Draft202012Validator.check_schema(raw)
            except Exception as error:row['issues'].append({'kind':'invalid_schema','error':type(error).__name__});continue
            transformed={**transform(raw),'$id':path.as_uri()}
            unresolved=reference_errors(transformed,path.as_uri(),reg)
            if unresolved:row['issues'].append({'kind':'unresolved_reference','details':unresolved})
            v=jsonschema.Draft202012Validator(transformed,registry=reg,format_checker=jsonschema.FormatChecker())
            good,bad=fixtures(area,name)
            row.update(valid_examples=len(good),invalid_examples=len(bad),formats=sorted({n['format'] for n in nodes(raw) if 'format'in n}))
            if area in AREAS+['deploy'] and (not good or not bad):row['issues'].append({'kind':'missing_required_fixture_polarity'})
            for expected,paths in [(True,good),(False,bad)]:
                for file in paths:
                    try:
                        value=json.loads(file.read_text())
                        selected=v
                        fragment=''
                        parts=file.stem.split('.')
                        if area=='boundary-contracts' and len(parts)>1 and 'type' not in raw and parts[1] in raw.get('$defs',{}):
                            fragment='#/$defs/'+parts[1]
                            selected=v.evolve(schema={'$ref':path.as_uri()+fragment})
                        errors=list(selected.iter_errors(value))
                        if area=='boundary-contracts' and isinstance(value,dict):
                            for key,spec in raw.get('properties',{}).items():
                                if key in value and spec.get('contentMediaType')=='application/json' and 'contentSchema' in spec:
                                    try:contents=json.loads(value[key])
                                    except ValueError:errors.append('invalid JSON content');continue
                                    errors.extend(v.evolve(schema={'$id':path.as_uri(),**spec['contentSchema']}).iter_errors(contents))
                        actual=not errors
                    except Exception as error:
                        row['issues'].append({'kind':'fixture_check_unresolved','file':str(file.relative_to(WS)),'error':type(error).__name__});continue
                    if expected!=actual:row['issues'].append({'kind':'fixture_verdict_mismatch','file':str(file.relative_to(WS)),'expected':expected,'rules':sorted({str(getattr(e,'validator','contentSchema')) for e in errors})})
                    if not expected or not actual:continue
                    for pointer,text in strings(value):
                        replacement=None
                        if re.match(r'^\d{4}-\d{2}-\d{2}T',text):replacement='2026-02-30T00:00:00Z'
                        elif text.startswith(('http://','https://')):replacement='https://[invalid-ipv6]/path'
                        if replacement is None:continue
                        mutated=replace(value,pointer,replacement)
                        try:errors=list(selected.iter_errors(mutated))
                        except Exception:continue
                        if errors and any(e.validator=='format' for e in errors):
                            cases.append({'area':area,'name':name,'fixture':str(file.relative_to(WS)),'pointer':list(pointer),'fragment':fragment,'control':value,'document':mutated,'expected':False})
            row['definition_checked']=not unresolved
    report={'schema_files':len(rows),'openapi_documents':7,'rows':rows,'format_probe_cases':len(cases)}
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');args.cases.write_text(json.dumps(cases,ensure_ascii=False)+'\n')
    print(json.dumps({'schema_files':len(rows),'schemas_with_findings':sum(bool(r['issues']) for r in rows),'format_probe_cases':len(cases)},ensure_ascii=False))

if __name__=='__main__':main()
