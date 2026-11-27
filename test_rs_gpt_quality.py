"""Offline evaluation of saved GPT manuscripts and relationship evidence."""
import copy
import json
import re
import unittest

from rs_gpt import (
    ROOT, GroundingError, birth_payload, check_claims, relationship_focus, validate_editorial,
)


LIVE_SAMPLES = ROOT / "docs/rs-gpt-live-20261126"
SAMPLES = {
    "01-yunha-dohyeon": ({"윤하님": "a", "도현님": "b"}, (2, 7, 5)),
    "02-haewon-jian": ({"해원님": "a", "지안님": "b"}, (2, 8, 5)),
}


def replay_sample(path, people):
    prose, diagnostic = path.read_text(encoding="utf-8").split("## 자동 검증 결과와 계산 근거")
    recorded = json.loads(diagnostic.split("```json", 1)[1].split("```", 1)[0])
    facts = recorded["reference"]["facts"]
    issues = []
    counts = []
    for number, chapter in enumerate(re.split(r"(?m)^## [1-3]장\.", prose)[1:], 1):
        counts.append(len(re.findall(r"(?m)^### ", chapter)))
        paragraphs = re.findall(r"(?m)^([^#\n][^\n]+)\n\n근거 ID · ([^\n]+)", chapter)
        chapter_refs = list(dict.fromkeys(ref for _, ids in paragraphs for ref in ids.split(", ")))
        for index, (body, ids) in enumerate(paragraphs, 1):
            try:
                check_claims(body, ids.split(", "), chapter_refs, facts, people,
                             {"chapter": number, "paragraph": index},
                             require_relation_locations=True)
            except GroundingError as exc:
                issues.append(exc.diagnostic)
    return recorded, tuple(counts), issues


class ManuscriptQualityTests(unittest.TestCase):
    def test_editorial_gate_rejects_heading_sprawl_and_unfocused_opening(self):
        path = ROOT / "docs/rs-gpt-review/01-yunha-dohyeon.json"
        sample = json.loads(path.read_text(encoding="utf-8"))
        manuscript, payload = sample["report"], sample["payload"]
        with self.assertRaises(GroundingError) as failure:
            validate_editorial(manuscript, payload)
        self.assertEqual(failure.exception.diagnostic["rule"], "heading_count")

        for chapter, starts in zip(manuscript["chapters"], ({0, 2}, {0, 2, 5}, {0, 2, 4})):
            for index, paragraph in enumerate(chapter["paragraphs"]):
                if index not in starts:
                    paragraph["heading"] = None
        self.assertEqual(validate_editorial(manuscript, payload)["paragraphs"], 18)

        reordered = copy.deepcopy(manuscript)
        second = reordered["chapters"][1]["paragraphs"]
        second[:] = second[2:5] + second[:2] + second[5:]
        with self.assertRaises(GroundingError) as failure:
            validate_editorial(reordered, payload)
        self.assertEqual(failure.exception.diagnostic["rule"], "chapter_two_opening_focus")

    def test_historical_samples_replay_and_wrong_ten_god_is_still_rejected(self):
        for stem, (people, expected_headings) in SAMPLES.items():
            with self.subTest(sample=stem):
                saved, headings, issues = replay_sample(LIVE_SAMPLES / f"{stem}.md", people)
                failure = saved["failure"]
                self.assertEqual(headings, expected_headings)
                self.assertNotIn(failure["excerpt"], {issue["excerpt"] for issue in issues})
                refs = failure["evidence_ids"]
                args = (refs, refs, saved["reference"]["facts"], people, {})
                check_claims(failure["excerpt"], *args)
                for wrong in (
                    failure["excerpt"].replace("식신", "편관"),
                    failure["excerpt"].replace("丁", "庚").replace("을목은", "갑목은"),
                ):
                    self.assertNotEqual(wrong, failure["excerpt"])
                    with self.assertRaises(GroundingError):
                        check_claims(wrong, *args)

    def test_relationship_focus_across_birth_inputs(self):
        # Dates pin outcomes under the existing engine and avoid sampling bias
        # from searching for a relation with the implementation under test.
        cases = (
            ("different elements, no direct relation", 19, 10, (), False),
            ("same elements, no direct relation", 28, None, (), True),
            ("different elements, combine with punishment", 21, 10, ("육합", "상형"), False),
            ("different elements, direct clash", 24, None, ("육충",), False),
            ("same elements, harm with punishment", 27, 10, ("육해", "상형"), True),
        )
        a = dict(year=1992, month=3, day=18, hour=None)
        for label, day, hour, kinds, same in cases:
            with self.subTest(case=label):
                b = dict(year=1992, month=3, day=day, hour=hour)
                for first, second in ((a, b), (b, a)):
                    payload = birth_payload(first, second, {})
                    facts = payload["facts"]
                    charts = payload["charts"]
                    focus = relationship_focus(facts)
                    self.assertEqual(charts["a"]["element"] == charts["b"]["element"], same)
                    if kinds:
                        self.assertEqual(set(kinds), {facts[ref]["kind"] for ref in focus["primary_ids"]})
                    else:
                        self.assertEqual(facts["pair.palaces"]["direct_branch_relation_ids"], [])
                        self.assertEqual(focus["primary_ids"], ["pair.a.reads.b", "pair.b.reads.a"])
                    self.assertTrue(set(focus["primary_ids"]).isdisjoint(focus["secondary_ids"]))
                    for ref in focus["primary_ids"] + focus["secondary_ids"]:
                        for source in facts[ref].get("sources", ()):
                            self.assertNotIn(source["pillar"], charts[source["person"]]["unresolved"])


if __name__ == "__main__":
    for name, (people, _) in SAMPLES.items():
        _, counts, issues = replay_sample(LIVE_SAMPLES / f"{name}.md", people)
        print(name, "headings:", counts)
        for issue in issues:
            print(f"  {issue['chapter']}.{issue['paragraph']} {issue['rule']}: {issue['excerpt']}")
