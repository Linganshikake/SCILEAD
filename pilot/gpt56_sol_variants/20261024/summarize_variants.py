"""Report completed evaluations without inventing missing scores or pooled ColdStart runs."""
import json
import statistics
import sys
from pathlib import Path

import variant_runtime as v
from evaluate_variants import BRANCHES, STAGES, METRICS, aggregate_results, boundary

COLD = BRANCHES[1:]
LB_KEYS = {"LR": "LR_exact_tdm_hit", "Finite nonempty": "LR_nonempty_finite_result",
           "PC": "PC_official", "RC": "RC_official", "RBO (values)": "RBO_official_value_rankings",
           "AO (paper IDs)": "AO_paper_id_macro_all_gold_boards"}
LEGACY = {"partially": v.PILOT / "full43_partially",
          **{b: v.PILOT / "full43_cold_start" / ("order_" + b[5:]) for b in COLD}}
STAGE_ROLES = {
    "partially": {
        "stage1": "Primary Partially tuple-extraction comparison, evaluated after its own dynamic name normalization.",
        "stage2": "Additional matching to the 27 Gold leaderboard triples; tuple metrics are post-alignment diagnostics, not the primary Partially tuple comparison or the same naming scope as Fully.",
    },
    "cold_start": {
        "stage1": "Dynamic open-vocabulary naming diagnostics; all three name sets started empty.",
        "stage2": "Post-leaderboard-alignment tuple diagnostics; ColdStart primary results are the stage-2 leaderboard metrics across the three paper orders.",
    },
}


def table(headers, rows):
    def cell(value):
        if value is None:
            return "—"
        if isinstance(value, float):
            return f"{value:.6f}"
        return str(value).replace("|", "\\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"] +
                     ["| " + " | ".join(cell(x) for x in row) + " |" for row in rows])


def source(path):
    return {"path": str(path), "sha256": v.sha(path)}


def checked_metrics(info, prediction):
    assert info.get("status") == "COMPLETE", "Evaluation entry is incomplete"
    path = Path(info["metrics_path"])
    assert v.sha(path) == info["metrics_sha256"], f"Stale metrics: {path}"
    expected = info.get("input_sha256", info.get("prediction_sha256"))
    assert expected == v.sha(prediction), f"Prediction changed after evaluation: {prediction}"
    for input_path, expected_hash in info.get("inputs_sha256", {}).items():
        assert v.sha(input_path) == expected_hash, f"Evaluation input changed: {input_path}"
    return v.read(path)


def collect(branch):
    run = v.TOP / branch
    result = {"status": "INCOMPLETE", "stages": {}, "leaderboards": {}, "leaderboard_sources": {}, "usage": {}, "normalization_progress": {}, "issues": []}
    # Accounting and saved stage progress remain visible before evaluation exists.
    for stage in STAGES:
        for filename, key in (("api_usage.json", "usage"), ("summary.json", "normalization_progress")):
            path = run / stage / filename
            if path.is_file():
                try:
                    data = v.read(path)
                    result[key][stage] = data if key == "usage" else {k: data[k] for k in ("status", "api_calls") if k in data}
                except (OSError, ValueError) as error:
                    result["issues"].append(f"Cannot read saved {stage}/{filename}: {error}")
    evaluation = run / "evaluation/status.json"
    if not evaluation.is_file():
        result["issues"].append("Evaluation has not been run")
        return result
    saved = v.read(evaluation)
    try:
        for stage, info in saved.get("stages", {}).items():
            summary = v.read(run / stage / "summary.json")
            assert summary["status"] == "COMPLETE"
            prediction = run / stage / STAGES[stage]
            assert summary["output_sha256"] == v.sha(prediction)
            metrics = checked_metrics(info, prediction)
            result["stages"][stage] = {"aggregate": metrics["aggregate"], "source": source(Path(info["metrics_path"])),
                                        "normalization": summary,
                                        "strict_result_auxiliary": v.read(run / "evaluation" / stage / "strict_result_metrics.json")["aggregate"]}
        for scope, info in saved.get("leaderboards", {}).items():
            result["leaderboards"][scope] = checked_metrics(info, run / "stage2" / STAGES["stage2"])["aggregate"]
            result["leaderboard_sources"][scope] = source(Path(info["metrics_path"]))
        result["issues"].extend(saved.get("missing", []))
        if saved.get("error"):
            result["issues"].append(saved["error"])
        if saved.get("status") == "COMPLETE" and set(result["stages"]) == set(STAGES) and set(result["leaderboards"]) == {"all27", "masked10"}:
            result["status"] = "COMPLETE"
    except (OSError, ValueError, KeyError, AssertionError) as error:
        result["status"] = "INVALID_OR_STALE"
        result["issues"].append(str(error))
    return result


