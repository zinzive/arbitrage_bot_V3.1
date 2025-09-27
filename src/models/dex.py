# src/models/dex.py
from dataclasses import dataclass
from web3.contract import Contract

@dataclass
class Dex:
    name: str
    router_address: str
    factory_address: str
    router_contract: Contract
    factory_contract: Contract
    fee: float = 0.003  # 0.3%