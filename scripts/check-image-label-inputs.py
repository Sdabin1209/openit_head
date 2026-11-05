#!/usr/bin/env python3
"""영역 이미지가 실제로 낸 라벨이 계약과 그 라벨을 받는 deploy 단계의 입력 스키마를 통과하는지 대조한다(기동 없음).

입력: deploy 작업 트리(인자 1)의 build/images.env(서비스=로컬 이미지)와 compose*.yaml, 이미지 라벨(docker image inspect).
대조(서비스 x 라벨):
  1 라벨 묶음 전체 -> 계약 ImageLabels
  2 io.openit.exposure -> 계약 Exposure, io.openit.jobs -> 계약 JobsDeclaration, io.openit.database -> 계약 DatabaseDeclaration
  3 compose 의 잡 서비스(deploy JOB_NAMES 의 키) -> 그 서비스 이미지의 선언에 그 잡 이름이 있다 -> deploy 내부 스키마 JobOverlayRequest 항목을 통과한다
  4 영역 게이트웨이를 거치는 서비스(io.openit.exposure 를 읽는 compose 서비스: 헤드 규칙 5 의 대상)는 라벨이 있다
  5 DB 서비스(이름이 -db 로 끝나는 서비스)는 io.openit.database 가 있고 DbSecretsRequest.declaration 으로 쓸 수 있다
왜 헤드 도구인가: 영역 사이 입력(계약)과 그것을 받는 쪽 스키마의 대조라서 영역 간 책임(구조 규칙 6)이다. deploy 코드는 import 하지 않는다(상수는 ast 로 읽는다).
변이 확인(2026-11-05): deploy c723925 에 돌리면 JobOverlayRequest jobs/24 ops-feedback-migrate 를 잡는다(1건). c3139a0 에서는 0건이다.
빌드하지 않은 변형(model-serving-gpu)은 "빌드 안 됨"으로 따로 낸다(통과로 세지 않는다).
종료 코드: 어긋남 0 이면 0, 있으면 1, 입력이 없으면 2. 값·비밀은 출력하지 않는다(라벨 내용 대신 칸 경로와 스키마 메시지만).
"""
import ast
import json
import pathlib
import re
import subprocess
import sys

import jsonschema
from referencing import Registry, Resource

WS = pathlib.Path(__file__).resolve().parents[2]
BC = WS / "boundary-contracts/boundary_contracts/schemas"


def load_dir(d):
    out = {}
    for f in d.glob("*.json"):
        s = json.loads(f.read_text(encoding="utf-8"))
        out[f.name] = s
    return out


def validator(schemas, name):
    reg = Registry().with_resources([(n, Resource.from_contents(s)) for n, s in schemas.items()] + [(s.get("$id", n), Resource.from_contents(s)) for n, s in schemas.items()])
    s = schemas[name if name.endswith(".json") else name + ".schema.json"]
    return jsonschema.Draft202012Validator(s, registry=reg, format_checker=jsonschema.FormatChecker())


def errs(v, doc):
    return ["/".join(map(str, e.absolute_path)) + ": " + e.message[:160] for e in v.iter_errors(doc)][:3]


