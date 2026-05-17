from network_sim import NetworkSimulator
import json
from datetime import datetime


def run_comprehensive_experiment():
    
    scenarios = [
        {
            "name": "Light congestion",
            "link_capacity": 50,
            "arrival_rate": 60,
            "weight_dist": "bimodal"
        },
        {
            "name": "Medium congestion",
            "link_capacity": 50,
            "arrival_rate": 75,
            "weight_dist": "bimodal"
        },
        {
            "name": "Heavy congestion",
            "link_capacity": 50,
            "arrival_rate": 100,
            "weight_dist": "bimodal"
        },
        {
            "name": "Uniform weights (light congestion)",
            "link_capacity": 50,
            "arrival_rate": 60,
            "weight_dist": "uniform"
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print("\n" + "=" * 70)
        print(f"Scenario: {scenario['name']}")
        print("=" * 70)
        
        simulator = NetworkSimulator(
            link_capacity=scenario['link_capacity'],
            arrival_rate=scenario['arrival_rate'],
            weight_dist=scenario['weight_dist'],
            sim_time=500
        )
        
        metrics_mw, metrics_num = simulator.run_both()
        
        mw_stats = {
            'scheduler': 'Max-Weight',
            'scenario': scenario['name'],
            'total_arrived': simulator.maxweight_scheduler.total_arrived,
            'total_transmitted': simulator.maxweight_scheduler.total_transmitted,
            'total_dropped': simulator.maxweight_scheduler.total_dropped,
            'loss_rate': (simulator.maxweight_scheduler.total_dropped / 
                         simulator.maxweight_scheduler.total_arrived),
            'avg_queue_length': sum(metrics_mw['queue_length']) / len(metrics_mw['queue_length']),
            'avg_queue_backlog': sum(metrics_mw['queue_backlog']) / len(metrics_mw['queue_backlog']),
            'avg_weighted_throughput': sum(metrics_mw['weighted_throughput']) / len(metrics_mw['weighted_throughput'])
        }
        
        num_stats = {
            'scheduler': 'NUM',
            'scenario': scenario['name'],
            'total_arrived': simulator.num_scheduler.total_arrived,
            'total_transmitted': simulator.num_scheduler.total_transmitted,
            'total_dropped': simulator.num_scheduler.total_dropped,
            'loss_rate': (simulator.num_scheduler.total_dropped / 
                         simulator.num_scheduler.total_arrived),
            'avg_queue_length': sum(metrics_num['queue_length']) / len(metrics_num['queue_length']),
            'avg_queue_backlog': sum(metrics_num['queue_backlog']) / len(metrics_num['queue_backlog']),
            'avg_weighted_throughput': sum(metrics_num['weighted_throughput']) / len(metrics_num['weighted_throughput'])
        }
        
        results.append(mw_stats)
        results.append(num_stats)
        
        print(f"\nMax-Weight:")
        print(f"  Average queue length: {mw_stats['avg_queue_length']:.1f}")
        print(f"  Average queue backlog: {mw_stats['avg_queue_backlog']:.2f}")
        print(f"  Weighted throughput: {mw_stats['avg_weighted_throughput']:.4f}")
        print(f"  Packet loss rate: {mw_stats['loss_rate']:.2%}")
        
        print(f"\nNUM:")
        print(f"  Average queue length: {num_stats['avg_queue_length']:.1f}")
        print(f"  Average queue backlog: {num_stats['avg_queue_backlog']:.2f}")
        print(f"  Weighted throughput: {num_stats['avg_weighted_throughput']:.4f}")
        print(f"  Packet loss rate: {num_stats['loss_rate']:.2%}")
        
        throughput_improvement = (mw_stats['avg_weighted_throughput'] / 
                                 num_stats['avg_weighted_throughput'] - 1) * 100
        print(f"\nMax-Weight throughput advantage: {throughput_improvement:+.2f}%")
    
    save_results(results)
    return results


def save_results(results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"experiment_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nExperiment results saved to '{filename}'")


def run_single_experiment():
    
    link_capacity = 50
    arrival_rate = 60
    sim_time = 500
    
    simulator = NetworkSimulator(
        link_capacity=link_capacity,
        arrival_rate=arrival_rate,
        weight_dist="bimodal",
        sim_time=sim_time
    )
    
    metrics_mw, metrics_num = simulator.run_both()
    simulator.print_summary()


if __name__ == '__main__':
    print("\nSelect experiment type:")
    print("1. Single baseline experiment (default)")
    print("2. Comprehensive multi-scenario experiment")
    
    try:
        choice = input("\nEnter choice (1/2, default 1): ").strip()
        if choice == '2':
            run_comprehensive_experiment()
        else:
            run_single_experiment()
    except KeyboardInterrupt:
        print("\n\nUser interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
