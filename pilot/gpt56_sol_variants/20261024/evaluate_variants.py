"""Offline original-main evaluation; writes only this experiment's evaluation outputs.

Run after preparation and normalization: python -B -X utf8 evaluate_variants.py
--branch all. Incomplete stages are reported, never treated as zero scores.
"""
import argparse
import contextlib
import json
import math
import shutil
import subprocess
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import SimpleNamespace

import variant_runtime as v

BRANCHES = ("partially", "cold_default", "cold_0", "cold_42")
STAGES = {"stage1": "normalized_output.json", "stage2": "leaderboard_normalized_output.json"}
METRICS = ("Task IIM", "Dataset IIM", "Metric IIM", "Result IIM", "TDM Exact Match", "TDMR Exact Match")


def boundary():
    def guard(event, args):
        if event in ("socket.connect", "socket.getaddrinfo"):
            raise RuntimeError("Evaluation is offline")
    sys.addaudithook(guard)
    v.setup()


def metric(p, r):
    return {"Precision": p, "Recall": r, "F1": 2 * p * r / (p + r) if p + r else 0.0}


def number(value):
    try:
        parsed = Decimal(str(value))
        return parsed if parsed.is_finite() else None
    except InvalidOperation:
        return None


def strict_metric(rows, gold):
    # Same separate diagnostic as the legacy adapters; never replaces official IIM.
    pn = {number(r["Result"]) for r in rows}
    gn = {number(r["Result"]) for r in gold}
    common = (pn & gn) - {None}
    pd = len(pn - {None}) + len({r["Result"] for r in rows if number(r["Result"]) is None})
    gd = len(gn - {None}) + len({str(r["Result"]) for r in gold if number(r["Result"]) is None})
    return metric(len(common) / pd if pd else 0, len(common) / gd if gd else 0)


def aggregate_results(result):
    aggregate = {k + " IIM": metric(x["Precision"], x["Recall"]) for k, x in result["Individual"].items()}
    aggregate["TDM Exact Match"] = metric(result["Exact Match Precision wo Results"], result["Exact Match Recall wo Results"])
    aggregate["TDMR Exact Match"] = metric(result["Exact Match Precision"], result["Exact Match Recall"])
    return aggregate


def close_metrics(left, right):
    assert all(math.isfinite(left[k]) and abs(left[k] - right[k]) < 1e-14 for k in ("Precision", "Recall", "F1")), (left, right)


def paper_order(conf):
    order = conf["paper_order"]
    if isinstance(order, str):
        order = v.read(order)["papers"]
    assert isinstance(order, list) and len(order) == len(set(order))
    return order


def check_rows(normalized, raw, order=None):
    assert set(normalized) == set(raw) and len(raw) == 43
    if order is not None:
        assert list(normalized) == order
    for paper, source in raw.items():
        rows = json.loads(source["output"])
        got = normalized[paper]
        assert len(got["normalized_output"]) == len(rows), paper
        assert got["source_documents"] == source["source_documents"], paper
        assert [r["Result"] for r in got["normalized_output"]] == [r["Result"] for r in rows], paper
    assert sum(len(x["normalized_output"]) for x in normalized.values()) == 335


