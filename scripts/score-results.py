#!/usr/bin/env python3
"""Score OpenSCAP results.xml (factory-compatible) and compare to release evidence."""
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
    ap = argparse.ArgumentParser(description="Score OpenSCAP results or compare to release evidence")
    ap.add_argument("--results", type=Path, help="Path to OpenSCAP results.xml")
    ap.add_argument("--verify-json", type=Path, default=Path("compliance/verify.json"))
    ap.add_argument("--profile", required=True)
    ap.add_argument("--release", help="Release folder name under compliance/releases/")
    ap.add_argument(
        "--compare",
        action="store_true",
        help="Compare computed score to compliance/releases/RELEASE/PROFILE/score.json",
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()
    root = args.repo_root.resolve()
    verify_path = args.verify_json if args.verify_json.is_absolute() else root / args.verify_json
    verify = json.loads(verify_path.read_text())
    min_score = float(verify.get("min_score", 90))
    exempt_file = verify.get("exempt_rules_file", "compliance/exempt-rules.txt")
    exempt = _load_exempt(root / exempt_file)

    results_path = args.results
    if args.compare:
        release = args.release or verify.get("release")
        if not release:
            print("ERROR: --release or verify.json release required for --compare", file=sys.stderr)
            return 2
        results_path = root / "compliance" / "prove-runs" / release / args.profile / "results.xml"
        expected_path = root / "compliance" / "releases" / release / args.profile / "score.json"
    else:
        expected_path = None
        if not results_path:
            print("ERROR: --results required unless --compare", file=sys.stderr)
            return 2

    if not results_path.is_file():
        print(f"ERROR: results not found: {results_path}", file=sys.stderr)
        return 1

    report = score_results(results_path, min_score=min_score, exempt=exempt)
    print(json.dumps(report, indent=2))
    print(report["openscap_line"])

    if args.compare and expected_path and expected_path.is_file():
        expected = json.loads(expected_path.read_text())
        exp_score = expected.get("score")
        got = report["score"]
        print(f"\nExpected (release evidence): {exp_score}% gate_pass={expected.get('gate_pass')}")
        if exp_score is not None and abs(float(exp_score) - float(got)) > 0.05:
            print("MISMATCH: score differs from pinned release evidence", file=sys.stderr)
            return 1
        if expected.get("gate_pass") and not report["gate_pass"]:
            print("MISMATCH: release passed gate but reprove did not", file=sys.stderr)
            return 1
        print("OK: reprove matches release evidence (within tolerance)")
    elif args.compare:
        print(f"NOTE: no expected score at {expected_path}; scored reprove only")

    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
