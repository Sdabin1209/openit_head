#!/usr/bin/env python3
"""영역 이미지의 주입 선언(계약 ContainerInputs 3.5.0, 영역 리포의 정본 파일)과 deploy compose 의 주입을 실행 없이 대조한다(2026-11-06).

왜 헤드 도구인가: deploy 는 기동 직전(up.sh)에 이미지 라벨로 같은 대조를 한다. 헤드는 이미지를 만들기 전에, 영역 리포의 선언 파일과 deploy compose 조합
전부를 같은 대조기(deploy scripts/check_container_inputs.py)로 맞춰 본다(영역 간 대조, 구조 규칙 6). deploy 코드는 import 하지 않고 진입점을 실행한다.
compose 조합: deploy 가 쓰는 것 전부(운영, 감시, E2E·데모 덧씌움, 외부 추론, 로컬 LLM, 레지스트리, 추론 호스트 3종). 필수 변수는 자리표시로 채운다.
종료 코드: 모든 조합 어긋남 0 이면 0, 아니면 1. 사용: check-container-inputs.py [deploy=<작업 트리>] [<영역>=<작업 트리> ...]
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

WS = pathlib.Path(__file__).resolve().parents[2]
TREES = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
DEPLOY = pathlib.Path(TREES.get("deploy", WS / "deploy"))
DECL = {"survey-service": "survey-service/deploy-inputs.json", "survey-db": "survey-service/db/inputs.json",
        "question-authoring": "question-authoring/deploy-inputs.json", "question-authoring-db": "question-authoring/db/inputs.json",
        "ops-feedback": "ops-feedback/deploy-inputs.json", "ops-feedback-db": "ops-feedback/db/inputs.json",
        "release-gate": "release-gate/deploy-inputs.json", "release-gate-db": "release-gate/db/inputs.json",
        "model-registry": "model-lab/deploy-inputs.json", "dataset-store": "synthetic-data/deploy-inputs.json",
        "model-serving": "model-runtime/deploy-inputs.json", "model-serving-gpu": "model-runtime/deploy-inputs.json",
        "kiosk-frontend": "kiosk-frontend/deploy-inputs.json", "admin-console": "admin-console/deploy-inputs.json",
        "area-gateway": "platform/area-gateway/inputs-area-gateway.json", "public-ingress": "platform/ingress/inputs-public-ingress.json",
        "monitoring": "platform/monitoring/inputs-monitoring.json", "backup-store": "platform/backup-store/inputs-backup-store.json",
        "step-ca": "platform/pki/inputs-step-ca.json", "identity": "platform/identity/inputs-identity.json",
        "identity-proxy": "platform/identity/inputs-identity-proxy.json", "identity-db": "platform/identity/inputs-identity-db.json"}
SETS = [["compose.yaml"], ["compose.yaml", "compose.monitoring.yaml"],
        ["compose.yaml", "test/compose.sandbox.yaml", "test/compose.risk-rules.yaml", "compose.backup-target.yaml", "compose.monitoring.yaml", "compose.step-ca-publish.yaml"],
        ["compose.yaml", "test/compose.sandbox.yaml", "compose.llm.yaml", "compose.llm.local.yaml"],
        ["compose.yaml", "test/compose.sandbox.yaml", "demo/compose.demo-mimic.yaml"],
        ["compose.yaml", "compose.external-inference.yaml"], ["compose.yaml", "compose.llm.yaml", "compose.llm.digest.yaml"], ["compose.yaml", "compose.registry.yaml"],
        ["compose.inference.yaml"], ["compose.inference.yaml", "compose.inference.remote.yaml"],
        ["compose.inference.yaml", "compose.inference.samehost.yaml", "test/compose.fake-model.yaml"]]
# 추론 호스트 이미지 변수는 우리 이미지 모양의 자리표시로 준다(대조기가 /openit/<이름> 으로 이미지를 고른다)
IMG = {"INFERENCE_IMAGE": "r/openit/model-serving@d", "INFERENCE_STEP_IMAGE": "r/openit/step-ca@d", "INFERENCE_GATEWAY_IMAGE": "r/openit/area-gateway@d",
       "MODEL_SERVING_GPU_IMAGE": "r/openit/model-serving-gpu@d"}


def render(files, overlay=None):
    # 왜 최소 환경: R9.1(C45) — 상속 환경을 통째로 넘기면 호스트의 우연한 변수가 compose 해석을 바꾼다. docker 호출에 필요한 이름만 넘긴다.
    env = {k: os.environ[k] for k in ("PATH", "HOME", "DOCKER_CONFIG", "DOCKER_HOST") if k in os.environ}; env["SECRETS_GID"] = "1000"; env.setdefault("INFERENCE_TLS_NAME", "infer.example.org")
    for f in files:
        for v in re.findall(r"\$\{([A-Za-z0-9_]+):\?", (DEPLOY / f).read_text(encoding="utf-8")):
            env.setdefault(v, IMG.get(v, "1" if v.endswith("_PORT") else "/x"))   # 경로 자리표시는 절대 경로(상대면 짧은 마운트 문법이 달리 읽힌다), 포트는 숫자
    env.update(IMG)
    env.setdefault("GATEWAY_HOST_NAMES", '\"localhost\", \"127.0.0.1\"')
    env["GATEWAY_PUBLIC_URL"] = os.environ.get("GATEWAY_PUBLIC_URL", "https://localhost:8443")
    env["INFERENCE_URL"] = os.environ.get("INFERENCE_URL", "https://inference.example.org")
    env["INFERENCE_STEP_CA_URL"] = os.environ.get("INFERENCE_STEP_CA_URL", "https://step-ca.example.org:9000")
    env.setdefault("INFERENCE_ALLOW_FAKE", "1")
    env["DEMO_MIMIC_FLOW_FILE"] = os.environ.get("DEMO_MIMIC_FLOW_FILE", str(DEPLOY / "test/fake-model/question_flow.json"))
    cmd = ["docker", "compose", "--project-directory", str(DEPLOY)] + [a for f in files for a in ("-f", str(DEPLOY / f))] + (["-f", str(overlay)] if overlay else []) + ["--profile", "jobs", "--profile", "local-inference", "config", "--format", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode:
        raise SystemExit(f"compose 해석 실패 {files}: {r.stderr[-300:]}")
    return r.stdout


def main():
    py = DEPLOY / ".venv/bin/python"
    bad = 0
    with tempfile.TemporaryDirectory() as t:
        d = pathlib.Path(t) / "decl"; d.mkdir()
        labels = pathlib.Path(t) / "labels"; labels.mkdir()
        for img, rel in DECL.items():
            repo, sub = rel.split("/", 1)
            doc = json.loads((pathlib.Path(TREES.get(repo, WS / repo)) / sub).read_text(encoding="utf-8"))
            doc["image"] = img   # 같은 선언 파일로 변형 이미지(model-serving-gpu)를 만든다(build-image.sh 와 같다)
            (d / f"{img}.json").write_text(json.dumps(doc, ensure_ascii=False))
            parent = (pathlib.Path(TREES.get(repo, WS / repo)) / sub).parent
            source = next((p for p in [parent / "deploy-jobs.json", parent / "jobs.json", parent / f"jobs-{img}.json"] if p.exists()), None)
            jobs = json.loads(source.read_text()) if source else None
            if jobs:
                (d / f"{img}.jobs.json").write_text(json.dumps(jobs))
            (labels / f"{img}.json").write_text(json.dumps({"io.openit.jobs": json.dumps(jobs)} if jobs else {}))
        for index, files in enumerate(SETS):
            cfg = pathlib.Path(t) / "cfg.json"; cfg.write_text(render(files))
            overlay = pathlib.Path(t) / f"jobs-{index}.json"
            generated = subprocess.run([str(py), str(DEPLOY / "scripts/gen-jobs.py"), "--out", str(overlay), "--compose-json", str(cfg), "--labels-dir", str(labels)], capture_output=True, text=True)
            if generated.returncode:
                raise SystemExit("job declaration generation failed: " + generated.stderr[-500:])
            if overlay.exists():
                cfg.write_text(render(files, overlay))
            r = subprocess.run([str(py), "-W", "ignore", str(DEPLOY / "scripts/check_container_inputs.py"), "--compose-json", str(cfg), "--declarations-dir", str(d), "--secrets-gid", "1000"],
                               capture_output=True, text=True)
            last = (r.stdout.strip().splitlines() or [r.stderr.strip()[-200:]])[-1]
            print(f"{'OK  ' if r.returncode == 0 else 'FAIL'} {' + '.join(files)}: {last}")
            if r.returncode:
                bad += 1
                print("\n".join("     " + x for x in (r.stdout + r.stderr).splitlines() if x.startswith("FAIL")))
    print(f"compose 조합 {len(SETS)}개, 어긋난 조합 {bad}개")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
