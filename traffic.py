import random
import math
from packet import Packet


class PoissonTrafficGenerator:
    
    def __init__(self, arrival_rate: float, weight_dist: str = "uniform"):
        self.arrival_rate = arrival_rate
        self.weight_dist = weight_dist
        self.packet_counter = 0
    
    @staticmethod
    def _poisson_sample(lam: float) -> int:
        L = math.exp(-lam)
        k = 0
        p = 1
        while p > L:
            k += 1
            p *= random.random()
        return k - 1
    
    def generate_arrivals(self, current_time: int) -> list[Packet]:
        num_arrivals = self._poisson_sample(self.arrival_rate)
        
        packets = []
        for _ in range(num_arrivals):
            weight = self._generate_weight()
            packet = Packet(
                packet_id=self.packet_counter,
                weight=weight,
                content=f"packet_{self.packet_counter}",
                arrival_time=current_time,
                size=1
            )
            packets.append(packet)
            self.packet_counter += 1
        
        return packets
    
    def _generate_weight(self) -> float:
        if self.weight_dist == "uniform":
            return random.uniform(0.1, 1.0)
        elif self.weight_dist == "normal":
            u1 = random.random()
            u2 = random.random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            w = 0.5 + 0.2 * z
            return max(0.1, min(1.0, w))
        elif self.weight_dist == "bimodal":
            if random.random() < 0.3:
                return random.uniform(0.8, 1.0)
            else:
                return random.uniform(0.1, 0.3)
        else:
            return random.uniform(0.1, 1.0)
