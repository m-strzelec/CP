import math
import time
from dataclasses import dataclass, field


@dataclass
class FileModel:
    client_id: int
    size: float
    created_at: float = field(default_factory=time.monotonic)

    def compute_priority(self, m: float, k: float, now: float = None) -> float:
        """Calculate file cost: 1 / m * log(s + 1) + k / sqrt(t)"""
        now = now or time.monotonic()
        t = now - self.created_at
        s = self.size
        return (1 / m) * math.log(s + 1) + k / math.sqrt(t)

    def __repr__(self):
        age = time.monotonic() - self.created_at
        return (
            f"<File cid={self.client_id}, "
            f"size={self.size}, "
            f"age={age:.2f}s>"
        )
