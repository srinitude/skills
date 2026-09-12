"""Reading checks must keep evidence and reject dense or changed text."""
import importlib.util
import unittest
from pathlib import Path

OWNER = Path(__file__).resolve().parents[1] / "markdown_checks.py"


def module():
    spec = importlib.util.spec_from_file_location("markdown_checks", OWNER)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class ReadingChecks(unittest.TestCase):
    def test_plain_text_and_full_text_are_kept(self):
        text = "# Read this\n\nRead the file. Run the test. Fix the bug.\n"
        result = module().check_text(text)
        self.assertEqual(result["text"], text)
        self.assertLessEqual(result["grade"], 6)
        self.assertEqual(result["failures"], [])
        self.assertTrue(result["blocks"])
        self.assertIn("Read this", result["prose"])

    def test_difficult_prose_fails(self):
        text = ("The institutional implementation necessitates interdisciplinary "
                "coordination and methodological standardization across jurisdictions.\n")
        result = module().check_text(text)
        self.assertGreater(result["grade"], 6)
        self.assertTrue(any(x["rule"] == "grade" for x in result["failures"]))


class ExtractionChecks(unittest.TestCase):
    def test_code_is_not_scored_but_is_retained_for_review(self):
        result = module().check_text("Read this code.\n\n```python\nprint('word')\n```\n")
        self.assertNotIn("print", result["prose"])
        self.assertTrue(any(x["kind"] == "fence" for x in result["excluded"]))
        self.assertIn("print", result["text"])

    def test_links_lists_and_tables_keep_their_prose(self):
        text = ("# Start\n\n- Read [this page](https://example.com).\n\n"
                "| Step | Task |\n| --- | --- |\n| One | Run the test. |\n")
        result = module().check_text(text)
        for word in ("Start", "Read", "this page", "Step", "Task", "Run the test"):
            self.assertIn(word, result["prose"])
        self.assertNotIn("https://", result["prose"])


class BoundaryChecks(unittest.TestCase):
    def test_short_text_requires_review(self):
        result = module().check_text("Read this.\n")
        self.assertEqual(result["grade"], None)
        self.assertEqual(result["score_state"], "short-text-review")

    def test_limits_and_missing_alt_are_visible(self):
        result = module().check_text("# One\n\n### Three\n\n![](a.png)\n" + "\n" * 201)
        rules = {x["rule"] for x in result["failures"]}
        self.assertTrue({"lines", "heading-order", "image-alt"} <= rules)


class PreservationChecks(unittest.TestCase):
    def test_frontmatter_has_an_explicit_exclusion(self):
        result = module().check_text("---\nname: a\n---\n\nRead the file.\n")
        self.assertNotIn("name", result["prose"])
        self.assertEqual(result["excluded"][0]["kind"], "frontmatter")

    def test_sections_cannot_hide_a_hard_paragraph(self):
        text = "# Easy\n\n" + "Read the file. " * 40
        text += "\n\n## Hard\n\nInterdisciplinary institutionalization necessitates methodological harmonization across numerous multinational administrative departments and regional regulatory authorities."
        result = module().check_text(text)
        self.assertTrue(any(x["rule"] == "block-grade" for x in result["failures"]))


class StructureChecks(unittest.TestCase):
    def test_full_native_structure_reaches_review(self):
        text = "# Start\n\n> Read **this**.\n\n1. Do this.\n   - Use `code`.\n\n[page]: guide.md\n\nRead [page].\n"
        result = module().check_text(text)
        syntax = result["syntax"]
        tokens = syntax["tokens"]
        types = {token["type"] for token in tokens}
        self.assertTrue({"heading_open", "blockquote_open", "ordered_list_open",
                         "bullet_list_open", "list_item_open"} <= types)
        inline = [child for token in tokens for child in token["children"] or []]
        self.assertTrue({"strong_open", "code_inline", "link_open"} <= {x["type"] for x in inline})
        self.assertEqual(tokens[0]["map"], [0, 1])
        self.assertEqual(syntax["references"]["PAGE"]["href"], "guide.md")
        self.assertEqual(result["text"], text)
        self.assertIn("not full target conformance", syntax["limit"])

    def test_structure_is_not_replaced_by_flat_prose(self):
        owner = module()
        flat = owner.check_text("First. Second.\n")
        ordered = owner.check_text("1. First.\n2. Second.\n")
        self.assertNotEqual(flat["syntax"]["tokens"], ordered["syntax"]["tokens"])
        self.assertEqual(flat["syntax"]["rules"], owner.PARSER.get_active_rules())



def workflow_review(base, request, env):
    import json
    from test_markdown_workflow import invoke, reply_for
    for phase in ["inventory", "mechanical", "review-request"]:
        code, data, error = invoke(phase, env)
        assert code == 0, error + str(data)
    for phase in ["macro-review", "micro-review", "line-review"]:
        code, waiting, error = invoke(phase, env)
        assert code == 3, error + str(waiting)
        reply = reply_for(data["result"], phase)
        assert set(waiting["stage_questions"]) == set(reply["files"][0]["answers"])
        path = base / (phase + ".json")
        path.write_text(json.dumps(reply))
        env["SKILL_MARKDOWN_REPLY"] = str(path)
        code, resumed, error = invoke(phase, env)
        assert code == 0, error + str(resumed)
    return invoke("review-check", env)


def repair_iterations(base):
    import json
    from test_markdown_workflow import fixture, binding, invoke
    request, env = fixture(base)
    body = Path(request["roots"][0]) / "SKILL.md"
    easy = body.read_text()
    hard = easy + "\nInstitutional implementation necessitates interdisciplinary coordination and methodological standardization across jurisdictions.\n"
    for iteration, content in enumerate([hard, easy]):
        body.write_text(content)
        request.update(run_id="repair-" + str(iteration), iteration=iteration)
        request["context"] = [{**item, **binding(body)} if item["role"] == "body" else item for item in request["context"]]
        Path(env["SKILL_MARKDOWN_REQUEST"]).write_text(json.dumps(request))
        env.pop("SKILL_MARKDOWN_REPLY", None)
        code, checked, error = workflow_review(base, request, env)
        assert code == (1 if iteration == 0 else 0), error + str(checked)
        if iteration == 0:
            assert "Fix the reported Markdown checks" in str(checked)
        else:
            assert invoke("accept", env)[0] == 0


class WorkflowReadingChecks(unittest.TestCase):
    def test_findings_reach_review_and_require_repair(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            repair_iterations(Path(temporary).resolve())


if __name__ == "__main__":
    unittest.main()
