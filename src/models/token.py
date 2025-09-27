from dataclasses import dataclass
from typing import Dict

@dataclass
class Token:
    symbol: str
    address: str
    decimals: int = 18
    
    def __eq__(self, other):
        return self.address.lower() == other.address.lower()
    
    def __hash__(self):
        return hash(self.address.lower())