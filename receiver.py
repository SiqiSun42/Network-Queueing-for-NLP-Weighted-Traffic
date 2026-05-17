from packet import Packet


class Receiver:
    
    def __init__(self, original_texts: list[str]):
        self.original_texts = original_texts
        self.received_packets = []
        self.lost_packets = []
    
    def receive(self, transmitted_packets: list[Packet]):
        self.received_packets.extend(transmitted_packets)
    
    def record_loss(self, lost_packet_ids: set):
        self.lost_packets = lost_packet_ids
    
    def get_received_content(self) -> str:
        contents = sorted([p.content for p in self.received_packets], 
                         key=lambda x: int(x.split('_')[1]))
        return ' '.join(contents)
    
    def get_statistics(self) -> dict:
        total_packets = len(self.received_packets) + len(self.lost_packets)
        received_count = len(self.received_packets)
        
        return {
            'total_packets': total_packets,
            'received_packets': received_count,
            'lost_packets': len(self.lost_packets),
            'delivery_rate': received_count / total_packets if total_packets > 0 else 0
        }
