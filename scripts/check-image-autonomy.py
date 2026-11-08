#!/usr/bin/env python3
"""규칙 C44(영역 이미지는 스스로 서는 단위, CONVENTIONS 13절 3.4.17): deploy 의 compose 파일이 영역 이미지에
command·entrypoint·healthcheck·user·volumes_from 을 쓰지 않는지 센다. 영역 Dockerfile 이 HEALTHCHECK·USER 를 갖는지도 본다.
예외(계약이 정한 것): 잡 서비스(job-*)의 command 는 JobsDeclaration 의 argv 실행이다(deploy 의 잡 실행, CONVENTIONS 13절 '유일한 예외').

보는 파일: deploy 안에서 git 이 추적하는 모든 .yaml/.yml 중 최상위에 services 가 있는 것(compose.yaml, compose.*.yaml, test/…, demo/…,
test/split/… 등 overlay 전부). 파일 이름이 compose 인데 읽지 못하면 종료 2.
서비스 이름으로 합쳐 본다(docker compose config 를 부르지 않는 정적 병합): 금지 키를 쓴 파일이 그 서비스에 image(또는 build)를 두면
그 정의로 판정하고(별도 스택, 예 test/split 은 제품과 같은 서비스 이름에 자기 대역 이미지를 둔다), 두지 않으면 overlay 이므로
다른 모든 파일의 같은 이름 서비스 정의를 합쳐 영역 이미지인지 본다. 그래서 base 가 image 를 두고 overlay 가 command 를 덮어쓰는 경우를 잡는다. overlay 의 !reset(키 제거)은 쓴 것이 아니다. extends.service 는 image 를 물려받는다.

영역 이미지 판정(image 값 하나):
  1. 경로에 /openit/ (deploy 레지스트리의 영역 이미지) 또는 deploy-build/ (로컬 빌드) 가 있으면 영역 이미지.
  2. ${변수} / ${변수:?메시지} / $변수 형태: 변수가 제3자 이미지 변수(deploy/locks/images.lock 의 *_IMAGE 중 값에 /openit/ 이 없는 것, 또는
     그 이름으로 끝나는 변수 — 예 INFERENCE_PAUSE_IMAGE 는 PAUSE_IMAGE)이면 제3자, 아니면 영역 이미지(모르는 변수는 엄격하게 영역으로 본다).
     ${변수:-기본값} 은 변수가 제3자가 아니면 기본값 리터럴로 다시 판정한다.
  3. 리터럴 참조(레지스트리·태그·digest 포함): 저장소 마지막 이름이 areas.json 영역 이름이거나 compose 가 /openit/<이름> 으로 쓰는 이름이면 영역 이미지.
  4. build: 만 있고 image 가 어디에도 없는 서비스는 deploy 가 영역 소스에서 빌드하는 것이라 영역 이미지.
  제3자 이미지(pause·util·registry·step-ca 상용 등)는 대상이 아니다.
보지 않는 것: compose 밖에서 만드는 서비스(ansible·셸이 docker run 으로 띄우는 것), include: 로 끌어오는 파일의 병합 순서, profiles 에 따른 활성 여부(모든 정의를 본다).
사용: check-image-autonomy.py [--deploy <deploy 폴더>] [--self-test]. 종료 0 통과, 1 위반, 2 사용 오류."""
import json
import pathlib
import re
import subprocess
import sys
try:
    import yaml
except ImportError:
    print("PyYAML 이 필요하다(head requirements-tools.txt)"); sys.exit(2)
WS = pathlib.Path(__file__).resolve().parents[2]
FORBIDDEN = ("command", "entrypoint", "healthcheck", "user", "volumes_from")
RESET = object()   # compose 의 !reset: 상위 파일의 값을 지운다(쓴 것이 아니다)


class _L(yaml.SafeLoader):
    pass


_L.add_constructor("!reset", lambda l, n: RESET)
_L.add_constructor("!override", lambda l, n: l.construct_sequence(n, deep=True) if isinstance(n, yaml.SequenceNode) else l.construct_scalar(n) if isinstance(n, yaml.ScalarNode) else l.construct_mapping(n, deep=True))
WHOLE_VAR = re.compile(r"^\$\{([A-Za-z_]\w*)(?:(:?[-?+])(.*))?\}$|^\$([A-Za-z_]\w*)$")