def evaluate_tdm(run, stage, path, conf):
    import tdm_eval
    out = run / "evaluation" / stage
    out.mkdir(parents=True, exist_ok=True)
    before = v.sha(path)
    raw = v.read(conf["input_path"])
    gold = v.read(conf["gold_path"])
    normalized = v.read(path)
    check_rows(normalized, raw, paper_order(conf))
    assert set(gold) == set(raw) and sum(len(x["TDMs"]) for x in gold.values()) == 295
    args = SimpleNamespace(gold_data_path=conf["gold_path"], normalized_tdm_output_path=str(path),
                           eval_results_path=str(out / "eval_results.json"), eval_values_path=str(out / "eval_values.json"))
    v.save(out / "invocation.json", vars(args))
    with (out / "run.log").open("w", encoding="utf-8") as log, contextlib.redirect_stdout(log):
        tdm_eval.main(args)
    result = v.read(out / "eval_results.json")
    values = v.read(out / "eval_values.json")
    baseline_values = v.read(v.BASE / "evaluation/eval_values.json")
    baseline = aggregate_results(v.read(v.BASE / "evaluation/eval_results.json"))
    aggregate = aggregate_results(result)
    per_paper, strict_per, strict_raw = {}, {}, {}
    for paper in normalized:
        row = {k + " IIM": metric(x["Precision"][paper], x["Recall"][paper]) for k, x in values["Individual"].items()}
        # The official per-paper precision key is misspelled; preserve its meaning.
        row["TDM Exact Match"] = metric(values["Exact Match Recall wo Precision"][paper], values["Exact Match Recall wo Results"][paper])
        row["TDMR Exact Match"] = metric(values["Exact Match Precision"][paper], values["Exact Match Recall"][paper])
        assert row["Result IIM"] == metric(baseline_values["Individual"]["Result"]["Precision"][paper], baseline_values["Individual"]["Result"]["Recall"][paper])
        per_paper[paper] = row
        strict_per[paper] = strict_metric(normalized[paper]["normalized_output"], gold[paper]["TDMs"])
        strict_raw[paper] = strict_metric(json.loads(raw[paper]["output"]), gold[paper]["TDMs"])
    close_metrics(aggregate["Result IIM"], baseline["Result IIM"])
    assert strict_per == strict_raw
    strict_aggregate = metric(sum(x["Precision"] for x in strict_per.values()) / len(raw),
                              sum(x["Recall"] for x in strict_per.values()) / len(raw))
    assert v.sha(path) == before
    v.save(out / "metrics_with_f1.json", {
        "status": "COMPLETE", "stage": stage, "input_path": str(path), "input_sha256": before,
        "papers": 43, "gold_tdmrs": 295, "predictions": 335, "aggregate": aggregate,
        "aggregation": "Official per-paper macro P/R; F1 is the harmonic mean of those macro P/R, not mean per-paper F1.",
        "mean_per_paper_f1_SEPARATE": {k: sum(x[k]["F1"] for x in per_paper.values()) / len(raw) for k in METRICS},
        "result_iim_unchanged": True, "result_baseline": str(v.BASE / "evaluation"), "comparison_tolerance": 1e-14,
    })
    v.save(out / "per_paper_metrics.json", per_paper)
    v.save(out / "strict_result_metrics.json", {
        "aggregate": strict_aggregate, "per_paper": strict_per, "unchanged_from_raw": True,
        "definition": "Legacy Decimal finite numeric equality; invalid strings remain distinct denominator entries. Auxiliary only.",
    })
    return {"status": "COMPLETE", "input_path": str(path), "input_sha256": before,
            "metrics_path": str(out / "metrics_with_f1.json"), "metrics_sha256": v.sha(out / "metrics_with_f1.json")}


def evaluate_leaderboards(out, gold_path, normalized_path):
    """Copy both audited helper scripts byte-for-byte; only common.py binds paths."""
    out = Path(out)
    gold_path, normalized_path = Path(gold_path), Path(normalized_path)
    source = v.PILOT / "full43_cs/leaderboard_evaluation"
    for name in ("official", "paper_metrics", "leaderboards", "reference"):
        (out / name).mkdir(parents=True, exist_ok=True)
    copies = []
    for name in ("run_official_leaderboard_eval.py", "evaluate_paper_metrics.py"):
        shutil.copyfile(source / name, out / name)
        assert v.sha(source / name) == v.sha(out / name)
        copies.append({"source": str(source / name), "copy": str(out / name), "sha256": v.sha(out / name)})
    common = f'''import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, {str(v.TOP)!r})
import variant_runtime as v
json, read, save, sha, REPO = v.json, v.read, v.save, v.sha, v.REPO
RUN = Path({str(out)!r})
BASE = Path({str(v.TOP)!r})
GOLD = Path({str(gold_path)!r})
NORMALIZED = Path({str(normalized_path)!r})
def boundary():
    def guard(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo'):
            raise RuntimeError('Evaluation is offline')
    sys.addaudithook(guard)
    v.setup()
def verify_frozen():
    return v.verify()
'''
    (out / "common.py").write_text(common, encoding="utf-8")
    hashes = {str(p): v.sha(p) for p in (gold_path, normalized_path, v.TOP / "merged/output.json")}
    for name in ("run_official_leaderboard_eval.py", "evaluate_paper_metrics.py"):
        with (out / (name + ".log")).open("w", encoding="utf-8") as log:
            completed = subprocess.run([sys.executable, "-B", "-X", "utf8", str(out / name)],
                                       cwd=out, stdout=log, stderr=subprocess.STDOUT)
        assert completed.returncode == 0, f"{out / (name + '.log')}: evaluator failed"
    assert all(v.sha(p) == h for p, h in hashes.items())
    metrics_path = out / "paper_metrics/leaderboard_metrics.json"
    metrics = v.read(metrics_path)
    assert metrics["aggregate"]["gold_leaderboards"] == len(v.read(gold_path))
    audit = {"status": "COMPLETE", "helpers": copies, "formulas_modified": False,
             "inputs_sha256": hashes, "gold_path": str(gold_path), "prediction_path": str(normalized_path),
             "metrics_path": str(metrics_path), "metrics_sha256": v.sha(metrics_path),
             "prediction_sha256": hashes[str(normalized_path)], "target_boards": len(v.read(gold_path)),
             "scope": "All 43 papers retained; only target Gold board set changes.", "new_api_requests": 0,
             "display_conventions": {"LR": "LR_exact_tdm_hit", "finite_nonempty_rate": "LR_nonempty_finite_result",
                                     "legacy_helper_wording": "Copied verbatim: its LR_primary prose is outdated and '27' wording is not a scope filter."}}
    v.save(out / "adapter_audit.json", audit)
    return audit


