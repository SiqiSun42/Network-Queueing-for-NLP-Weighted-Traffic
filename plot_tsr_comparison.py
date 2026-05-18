from network_sim import NetworkSimulator
import json
from pathlib import Path

SLIDES_DIR = Path(__file__).resolve().parent / "slides_images"


class TSRComparison:
    
    def __init__(self, link_capacity: int = 50):
        self.link_capacity = link_capacity
        self.results = {}
    
    def run_congestion_sweep(self, lambda_over_c_values=[0.6, 0.8, 1.0, 1.2, 1.5], 
                            num_runs=3, sim_time=500):
        
        print("=" * 80)
        print("Weighted throughput vs congestion (lambda/C)")
        print("=" * 80)
        print(f"λ/C values: {lambda_over_c_values}")
        print(f"Runs per value: {num_runs}")
        print(f"Simulation time: {sim_time} timeslots\n")
        
        self.results = {
            'maxweight': [],
            'num': [],
        }
        
        for lambda_over_c in lambda_over_c_values:
            arrival_rate = int(self.link_capacity * lambda_over_c)
            
            print(f"\nTesting λ/C = {lambda_over_c} (λ={arrival_rate}, C={self.link_capacity})")
            print("-" * 60)
            
            mw_tsr_list = []
            num_tsr_list = []
            
            for run in range(num_runs):
                print(f"  Run {run + 1}/{num_runs}...", end=" ", flush=True)
                
                simulator = NetworkSimulator(
                    link_capacity=self.link_capacity,
                    arrival_rate=arrival_rate,
                    weight_dist="semantic",
                    sim_time=sim_time,
                    corpus_file="corpus.txt"
                )
                
                metrics_mw, metrics_num = simulator.run_both()
                
                avg_tsr_mw = sum(metrics_mw['weighted_throughput']) / len(metrics_mw['weighted_throughput']) if metrics_mw['weighted_throughput'] else 0
                avg_tsr_num = sum(metrics_num['weighted_throughput']) / len(metrics_num['weighted_throughput']) if metrics_num['weighted_throughput'] else 0
                
                mw_tsr_list.append(avg_tsr_mw)
                num_tsr_list.append(avg_tsr_num)
                
                print(f"MW={avg_tsr_mw:.3f}, NUM={avg_tsr_num:.3f}")
            
            avg_mw = sum(mw_tsr_list) / len(mw_tsr_list)
            avg_num = sum(num_tsr_list) / len(num_tsr_list)
            
            self.results['maxweight'].append(avg_mw)
            self.results['num'].append(avg_num)
            
            print(f"  Average - Max-Weight: {avg_mw:.4f}, NUM: {avg_num:.4f}")
        
        self._save_results(lambda_over_c_values)
        return self.results
    
    def _save_results(self, lambda_over_c_values):
        SLIDES_DIR.mkdir(parents=True, exist_ok=True)
        filename = SLIDES_DIR / "weighted_throughput_vs_lambda_over_c.json"
        
        data = {
            'lambda_over_c': lambda_over_c_values,
            'link_capacity': self.link_capacity,
            'metric_mean_per_timeslot': 'mean over timeslots of (sum of semantic weights of packets transmitted in that slot)',
            'y_axis': '100 * (that_mean / link_capacity); comparable scale, not end-to-end task success rate',
            'results': self.results,
            'normalized_series_percent_of_C': {
                'maxweight': [100.0 * v / self.link_capacity for v in self.results['maxweight']],
                'num': [100.0 * v / self.link_capacity for v in self.results['num']],
            },
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nResults saved to {filename}")
    
    def plot_tsr_comparison(self, lambda_over_c_values=[0.6, 0.8, 1.0, 1.2, 1.5]):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed, skipping plot")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_pos = list(range(len(lambda_over_c_values)))
        
        mw_y = [100.0 * v / self.link_capacity for v in self.results['maxweight']]
        num_y = [100.0 * v / self.link_capacity for v in self.results['num']]
        
        ax.plot(x_pos, mw_y, marker='o', linewidth=2,
               markersize=8, label='Max-Weight', color='#1f77b4')
        ax.plot(x_pos, num_y, marker='s', linewidth=2,
               markersize=8, label='NUM', color='#ff7f0e')
        
        ax.set_xlabel('lambda / C', fontsize=12)
        ax.set_ylabel('Mean (sum of transmitted weights per slot) / C  (%)', fontsize=12)
        ax.set_title('Semantic-weighted throughput vs offered load', fontsize=13, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(v) for v in lambda_over_c_values])
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        fig.text(
            0.5,
            0.02,
            'Not end-to-end TSR: each slot sums semantic weights of forwarded packets; '
            'axis divides that time-average by link capacity C.',
            ha='center',
            fontsize=9,
        )
        plt.tight_layout(rect=[0, 0.08, 1, 1])
        SLIDES_DIR.mkdir(parents=True, exist_ok=True)
        filename = SLIDES_DIR / "weighted_throughput_vs_lambda_over_c.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {filename}")


if __name__ == '__main__':
    comparison = TSRComparison(link_capacity=50)
    
    print("\n" + "=" * 80)
    print("Weighted throughput vs congestion")
    print("=" * 80)
    comparison.run_congestion_sweep(
        lambda_over_c_values=[0.6, 0.8, 1.0, 1.2, 1.5],
        num_runs=3,
        sim_time=300
    )
    
    comparison.plot_tsr_comparison([0.6, 0.8, 1.0, 1.2, 1.5])
