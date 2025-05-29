import numpy as np

class StateEstimator:
    def __init__(self, grid):
        self.grid = grid
    
    def perceive_environment(self, agent):
        """Perceive the current cell and its surroundings."""
        x, y = agent.x, agent.y
        perception = {'current': self.grid.get_cell_info(x, y)}
        return perception
    