def baselines():
    result = {"gpt41": {}, "gpt56_fully": {}, "sources": [], "issues": []}
    for branch, root in LEGACY.items():
        stages = {}
        for stage in STAGES:
            path = root / "evaluation" / stage / "metrics_with_f1.json"
            stages[stage] = v.read(path)["aggregate"]
            result["sources"].append(source(path))
        boards = {}
        for scope in ("all27", "masked10"):
            path = (root / "leaderboard_evaluation" / ("masked_subset" if scope == "masked10" else scope) if branch == "partially"
                    else root / "evaluation" / scope) / "paper_metrics/leaderboard_metrics.json"
            boards[scope] = v.read(path)["aggregate"]
            result["sources"].append(source(path))
        result["gpt41"][branch] = {"stages": stages, "leaderboards": boards}
    path = v.BASE / "evaluation/eval_results.json"
    result["gpt56_fully"]["tdm"] = aggregate_results(v.read(path))
    result["sources"].append(source(path))
    root = v.TOP / "evaluation_references/gpt56_fully"
    status = root / "status.json"
    result["gpt56_fully"]["leaderboards"] = {}
    if status.is_file() and v.read(status).get("status") == "COMPLETE":
        try:
            for scope, info in v.read(status)["leaderboards"].items():
                result["gpt56_fully"]["leaderboards"][scope] = checked_metrics(info, v.BASE / "merged/normalized_output.json")["aggregate"]
                result["sources"].append(source(Path(info["metrics_path"])))
            assert set(result["gpt56_fully"]["leaderboards"]) == {"all27", "masked10"}, "Fully reference scopes are incomplete"
        except (OSError, KeyError, ValueError, AssertionError) as error:
            result["issues"].append(str(error))
    else:
        result["issues"].append("GPT-5.6 Fully leaderboard reference evaluation is incomplete")
    return result


def statistics_for(values):
    assert set(values) == set(COLD)
    numbers = list(values.values())
    return {"values": values, "mean": statistics.mean(numbers),
            "sample_std_ddof1": statistics.stdev(numbers), "population_std_ddof0": statistics.pstdev(numbers)}


def cold_statistics(runs):
    missing = [b for b in COLD if runs[b]["status"] != "COMPLETE"]
    if missing:
        return {"status": "INCOMPLETE", "missing_runs": missing, "n_required": 3,
                "reason": "No partial-run mean, zero imputation, or prediction pooling."}
    result = {"status": "COMPLETE", "n": 3, "main_ddof": 1, "additional_ddof": 0,
              "author_ddof": "Unconfirmed", "aggregation": "Per-run macro metrics, then mean and SD across three independent runs; no prediction pooling.",
              "stages": {}, "leaderboards": {}}
    for stage in STAGES:
        result["stages"][stage] = {name: {measure: statistics_for({b: runs[b]["stages"][stage]["aggregate"][name][measure] for b in COLD})
                                                 for measure in ("Precision", "Recall", "F1")} for name in METRICS}
    for scope in ("all27", "masked10"):
        result["leaderboards"][scope] = {name: statistics_for({b: runs[b]["leaderboards"][scope][key] for b in COLD}) for name, key in LB_KEYS.items()}
    return result


