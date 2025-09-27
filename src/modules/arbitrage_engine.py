# src/modules/arbitrage_engine.py
import numpy as np  # Добавить в начале файла
import networkx as nx
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class ArbitrageEngine:
    def __init__(self, min_profitability: float = 0.005, max_cycle_length: int = 3):
        self.min_profitability = min_profitability
        self.max_cycle_length = max_cycle_length
    
    def find_opportunities(self, prices: Dict[str, Dict[Tuple[str, str], float]]) -> List[Dict]:
        opportunities = []
        
        for dex_name, dex_prices in prices.items():
            graph = nx.DiGraph()
            
            for (token_in, token_out), price in dex_prices.items():
                if price > 0:
                    # Используем отрицательный логарифм
                    weight = -np.log(price)
                    graph.add_edge(token_in, token_out, weight=weight, price=price)
            
            try:
                # Алгоритм Беллмана-Форда для поиска отрицательных циклов
                for node in graph.nodes():
                    distances = {n: float('inf') for n in graph.nodes()}
                    predecessors = {n: None for n in graph.nodes()}
                    distances[node] = 0
                    
                    # Релаксация ребер
                    for _ in range(len(graph.nodes()) - 1):
                        for u, v, data in graph.edges(data=True):
                            if distances[u] + data['weight'] < distances[v]:
                                distances[v] = distances[u] + data['weight']
                                predecessors[v] = u
                    
                    # Проверка на отрицательные циклы
                    for u, v, data in graph.edges(data=True):
                        if distances[u] + data['weight'] < distances[v]:
                            cycle = self._reconstruct_cycle(predecessors, u, v)
                            if cycle and len(cycle) <= self.max_cycle_length + 1:
                                profit = self._calculate_profitability(cycle, graph)
                                if profit >= self.min_profitability:
                                    opportunities.append({
                                        'dex': dex_name,
                                        'path': cycle,
                                        'profit': profit
                                    })
            except Exception as e:
                logger.error(f"Error finding cycles: {e}")
        
        return opportunities

    def _reconstruct_cycle(self, predecessors: Dict, start: str, end: str) -> List[str]:
        cycle = []
        current = end
        while current != start:
            cycle.append(current)
            current = predecessors[current]
            if current is None:
                return []
        cycle.append(start)
        return cycle[::-1]

    def _calculate_profitability(self, cycle: List[str], graph: nx.DiGraph) -> float:
        if len(cycle) < 2:
            return 0.0
        
        product = 1.0
        for i in range(len(cycle) - 1):
            product *= graph[cycle[i]][cycle[i + 1]]['price']
        
        # Замыкаем цикл
        if cycle[0] != cycle[-1]:
            product *= graph[cycle[-1]][cycle[0]]['price']
        
        return product - 1.0

    def _safe_log(self, x: float) -> float:
        return 0 if x <= 0 else float(np.log(x))