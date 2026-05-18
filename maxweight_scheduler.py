from collections import deque
from packet import Packet


class MaxWeightScheduler:
    
    def __init__(self, link_capacity: int):
        self.link_capacity = link_capacity
        self.queue = deque()
        self.total_arrived = 0
        self.total_transmitted = 0
        self.total_dropped = 0
        self.total_arrived_weight = 0.0
        self.total_dropped_weight = 0.0
        self.wait_by_tier = {'low': [], 'medium': [], 'high': []}
    
    def _record_wait(self, pkt: Packet, slot: int):
        delay = slot - pkt.arrival_time
        self.wait_by_tier[pkt.weight_tier()].append(delay)
    
    def enqueue(self, packets: list[Packet]):
        self.queue.extend(packets)
        self.total_arrived += len(packets)
        self.total_arrived_weight += sum(p.weight for p in packets)
    
    def schedule(self, slot: int) -> list[Packet]:
        transmitted = []
        
        max_queue_size = self.link_capacity * 5
        while len(self.queue) > max_queue_size:
            drop_pkt = min(self.queue, key=lambda p: p.weight)
            self._record_wait(drop_pkt, slot)
            self.queue.remove(drop_pkt)
            self.total_dropped += 1
            self.total_dropped_weight += drop_pkt.weight
        
        if not self.queue:
            return transmitted
        
        queue_len = len(self.queue)
        
        queue_list = list(self.queue)
        queue_list.sort(key=lambda p: queue_len * p.weight, reverse=True)
        
        for i in range(min(self.link_capacity, len(queue_list))):
            transmitted.append(queue_list[i])
        
        for pkt in transmitted:
            self._record_wait(pkt, slot)
            self.queue.remove(pkt)
        
        self.total_transmitted += len(transmitted)
        return transmitted
    
    def get_queue_length(self) -> int:
        return len(self.queue)
    
    def get_queue_backlog(self) -> float:
        return sum(p.weight for p in self.queue)
