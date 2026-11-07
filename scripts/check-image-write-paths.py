#!/usr/bin/env python3
"""영역 이미지의 셸 진입점·초기화 스크립트가 쓰는 경로가 deploy 가 그 이미지에 주는 쓰기 가능 경로 안인지 실행 없이 대조한다(2026-11-06).

왜: deploy 는 영역 이미지를 읽기 전용 루트로 띄우고 tmpfs·볼륨만 쓰게 한다. question-authoring-db·survey-db 가 그 밖(/var/lib/postgresql-tls,
/var/lib/postgresql/tls)에 TLS 사본을 만들다 E2E 기동에서 재시작을 반복했다. 실행해 보기 전에 코드에서 잡을 수 있었다.
입력: 이미지별 주입 선언(계약 ContainerInputs 3.5.0: 영역 리포의 정본 파일, 아래 DECL)의 쓰기 경로, 이미지별 스크립트 폴더(아래 SOURCES).
      변수 경로는 같은 스크립트의 대입, 선언의 path_env 값, Env 계약 기본값, mktemp(-> /tmp)로 푼다.
판정: 쓰기 명령(install -d·mkdir·touch·cp·mv·install·tee·> 리다이렉트)의 절대 경로 대상이 쓰기 가능 경로(와 /dev·/proc) 아래가 아니면 위반.
      같은 파일의 단순 대입(NAME=/경로)은 풀어서 본다. 풀지 못한 변수 경로는 '확인 못 함'으로 따로 낸다(통과로 세지 않는다).
종료 코드: 위반 0 이고 확인 못 함 0 이면 0, 아니면 1.
"""
import json
import pathlib
import re
import sys

import yaml

WS = pathlib.Path(__file__).resolve().parents[2]
TREES = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
DEPLOY = pathlib.Path(TREES.get("deploy", WS / "deploy"))
# 이미지 -> 그 이미지 안에서 도는 셸 스크립트가 있는 리포 폴더(Dockerfile 이 COPY 하는 곳)
SOURCES = {
    "survey-db": ("survey-service", "db"), "question-authoring-db": ("question-authoring", "db"),
    "ops-feedback-db": ("ops-feedback", "db"), "release-gate-db": ("release-gate", "db"),
    "identity-db": ("platform", "identity/db"), "public-ingress": ("platform", "ingress"),
    "step-ca": ("platform", "pki/image"), "backup-store": ("platform", "backup-store"),
    "monitoring": ("platform", "monitoring"), "area-gateway": ("platform", "area-gateway"),
}
ALWAYS = ("/dev/", "/proc/")
DECL = {"survey-db": "survey-service/db/inputs.json", "question-authoring-db": "question-authoring/db/inputs.json", "ops-feedback-db": "ops-feedback/db/inputs.json",
        "release-gate-db": "release-gate/db/inputs.json", "identity-db": "platform/identity/inputs-identity-db.json", "public-ingress": "platform/ingress/inputs-public-ingress.json",
        "step-ca": "platform/pki/inputs-step-ca.json", "backup-store": "platform/backup-store/inputs-backup-store.json", "monitoring": "platform/monitoring/inputs-monitoring.json",
        "area-gateway": "platform/area-gateway/inputs-area-gateway.json"}
BC = WS / "boundary-contracts/boundary_contracts/schemas"


def env_defaults(name):
    d = json.loads((BC / f"{name}.schema.json").read_text(encoding="utf-8"))
    out = {k: v["default"] for k, v in d.get("properties", {}).items() if isinstance(v, dict) and isinstance(v.get("default"), str)}
    for a in d.get("allOf", []):
        if "$ref" in a:
            out.update(env_defaults(a["$ref"].split("/")[-1].replace(".schema.json", "")))
    return out


def declared(img):
    """이미지의 쓰기 가능 경로(모든 역할·잡)와 변수 해석표(path_env -> 선언 경로, Env 기본값)."""
    d = json.loads((pathlib.Path(TREES.get(DECL[img].split("/")[0], WS / DECL[img].split("/")[0])) / DECL[img].split("/", 1)[1]).read_text(encoding="utf-8"))
    paths, env = set(), {}
    for st in list(d["roles"].values()) + list(d["jobs"].values()):
        paths |= {w["path"] for w in st["writable"]}
        env.update(env_defaults(st["env_schema"]))
        env.update({f["path_env"]: f["path"] for f in st["files"] if f.get("path_env")})
    return sorted(paths), env
