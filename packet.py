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
