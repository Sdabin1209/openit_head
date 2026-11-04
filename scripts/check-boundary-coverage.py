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


EXEC_RE = re.compile(r'(?:\bdocker|"\$DOCKER"|\$DOCKER|\bdc\b[^|;\n]*|\bcompose\b[^|;\n]*)\s+exec\s+(?:-[a-zA-Z]+\s+)*["$\w]' + r"|[\"']exec[\"']\s*[,)\]]")   # 문서 문장의 'exec/run' 은 명령이 아니다. 파이썬 목록 형식("exec", ...)도 잡는다
TOOL_RE = re.compile(r'RESTIC_IMAGE|backup_restic\b|\$\{?UTIL(?:_REF)?\b|PAUSE')   # deploy 배포·백업 도구 이미지(제3자 도구, deploy 자기 데이터): 영역 이미지가 아니다
ENTRY_RE = re.compile(r'--entrypoint\b')
AREA_IMG_RE = re.compile(r'openit/(?!pause|util)[a-z][a-z0-9-]*@|\$\{?(?!UTIL|PAUSE)[A-Z_]*_DIGEST\b|\bIMG\b|\$\(cn ')


def check_no_area_internals(deploy_dir: Path, ref: str = "HEAD") -> list[str]:
    """규칙 7(CONVENTIONS 13절, 3.4.16: deploy 는 환경을 한 번 구성하고 실행 중에 영역 안으로 들어가지 않는다. 영역 사이 통신은 게이트웨이):
    deploy 의 운영·시험 스크립트(커밋된 판)가 (a) 컨테이너 안에서 명령을 실행(docker exec, compose exec)하거나
    (b) 영역 이미지를 진입점 바꾸기·부명령으로 띄우면(--entrypoint, openit 영역 이미지 docker run) 빈칸이다.
    허용: 서비스 기동, JobsDeclaration 잡 실행(compose run job-*), deploy 도구 이미지(util·pause)·백업 도구 이미지 실행, deploy 자기 시험(scripts/test*)."""
    bad = []
    r = subprocess.run(["git", "-C", str(deploy_dir), "ls-tree", "-r", "--name-only", ref], capture_output=True, text=True)
    for path in r.stdout.splitlines():
        if not (path.startswith("scripts/") or path.startswith("ansible/")) or not path.endswith((".sh", ".py", ".yml")):
            continue
        name = path.rsplit("/", 1)[-1]
        if name.startswith("test"):
            continue
        text = subprocess.run(["git", "-C", str(deploy_dir), "show", f"{ref}:{path}"], capture_output=True, text=True).stdout
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith("#") or s.startswith('"""') or not s:
                continue
            code = s.split("  #", 1)[0]
            if EXEC_RE.search(code):
                bad.append(f"{path}:{i}: 컨테이너 안 실행(exec) — deploy 는 실행 중에 영역 안으로 들어가지 않는다: {code[:110]}")
            elif TOOL_RE.search(code):
                continue
            elif ENTRY_RE.search(code) or (re.search(r'(?:docker|\$DOCKER"?)\s+run\b', code) and AREA_IMG_RE.search(code)):
                bad.append(f"{path}:{i}: 영역 이미지의 내부 명령 호출(run/--entrypoint) — 잡 선언·환경 구성만 쓴다: {code[:110]}")
    return bad


