#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 StigReady
# SPDX-License-Identifier: MIT
"""Score an OpenSCAP results.xml from your own host with this role's exception list.

The score counts pass and fail rule results, leaving out the rules listed in
compliance/exempt-rules.txt, and checks it against min_score in compliance/verify.json.
No OpenSCAP results ship with this repository, so there is no published score to compare to.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_exempt(path: Path | None) -> set[str]:
    if not path or not path.is_file():
        return set()
    out: set[str] = set()
    for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.add(ln)
    return out


def _parse_results(results_xml: Path, exempt: set[str]) -> tuple[int, int, int, list[str]]:
    try:
        from defusedxml.ElementTree import parse as parse_xml
    except ImportError:
        import xml.etree.ElementTree as ET  # noqa: S405

        parse_xml = ET.parse  # type: ignore[assignment]

    tree = parse_xml(str(results_xml))
    root = tree.getroot()
    ns = {"xccdf": "http://checklists.nist.gov/xccdf/1.2"}
    pass_n = fail_n = other = 0
    fails: list[str] = []
    for rr in root.findall(".//xccdf:rule-result", ns):
        rule_id = rr.get("idref", "")
        short = rule_id.split("content_rule_")[-1] if "content_rule_" in rule_id else rule_id
        if short in exempt or rule_id in exempt:
            continue
        result_el = rr.find("xccdf:result", ns)
        result = (result_el.text or "").strip() if result_el is not None else ""
        if result == "pass":
            pass_n += 1
        elif result == "fail":
            fail_n += 1
            fails.append(short)
        elif result in ("notapplicable", "notselected"):
            continue
        else:
            other += 1
    return pass_n, fail_n, other, fails


def score_results(
    results_xml: Path,
    *,
    min_score: float,
    exempt: set[str],
) -> dict:
    pass_n, fail_n, other, fails = _parse_results(results_xml, exempt)
    total = pass_n + fail_n
    score = round((100.0 * pass_n / total) if total else 0.0, 2)
    gate = score >= min_score
    line = f"OpenSCAP: pass={pass_n} fail={fail_n} score={score:.1f}% (target {min_score:.0f}%)"
    return {
        "pass": pass_n,
        "fail": fail_n,
        "other": other,
        "total_scored": total,
        "score": score,
        "min_score": min_score,
        "meets_floor": gate,
        "gate_pass": gate,
        "failures": sorted(fails),
        "openscap_line": line,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Score an OpenSCAP results.xml from your own host with this role's exception list "
        "(compliance/exempt-rules.txt) and the min_score in compliance/verify.json."
    )
    ap.add_argument("--results", type=Path, required=True, help="Path to the OpenSCAP results.xml from your host")
    ap.add_argument("--verify-json", type=Path, default=Path("compliance/verify.json"))
    ap.add_argument("--profile", required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()
    root = args.repo_root.resolve()
    verify_path = args.verify_json if args.verify_json.is_absolute() else root / args.verify_json
    verify = json.loads(verify_path.read_text())
    min_score = float(verify.get("min_score", 90))
    exempt_file = verify.get("exempt_rules_file", "compliance/exempt-rules.txt")
    exempt = _load_exempt(root / exempt_file)

    if not args.results.is_file():
        print(f"ERROR: results not found: {args.results}", file=sys.stderr)
        return 1

    report = score_results(args.results, min_score=min_score, exempt=exempt)
    print(json.dumps(report, indent=2))
    print(report["openscap_line"])
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
