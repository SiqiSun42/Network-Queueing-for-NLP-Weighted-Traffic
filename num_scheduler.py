from collections import deque
from packet import Packet


class NUMScheduler:
    
    def __init__(self, link_capacity: int, num_flow_classes: int = 2):
        self.link_capacity = link_capacity
        self.num_flow_classes = num_flow_classes
        self.queue = deque()
        self.total_arrived = 0
        self.total_transmitted = 0
        self.total_dropped = 0
        self.total_arrived_weight = 0.0
        self.total_dropped_weight = 0.0
        
        self.optimal_rates = self._initialize_optimal_rates()
    
    def _initialize_optimal_rates(self) -> dict:
        rates = {}
        rates['high'] = self.link_capacity * 2 / 3
        rates['low'] = self.link_capacity * 1 / 3
        return rates
    
    def enqueue(self, packets: list[Packet]):
        self.queue.extend(packets)
        self.total_arrived += len(packets)
        self.total_arrived_weight += sum(p.weight for p in packets)
    
    def schedule(self) -> list[Packet]:
        transmitted = []
        
        if not self.queue:
            return transmitted
        
        high_priority = [p for p in self.queue if p.weight > 0.6]
        low_priority = [p for p in self.queue if p.weight <= 0.6]
        
        high_capacity = min(len(high_priority), int(self.optimal_rates['high']))
        low_capacity = min(len(low_priority), 
                          int(self.optimal_rates['low']),
                          self.link_capacity - high_capacity)
        
        for i in range(high_capacity):
            transmitted.append(high_priority[i])
        
        for i in range(low_capacity):
            transmitted.append(low_priority[i])
        
        for pkt in transmitted:
            self.queue.remove(pkt)
        
        max_queue_size = self.link_capacity * 5
        while len(self.queue) > max_queue_size:
            drop_pkt = min(self.queue, key=lambda p: p.weight)
            self.queue.remove(drop_pkt)
            self.total_dropped += 1
            self.total_dropped_weight += drop_pkt.weight
        
        self.total_transmitted += len(transmitted)
        return transmitted
    
    def get_queue_length(self) -> int:
        return len(self.queue)
    
    def get_queue_backlog(self) -> float:
        return sum(p.weight for p in self.queue)