def third_party_vars(lock_text: str):
    """images.lock 의 *_IMAGE 중 값이 영역 레지스트리(/openit/)가 아닌 것의 이름."""
    out = set()
    for ln in lock_text.splitlines():
        m = re.match(r"([A-Z0-9_]+_IMAGE)=(\S+)", ln)
        if m and "/openit/" not in m.group(2):
            out.add(m.group(1))
    return out


def is_area_image(img, third, published):
    img = str(img).strip().strip("\"'")
    if "/openit/" in img or "deploy-build/" in img:
        return True
    m = WHOLE_VAR.match(img)
    if m:
        v, op, default = m.group(1) or m.group(4), m.group(2), m.group(3)
        if any(v == t or v.endswith("_" + t) for t in third):
            return False
        if op in (":-", "-") and default:
            return is_area_image(default, third, published)   # 기본값 리터럴로 다시 판정
        return True   # 모르는 변수는 엄격하게 영역 이미지
    repo = re.split(r"[@:$]", img.rsplit("/", 1)[-1])[0]
    return repo in published


def load_compose(text):
    y = yaml.load(text, Loader=_L)
    return y if isinstance(y, dict) and isinstance(y.get("services"), dict) else None


def violations(files, third, published):
    """files: [(이름, compose 텍스트)]. 서비스 이름별로 모든 파일을 합쳐 판정한다."""
    out, images, uses, extends = [], {}, [], {}
    for name, text in files:
        y = load_compose(text)
        if not y:
            continue
        for svc, s in y["services"].items():
            s = s if isinstance(s, dict) else {}
            if isinstance(s.get("image"), str):
                images.setdefault(svc, []).append((name, s["image"]))
            elif "build" in s and s["build"] is not RESET:
                images.setdefault(svc, []).append((name, "deploy-build/<build>"))
            ext = s.get("extends")
            if isinstance(ext, dict) and isinstance(ext.get("service"), str):
                extends[svc] = ext["service"]
            for k in FORBIDDEN:
                if k in s and s[k] is not RESET and not (k == "command" and str(svc).startswith("job-")):
                    uses.append((name, svc, k))
    for name, svc, k in uses:
        chain, cur = [svc], svc
        while cur in extends and extends[cur] not in chain:
            cur = extends[cur]
            chain.append(cur)
        own = [(n, i) for c in chain for n, i in images.get(c, []) if n == name]
        # 파일이 자기 서비스에 image 를 두면 그 image 로만 판정한다(별도 스택, 예 test/split). image 가 없으면 overlay 이므로 다른 파일의 정의를 합쳐 본다
        defs = own or [(n, i) for c in chain for n, i in images.get(c, [])]
        area = [n for n, i in defs if is_area_image(i, third, published)]
        if area:
            where = "" if area[0] == name else f" (image 는 {area[0]} 에서 정의)"
            out.append(f"{name}: {svc}: 영역 이미지에 {k} 를 쓴다{where}(C44)")
    return sorted(set(out))


def published_names(files, ws=WS):
    names = {a["name"] for a in (lambda d: d["areas"] if isinstance(d, dict) else d)(json.loads((ws / "head/shared/areas.json").read_text()))}
    for _, text in files:
        names |= set(re.findall(r"/openit/([A-Za-z0-9._-]+)", text))
    return names


def dockerfile_gaps(ws=WS):
    out = []
    for f in sorted(ws.glob("*/Dockerfile*")) + sorted(ws.glob("*/*/Dockerfile*")):
        rel = f.relative_to(ws)
        if any(p in ("build", "node_modules", "turn-engine", "test-e2e", "deploy", "head") for p in rel.parts):
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"^HEALTHCHECK\b", t, re.M):
            out.append(f"{rel}: HEALTHCHECK 없음(C44)")
        if not re.search(r"^USER\s+(?!root\b|0\b)", t, re.M):
            out.append(f"{rel}: root 가 아닌 USER 없음(C44·공통 규칙)")
    return out


def compose_files(d: pathlib.Path):
    """deploy 의 추적 yaml 중 services 를 가진 것. 읽지 못하는 compose 이름 파일이 있으면 (None, 오류 목록)."""
    r = subprocess.run(["git", "-C", str(d), "ls-files"], capture_output=True, text=True)
    rels = r.stdout.splitlines() if r.returncode == 0 else [str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() and ".git" not in p.parts]
    files, errs = [], []
    for rel in rels:
        if not re.search(r"\.ya?ml$", rel):
            continue
        t = (d / rel).read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"^services\s*:", t, re.M):
            continue
        try:
            ok = load_compose(t) is not None
        except yaml.YAMLError:
            ok = False
        if ok:
            files.append((rel, t))
        elif "compose" in rel:
            errs.append(f"{rel}: compose 를 읽지 못했다")
    return files, errs