def build_report(runs, baseline, cold, status):
    lines = ["# GPT-5.6 Sol Partially / ColdStart evaluation", "", f"Status: **{status}**.", "",
             "Completion refers to all required official stages and hash-checked evaluations. Historical failed attempts remain in the accounting after an authorized recovery; completion does not require failed_or_unknown=0.", "",
             "Scope: 43 papers, 335 recovered extraction rows, 295 Gold rows; the paper keys are reordered to the legacy order while each paper's records, fields and source documents are preserved.", "",
             "Official normalization and evaluator algorithms are retained. Requests use gpt-5.6-sol, reasoning_effort=medium, max_completion_tokens=32768, stream=false, and omit seed/temperature. Method masking seed is integer 0; ColdStart order seeds are None, string '0', string '42'; PYTHONHASHSEED=0.", "",
             "The GPT-4.1 history used 284 extraction rows and uncapped generation with temperature/seed=0. Cross-model differences therefore include extraction and generation-policy differences; they are not an isolated normalization-model comparison. Fully CS belongs to a separate agent and is not included in this report's completion status.", "",
             "## Branch readiness", "", table(["Branch", "Evaluation status", "Last saved stage 1", "Last saved stage 2", "Issues"], [[b, runs[b]["status"], *[runs[b].get("normalization_progress", {}).get(s, {}).get("status") for s in STAGES], "; ".join(runs[b]["issues"])] for b in BRANCHES]), "",
             "Saved stage statuses and usage are snapshots and may lag a resumed worker. Missing or incomplete evaluations receive no score; omitted tuple tables and dashes do not mean zero. Available completed stages are reported independently.", "",
             "## Both-stage TDM / TDMR metrics", "",
             "P/R are official per-paper macro means. F1 is 2PR/(P+R) using those means. The separate mean of per-paper F1 remains in the evaluation JSON.", "",
             "Partially stage 1 is the primary tuple-extraction comparison after dynamic normalization. Stage 2 adds matching to the 27 Gold leaderboard triples and supplies leaderboard evaluation; its tuple scores are supplementary post-alignment diagnostics. Fully normalizes individual fields against the full predefined name sets, so stage-2 Partially scores must not be presented as the same naming scope as Fully. Even the primary stage-1 comparison has intentionally different candidate availability. ColdStart tuple metrics at both stages are diagnostic; its primary results are the three-order leaderboard scores. Both stages are retained without choosing the higher score.", ""]
    for branch in BRANCHES:
        for stage, data in runs[branch]["stages"].items():
            rows = []
            for name in METRICS:
                current = data["aggregate"][name]
                previous = baseline["gpt41"][branch]["stages"][stage][name]
                fully = baseline["gpt56_fully"]["tdm"][name]
                rows.append([name, current["Precision"], current["Recall"], current["F1"], previous["F1"], current["F1"] - previous["F1"], fully["F1"]])
            role = STAGE_ROLES["partially" if branch == "partially" else "cold_start"][stage]
            lines += [f"### {branch} / {stage}", "", role, "",
                      table(["Metric", "P", "R", "F1", "GPT-4.1 same variant/stage F1", "Delta F1", "GPT-5.6 Fully reference F1"], rows), "",
                      "Strict Decimal Result diagnostic (auxiliary): " + json.dumps(data["strict_result_auxiliary"]) + ".", ""]
    lines += ["## Leaderboards", "",
              "LR is exact TDM hit before numeric conversion; finite nonempty rate is separate. PC/RC/RBO use unchanged official formulas. Official RBO compares deduplicated numeric scores. AO compares paper IDs, sorts ties by paper ID, and averages prefix overlap through min(rank-list lengths). Empty predictions remain zero in the full 27/10-board denominator; RC is not clipped. All 43 papers participate in both scopes.", ""]
    for scope in ("all27", "masked10"):
        rows = []
        for branch in BRANCHES:
            previous = baseline["gpt41"][branch]["leaderboards"][scope]
            rows.append(["GPT-4.1 " + branch, *[previous[key] for key in LB_KEYS.values()]])
            current = runs[branch]["leaderboards"].get(scope)
            if current is not None:
                rows.append(["GPT-5.6 " + branch, *[current[key] for key in LB_KEYS.values()]])
            else:
                rows.append(["GPT-5.6 " + branch + " (unavailable)", *[None for _ in LB_KEYS]])
        fully = baseline["gpt56_fully"]["leaderboards"].get(scope)
        if fully is not None:
            rows.append(["GPT-5.6 Fully", *[fully[key] for key in LB_KEYS.values()]])
        lines += [f"### {scope}", "", table(["Run", *LB_KEYS], rows), ""]
    lines += ["## ColdStart three-order aggregation", ""]
    if cold["status"] != "COMPLETE":
        lines += ["INCOMPLETE: " + ", ".join(cold["missing_runs"]) + ". No three-run mean or SD is reported.", ""]
    else:
        lines += ["Each run is macro-averaged first. Main SD uses ddof=1; population SD uses ddof=0. The author's ddof is unconfirmed. Complete P/R/F1 statistics are saved in summary/cold_statistics.json.", ""]
        for scope, metrics in cold["leaderboards"].items():
            rows = []
            for name, item in metrics.items():
                old = statistics_for({b: baseline["gpt41"][b]["leaderboards"][scope][LB_KEYS[name]] for b in COLD})
                rows.append([name, item["mean"], item["sample_std_ddof1"], item["population_std_ddof0"], old["mean"], old["sample_std_ddof1"]])
            lines += [f"### {scope}", "", table(["Metric", "Mean", "Sample SD", "Population SD", "GPT-4.1 mean", "GPT-4.1 sample SD"], rows), ""]
        for stage, metrics in cold["stages"].items():
            lines += [f"### {stage} F1 diagnostics", "", table(["Metric", "Mean F1", "Sample SD", "Population SD"],
                       [[name, item["F1"]["mean"], item["F1"]["sample_std_ddof1"], item["F1"]["population_std_ddof0"]] for name, item in metrics.items()]), ""]
    usage_rows = []
    for branch, run in runs.items():
        for stage, usage in run["usage"].items():
            logical = usage.get("logical_completed")
            if logical is None:
                # Older successful workers lack the counter; their completed-stage
                # cursor is the number of logical requests, not physical attempts.
                normalized = run["stages"].get(stage, {}).get("normalization", run.get("normalization_progress", {}).get(stage, {}))
                if normalized.get("status") == "COMPLETE":
                    logical = normalized.get("api_calls")
            usage_rows.append([branch, stage, usage.get("attempts"), usage.get("successful_responses"), usage.get("failed_or_unknown"),
                               usage.get("unknown_usage_attempts"), logical, usage.get("authorized_additional_attempts"),
                               usage.get("prompt_tokens"), usage.get("completion_tokens"), usage.get("total_tokens")])
    lines += ["## Recorded API usage", "", table(["Branch", "Stage", "Physical attempts", "Accepted responses", "Historical failed/unknown", "Unknown usage", "Logical completed", "Authorized extra attempts", "Prompt", "Completion", "Total tokens"], usage_rows), "",
              "Physical attempts include original HTTP 524 failures or HTTP 403 quota refusals and their explicitly authorized retries. Each successful one-retry recovery contributes two physical attempts, one accepted response, and one completed logical request; the original failed attempt remains recorded after recovery or refill. Its missing token usage remains unknown, rather than being inferred as zero. Accepted parent pointers and saved-response replays are not additional network attempts. An absent counter is shown as missing; for older completed workers only, logical count may come from the completed-stage request cursor. These accounting fields do not change metric aggregation or require historical failures to be zero for completion.", "",
              "These counters describe normalization calls already recorded by the parent runner. Evaluation/reporting makes zero API requests. Missing usage stays missing; charges are not inferred from tokens. Historical requests: Partially 340+204; ColdStart default 279+282, string-0 293+282, string-42 283+281 (2244 total).", "",
              "## Reproducibility and limitations", "",
              "Source paths and hashes, all branch metrics, comparisons and status are in summary/variant_comparison.json. Per-paper values and strict Result diagnostics are in each branch's evaluation directory. Leaderboard helper scripts are copied byte-for-byte; generated common.py binds the new predictions and the experiment's 335-row merged raw input. Helper LR_primary prose is a legacy label; this report explicitly uses LR_exact_tdm_hit.", "",
              "The supplied 27 boards and the exact historical masked 10 are retained. New scores never alter prompts, candidate sets, parsing, Gold, or ranking formulas. A report marked complete refers only to completed and hash-checked evaluations, not an independent API replay validation.", ""]
    if baseline["issues"]:
        lines += ["Reference issues: " + "; ".join(baseline["issues"]), ""]
    return "\n".join(lines)


