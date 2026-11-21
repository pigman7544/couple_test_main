import json
from pathlib import Path
from collections import Counter
import re
from io import BytesIO

from compatibility_v14 import analyze_pair
from compatibility_v12 import report_markdown
from evaluate_compatibility_v13 import fixtures

OUT = Path(__file__).parent
STEMS = "甲乙丙丁戊己庚辛壬癸"
HIDDEN = dict(zip("子丑寅卯辰巳午未申酉戌亥",
                  "癸 己辛癸 甲丙戊 乙 戊癸乙 丙庚戊 丁己 己乙丁 庚壬戊 辛 戊丁辛 壬甲".split()))
RULES = {
    "천간합": "甲己 乙庚 丙辛 丁壬 戊癸", "육합": "子丑 寅亥 卯戌 辰酉 巳申 午未",
    "삼합": "申子辰 亥卯未 寅午戌 巳酉丑", "육충": "子午 丑未 寅申 卯酉 辰戌 巳亥",
    "상형": "子卯 寅巳 巳申 申寅 丑戌 戌未 未丑", "삼형": "寅巳申 丑戌未",
    "자형": "辰辰 午午 酉酉 亥亥", "육해": "子未 丑午 寅巳 卯辰 申亥 酉戌",
}
POSITIONS = ("year", "month", "day", "hour")
SAMPLES = (1, 2, 4)

def god(day, target):
    i, j = map(STEMS.index, (day, target))
    # 목→화→토→금→수. 같은 극성이 먼저 온다.
    return (("비견", "겁재"), ("식신", "상관"), ("편재", "정재"),
            ("편관", "정관"), ("편인", "정인"))[(j // 2 - i // 2) % 5][(i ^ j) & 1]

def verify(result):
    charts, evidence = result["charts"], result["evidence"]
    for owner, chart in charts.items():
        pillars = chart["pillars"]
        day = chart["day_master"]
        assert day == pillars["day"][0]
        for pos, pair in pillars.items():
            if pair is None:
                assert not any(key.startswith(f"{owner}.{pos}.") for key in evidence)
                continue
            stem, branch = pair
            assert evidence[f"{owner}.{pos}.stem"]["symbol"] == stem
            detail = chart["details"][pos]
            assert (detail["stem"], detail["branch"]) == (stem, branch)
            assert detail["stem_ten_god"] == (None if pos == "day" else god(day, stem))
            assert {row["stem"]: row["ten_god"] for row in detail["hidden_stems"]} == {
                hidden: god(day, hidden) for hidden in HIDDEN[branch]}
            for hidden, tier in zip(HIDDEN[branch], ("본기", "중기", "여기")):
                row = evidence[f"{owner}.{pos}.hidden.{hidden}"]
                assert (row["branch"], row["symbol"], row["tier"]) == (branch, hidden, tier)
        assert evidence[f"{owner}.coverage"]["unresolved_pillars"] == [
            pos for pos, pillar in pillars.items() if pillar is None]
        for placement in result["contexts"][owner]["placements"]:
            assert placement["ten_god"] == god(day, placement["stem"])
    for key, row in evidence.items():
        if row.get("kind") in RULES:
            kind = row["kind"]
            assert row["layer"] == ("stem" if kind == "천간합" else "branch")
            symbols = []
            for source in row["sources"]:
                owner = source["person"]
                other = "a" if owner == "b" else "b"
                stem, branch = charts[owner]["pillars"][source["pillar"]]
                visible = row["layer"] == "stem"
                symbol, read = (stem, stem) if visible else (branch, HIDDEN[branch][0])
                assert (source["symbol"], source["read_stem"]) == (symbol, read)
                assert evidence[source["source_id"]]["symbol"] == read
                assert source["owner_ten_god"] == god(charts[owner]["day_master"], read)
                assert source["other_ten_god"] == god(charts[other]["day_master"], read)
                symbols.append(symbol)
            assert sorted(symbols) in [sorted(group) for group in RULES[kind].split()]
        elif key in ("pair.a.reads.b", "pair.b.reads.a"):
            left, right = (evidence[ref]["symbol"] for ref in row["source_ids"])
            assert row["ten_god"] == god(left, right)
    for chapter in result["report"]:
        for para in chapter["paragraphs"]:
            assert para["evidence_ids"] and set(para["evidence_ids"]) <= set(evidence)

def create_packets(include_templates=False):
    inputs = list(fixtures())
    for n in SAMPLES:
        births = inputs[n-1]
        result = analyze_pair(*births)
        verify(result)
        keys = sorted({key for chapter in result["report"] for para in chapter["paragraphs"]
                       for key in para["evidence_ids"]})
        packet = {"births": births, "charts": result["charts"],
                  "evidence": {key: {**result["evidence"][key], **(
                      {"ten_god_from_own_day": god(
                          result["charts"][result["evidence"][key]["person"]]["day_master"],
                          result["evidence"][key]["symbol"])}
                      if "symbol" in result["evidence"][key] else {})}
                      for key in keys}}
        (OUT / f"{n:02}-evidence.json").write_text(
            json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if include_templates:
            (OUT / f"{n:02}-A.md").write_text(report_markdown(result), encoding="utf-8", newline="\n")
            (OUT / f"{n:02}-A-links.json").write_text(
                json.dumps(result["report"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def verify_http():
    from server import Handler

    class MemoryHandler(Handler):
        def __init__(self, path, payload):
            body = json.dumps(payload).encode()
            self.path = path
            self.headers = {"Content-Length": str(len(body))}
            self.rfile = BytesIO(body)
            self.wfile = BytesIO()

        def send_response(self, code, message=None):
            self.status = code

        def send_header(self, keyword, value):
            pass

        def end_headers(self):
            pass

    fixtures_by_index = list(fixtures())
    for n in SAMPLES:
        births = fixtures_by_index[n - 1]
        expected = analyze_pair(*births)
        payload = {
            owner: {
                "date": "{year:04d}-{month:02d}-{day:02d}".format(**birth),
                "time": None if birth["hour"] is None else f"{birth['hour']:02d}:00",
            }
            for owner, birth in zip(("a", "b"), births)
        }
        responses = {}
        for mode in ("preview", "report"):
            handler = MemoryHandler(f"/api/compatibility/{mode}", payload)
            handler.do_POST()
            assert handler.status == 200
            responses[mode] = json.loads(handler.wfile.getvalue())
        assert responses["report"] == {"version": "1.4", "chapters": expected["report"]}
        assert responses["preview"]["excerpt"] == expected["report"][1]["paragraphs"][0]["text"]
        assert responses["preview"]["chapters"] == [ch["title"] for ch in expected["report"]]

def measure():
    for side in ("A", "B"):
        docs = []
        for n in SAMPLES:
            lines = (OUT / f"{n:02}-{side}.md").read_text(encoding="utf-8").splitlines()
            body = " ".join(line for line in lines if line and not line.startswith("##")
                            and not line.startswith("전통 명리의 상징을 바탕으로 구성한 대화 제안입니다."))
            docs.append(re.split(r"(?<=[.!?]) +", body))
        counts = Counter(sentence for doc in docs for sentence in set(doc))
        shared = sum(count > 1 for count in counts.values())
        occurrences = sum(counts[sentence] > 1 for doc in docs for sentence in doc)
        print(side, "sentences", list(map(len, docs)), "shared_unique", shared, "shared_occurrences", occurrences)

if __name__ == "__main__":
    import sys
    create_packets("--templates" in sys.argv)
    if "--http" in sys.argv:
        verify_http()
    if "--measure" in sys.argv:
        measure()

