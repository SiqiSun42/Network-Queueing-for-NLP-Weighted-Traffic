from collections import deque
from packet import Packet


class DropTailScheduler:
    
    def __init__(self, link_capacity: int, buffer_size: int = None):
        self.link_capacity = link_capacity
        self.buffer_size = buffer_size if buffer_size else link_capacity * 10
        self.queue = deque()
        self.total_arrived = 0
        self.total_transmitted = 0
        self.total_dropped = 0
    
    def enqueue(self, packets: list[Packet]):
        for pkt in packets:
            if len(self.queue) < self.buffer_size:
                self.queue.append(pkt)
            else:
                self.total_dropped += 1
            self.total_arrived += 1
    
    def schedule(self) -> list[Packet]:
        transmitted = []
        for _ in range(min(self.link_capacity, len(self.queue))):
            transmitted.append(self.queue.popleft())
        
        self.total_transmitted += len(transmitted)
        return transmitted
    
    def get_queue_length(self) -> int:
        return len(self.queue)
    
    def get_queue_backlog(self) -> float:
        return sum(p.weight for p in self.queue)