def main():
    boundary()
    required = [v.TOP / name for name in ("protected_hashes.json", "inputs/output.json", "experiment_manifest.json")]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        result = {"status": "INCOMPLETE", "missing": missing, "reason": "Preparation is unfinished"}
        v.save(v.TOP / "summary/report_status.json", result)
        print(json.dumps(result)); return 2
    integrity = v.verify()
    runs = {branch: collect(branch) for branch in BRANCHES}
    baseline = baselines()
    cold = cold_statistics(runs)
    status = "COMPLETE" if all(r["status"] == "COMPLETE" for r in runs.values()) and not baseline["issues"] else "INCOMPLETE"
    result = {"status": status, "completion_scope": "Four variant evaluations and GPT56 Fully reference; excludes Fully CS and does not certify API replay.",
              "branches": runs, "baselines": baseline, "cold_statistics": cold, "source_integrity": integrity,
              "stage_metric_roles": STAGE_ROLES,
              "request_accounting": {"attempts": "Physical HTTP attempts, including original failures and authorized retries.",
                                     "successful_responses": "Accepted physical responses; a parent retry pointer is not another response.",
                                     "failed_or_unknown": "Historical physical failures or uncertain attempts; retained after recovery.",
                                     "logical_completed": "Completed official request positions; replay is not another position.",
                                     "authorized_additional_attempts": "Explicitly authorized additional physical attempts, separate from automatic retries.",
                                     "completion_requires_zero_historical_failures": False},
              "new_api_requests": 0, "historical_request_counts": {"partially": [340, 204], "cold_default": [279, 282], "cold_0": [293, 282], "cold_42": [283, 281]}}
    v.save(v.TOP / "summary/variant_comparison.json", result)
    v.save(v.TOP / "summary/cold_statistics.json", cold)
    (v.TOP / "report.md").write_text(build_report(runs, baseline, cold, status), encoding="utf-8")
    v.save(v.TOP / "summary/report_status.json", {"status": status, "report_sha256": v.sha(v.TOP / "report.md"),
                                                "branch_statuses": {b: r["status"] for b, r in runs.items()}, "source_integrity": v.verify(),
                                                "completion_scope": result["completion_scope"], "new_api_requests": 0})
    print(json.dumps({"status": status, "report": str(v.TOP / "report.md"), "cold_statistics": cold["status"]}))
    return 0 if status == "COMPLETE" else 2


if __name__ == "__main__":
    sys.exit(main())
