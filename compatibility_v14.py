"""Offline Yeonyeon v1.4. Chart facts, hypotheses and prose are separate outputs."""

from compatibility_v11 import SUPPORT
from compatibility_v12 import analyze_pair as analyze_v12, review_report
from compatibility_v13 import ASSUMPTIONS, natal_hypothesis, relationship_hypothesis
from compatibility_v14_prose import render

# Interpretive vocabulary for five role families, with no predicted behavior.
LENSES = {
    "비견": "agency", "겁재": "agency",
    "식신": "expression", "상관": "expression",
    "정재": "commitment", "편재": "commitment",
    "정관": "standard", "편관": "standard",
    "정인": "reception", "편인": "reception",
}


def infer(base):
    evidence = base["evidence"]
    natal = {}
    for owner, context in base["contexts"].items():
        finding = natal_hypothesis(owner, context, evidence)
        natal[owner] = {
            **finding,
            "unresolved_pillars": context["unresolved_pillars"],
            "lead_lens": LENSES[finding["lead"]["ten_god"]],
            "alternative_lens": (
                LENSES[finding["alternative"]["ten_god"]]
                if finding["alternative"] else None
            ),
        }

    relationship = relationship_hypothesis(evidence, base["interactions"], natal)
    lead_id, counter_id = relationship["lead_id"], relationship["counter_id"]
    support_id = tension_id = None
    for ref in (lead_id, counter_id):
        if ref and evidence[ref]["kind"] in SUPPORT:
            support_id = ref
        elif ref:
            tension_id = ref

    scope = "unpaired"
    shared_slots = []
    if support_id and tension_id:
        support, tension = evidence[support_id], evidence[tension_id]
        support_slots = {(s["person"], s["pillar"]) for s in support["sources"]}
        tension_slots = {(s["person"], s["pillar"]) for s in tension["sources"]}
        shared_slots = sorted(support_slots & tension_slots)
        if support_slots == tension_slots:
            scope = "same_sources" if support["layer"] == tension["layer"] else "same_slots"
        else:
            scope = "partial" if shared_slots else "separate"

    return {
        "natal": natal,
        "relationship": {
            **relationship,
            "support_id": support_id,
            "tension_id": tension_id,
            "scope": scope,
            "shared_slots": shared_slots,
            "direction_lenses": [
                LENSES[evidence[ref]["ten_god"]] for ref in relationship["direction_ids"]
            ],
        },
    }


def analyze_pair(a, b):
    """Accept the existing birth dictionaries and return a three-chapter draft."""
    base = analyze_v12(a, b)
    plan = infer(base)
    report = render(plan, base["evidence"])
    return {
        **base,
        "version": "1.4",
        "assumptions": ASSUMPTIONS,
        "plan": plan,
        "report": report,
        "review": review_report(report, base["evidence"]),
    }
