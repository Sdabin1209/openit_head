"""The source audit includes local code, not ignored runtime checkout copies."""
import importlib.util
from pathlib import Path
import os
import subprocess

# RUNTIME R9.1: 하위 프로세스에 상속 환경을 통째로 넘기지 않고 최소 이름만
ENV = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "TMPDIR") if k in os.environ}
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "cross_area_check", Path(__file__).with_name("cross-area-check.py")
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class Sources(unittest.TestCase):
    def test_local_source_is_included_and_ignored_runtime_copy_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True, env=ENV)
            (root / ".gitignore").write_text("state/\n")
            (root / "tracked.py").write_text("pass\n")
            subprocess.run(["git", "-C", directory, "add", "."], check=True, env=ENV)
            (root / "local.py").write_text("pass\n")
            (root / "state/areas/old").mkdir(parents=True)
            (root / "state/areas/old/invalid-example.json").write_text("{}\n")
            (root / "tests").mkdir()
            (root / "tests/test_example.py").write_text("pass\n")
            self.assertEqual(
                {path.relative_to(root).as_posix() for path in AUDIT.files(root)
                 if path.name != ".gitignore"},
                {"tracked.py", "local.py"},
            )


if __name__ == "__main__":
    unittest.main()