def self_test():
    bad = []
    third = {"PAUSE_IMAGE", "UTIL_IMAGE"}
    pub = {"survey-service", "platform"}

    def v(*texts):
        return violations([(f"f{i}.yaml", t) for i, t in enumerate(texts)], third, pub)
    base = "services:\n  s:\n    image: ${R}/openit/a@sha256:1\n"
    pos = {
        "영역 이미지 healthcheck(레지스트리·digest)": v("services:\n  s:\n    image: ${R:?x}/openit/a@${D:?y}\n    healthcheck: {test: [x]}\n"),
        "로컬 빌드 이미지": v("services:\n  s:\n    image: deploy-build/model-serving:abc\n    user: '1'\n"),
        "overlay 가 base 서비스의 command 를 덮어씀": v(base, "services:\n  s:\n    command: [x]\n"),
        "overlay 가 image 를 두고 base 가 entrypoint": v("services:\n  s:\n    entrypoint: [x]\n", "services:\n  s:\n    image: ${R}/openit/a@sha256:1\n"),
        "리터럴 레지스트리 영역 이미지": v("services:\n  s:\n    image: reg.local:5000/survey-service@sha256:1\n    volumes_from: [x]\n"),
        "모르는 변수는 영역으로": v("services:\n  s:\n    image: ${INFERENCE_IMAGE:?m}\n    command: [x]\n"),
        "build 만 있는 서비스": v("services:\n  s:\n    build: ./x\n    user: '1'\n"),
        "extends 로 물려받음": v(base + "  t:\n    extends: {service: s}\n    command: [x]\n"),
    }
    for k, r in pos.items():
        if not r:
            bad.append(f"놓침: {k}")
    neg = {
        "잡 command": v("services:\n  job-x:\n    image: ${R}/openit/a@sha256:1\n    command: [x]\n"),
        "제3자 변수 user": v("services:\n  p:\n    image: ${PAUSE_IMAGE:?lock}\n    user: '1'\n"),
        "접두 붙은 제3자 변수": v("services:\n  p:\n    image: ${INFERENCE_PAUSE_IMAGE:?m}\n    command: [x]\n"),
        "기본값이 제3자 리터럴": v("services:\n  p:\n    image: ${SPLIT_IMAGE:-python:3.12-slim}\n    command: [x]\n"),
        "제3자 리터럴": v("services:\n  p:\n    image: docker.io/library/python@sha256:1\n    command: [x]\n"),
        "overlay !reset": v(base, "services:\n  s:\n    command: !reset null\n"),
        "금지 키 없음": v(base + "    environment: {A: b}\n"),
        "같은 이름의 별도 스택(자기 제3자 image)": v(base, "services:\n  s:\n    image: ${SPLIT_IMAGE:-python:3.12-slim}\n    command: [x]\n"),
        "다른 서비스의 overlay": v(base, "services:\n  other:\n    image: ${PAUSE_IMAGE}\n    command: [x]\n"),
    }
    for k, r in neg.items():
        if r:
            bad.append(f"거짓양성: {k}")
    if third_party_vars("A_IMAGE=docker.io/x@sha256:1\nB_DIGEST=sha256:2\nC_IMAGE=r/openit/c@sha256:3\n") != {"A_IMAGE"}:
        bad.append("images.lock 읽기")
    print("self-test:", "OK" if not bad else bad)
    return not bad


def main():
    if "--self-test" in sys.argv:
        return 0 if self_test() else 1
    if not self_test():
        return 1
    d = pathlib.Path(sys.argv[sys.argv.index("--deploy") + 1]) if "--deploy" in sys.argv else WS / "deploy"
    lock = d / "locks/images.lock"
    if not lock.exists():
        print(f"사용 오류: {lock} 를 찾지 못했다(제3자 이미지 변수의 정본)")
        return 2
    files, errs = compose_files(d)
    if errs or not files:
        print("\n".join(errs) or "사용 오류: compose 파일이 없다")
        return 2
    third = third_party_vars(lock.read_text(encoding="utf-8"))
    v = violations(files, third, published_names(files)) + dockerfile_gaps()
    print(f"compose {len(files)}개, 제3자 이미지 변수 {len(third)}개, 위반 {len(v)}건")
    print("\n".join(v) if v else "OK: 영역 이미지 자립(C44)")
    return 1 if v else 0


if __name__ == "__main__":
    sys.exit(main())
