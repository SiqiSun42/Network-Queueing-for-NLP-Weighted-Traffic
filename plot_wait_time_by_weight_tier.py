import json
from pathlib import Path

from network_sim import NetworkSimulator

SLIDES_DIR = Path(__file__).resolve().parent / "slides_images"

TIERS = [
    ("low", "Low weight (w<=0.35)"),
    ("medium", "Medium weight (0.35<w<=0.65)"),
    ("high", "High weight (w>0.65)"),
]


def tier_averages(scheduler):
    out = {}
    for key, _ in TIERS:
        samples = scheduler.wait_by_tier[key]
        out[key] = {
            "count": len(samples),
            "mean_slots": (sum(samples) / len(samples)) if samples else None,
        }
    return out


def main():
    link_capacity = 50
    arrival_rate = 60
    sim_time = 500
    sim = NetworkSimulator(
        link_capacity=link_capacity,
        arrival_rate=arrival_rate,
        weight_dist="semantic",
        sim_time=sim_time,
        corpus_file="corpus.txt",
    )
    print("Running simulation for wait-time statistics...")
    sim.run_both()

    mw = sim.maxweight_scheduler
    nm = sim.num_scheduler

    payload = {
        "link_capacity": link_capacity,
        "arrival_rate": arrival_rate,
        "lambda_over_c": arrival_rate / link_capacity,
        "sim_time": sim_time,
        "weight_tier_thresholds": "low: w<=0.35; medium: 0.35<w<=0.65; high: w>0.65",
        "delay_definition": "timeslots from arrival slot to slot where packet is transmitted or dropped",
        "maxweight": tier_averages(mw),
        "num": tier_averages(nm),
    }

    SLIDES_DIR.mkdir(parents=True, exist_ok=True)

    json_path = SLIDES_DIR / "wait_time_by_weight_tier.json"
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved {json_path}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skipping bar chart")
        return

    x_labels = [lbl for _, lbl in TIERS]
    xs = range(len(TIERS))
    bar_w = 0.35
    mw_vals = []
    nm_vals = []
    for key, _ in TIERS:
        sm = mw.wait_by_tier[key]
        sn = nm.wait_by_tier[key]
        mw_vals.append(sum(sm) / len(sm) if sm else 0.0)
        nm_vals.append(sum(sn) / len(sn) if sn else 0.0)
        print(
            f"{key}: Max-Weight n={len(sm)} mean={mw_vals[-1]:.3f}; "
            f"NUM n={len(sn)} mean={nm_vals[-1]:.3f}"
        )

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - bar_w / 2 for i in xs], mw_vals, width=bar_w, label="Max-Weight", color="#1f77b4")
    ax.bar([i + bar_w / 2 for i in xs], nm_vals, width=bar_w, label="NUM", color="#ff7f0e")
    ax.set_xticks(list(xs))
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Mean delay (timeslots)")
    ax.set_title("Average queueing delay by semantic weight tier")
    ax.text(
        0.02,
        0.98,
        f"Completed packets only; lambda/C={arrival_rate / link_capacity:.2f}",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
    )
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    png_path = SLIDES_DIR / "average_wait_slots_by_weight_tier.png"
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    print(f"Saved {png_path}")


if __name__ == "__main__":
    main()
