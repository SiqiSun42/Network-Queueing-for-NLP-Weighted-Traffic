from traffic import PoissonTrafficGenerator
from maxweight_scheduler import MaxWeightScheduler
from num_scheduler import NUMScheduler
from packet import Packet


class NetworkSimulator:
    
    def __init__(self, 
                 link_capacity: int,
                 arrival_rate: float,
                 weight_dist: str = "uniform",
                 sim_time: int = 1000):
        self.link_capacity = link_capacity
        self.arrival_rate = arrival_rate
        self.sim_time = sim_time
        
        self.traffic_gen = PoissonTrafficGenerator(arrival_rate, weight_dist)
        
        self.maxweight_scheduler = MaxWeightScheduler(link_capacity)
        self.num_scheduler = NUMScheduler(link_capacity)
        
        self.metrics_maxweight = {
            'time': [],
            'queue_length': [],
            'queue_backlog': [],
            'transmitted': [],
            'dropped': [],
            'weighted_throughput': []
        }
        
        self.metrics_num = {
            'time': [],
            'queue_length': [],
            'queue_backlog': [],
            'transmitted': [],
            'dropped': [],
            'weighted_throughput': []
        }
    
    def run_maxweight(self):
        print("Running Max-Weight scheduler simulation...")
        self.maxweight_scheduler = MaxWeightScheduler(self.link_capacity)
        self.traffic_gen = PoissonTrafficGenerator(self.arrival_rate)
        
        for t in range(self.sim_time):
            arrivals = self.traffic_gen.generate_arrivals(t)
            self.maxweight_scheduler.enqueue(arrivals)
            
            transmitted = self.maxweight_scheduler.schedule()
            
            weighted_throughput = sum(p.weight for p in transmitted)
            
            self.metrics_maxweight['time'].append(t)
            self.metrics_maxweight['queue_length'].append(
                self.maxweight_scheduler.get_queue_length()
            )
            self.metrics_maxweight['queue_backlog'].append(
                self.maxweight_scheduler.get_queue_backlog()
            )
            self.metrics_maxweight['transmitted'].append(len(transmitted))
            self.metrics_maxweight['dropped'].append(
                self.maxweight_scheduler.total_dropped
            )
            self.metrics_maxweight['weighted_throughput'].append(weighted_throughput)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{self.sim_time} - "
                      f"Queue Length: {self.maxweight_scheduler.get_queue_length()} - "
                      f"Dropped: {self.maxweight_scheduler.total_dropped}")
        
        return self.metrics_maxweight
    
    def run_num(self):
        print("Running NUM scheduler simulation...")
        self.num_scheduler = NUMScheduler(self.link_capacity)
        self.traffic_gen = PoissonTrafficGenerator(self.arrival_rate)
        
        for t in range(self.sim_time):
            arrivals = self.traffic_gen.generate_arrivals(t)
            self.num_scheduler.enqueue(arrivals)
            
            transmitted = self.num_scheduler.schedule()
            
            weighted_throughput = sum(p.weight for p in transmitted)
            
            self.metrics_num['time'].append(t)
            self.metrics_num['queue_length'].append(
                self.num_scheduler.get_queue_length()
            )
            self.metrics_num['queue_backlog'].append(
                self.num_scheduler.get_queue_backlog()
            )
            self.metrics_num['transmitted'].append(len(transmitted))
            self.metrics_num['dropped'].append(
                self.num_scheduler.total_dropped
            )
            self.metrics_num['weighted_throughput'].append(weighted_throughput)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{self.sim_time} - "
                      f"Queue Length: {self.num_scheduler.get_queue_length()} - "
                      f"Dropped: {self.num_scheduler.total_dropped}")
        
        return self.metrics_num
    
    def run_both(self):
        print("=" * 60)
        print("Starting network simulation comparison experiment")
        print("=" * 60)
        print(f"Simulation parameters:")
        print(f"  Link capacity: {self.link_capacity} packets/timeslot")
        print(f"  Arrival rate: {self.arrival_rate} packets/timeslot")
        print(f"  Simulation duration: {self.sim_time} timeslots")
        print("=" * 60)
        
        self.run_maxweight()
        print()
        self.run_num()
        
        return self.metrics_maxweight, self.metrics_num
    
    def print_summary(self):
        print("\n" + "=" * 60)
        print("Simulation Results Summary")
        print("=" * 60)
        
        print("\nMax-Weight Scheduler:")
        print(f"  Total arrived packets: {self.maxweight_scheduler.total_arrived}")
        print(f"  Total transmitted packets: {self.maxweight_scheduler.total_transmitted}")
        print(f"  Total dropped packets: {self.maxweight_scheduler.total_dropped}")
        loss_rate_mw = (self.maxweight_scheduler.total_dropped / 
                        self.maxweight_scheduler.total_arrived)
        print(f"  Packet loss rate: {loss_rate_mw:.2%}")
        avg_weighted_mw = sum(self.metrics_maxweight['weighted_throughput']) / len(self.metrics_maxweight['weighted_throughput'])
        print(f"  Average weighted throughput: {avg_weighted_mw:.4f}")
        
        print("\nNUM Scheduler:")
        print(f"  Total arrived packets: {self.num_scheduler.total_arrived}")
        print(f"  Total transmitted packets: {self.num_scheduler.total_transmitted}")
        print(f"  Total dropped packets: {self.num_scheduler.total_dropped}")
        loss_rate_num = (self.num_scheduler.total_dropped / 
                         self.num_scheduler.total_arrived)
        print(f"  Packet loss rate: {loss_rate_num:.2%}")
        avg_weighted_num = sum(self.metrics_num['weighted_throughput']) / len(self.metrics_num['weighted_throughput'])
        print(f"  Average weighted throughput: {avg_weighted_num:.4f}")
        
        print("\nComparison:")
        print(f"  Max-Weight advantage: {(avg_weighted_mw / avg_weighted_num - 1) * 100:+.2f}%")
        print("=" * 60)