def module_dict(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for st in tree.body:
        if isinstance(st, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in st.targets):
            return ast.literal_eval(st.value)
    raise SystemExit(f"{path}: {name} 를 상수로 읽지 못했다")


def main():
    if len(sys.argv) != 2:
        print("사용: check-image-label-inputs.py <deploy 작업 트리>", file=sys.stderr)
        return 2
    D = pathlib.Path(sys.argv[1])
    env = D / "build/images.env"
    if not env.exists():
        print(f"입력 없음: {env}(build-images.sh 를 먼저)", file=sys.stderr)
        return 2
    images = {}
    for line in env.read_text().splitlines():
        f = line.split()   # images.env 한 줄: <서비스> <로컬 이미지> <커밋> <의존 태그>
        if len(f) >= 2 and re.fullmatch(r"[a-z0-9-]+", f[0]):
            images[f[0]] = f[1]
    bc = load_dir(BC)
    dep = load_dir(D / "schemas")
    V = {n: validator(bc, n) for n in ("ImageLabels", "Exposure", "JobsDeclaration", "DatabaseDeclaration")}
    VO = validator(dep, "JobOverlayRequest")
    gj = D / "openit_deploy/wiring/cli_gen_jobs.py"
    JOB_NAMES = module_dict(gj, "JOB_NAMES")
    labels, bad, checked = {}, [], 0
    for svc, ref in sorted(images.items()):
        r = subprocess.run(["docker", "image", "inspect", ref, "--format", "{{json .Config.Labels}}"], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(f"{svc}: 이미지 {ref} 를 읽지 못했다")
            continue
        lb = json.loads(r.stdout) or {}
        labels[svc] = lb
        checked += 1
        bad += [f"{svc}: ImageLabels {e}" for e in errs(V["ImageLabels"], lb)]
        for key, sch in (("io.openit.exposure", "Exposure"), ("io.openit.jobs", "JobsDeclaration"), ("io.openit.database", "DatabaseDeclaration")):
            if key in lb:
                checked += 1
                try:
                    doc = json.loads(lb[key])
                except ValueError:
                    bad.append(f"{svc}: {key} 가 JSON 이 아니다")
                    continue
                bad += [f"{svc}: {key} -> {sch} {e}" for e in errs(V[sch], doc)]
    # compose 서비스 -> 이미지 서비스 이름(…/openit/<이름>@${…})
    svc_img, svc_img_all, variants = {}, set(), []
    import yaml

    class L(yaml.SafeLoader):   # compose 의 병합 태그(!reset, !override)는 값만 읽는다
        pass
    L.add_multi_constructor("!", lambda loader, suffix, node: loader.construct_scalar(node) if isinstance(node, yaml.ScalarNode) else
                            (loader.construct_sequence(node) if isinstance(node, yaml.SequenceNode) else loader.construct_mapping(node)))
    for f in sorted(D.glob("compose*.yaml")):
        y = yaml.load(f.read_text(encoding="utf-8"), Loader=L) or {}
        for cs, body in (y.get("services") or {}).items():
            svc_img_all.add(cs)
            m = re.search(r"/openit/([a-z0-9-]+)@", str((body or {}).get("image", "")))
            if m:
                # 같은 서비스를 여러 compose 파일이 다른 이미지로 줄 수 있다(model-serving: CPU / GPU 변형). 기본 compose.yaml 쪽을 앞에 둔다
                if f.name == "compose.yaml" or cs not in svc_img:
                    svc_img[cs] = (m.group(1), f.name)
                variants.append((cs, m.group(1), f.name))
    jobs = []
    for cs, job in sorted(JOB_NAMES.items()):
        checked += 1
        if cs not in svc_img:
            bad.append(f"JOB_NAMES {cs}: compose 서비스가 없다")
            continue
        img, cf = svc_img[cs]
        lb = labels.get(img)
        if lb is None:
            bad.append(f"{cf}:{cs}: 이미지 {img} 가 빌드 목록(images.env)에 없다")
            continue
        decl = json.loads(lb.get("io.openit.jobs", "null") or "null")
        if not decl:
            bad.append(f"{cf}:{cs}: 이미지 {img} 에 io.openit.jobs 가 없다")
            continue
        j = next((x for x in decl.get("jobs", []) if x.get("name") == job), None)
        if j is None:
            bad.append(f"{cf}:{cs}: 이미지 {img} 선언에 잡 {job} 가 없다: {[x.get('name') for x in decl.get('jobs', [])]}")
            continue
        jobs.append({"compose_service": cs, "declared": j})
    if jobs:
        bad += [f"JobOverlayRequest {e}" for e in errs(VO, {"jobs": jobs})]
    # 노출을 읽는 서비스(compose 에서 영역 게이트웨이 짝이 있는 서비스)와 DB 서비스
    for cs, (img, cf) in sorted(svc_img.items()):
        lb = labels.get(img)
        if lb is None:
            bad.append(f"{cf}:{cs}: 이미지 {img} 가 빌드 목록(images.env)에 없다")
            continue
        if img.endswith("-db"):
            checked += 1
            if "io.openit.database" not in lb:
                bad.append(f"{cf}:{cs}: DB 이미지 {img} 에 io.openit.database 가 없다")
    # 영역 게이트웨이: compose 의 <서비스>-gw 짝(deploy gen-gateways 와 같은 선택). 짝 서비스 이미지에 노출 라벨이 있고 GatewayExposureRequest 를 통과한다
    VG = validator(dep, "GatewayExposureRequest")
    for gwname in sorted(n for n in svc_img_all if n.endswith("-gw")):
        cs = gwname[:-3]
        checked += 1
        img = svc_img.get(cs, (None,))[0]
        lb = labels.get(img)
        if lb is None or "io.openit.exposure" not in lb:
            bad.append(f"게이트웨이 {gwname}: 짝 서비스 {cs} 의 이미지({img})에 io.openit.exposure 가 없다")
            continue
        bad += [f"GatewayExposureRequest {cs} {e}" for e in errs(VG, {"service": cs, "labels": lb, "declaration_errors": []})]
    unbuilt = sorted({(cs, img, cf) for cs, img, cf in variants if img not in labels})
    for cs, img, cf in unbuilt:
        print(f"빌드 안 됨(대조 못 함): {cf}:{cs} -> {img}")
    print(f"이미지 {len(labels)}개, compose 서비스 {len(svc_img)}개, 잡 {len(JOB_NAMES)}개, 대조 {checked}건, 어긋남 {len(bad)}건")
    for b in bad:
        print("어긋남", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
