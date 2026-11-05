"""The audit must distinguish mismatches, unresolved calls and verified statuses."""
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "check-e2e-expectations.py"
spec = importlib.util.spec_from_file_location("e2e_expectations", SOURCE)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Expectations(unittest.TestCase):
    def scan(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e2e_steps.py"
            path.write_text(source)
            return checker.scan(path)

    def test_arbitrary_success_status_is_not_accepted(self):
        r = self.scan('def call(method, path): pass\nc = call("POST", "/v1/materials"); assert c == 299\n')
        self.assertEqual(len(r["violations"]), 1)
        self.assertEqual(r["verified"], 0)

    def test_lambda_forwarding_uses_argument_not_status_inference(self):
        r = self.scan('def call(method, path): pass\nproxy = lambda m, p: call(m, p)\nc = proxy("POST", "/v1/materials"); assert c == 200\n')
        self.assertEqual(r, {"verified": 1, "violations": [], "unresolved": []})

    def test_unknown_method_is_not_counted_as_verified(self):
        r = self.scan('c = unknown("/v1/materials"); assert c == 200\n')
        self.assertEqual(len(r["unresolved"]), 1)
        self.assertEqual(r["verified"], 0)

    def test_negative_assertion_is_not_a_declared_expected_status(self):
        r = self.scan('def call(method, path): pass\nc = call("POST", "/v1/materials"); assert c != 299\n')
        self.assertEqual(r, {"verified": 0, "violations": [], "unresolved": []})

    def test_service_collision_does_not_union_incompatible_statuses(self):
        specs = [("a", "POST", re.compile("^/v1/same$"), {200}),
                 ("b", "POST", re.compile("^/v1/same$"), {201})]
        self.assertTrue(checker.check("POST", "/v1/same", {201}, specs).startswith("UNRESOLVED"))
