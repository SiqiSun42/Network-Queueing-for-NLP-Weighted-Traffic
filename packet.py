from dataclasses import dataclass


@dataclass
class Packet:
    packet_id: int
    weight: float
    content: str = ""
    arrival_time: int = 0
    size: int = 1

    def __lt__(self, other):
        return self.weight > other.weight

    def weight_tier(self) -> str:
        if self.weight <= 0.35:
            return 'low'
        if self.weight <= 0.65:
            return 'medium'
        return 'high'