def evaluate_branch(branch):
    run = v.TOP / branch
    status = {"branch": branch, "status": "INCOMPLETE", "stages": {}, "leaderboards": {}, "missing": []}
    if not (run / "config.json").is_file():
        status["missing"].append(str(run / "config.json"))
        return status
    try:
        conf = v.read(run / "config.json")
        assert v.sha(conf["input_path"]) == conf["input_sha256"]
        assert v.read(conf["input_path"]) == v.read(v.TOP / "merged/output.json")
        assert len(v.read(conf["leaderboards_path"])) == 27
        assert len(v.read(v.TOP / "masking/partially_masked_leaderboards.json")) == 10
        assert v.sha(v.TOP / "masking/partially_masked_leaderboards.json") == v.sha(v.PILOT / "full43_partially/masking/partially_masked_leaderboards.json")
        for stage, filename in STAGES.items():
            path, summary = run / stage / filename, run / stage / "summary.json"
            if not path.is_file() or not summary.is_file() or v.read(summary).get("status") != "COMPLETE":
                status["missing"].append(f"{branch}/{stage}: completed normalization required")
                continue
            assert v.read(summary)["output_sha256"] == v.sha(path), f"{stage}: output hash mismatch"
            status["stages"][stage] = evaluate_tdm(run, stage, path, conf)
        if "stage2" in status["stages"]:
            for scope, gold in (("all27", Path(conf["leaderboards_path"])),
                                ("masked10", v.TOP / "masking/partially_masked_leaderboards.json")):
                status["leaderboards"][scope] = evaluate_leaderboards(run / "evaluation" / scope, gold, run / "stage2" / STAGES["stage2"])
        if len(status["stages"]) == 2 and len(status["leaderboards"]) == 2:
            status["status"] = "COMPLETE"
    except Exception as error:
        status.update(status="FAILED", error_type=type(error).__name__, error=str(error))
    v.save(run / "evaluation/status.json", status)
    return status


def evaluate_fully_reference(conf):
    out = v.TOP / "evaluation_references/gpt56_fully"
    normalized = v.BASE / "merged/normalized_output.json"
    status = {"status": "INCOMPLETE", "source": str(v.BASE), "leaderboards": {}}
    try:
        check_rows(v.read(normalized), v.read(v.TOP / "inputs/output.json"))
        for scope, gold in (("all27", Path(conf["leaderboards_path"])),
                            ("masked10", v.TOP / "masking/partially_masked_leaderboards.json")):
            status["leaderboards"][scope] = evaluate_leaderboards(out / scope, gold, normalized)
        historical = v.read(v.BASE / "leaderboard/eval_results.json")["gold_results"]
        actual = v.read(out / "all27/paper_metrics/leaderboard_metrics.json")["aggregate"]
        for new, old in (("PC_official", "Paper Coverage"), ("RC_official", "Result Coverage"), ("RBO_official_value_rankings", "RBO")):
            assert abs(actual[new] - historical[old]) < 1e-14
        status["status"] = "COMPLETE"
    except Exception as error:
        status.update(status="FAILED", error_type=type(error).__name__, error=str(error))
    v.save(out / "status.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", choices=("all",) + BRANCHES, default="all")
    args = parser.parse_args()
    boundary()
    required = [v.TOP / p for p in ("experiment_manifest.json", "protected_hashes.json", "inputs/output.json", "merged/output.json", "masking/partially_masked_leaderboards.json")]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        result = {"status": "INCOMPLETE", "reason": "Preparation is unfinished", "missing": missing, "new_api_requests": 0}
        v.save(v.TOP / "evaluation_status.json", result)
        print(json.dumps(result)); return 2
    v.verify()
    selected = BRANCHES if args.branch == "all" else (args.branch,)
    results = {branch: evaluate_branch(branch) for branch in selected}
    configs = [v.TOP / branch / "config.json" for branch in BRANCHES if (v.TOP / branch / "config.json").is_file()]
    reference = evaluate_fully_reference(v.read(configs[0])) if configs else {"status": "INCOMPLETE"}
    complete = all(x["status"] == "COMPLETE" for x in results.values()) and reference["status"] == "COMPLETE"
    result = {"status": "COMPLETE" if complete else "INCOMPLETE", "selected_branches": list(selected),
              "scope": "Selected branch evaluations only; no claim that other branches or Fully CS are complete.",
              "branches": results, "gpt56_fully_reference": reference, "new_api_requests": 0, "source_integrity": v.verify()}
    v.save(v.TOP / "evaluation_status.json", result)
    print(json.dumps({"status": result["status"], "branches": {k: x["status"] for k, x in results.items()},
                      "fully_reference": reference["status"]}, ensure_ascii=False))
    return 0 if complete else 2


if __name__ == "__main__":
    sys.exit(main())
