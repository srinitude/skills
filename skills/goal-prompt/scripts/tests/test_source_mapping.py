"""Lineage checks."""
import hashlib, json, pathlib, unittest
S=pathlib.Path(__file__).resolve().parents[2]
R=S.parents[1]
E=R/"evidence/ports/goal-prompt"
P="8c1269a76a5ad57e785f4968a4ca71ccd8d15ee5a22e4955573dfcfb6b182243"
H={"SKILL.md":"5a27d47bc07ddd68a60a09e26e774cfa487c20853a569c502f9d5f5b5addac59","references/plan-package-input.md":"3b657d32a7e8f7ee4a9af0b91895605fd52b5e57d1b42eb653d5e6fa217be955"}
def load(p): return json.loads((S/p).read_text())
class TestLineage(unittest.TestCase):
 def test_packet(self):
  m=json.loads((R/"evidence/ports/goal-prompt/manifest.json").read_text()); rows=[]
  for f in m["files"]:
   data=(E/f["evidence_path"]).read_bytes(); sha=hashlib.sha256(data).hexdigest(); self.assertEqual(sha,H[f["source_path"]]); rows.append(f'{f["source_path"]}\0{sha}\n')
  self.assertEqual(hashlib.sha256("".join(rows).encode()).hexdigest(),P); self.assertEqual(m["source_case_ids"],[])
 def test_mapping(self):
  m=load("evals/source-mapping.json"); self.assertEqual(m["coverage"],{"mapped_nonblank_lines":171,"ratio":1.0,"source_nonblank_lines":171}); self.assertEqual(len(m["entries"]),171); self.assertTrue(all(x["action"]!="drop" and x["review_state"]=="approved" for x in m["entries"]))
 def test_cases(self):
  l=load("evals/source-lineage.json"); c=load("evals/cases.json"); self.assertEqual(l["source_case_ids"],["GOAL-NO-NATIVE-CASES"]); self.assertEqual([x["source_id"] for x in c["cases"]],l["active_case_ids"])
 def test_portable(self):
  t=(S/"SKILL.md").read_text(); self.assertNotIn("global-coding-policy",t); self.assertIn("1900",t); self.assertIn("exactly six lines",t)
if __name__=="__main__": unittest.main()