WRITE = re.compile(r"(?:install\s+(?:-[a-zA-Z]+\s+\S+\s+)*-d\s+(?:-[a-zA-Z]+\s+\S+\s+)*|mkdir\s+(?:-p\s+)?|touch\s+|tee\s+(?:-a\s+)?|>>?\s*)(\"?[$/][^\s\"'|;&)]+)")
MV_CP = re.compile(r"\b(?:cp|mv|install)\s+(?:-[a-zA-Z]+\s+(?:\S+\s+)?)*\S+\s+(\"?[$/][^\s\"'|;&)]+)")


def writable(compose):
    out = {}
    for n, b in compose["services"].items():
        m = re.search(r"/openit/([a-z0-9-]+)@", str(b.get("image", "")))
        if not m or n.startswith("job-"):
            continue
        paths = {str(t).split(":")[0] for t in (b.get("tmpfs") or [])}
        for v in b.get("volumes") or []:
            if isinstance(v, str):
                p = v.split(":")
                if len(p) >= 2 and not (len(p) > 2 and "ro" in p[2].split(",")):
                    paths.add(p[1])
            elif isinstance(v, dict) and not v.get("read_only"):
                paths.add(v.get("target"))
        out.setdefault(m.group(1), set()).update(x for x in paths if x)
    return out


def main():
    class L(yaml.SafeLoader):
        pass
    L.add_multi_constructor("!", lambda l, s, n: l.construct_scalar(n) if isinstance(n, yaml.ScalarNode) else (l.construct_sequence(n) if isinstance(n, yaml.SequenceNode) else l.construct_mapping(n)))
    bad, unknown, n = [], [], 0
    for img, (repo, sub) in sorted(SOURCES.items()):
        root = pathlib.Path(TREES.get(repo, WS / repo)) / sub
        allowed, denv = declared(img)
        for f in sorted(root.glob("*.sh")):
            text = f.read_text(encoding="utf-8")
            env = dict(denv)
            env.setdefault("PGDATA", "/var/lib/postgresql/data")   # 공식 postgres 이미지의 ENV PGDATA(기반 이미지 사실, DB 이미지 Dockerfile 이 바꾸지 않는다)
            env.update(dict(re.findall(r"(?:^|;)\s*([A-Za-z_][A-Za-z0-9_]*)=\"?(/[^\s\"';]+)", text, re.M)))   # 같은 스크립트의 단순 대입(소문자 지역 변수, 한 줄 여러 대입 포함)
            env.update({k: "/tmp/" + k for k in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)=\$\(mktemp", text, re.M)})   # mktemp 는 /tmp 아래(TMPDIR 기본)
            for k, v in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)=\"?\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?\"?\s*$", text, re.M):   # NAME=$OTHER
                if v in env: env[k] = env[v]
            for i, line in enumerate(text.splitlines(), 1):
                code = line.split(" #", 1)[0]
                if code.lstrip().startswith("#"):
                    continue
                for m in list(WRITE.finditer(code)) + list(MV_CP.finditer(code)):
                    tgt = m.group(1).strip('"')
                    for _ in range(3):   # 겹친 변수(NAME=$OTHER/...)를 몇 번 푼다
                        tgt = re.sub(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}?", lambda x: env.get(x.group(1), x.group(2) if x.group(2) else x.group(0)), tgt)
                    if tgt.startswith("/dev/null") or tgt.startswith(ALWAYS):
                        continue
                    n += 1
                    if "$" in tgt:
                        head = tgt.split("$", 1)[0]
                        # 폴더까지 풀리고 마지막 이름만 변수(반복문의 파일 이름)면 그 폴더에 쓸 수 있는지로 판정한다
                        if head.endswith("/") and "/" not in tgt[len(head):] and head != "/":
                            tgt = head.rstrip("/")
                        else:
                            unknown.append(f"{repo}/{sub}/{f.name}:{i} {tgt}")
                            continue
                    if not any(tgt == a or tgt.startswith(a.rstrip("/") + "/") for a in allowed):
                        bad.append(f"{repo}/{sub}/{f.name}:{i} {img}: {tgt} 는 쓰기 가능 경로 {allowed} 밖이다")
    print(f"쓰기 대상 {n}곳, 위반 {len(bad)}, 확인 못 함 {len(unknown)}")
    for b in bad:
        print("위반", b)
    for u in unknown:
        print("확인 못 함", u)
    return 1 if (bad or unknown) else 0


if __name__ == "__main__":
    sys.exit(main())