# 규칙 8(닫힌 목록, Compose Specification 의 service 키): 영역 이미지를 쓰는 서비스의 키를 모두 분류한다. 분류표에 없는 키는 빈칸이다(새 키가 몰래 들어오지 못하게).
#  "rule": 다른 규칙이 내용을 대조한다(1 이미지, 2 환경, 3 마운트·비밀·설정, 6 출구, 9 망).
#  "env": 순수 환경(자원·보안·수명·로그·순서) — 컴포넌트 내부를 몰라도 쓸 수 있다(deploy 는 환경을 구성한다).
#  "internal": 컴포넌트 내부(실행 명령·확인 명령·이미지 사용자·다른 컨테이너 볼륨)를 알아야 쓰는 키 — 영역 이미지에 쓰면 빈칸.
#   대신: 실행 방식은 이미지 기본값 또는 계약 Env 의 값, 확인은 이미지 HEALTHCHECK, 사용자는 이미지 USER, 볼륨은 계약 출력 마운트.
KEY_CLASS = {
    "image": "rule", "environment": "rule", "env_file": "rule", "volumes": "rule", "tmpfs": "rule", "secrets": "rule", "configs": "rule",
    "networks": "rule", "network_mode": "rule", "ports": "rule", "extra_hosts": "rule",
    "cap_add": "env", "cap_drop": "env", "cpus": "env", "mem_limit": "env", "pids_limit": "env", "shm_size": "env", "read_only": "env",
    "security_opt": "env", "sysctls": "env", "restart": "env", "stop_grace_period": "env", "logging": "env", "depends_on": "env",
    "profiles": "env", "container_name": "env", "group_add": "env",   # group_add: deploy 자기 비밀 파일의 읽기 그룹(deploy 소유 권한)
    "command": "internal", "entrypoint": "internal", "healthcheck": "internal", "user": "internal", "volumes_from": "internal",
}
JOB_SERVICE_RE = re.compile(r"^job-")   # JobsDeclaration 잡: 명령은 이미지 라벨 io.openit.jobs 에서 온다(덧씌우기 파일). compose 의 자리표시 command 는 잡 정의가 대신한다


def check_compose_keys(services: dict[str, dict]) -> list[str]:
    bad = []
    for key, s in services.items():
        n = key.split(":", 1)[1]
        img = str((s or {}).get("image", ""))
        if not re.search(r"openit/(?!pause|util)|_DIGEST|INFERENCE_IMAGE", img):
            continue
        for k in (s or {}):
            c = KEY_CLASS.get(k)
            if c is None:
                bad.append(f"{key}: compose 키 '{k}' 가 분류표(KEY_CLASS)에 없다 — 분류하고 규칙을 붙인다")
            elif c == "internal" and not (k == "command" and JOB_SERVICE_RE.match(n)):
                bad.append(f"{key}: '{k}' 는 영역 이미지 내부를 아는 키다(이미지 기본값·HEALTHCHECK·USER·계약 Env 로)")
    return bad


AREA_REPOS = ["survey-service", "question-authoring", "ops-feedback", "release-gate", "model-lab", "synthetic-data", "model-runtime",
              "kiosk-frontend", "admin-console", "platform"]
ENV_READ_RES = [
    re.compile(r'(?:os\.environ|environ|\benv)\s*\[\s*["\']([A-Z][A-Z0-9_]+)["\']'),
    re.compile(r'(?:os\.environ|environ|\benv)\.get\(\s*["\']([A-Z][A-Z0-9_]+)["\']'),
    re.compile(r'os\.getenv\(\s*["\']([A-Z][A-Z0-9_]+)["\']'),
    re.compile(r'read_secret\(\s*["\']([A-Z][A-Z0-9_]+)["\']'),
    re.compile(r'process\.env(?:\.([A-Z][A-Z0-9_]+)|\[\s*["\']([A-Z][A-Z0-9_]+)["\']\s*\])'),
    re.compile(r'os\.(?:Getenv|LookupEnv)\(\s*"([A-Z][A-Z0-9_]+)"'),
    re.compile(r'\$\{([A-Z][A-Z0-9_]{2,})(?::?[-?=+])'),
]
# 실행 환경의 표준 변수(POSIX·언어 런타임·TLS): 계약 밖 경계 값이 아니다
STD_ENV = {"PATH", "HOME", "USER", "HOSTNAME", "TZ", "LANG", "LC_ALL", "TMPDIR", "PWD", "SHELL", "TERM", "SSL_CERT_FILE", "SSL_CERT_DIR",
           "PYTHONPATH", "PYTHONUNBUFFERED", "PYTHONDONTWRITEBYTECODE", "NODE_ENV", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "XDG_CACHE_HOME", "CI",
           "SOURCE_DATE_EPOCH",                                             # reproducible-builds.org 표준
           "PGDATA", "POSTGRES_USER", "POSTGRES_DB", "POSTGRES_PASSWORD_FILE", "POSTGRES_INITDB_ARGS"}   # postgres 공식 이미지(DB 이미지의 기반)가 정한 이름
