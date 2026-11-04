#!/usr/bin/env python3
"""경계 전수 점검(2026-11-04, 사용자 지시 "컴포넌트 목록에서 출발해 빈틈없음을 보장"). 종료 코드 0 = 빈칸 0건.

왜: 계약 문서끼리 대조하면 계약에 없는 경계는 목록에 오를 수 없다. 그래서 실제로 돌아가는 구성(deploy compose)의
서비스 하나하나에서 출발해, 그 서비스가 받는 입력(이미지·환경 변수·마운트)이 계약에 짝이 있는지 기계로 본다.

규칙(정본: boundary-contracts CONVENTIONS 13절, 3.4.10~):
1) 이미지: openit/<이름> 은 PublishRequest.service 에 있어야 한다. deploy 배포 도구(pause·util 이미지)만 예외(배포 때 설정, 13절 예외).
   그 밖의 이미지(공식 postgres·keycloak·oauth2-proxy 를 직접 띄우기 등)는 빈칸이다 — 받는 영역 이미지로 내야 한다.
2) 환경 변수: 이미지 이름 → 받는 쪽 Env 스키마(아래 표). 이름 또는 이름+_FILE 이 그 스키마나 CommonEnv 에 있어야 한다. SSL_CERT_FILE 은 IN-ROOT.
3) 마운트 대상 경로: 받는 쪽 Env 스키마의 경로 기본값(또는 그 아래), 또는 이미지가 선언한 VOLUME(docker image inspect), 또는 deploy 도구.
   이미지가 이 PC 에 없으면 VOLUME 을 확인하지 못한 것으로 세고 실패로 둔다(확인 못한 것을 통과로 세지 않는다).

사용: python3 head/scripts/check-boundary-coverage.py --deploy <deploy 작업 트리>   (--self-test: 규칙을 어긴 입력이 실패하는지)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

WS = Path(__file__).resolve().parents[2]
SCHEMAS = WS / "boundary-contracts" / "boundary_contracts" / "schemas"
COMPOSE = ["compose.yaml", "compose.monitoring.yaml", "compose.inference.yaml"]
DEPLOY_TOOLS = {"pause", "util"}   # 배포 도구 이미지(locks 의 PAUSE_IMAGE·UTIL_IMAGE): 배포 때 설정 예외
# 이미지 이름 → 받는 쪽 Env 스키마(PublishRequest.service 와 같은 이름). 영역 서비스 Env 는 각 영역 소유 이름.
ENV_OF = {
    "survey-service": "SurveyServiceEnv", "question-authoring": "QuestionAuthoringEnv", "ops-feedback": "OpsFeedbackServerEnv",
    "release-gate": "GateEnv", "model-registry": "ModelRegistryEnv", "dataset-store": "DatasetStoreEnv",
    "model-serving": "ModelServingEnv", "model-serving-gpu": "ModelServingEnv", "kiosk-frontend": "KioskFrontendEnv",
    "admin-console": "AdminConsoleEnv", "area-gateway": "AreaGatewayEnv", "public-ingress": "PublicIngressEnv",
    "monitoring": "MonitoringEnv", "backup-store": "BackupStoreEnv", "step-ca": "StepCaEnv", "identity": "IdentityEnv",
    "identity-proxy": "IdentityProxyEnv", "identity-db": "AreaDatabaseEnv", "survey-db": "AreaDatabaseEnv",
    "question-authoring-db": "AreaDatabaseEnv", "ops-feedback-db": "AreaDatabaseEnv", "release-gate-db": "AreaDatabaseEnv",
}


def schema_names(name: str) -> tuple[set[str], set[str]]:
    """(환경 이름 집합, 경로 기본값 집합)."""
    s = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    names: set[str] = set()
    paths: set[str] = set()

    def walk(o):   # 스키마 어디에 있든(properties.env.properties 처럼 안쪽 포함) 대문자 환경 이름과 경로 기본값을 모은다
        if isinstance(o, dict):
            for k, v in (o.get("properties") or {}).items():
                if re.match(r"^[A-Z][A-Z0-9_]*$", k):
                    names.add(k)
                    if isinstance(v, dict) and isinstance(v.get("default"), str) and v["default"].startswith("/"):
                        paths.add(v["default"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(s)
    return names, paths


def required_names(name: str) -> set[str]:
    """받는 쪽 Env 스키마의 최상위 required(필수 입력). deploy 가 NAME 또는 NAME_FILE 로 넘겨야 한다(3.4.13 보강: 반대 방향)."""
    s = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    return {r for r in s.get("required", []) if re.match(r"^[A-Z][A-Z0-9_]*$", r)}


def publishable() -> set[str]:
    s = (SCHEMAS / "PublishRequest.schema.json").read_text(encoding="utf-8")
    m = re.search(r'"service"\s*:\s*\{[^}]*"enum"\s*:\s*\[([^\]]*)\]', s, re.S)
    return set(re.findall(r'"([a-z0-9-]+)"', m.group(1))) if m else set()


def image_key(image: str) -> str | None:
    if not image:
        return None
    m = re.search(r"openit/([a-z0-9-]+)@", image)
    if m:
        return m.group(1)
    m = re.match(r"\$\{([A-Z_]+)_IMAGE", image)
    if m:
        k = m.group(1).lower()      # PAUSE_IMAGE → pause, UTIL_IMAGE → util, POSTGRES_IMAGE → postgres ...
        # compose.inference.yaml 은 다른 서버라 이미지 변수 이름에 INFERENCE_ 가 붙는다(같은 게시 이미지)
        return {"inference": "model-serving", "inference_gateway": "area-gateway", "inference_step": "step-ca",
                "inference_pause": "pause", "inference_util": "util"}.get(k, k)
    return image.split(":")[0].split("/")[-1]


def image_volumes(key: str) -> set[str] | None:
    r = subprocess.run(["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"], capture_output=True, text=True)
    cand = [x for x in r.stdout.split() if x.split(":")[0].endswith("/" + key) or x.split(":")[0] == key]
    for img in cand:
        r = subprocess.run(["docker", "image", "inspect", "--format", "{{json .Config.Volumes}}", img], capture_output=True, text=True)
        if r.returncode == 0:
            return set(json.loads(r.stdout.strip() or "null") or {})
    return None


def env_file_names(s: dict, base: Path | None) -> list[str]:
    """compose env_file 의 이름들. 경로의 ${VAR:-기본} 은 기본값으로 푼다. 파일이 없으면 이름 없음(그 서비스의 필수 입력 점검이 잡는다)."""
    out: list[str] = []
    files = s.get("env_file") or []
    files = [files] if isinstance(files, (str, dict)) else files
    for f in files:
        f = f.get("path") if isinstance(f, dict) else f
        f = re.sub(r"\$\{[A-Z_]+:-([^}]*)\}", r"\1", str(f))
        p = (base / f) if base and not f.startswith("/") else Path(f)
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^\s*([A-Z][A-Z0-9_]*)\s*=", line)
                if m:
                    out.append(m.group(1))
    return out


def check(services: dict[str, dict], deploy_dir: Path | None = None) -> list[str]:
    bad: list[str] = []
    common, _ = schema_names("CommonEnv")
    pub = publishable()
    for name, s in sorted(services.items()):
        key = image_key(str(s.get("image") or ""))
        if key in DEPLOY_TOOLS:
            continue
        if key not in pub:
            bad.append(f"{name}: 이미지 '{key}' 는 계약 PublishRequest 에 없다(받는 영역 이미지로 내야 한다)")
            continue
        env_schema = ENV_OF.get(key)
        if not env_schema:
            bad.append(f"{name}: 이미지 '{key}' 의 Env 스키마가 정해지지 않았다")
            continue
        names, paths = schema_names(env_schema)
        env = s.get("environment") or {}
        env_names = (list(env) if isinstance(env, dict) else [e.split("=", 1)[0] for e in env]) + env_file_names(s, deploy_dir)
        for e in env_names:
            base = e[:-5] if e.endswith("_FILE") else e
            if e in names | common or base in names | common or e == "SSL_CERT_FILE":
                continue
            bad.append(f"{name}: 환경 '{e}' 가 {env_schema}·CommonEnv 에 없다")
        given = {e[:-5] if e.endswith("_FILE") else e for e in env_names} | set(env_names)
        runs_subcommand = s.get("command") is not None   # 도우미·잡은 부명령을 돈다: 서비스 본체(serve)의 필수 입력은 요구하지 않는다(GateEnv x-note 등)
        for r in ([] if runs_subcommand else sorted(required_names(env_schema))):
            base = r[:-5] if r.endswith("_FILE") else r
            if r not in given and base not in given:
                bad.append(f"{name}: 필수 입력 '{r}' 를 deploy 가 넘기지 않는다({env_schema})")
        vols = None
        for v in s.get("volumes") or []:
            if isinstance(v, dict):
                tgt = v.get("target")
            else:   # 짧은 표기 '<원본>:<대상>[:ro]' — 원본의 ${VAR:-기본} 안 콜론은 나누지 않는다
                parts = re.split(r":(?![^{]*\})", str(v))
                tgt = parts[1] if len(parts) >= 2 else None
            if not tgt:
                continue
            if any(tgt == p or tgt.startswith(p.rstrip("/") + "/") or p.startswith(tgt.rstrip("/") + "/") for p in paths):
                continue
            if tgt == "/etc/openit/pki" or tgt.startswith("/etc/openit/pki/"):
                continue   # IN-ROOT(SSL_CERT_FILE 이 가리키는 루트 폴더, RUNTIME IN-ROOT)
            if vols is None:
                vols = image_volumes(key)
            if vols is None:
                bad.append(f"{name}: 마운트 '{tgt}' — 이미지 {key} 가 이 PC 에 없어 VOLUME 을 확인하지 못했다")
            elif tgt not in vols:
                bad.append(f"{name}: 마운트 '{tgt}' 가 {env_schema} 경로에도 이미지 VOLUME 에도 없다")
    return bad


def check_egress_names(ws: Path, pub: set[str]) -> list[str]:
    """규칙 4(CONVENTIONS 13절 서비스 이름): 영역 노출 선언의 egress 받는 쪽 이름은 게시 이미지 이름(PublishRequest.service)이다."""
    bad = []
    for f in sorted(ws.glob("*/deploy-exposure.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(d, dict) and d.get("service") and d["service"] not in pub:
            bad.append(f"{f.parent.name}: Exposure service '{d['service']}' 가 게시 이미지 이름(PublishRequest.service)이 아니다")
        for e in (d.get("egress") or []) if isinstance(d, dict) else []:
            if not e.startswith("external:") and e not in pub:
                bad.append(f"{f.parent.name}: egress '{e}' 가 게시 이미지 이름(PublishRequest.service)이 아니다")
    return bad


def exposure_services(ws: Path) -> dict[str, list]:
    """영역이 낸 노출 선언(Exposure)의 service 이름들: 각 영역 리포의 커밋된(HEAD) *exposure*.json.
    왜 HEAD 인가: 이미지는 커밋에서 빌드된다(deploy build-images 는 영역 사본의 HEAD). 작업 트리의 미커밋 파일은 아직 낸 것이 아니다."""
    import subprocess
    out: dict[str, list] = {}
    for repo in sorted(p for p in ws.iterdir() if (p / ".git").exists() and p.name not in ("deploy", "boundary-contracts", "head")):
        r = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True)
        for path in r.stdout.splitlines():
            if "exposure" not in path.rsplit("/", 1)[-1] or not path.endswith(".json") or "node_modules/" in path:
                continue
            c = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{path}"], capture_output=True, text=True)
            try:
                d = json.loads(c.stdout)
            except ValueError:
                continue
            if isinstance(d, dict) and isinstance(d.get("service"), str):
                out[d["service"]] = list(d.get("egress") or [])
    return out


def check_gateway_exposure(services: dict[str, dict], declared: set[str]) -> list[str]:
    """규칙 5(ImageLabels io.openit.exposure, 2026-11-05 E2E 에서 identity·identity-proxy 가 빠져 드러남): compose 에 영역 게이트웨이 <서비스>-gw 가 있으면
    그 서비스의 영역이 노출 선언(Exposure, service=<서비스>)을 낸다. 없으면 deploy 의 gen-gateways 가 그 게이트웨이를 만들지 못한다."""
    bad = []
    for key in services:
        n = key.split(":", 1)[1]
        if n.endswith("-gw") and n[:-3] not in declared:
            bad.append(f"{n}: 서비스 '{n[:-3]}' 의 노출 선언(Exposure service='{n[:-3]}', 이미지 라벨 io.openit.exposure)을 어느 영역도 내지 않는다")
    return bad


def check_egress_proxy(services: dict[str, dict], declared: dict[str, list]) -> list[str]:
    """규칙 6(CommonEnv.OPENIT_EGRESS_PROXY, RUNTIME R1.8, 2026-11-05 identity-proxy 가 출구를 거치지 않던 것): 노출 선언에 영역 밖 호출(egress)이 있는 서비스는
    compose 에서 OPENIT_EGRESS_PROXY 를 받는다(자기 영역 게이트웨이 CONNECT 출구). 받지 않으면 그 호출은 게이트웨이를 거치지 않는다."""
    bad = []
    for key, s in services.items():
        n = key.split(":", 1)[1]
        if declared.get(n):
            env = s.get("environment") or {}
            names = set(env) if isinstance(env, dict) else {str(e).split("=", 1)[0] for e in env}
            if "OPENIT_EGRESS_PROXY" not in names:
                bad.append(f"{n}: 노출 선언에 egress {declared[n]} 가 있는데 compose 가 OPENIT_EGRESS_PROXY(자기 게이트웨이 출구)를 주지 않는다")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", default=str(WS / "deploy" / "build" / "wt-deploy-450-lg"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        bad = check({"x": {"image": "${DEPLOY_REGISTRY}/openit/survey-service@sha", "environment": {"NOT_IN_CONTRACT": "1"}},
                     "y": {"image": "postgres:16"},
                     "z": {"image": "${DEPLOY_REGISTRY}/openit/public-ingress@sha", "environment": {"GATEWAY_HOSTS": "a"}}})
        ok = (len([b for b in bad if b.startswith("x:")]) >= 1 and len([b for b in bad if b.startswith("y:")]) == 1
              and any(b.startswith("z:") and "INGRESS_DEVICE_CA_FILE" in b for b in bad))
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "x").mkdir(); (Path(td) / "x" / "deploy-exposure.json").write_text('{"service": "ops-feedback-ingest", "egress": ["ops-feedback-ingest", "release-gate", "external:backup"]}')
            eb = check_egress_names(Path(td), publishable())
        ok = ok and len(eb) == 2 and all("ops-feedback-ingest" in x for x in eb)
        gb = check_gateway_exposure({"compose.yaml:survey-service-gw": {}, "compose.yaml:identity-gw": {}}, {"survey-service"})
        ok = ok and len(gb) == 1 and gb[0].startswith("identity-gw:")
        pb = check_egress_proxy({"compose.yaml:a": {"environment": {"OPENIT_EGRESS_PROXY": "http://127.0.0.1:3128"}}, "compose.yaml:b": {"environment": ["X=1"]}, "compose.yaml:c": {}},
                                {"a": ["x"], "b": ["y"], "c": []})
        ok = ok and len(pb) == 1 and pb[0].startswith("b:")
        print("self-test", "OK" if ok else f"FAIL {bad} {eb}")
        return 0 if ok else 1
    services: dict[str, dict] = {}
    for f in COMPOSE:
        p = Path(a.deploy) / f
        if p.exists():
            for n, s in ((yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("services") or {}).items():
                services[f"{f}:{n}"] = s
    bad = check(services, Path(a.deploy)) + check_egress_names(WS, publishable()) + check_gateway_exposure(services, (decl := exposure_services(WS))) + check_egress_proxy(services, decl)
    for b in bad:
        print(b)
    print(f"서비스 {len(services)}개, 빈칸 {len(bad)}건")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
