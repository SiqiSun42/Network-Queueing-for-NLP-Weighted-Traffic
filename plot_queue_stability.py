from network_sim import NetworkSimulator
from pathlib import Path

SLIDES_DIR = Path(__file__).resolve().parent / "slides_images"


class QueueStabilityAnalysis:
    
    def run_single_scenario(self, link_capacity=50, arrival_rate=60, sim_time=500):
        
        print("=" * 80)
        print("Queue Stability Analysis (moderate congestion)")
        print("=" * 80)
        print(f"lambda/C = {arrival_rate/link_capacity:.2f}")
        print(f"Link capacity: {link_capacity}, Arrival rate: {arrival_rate}")
        print("Both schedulers use max_queue_size = 5C before dropping lowest-weight packets.")
        print("")
        
        simulator = NetworkSimulator(
            link_capacity=link_capacity,
            arrival_rate=arrival_rate,
            weight_dist="semantic",
            sim_time=sim_time,
            corpus_file="corpus.txt"
        )
        
        print("Running Max-Weight scheduler...")
        simulator.maxweight_scheduler = __import__('maxweight_scheduler').MaxWeightScheduler(link_capacity)
        simulator.traffic_gen = __import__('traffic').PoissonTrafficGenerator(arrival_rate, "semantic", "corpus.txt")
        
        mw_queue_lengths = []
        mw_times = []
        
        for t in range(sim_time):
            arrivals = simulator.traffic_gen.generate_arrivals(t)
            simulator.maxweight_scheduler.enqueue(arrivals)
            mw_queue_lengths.append(simulator.maxweight_scheduler.get_queue_length())
            transmitted = simulator.maxweight_scheduler.schedule()
            mw_times.append(t)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{sim_time} - Queue (after enqueue, before schedule): {mw_queue_lengths[-1]}")
        
        print("\nRunning NUM scheduler...")
        simulator.num_scheduler = __import__('num_scheduler').NUMScheduler(link_capacity)
        simulator.traffic_gen = __import__('traffic').PoissonTrafficGenerator(arrival_rate, "semantic", "corpus.txt")
        
        num_queue_lengths = []
        num_times = []
        
        for t in range(sim_time):
            arrivals = simulator.traffic_gen.generate_arrivals(t)
            simulator.num_scheduler.enqueue(arrivals)
            num_queue_lengths.append(simulator.num_scheduler.get_queue_length())
            transmitted = simulator.num_scheduler.schedule()
            num_times.append(t)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{sim_time} - Queue (after enqueue, before schedule): {num_queue_lengths[-1]}")
        
        return {
            'times': mw_times,
            'mw_queue': mw_queue_lengths,
            'num_queue': num_queue_lengths,
            'lambda_over_c': arrival_rate / link_capacity,
        }
    
    def plot_queue_stability(self, data):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed, skipping plot")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(data['times'], data['mw_queue'], linewidth=1.5, 
               label='Max-Weight', alpha=0.7, color='#1f77b4')
        ax.plot(data['times'], data['num_queue'], linewidth=1.5, 
               label='NUM', alpha=0.7, color='#ff7f0e')
        
        ax.axhline(y=sum(data['mw_queue'])/len(data['mw_queue']), 
                  color='#1f77b4', linestyle='--', alpha=0.5, linewidth=1)
        ax.axhline(y=sum(data['num_queue'])/len(data['num_queue']), 
                  color='#ff7f0e', linestyle='--', alpha=0.5, linewidth=1)
        
        ax.set_xlabel('Time (timeslots)', fontsize=12)
        ax.set_ylabel('Queue Length (packets)', fontsize=12)
        lc = data.get('lambda_over_c', 0)
        ax.set_title('Queue backlog over full horizon', fontsize=14, fontweight='bold')
        ax.text(
            0.02,
            0.98,
            f'Offered load lambda/C = {lc:.2f} (same 5C drop threshold for both)',
            transform=ax.transAxes,
            va='top',
            fontsize=10,
        )
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        SLIDES_DIR.mkdir(parents=True, exist_ok=True)
        filename = SLIDES_DIR / "queue_length_full_horizon.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to {filename}")

        zoom_n = min(150, len(data['times']))
        if zoom_n > 10:
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.plot(data['times'][:zoom_n], data['mw_queue'][:zoom_n], linewidth=1.5,
                    label='Max-Weight', alpha=0.85, color='#1f77b4')
            ax2.plot(data['times'][:zoom_n], data['num_queue'][:zoom_n], linewidth=1.5,
                    label='NUM', alpha=0.85, color='#ff7f0e')
            ax2.set_xlabel('Time (timeslots)', fontsize=12)
            ax2.set_ylabel('Queue Length (packets)', fontsize=12)
            lc = data.get('lambda_over_c', 0)
            ax2.set_title('Queue backlog during early transient', fontsize=13, fontweight='bold')
            ax2.text(
                0.02,
                0.98,
                f'lambda/C = {lc:.2f}, first {zoom_n} timeslots',
                transform=ax2.transAxes,
                va='top',
                fontsize=10,
            )
            ax2.legend(fontsize=11)
            ax2.grid(True, alpha=0.3)
            plt.tight_layout()
            zname = SLIDES_DIR / "queue_length_early_window.png"
            plt.savefig(zname, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {zname}")


if __name__ == '__main__':
    analysis = QueueStabilityAnalysis()
    
    print("\n" + "=" * 80)
    print("PART 2: Queue Stability Analysis")
    print("=" * 80)
    data = analysis.run_single_scenario(link_capacity=50, arrival_rate=52, sim_time=500)
    analysis.plot_queue_stability(data)
