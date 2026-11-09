"""헤드 정적 점검의 self-test 묶음(2026-11-09). 점검과 규칙 대응(rules-coverage.py 가 이 머리 6줄의 ID 를 읽는다):
check-strict-json-entry C43 D117 · check-like-version C43 D117 · check-error-values C25 · check-component-wiring-import C3 C4 D104 ·
check-docker-skip C22 C33 D123 · check-hand-contract-types C43 D104 · check-real-time-tests C45 U422 · check-env-inheritance C45 ·
check-docker-context C24(docker 호출은 프로젝트 자체 설정만, DOCKER_CONTEXT 우선순위·해석 실패를 삼키지 않음, 2026-11-09)
각 점검의 --self-test(위반 예·통과 예)가 rc=0 인지 본다. 전 리포 검사(rc=1 이 위반)는 헤드가 점검마다 직접 돌린다.
사용: python3 scripts/test_head_static_checks.py  (pytest 로도 돈다). 종료 0 통과, 1 실패."""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CHECKS = ["check-strict-json-entry.py", "check-like-version.py", "check-error-values.py", "check-component-wiring-import.py",
          "check-docker-skip.py", "check-hand-contract-types.py", "check-real-time-tests.py", "check-env-inheritance.py", "check-docker-context.py"]
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}   # R9.1: 최소 환경만 넘긴다


def self_test_rc(name):
    return subprocess.run([sys.executable, str(HERE / name), "--self-test"], capture_output=True, text=True, env=ENV).returncode


def test_self_tests_pass():
    bad = {c: rc for c in CHECKS if (rc := self_test_rc(c)) != 0}
    assert not bad, bad


if __name__ == "__main__":
    res = {c: self_test_rc(c) for c in CHECKS}
    for c, rc in res.items():
        print(f"{c} self-test rc={rc}")
    sys.exit(1 if any(res.values()) else 0)
