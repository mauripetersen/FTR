from internal_forces import *


class Beam:
    def __init__(self, supports, section, material):
        self.supports = supports      # Ex: [(0, 'fixed'), (5, 'roller')]
        # roller
        # pinned
        # fixed
        self.section = section        # Ex: {'b': 30, 'h': 50}
        self.material = material      # Ex: {'E': 30e6, 'fck': 25}
        self.loads = []              # Armazena cargas adicionadas
        self.spans = self._calculate_spans()

    def _calculate_spans(self):
        """Calcula os comprimentos dos vãos a partir das posições dos apoios."""
        positions = [pos for pos, _ in self.supports]
        spans = []
        for i in range(len(positions) - 1):
            spans.append(positions[i + 1] - positions[i])
        return spans

    def add_support(self):
        self.supports = None

    def add_point_load(self, position, magnitude):
        self.loads.append({'type': 'point', 'pos': position, 'val': magnitude})

    def add_distributed_load(self, start, end, magnitude):
        self.loads.append({'type': 'dist', 'start': start, 'end': end, 'val': magnitude})

    def calculate(self):
        # Aqui você chamaria métodos do solver.py
        from .solver import calculate_reactions
        return calculate_reactions(self)
