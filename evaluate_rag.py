import json
from pathlib import Path

from semantic_simulator import SemanticCommunicationSimulator

SLIDES_DIR = Path(__file__).resolve().parent / "slides_images"


def run_rag_evaluation():
    
    print("\n" + "=" * 70)
    print("Phase 3: End-to-end semantic TSR evaluation (delivered payload vs corpus)")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Semantic weights\n(λ/C = 1.2)",
            "link_capacity": 50,
            "arrival_rate": 60,
            "weight_dist": "semantic",
            "corpus_file": "corpus.txt"
        },
        {
            "name": "Semantic weights\n(λ/C = 2.0)",
            "link_capacity": 50,
            "arrival_rate": 100,
            "weight_dist": "semantic",
            "corpus_file": "corpus.txt"
        }
    ]
    
    scenario_snapshots = []
    
    for scenario in scenarios:
        print("\n" + "=" * 70)
        print(f"Scenario: {scenario['name']}")
        print("=" * 70)
        
        simulator = SemanticCommunicationSimulator(
            link_capacity=scenario['link_capacity'],
            arrival_rate=scenario['arrival_rate'],
            weight_dist=scenario['weight_dist'],
            sim_time=500,
            corpus_file=scenario.get('corpus_file')
        )
        
        simulator.run_with_evaluation()
        scenario_snapshots.append(simulator.export_metrics_snapshot(scenario['name']))
    
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "description": "TSR from rag.py weighted_similarity(original_line_i, aggregate_delivered_packet_text) over first 3 corpus lines (None if no corpus). "
        "Semantic traffic packet payloads carry segment text; Max-Weight and NUM replay the same arrival trace.",
        "scenarios": scenario_snapshots,
    }
    json_path = SLIDES_DIR / "tsr_evaluation_results.json"
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved TSR results to {json_path}")
    
    txt_path = SLIDES_DIR / "tsr_evaluation_summary.txt"
    lines = [
        "TSR evaluation summary",
        "",
    ]
    for snap in scenario_snapshots:
        lines.append(f"Scenario: {snap.get('scenario_name', '')}")
        for sched in ("maxweight", "num"):
            s = snap["schedulers"][sched]
            avg = s.get("average_tsr")
            avg_sp = s.get("average_semantic_preservation")
            lines.append(
                f"  {sched.upper()}: average_tsr={avg} average_semantic_preservation={avg_sp} "
                f"dropped={s.get('packets_dropped')}"
            )
        lines.append("")
    with open(txt_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Saved readable summary to {txt_path}")
    
    _save_tsr_bar_chart(scenario_snapshots, SLIDES_DIR / "tsr_average_by_scenario.png")


def _save_tsr_bar_chart(scenario_snapshots: list, png_path: Path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MaxNLocator
    except ImportError:
        print("matplotlib not installed, skipping TSR bar chart")
        return
    
    labels = []
    mw_vals = []
    nm_vals = []
    for snap in scenario_snapshots:
        name = snap.get("scenario_name") or "scenario"
        labels.append(name[:32] + ("..." if len(name) > 32 else ""))
        mwm = snap["schedulers"]["maxweight"].get("average_tsr")
        nmm = snap["schedulers"]["num"].get("average_tsr")
        mw_vals.append(float(mwm) if mwm is not None else 0.0)
        nm_vals.append(float(nmm) if nmm is not None else 0.0)
    
    if not labels:
        return
    
    xs = range(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    bars_mw = ax.bar([i - w / 2 for i in xs], mw_vals, width=w, label="Max-Weight", color="#1f77b4")
    bars_nm = ax.bar([i + w / 2 for i in xs], nm_vals, width=w, label="NUM", color="#ff7f0e")
    ax.bar_label(bars_mw, fmt="%.4f", fontsize=7, padding=2)
    ax.bar_label(bars_nm, fmt="%.4f", fontsize=7, padding=2)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, rotation=18, ha="right")
    ax.set_ylabel("Average TSR")
    ax.set_title("Average Task Success Rate by scenario")
    all_vals = mw_vals + nm_vals
    ymax = max(all_vals) if all_vals else 0.0
    if ymax <= 0:
        y_top = 0.05
    else:
        y_top = ymax * 1.22 + 1e-9
    ax.set_ylim(0, y_top)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=7, min_n_ticks=4))
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout(pad=1.4)
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    print(f"Saved TSR bar chart to {png_path}")


if __name__ == '__main__':
    run_rag_evaluation()
