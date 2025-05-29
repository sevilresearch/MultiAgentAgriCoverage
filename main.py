from grid import Grid
from agent import Agent
from state_estimation import StateEstimator
from behavior_planning import LocalPlanner, PreassignedPlanner, PreassignedSweepFromSpawnPlanner
import visualization
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="tkinter")

import numpy as np
import time

def create_seeded_grid(size=(7, 15), seed=42):
    """Create a grid with fixed seed for consistent randomized initialization."""
    np.random.seed(seed)
    grid = Grid(size=size)
    return grid

def print_stats_main(run, agents):
    """Print post-simulation statistics for each agent."""
    for i, agent in enumerate(agents):
        print(f"Agent {i+1} ({agent.color}) stats:")
        print(f"  Total cells travelled: {agent.cells_travelled}")
        print(f"  visited cells travelled: {agent.agents_actual_visited_cells}")
        print(f"  Total revisits: {agent.revisit_count}")
        print(f"  Percentage of revisited cells: {agent.get_revisit_percentage():.2f}%")

def main():
    runs = 1
    seed = 42

    # Planner and experiment configuration:
    # - use_preassigned: selects strict static column assignment
    # - use_preassigned_block: selects sweeping strategy starting from spawn point
    use_preassigned = False
    use_preassigned_block = True 
    no_of_agents = 3

    # Predefined agent spawn locations for different agent counts
    agent_pos_1 = [(0, 0)]
    agent_pos_2 = [(0, 0), (1, 0)]
    agent_pos_3 = [(0, 0), (1, 0), (2, 0)]
    agent_pos_4 = [(0, 0), (1, 0), (2, 0), (3, 0)]

    # Assign appropriate positions based on agent count
    if no_of_agents == 1:
        agent_positions = agent_pos_1
    elif no_of_agents == 2:
        agent_positions = agent_pos_2
    elif no_of_agents == 3:
        agent_positions = agent_pos_3
    elif no_of_agents == 4:
        agent_positions = agent_pos_4

    for run in range(runs):
        base_grid = create_seeded_grid(size=(7, 15), seed=seed + run)

        start_time = time.time()
        global_explored_cells = set()

        Agent.used_colors.clear()
        agents = []

        # Initialize the farm grid
        grid = Grid(size=(7, 15))
        grid.boundaries = base_grid.boundaries.copy()

        # Select planning strategy
        state_estimator = StateEstimator(grid)
        if use_preassigned:
            behavior_planner = PreassignedPlanner()
            reroute_threshold = 200
        elif not use_preassigned and not use_preassigned_block:
            behavior_planner = LocalPlanner()
            reroute_threshold = 3
        else:
            behavior_planner = PreassignedSweepFromSpawnPlanner()
            reroute_threshold = 200

        # Instantiate agents and assign shared memory
        agents = [Agent(grid, global_explored_cells, reroute_threshold, pos, [], behavior_planner=behavior_planner) for pos in agent_positions]
        for agent in agents:
            agent.agents = agents  # Share reference to all agents

        print(f"\n--- run {run+1} ---")
        sim_time = visualization.display_grid(grid, agents, state_estimator, behavior_planner)

        end_time = time.time()
        run_time = end_time - start_time
        print_stats_main(runs, agents)

        print(f"Time taken for Run {run + 1}: {run_time:.2f} seconds")
        print(f"Sim time: \033[92m'{sim_time:.2f}\033[0m' units")
        sim_steps_per_sec = sim_time / run_time
        print(f"Sim speed: {sim_steps_per_sec:.4f} steps/sec")

        total_cells = grid.size[0] * grid.size[1]
        explored_percent = (len(global_explored_cells) / total_cells) * 100
        print(f"Explored: {explored_percent:.2f}% of the grid")

if __name__ == "__main__":
    main()
