"""Offline candidate. Derive a relationship brief from unchanged chart facts."""

from compatibility_v12 import analyze_pair as analyze_facts, review_report
from compatibility_v14 import infer
from compatibility_editorial_prose import render


def role_brief(owner, finding):
    lead = finding["lead"]
    alternative = finding["alternative"]
    repeated = [item["id"] for item in finding["ranked_roles"]
                if item["stem"] == lead["stem"] and item["id"] != lead["id"]]
    placement = "hidden"
    if lead["visible_role_ids"]:
        placement = "visible"
    elif lead["id"] == finding["month_id"]:
        placement = "month"
    return {
        "owner": owner, "lead": lead["id"], "role": lead["ten_god"],
        "alternative": alternative["id"] if alternative else None,
        "alternative_role": alternative["ten_god"] if alternative else None,
        "placement": placement, "exposed": lead["visible_role_ids"],
        "repeated": repeated, "missing": finding["unresolved_pillars"],
    }


def interaction_brief(ref, evidence):
    if not ref:
        return None
    card = evidence[ref]
    return {"id": ref, "kind": card["kind"], "layer": card["layer"],
            "sources": card["sources"]}


def build_brief(base):
    ranked = infer(base)
    evidence = base["evidence"]
    relationship = ranked["relationship"]
    support = interaction_brief(relationship["support_id"], evidence)
    tension = interaction_brief(relationship["tension_id"], evidence)
    directions = [{"id": ref, "role": evidence[ref]["ten_god"]}
                  for ref in relationship["direction_ids"]]
    # Interpret both viewpoints on one actual letter, prioritizing a shared
    # slot and then the same letter across the interaction. Never infer a
    # life domain from a pillar.
    focus = (tension or support)
    contrast = None
    if focus:
        by_stem = {}
        for source in focus["sources"]:
            by_stem.setdefault(source["read_stem"], []).append(source["source_id"])
        source = max(focus["sources"], key=lambda row: (
            len(by_stem[row["read_stem"]]),
            (row["person"], row["pillar"]) in relationship["shared_slots"],
            row["pillar"] == "day",
        ))
        roles = [source["owner_ten_god"], source["other_ten_god"]]
        if source["person"] == "b":
            roles.reverse()
        contrast = {"source": source, "roles": roles,
                    "same_letter": by_stem[source["read_stem"]]}
    return {
        "natal": [role_brief(owner, finding) for owner, finding in ranked["natal"].items()],
        "relationship": {
            "support": support, "tension": tension, "directions": directions,
            "scope": relationship["scope"], "shared_slots": relationship["shared_slots"],
            "contrast": contrast,
        },
    }


def analyze_pair(a, b):
    """Generate the review candidate without changing the public report path."""
    base = analyze_facts(a, b)
    plan = build_brief(base)
    report = render(plan, base["evidence"])
    return {**base, "version": "1.5-editorial", "plan": plan, "report": report,
            "review": review_report(report, base["evidence"])}