WSGI_KEYS = re.compile(r"^(REQUEST_METHOD|PATH_INFO|SCRIPT_NAME|QUERY_STRING|CONTENT_TYPE|CONTENT_LENGTH|SERVER_NAME|SERVER_PORT|SERVER_PROTOCOL|REMOTE_ADDR|REQUEST_URI|RAW_URI|HTTP_[A-Z0-9_]*)$")   # PEP 3333 요청 환경(프로세스 환경이 아니다)


def env_schema_names(repo: str) -> set[str]:
    names = set()
    for p in SCHEMAS.glob("*Env.schema.json"):
        s = json.loads(p.read_text(encoding="utf-8"))
        cons = s.get("x-consumers") or []
        if "*" in cons or repo in cons:
            names |= schema_names(p.name[: -len(".schema.json")])[0]
    return names


def check_area_env_reads(ws: Path) -> list[str]:
    """규칙 10(구조 규칙 4: 컴포넌트는 자기 입력 스키마만 안다): 영역 코드(커밋된 판, 시험·개발 스크립트 제외)가 읽는 환경 변수 이름은
    그 영역이 받는 Env 스키마(x-consumers)·CommonEnv·잡 선언(env, secret_files)·이미지 안 Dockerfile ENV·실행 표준 변수 중 하나여야 한다(NAME_FILE 은 NAME 으로도 맞춘다)."""
    bad = []
    for repo in AREA_REPOS:
        rp = ws / repo
        if not (rp / ".git").exists():
            continue
        allowed = env_schema_names(repo) | STD_ENV
        files = subprocess.run(["git", "-C", str(rp), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True).stdout.splitlines()
        for f in files:
            base = f.rsplit("/", 1)[-1]
            if base.startswith("Dockerfile"):
                t = subprocess.run(["git", "-C", str(rp), "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
                for m in re.finditer(r'^\s*(?:ENV|ARG)\s+([A-Z][A-Z0-9_]+)', t, re.M):
                    allowed.add(m.group(1))
            if base.endswith(".json") and "jobs" in base:
                try:
                    for j in json.loads(subprocess.run(["git", "-C", str(rp), "show", f"HEAD:{f}"], capture_output=True, text=True).stdout).get("jobs", []):
                        allowed |= set(j.get("env") or []) | set(j.get("secret_files") or [])
                except (ValueError, AttributeError):
                    pass
        for f in files:
            if not f.endswith((".py", ".ts", ".tsx", ".js", ".mjs", ".go", ".sh")) or re.search(r"(^|/)(tests?|scripts|node_modules|e2e|dev|mock-server)/|\.test\.|_test\.|test_", f):
                continue
            t = subprocess.run(["git", "-C", str(rp), "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
            for i, line in enumerate(t.splitlines(), 1):
                if line.lstrip().startswith(("#", "//")):
                    continue
                for rx in ENV_READ_RES:
                    for m in rx.finditer(line):
                        n = next(g for g in m.groups() if g)
                        if WSGI_KEYS.match(n) or re.match(r"\s*=(?!=)", line[m.end():]) or re.search(r"\]\s*,\s*env\[", line):
                            continue   # 요청 환경 키, 또는 읽기가 아니라 하위 프로세스 환경에 써 넣기
                        if n in allowed or (n.endswith("_FILE") and n[:-5] in allowed) or n + "_FILE" in allowed:
                            continue
                        bad.append(f"{repo}/{f}:{i}: 환경 변수 '{n}' 를 읽는데 이 영역의 Env 스키마·CommonEnv·잡 선언·이미지 ENV 에 없다")
    return bad


URL_RE = re.compile(r'https?://([a-z][a-z0-9-]*)(?=[:/"\'\s`}]|$)')


def check_call_targets(services: dict[str, dict], ws: Path, pub: set[str], declared: dict[str, list]) -> list[str]:
    """규칙 11(RUNTIME R1.8, CONVENTIONS 13절: 영역 밖 호출은 노출 선언 egress 에 적은 상대에게만, 게이트웨이를 거쳐):
    (a) compose 가 서비스 X 에게 주는 환경 값의 URL 이 다른 서비스 Y(게시 이미지 이름)를 가리키면 Y 는 X 의 egress 에 있어야 한다.
    (b) 영역 코드(커밋된 판, 시험·개발 제외)에 적힌 URL 이 다른 서비스를 가리키면 그 영역 서비스 중 하나의 egress 에 있어야 한다."""
    bad = []
    for key, s in services.items():
        n = key.split(":", 1)[1]
        if n not in declared:
            continue
        env = s.get("environment") or {}
        vals = env.values() if isinstance(env, dict) else [str(e).split("=", 1)[-1] for e in env]
        for v in vals:
            for m in URL_RE.finditer(str(v)):
                y = m.group(1)
                if y in pub and y != n and y not in declared[n]:
                    bad.append(f"{key}: 환경 값이 '{y}' 를 부르게 하는데 {n} 의 노출 선언 egress {declared[n]} 에 없다")
    repo_egress: dict[str, set] = {}
    for repo in AREA_REPOS:
        rp = ws / repo
        if not (rp / ".git").exists():
            continue
        files = subprocess.run(["git", "-C", str(rp), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True).stdout.splitlines()
        own, eg = set(), set()
        for f in files:
            if "exposure" in f.rsplit("/", 1)[-1] and f.endswith(".json") and "node_modules/" not in f and "/tests/" not in f:
                try:
                    d = json.loads(subprocess.run(["git", "-C", str(rp), "show", f"HEAD:{f}"], capture_output=True, text=True).stdout)
                except ValueError:
                    continue
                if isinstance(d, dict) and d.get("service"):
                    own.add(d["service"]); eg |= set(d.get("egress") or [])
        for f in files:
            if not f.endswith((".py", ".ts", ".tsx", ".js", ".mjs", ".go", ".sh")) or re.search(r"(^|/)(tests?|scripts|node_modules|e2e|dev|mock-server)/|\.test\.|_test\.|test_", f):
                continue
            t = subprocess.run(["git", "-C", str(rp), "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
            for i, line in enumerate(t.splitlines(), 1):
                if line.lstrip().startswith(("#", "//", "*")):
                    continue
                for m in URL_RE.finditer(line):
                    y = m.group(1)
                    if y in pub and y not in own and y not in eg:
                        bad.append(f"{repo}/{f}:{i}: 코드가 '{y}' 를 부르는 주소를 갖는데 이 영역의 노출 선언 egress {sorted(eg)} 에 없다")
    return bad


def check_networks(services: dict[str, dict], declared: dict[str, list]) -> list[str]:
    """규칙 9(CONVENTIONS 13절, RUNTIME R1.8: 영역 사이 길은 노출 선언이 정한 호출 관계뿐): compose 망에 두 영역 이상의 서비스(네트워크 공간 <서비스>-net,
    공개 입구 gateway, backup-store)가 붙어 있으면, 그 쌍마다 한쪽의 egress 에 다른 쪽이 있어야 한다(공개 입구는 노출 선언을 낸 서비스, backup-store 는 external:backup).
    같은 영역 안의 망(DB 망, 감시 망 등 구성원이 한 영역)은 대상이 아니다. 받는 쪽은 망에서 게이트웨이(443)만 열려 있으므로 이 쌍 대조가 영역 사이 길의 전부다."""
    mem: dict[str, set] = {}
    for key, s in services.items():
        n = key.split(":", 1)[1]
        svc = n[:-4] if n.endswith("-net") else n
        if svc not in declared and svc not in ("gateway", "backup-store"):
            continue
        nets = s.get("networks") or {}
        for k in (nets if isinstance(nets, dict) else nets):
            mem.setdefault(k, set()).add(svc)

    def linked(a: str, b: str) -> bool:
        if "gateway" in (a, b):
            return (b if a == "gateway" else a) in declared   # 공개 입구는 노출 선언을 낸 서비스로 간다
        if "backup-store" in (a, b):
            return "external:backup" in declared.get(b if a == "backup-store" else a, [])
        return b in declared.get(a, []) or a in declared.get(b, [])
    bad = []
    for net, ms in sorted(mem.items()):
        ms = sorted(ms)
        for i, a in enumerate(ms):
            for b in ms[i + 1:]:
                if not linked(a, b):
                    bad.append(f"망 {net}: {a} 와 {b} 가 같은 망에 있는데 어느 쪽 노출 선언 egress 에도 서로가 없다(계약에 없는 길)")
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
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "init", "-q", td]); (Path(td) / "scripts").mkdir()
            (Path(td) / "scripts" / "a.sh").write_text('"$DOCKER" exec "$C" pg_dump -U x\n# docker exec in comment\n"$DOCKER" run --rm "$UTIL" true\n')
            (Path(td) / "scripts" / "test-x.sh").write_text('docker exec c id\n')
            subprocess.run(["git", "-C", td, "add", "-A"]); subprocess.run(["git", "-C", td, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "t"])
            xb = check_no_area_internals(Path(td))
        ok = ok and len(xb) == 1 and xb[0].startswith("scripts/a.sh:1:")
        kb = check_compose_keys({"compose.yaml:a-cert": {"image": "${DEPLOY_REGISTRY}/openit/step-ca@sha", "command": ["cert", "a"], "cpus": 1},
                                 "compose.yaml:job-a": {"image": "${DEPLOY_REGISTRY}/openit/a@sha", "command": ["sh"]},
                                 "compose.yaml:b": {"image": "${DEPLOY_REGISTRY}/openit/b@sha", "weird_key": 1},
                                 "compose.yaml:pg": {"image": "postgres:16", "command": ["x"]}})
        cb = check_call_targets({"compose.yaml:survey-service": {"environment": {"A_URL": "https://release-gate/v1", "B_URL": "https://ops-feedback:443/x"}}},
                                Path("/nonexistent"), publishable(), {"survey-service": ["release-gate"]})
        ok = ok and len(cb) == 1 and "'ops-feedback'" in cb[0]
        nb = check_networks({"compose.yaml:a-net": {"networks": ["x", "y"]}, "compose.yaml:b-net": {"networks": ["x"]}, "compose.yaml:c-net": {"networks": ["y"]}},
                            {"a": ["b"], "b": [], "c": []})
        ok = ok and len(nb) == 1 and "망 y" in nb[0]
        ok = ok and len(kb) == 2 and any("a-cert" in x and "'command'" in x for x in kb) and any("weird_key" in x for x in kb)
        print("self-test", "OK" if ok else f"FAIL {bad} {eb}")
        return 0 if ok else 1
    services: dict[str, dict] = {}
    for f in COMPOSE:
        p = Path(a.deploy) / f
        if p.exists():
            for n, s in ((yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("services") or {}).items():
                services[f"{f}:{n}"] = s
    bad = check(services, Path(a.deploy)) + check_egress_names(WS, publishable()) + check_gateway_exposure(services, (decl := exposure_services(WS))) + check_egress_proxy(services, decl) + check_no_area_internals(Path(a.deploy)) + check_compose_keys(services) + check_area_env_reads(WS) + check_call_targets(services, WS, publishable(), decl) + check_networks(services, decl)
    for b in bad:
        print(b)
    print(f"서비스 {len(services)}개, 빈칸 {len(bad)}건")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
