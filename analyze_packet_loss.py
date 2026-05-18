from network_sim import NetworkSimulator
import json
from pathlib import Path

SLIDES_DIR = Path(__file__).resolve().parent / "slides_images"


class PacketLossAnalysis:
    
    @staticmethod
    def run_analysis(link_capacity=50, arrival_rate=75, sim_time=300):
        
        print("=" * 80)
        print("Packet loss: unweighted vs semantic-weighted")
        print("=" * 80)
        
        simulator = NetworkSimulator(
            link_capacity=link_capacity,
            arrival_rate=arrival_rate,
            weight_dist="semantic",
            sim_time=sim_time,
            corpus_file="corpus.txt"
        )
        
        print("\nRunning simulations...\n")
        simulator.run_both()
        
        results = {}
        
        for scheduler_name, scheduler in [('maxweight', simulator.maxweight_scheduler),
                                         ('num', simulator.num_scheduler)]:
            
            total_arrived = scheduler.total_arrived
            total_dropped = scheduler.total_dropped
            aw = getattr(scheduler, 'total_arrived_weight', 0.0)
            dw = getattr(scheduler, 'total_dropped_weight', 0.0)
            
            unweighted_loss_rate = total_dropped / total_arrived if total_arrived > 0 else 0
            weighted_loss_rate = dw / aw if aw > 0 else 0
            
            print(f"\n{scheduler_name.upper()}:")
            print(f"  Total arrived packets: {total_arrived}")
            print(f"  Total dropped packets: {total_dropped}")
            print(f"  Unweighted loss rate: {unweighted_loss_rate:.2%}")
            print(f"  Weighted loss rate (sum w dropped / sum w arrived): {weighted_loss_rate:.2%}")
            
            results[scheduler_name] = {
                'total_arrived': total_arrived,
                'total_dropped': total_dropped,
                'total_arrived_weight': aw,
                'total_dropped_weight': dw,
                'unweighted_loss_rate': unweighted_loss_rate,
                'weighted_loss_rate': weighted_loss_rate,
                'transmitted': scheduler.total_transmitted,
            }
        
        meta = {
            'link_capacity': link_capacity,
            'arrival_rate': arrival_rate,
            'lambda_over_c': arrival_rate / link_capacity,
            'sim_time': sim_time,
            'schedulers': results,
        }
        
        SLIDES_DIR.mkdir(parents=True, exist_ok=True)
        fn = SLIDES_DIR / "packet_loss_comparison.json"
        with open(fn, 'w') as f:
            json.dump(meta, f, indent=2)
        print(f"\nSaved {fn}")
        
        PacketLossAnalysis.plot_bar_chart(meta)
        
        return meta
    
    @staticmethod
    def plot_bar_chart(meta):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available, skipping bar chart")
            return
        
        mw = meta['schedulers']['maxweight']
        nm = meta['schedulers']['num']
        
        labels = ['Max-Weight', 'NUM']
        uw = [100 * mw['unweighted_loss_rate'], 100 * nm['unweighted_loss_rate']]
        ww = [100 * mw['weighted_loss_rate'], 100 * nm['weighted_loss_rate']]
        
        x = [0, 1]
        w = 0.35
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar([i - w / 2 for i in x], uw, width=w, label='Unweighted loss %', color='#7f7f7f')
        ax.bar([i + w / 2 for i in x], ww, width=w, label='Weighted loss %', color='#2ca02c')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel('Loss rate (%)')
        lc = meta['lambda_over_c']
        ax.set_title('Packet loss: unweighted vs semantic-weighted', fontsize=13, fontweight='bold')
        ax.text(
            0.02,
            0.98,
            f'Offered load lambda/C = {lc:.2f}',
            transform=ax.transAxes,
            va='top',
            fontsize=10,
        )
        ax.legend()
        ax.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()
        SLIDES_DIR.mkdir(parents=True, exist_ok=True)
        out = SLIDES_DIR / "packet_loss_weighted_vs_unweighted.png"
        plt.savefig(out, dpi=300, bbox_inches='tight')
        print(f"Saved {out}")
    
    @staticmethod
    def print_comparison(meta):
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)
        mw = meta['schedulers']['maxweight']
        nm = meta['schedulers']['num']
        print(f"\nUnweighted loss gap (NUM - Max-Weight): {(nm['unweighted_loss_rate'] - mw['unweighted_loss_rate']) * 100:+.2f} pp")
        print(f"Weighted loss gap (NUM - Max-Weight): {(nm['weighted_loss_rate'] - mw['weighted_loss_rate']) * 100:+.2f} pp")


if __name__ == '__main__':
    analysis = PacketLossAnalysis()
    meta = analysis.run_analysis(link_capacity=50, arrival_rate=75, sim_time=300)
    analysis.print_comparison(meta)
