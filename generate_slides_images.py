import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    scripts = [
        ROOT / "plot_tsr_comparison.py",
        ROOT / "plot_queue_stability.py",
        ROOT / "analyze_packet_loss.py",
    ]
    for path in scripts:
        subprocess.check_call([sys.executable, str(path)], cwd=str(ROOT))


if __name__ == "__main__":
    main()
