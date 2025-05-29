import visualization

class LocalPlanner:
    def select_movement_action(self, agent, perception_data, agents):
        # Initialize state variables if not already set
        if not hasattr(agent, 'committed_column'):
            agent.committed_column = None
        if not hasattr(agent, 'column_sweep_direction'):
            agent.column_sweep_direction = {}
        if not hasattr(agent, 'helper_column'):
            agent.helper_column = None

        grid_w = agent.grid.size[1]
        grid_h = agent.grid.size[0]
        explored = agent.global_explored_cells

        # Returns unexplored cells in a column
        def get_cells_needing_work(col_x):
            return [(col_x, y) for y in range(grid_h) if (col_x, y) not in explored]

        # Identify columns that are both unexplored and unoccupied
        unexplored_unoccupied_columns = [
            x for x in range(grid_w)
            if len(get_cells_needing_work(x)) > 0
            and not any(a.x == x and a != agent for a in agents)
        ]
        allow_help_anywhere = len(unexplored_unoccupied_columns) == 0

        # Decide default sweeping direction based on initial position
        if not hasattr(agent, 'sweep_direction'):
            agent.sweep_direction = 'left' if agent.x < grid_w // 2 else 'right'

        # Create priority list of columns based on sweeping direction
        if agent.sweep_direction == 'left':
            ordered_columns = list(range(agent.x, -1, -1)) + list(range(agent.x + 1, grid_w))
        else:
            ordered_columns = list(range(agent.x, grid_w)) + list(range(agent.x - 1, -1, -1))

        # Non-helper column sweep
        for x in ordered_columns:
            occupied = any(a.x == x and a.y not in [0, grid_h-1] and a != agent for a in agents)
            if occupied and not allow_help_anywhere:
                continue
            targets = get_cells_needing_work(x)
            if targets:
                if x not in agent.column_sweep_direction:
                    agent.column_sweep_direction[x] = 'down' if agent.y <= grid_h // 2 else 'up'
                direction = agent.column_sweep_direction[x]
                sorted_targets = sorted(targets, key=lambda p: p[1]) if direction == 'down' else sorted(targets, key=lambda p: -p[1])
                return agent._move_towards_target(*sorted_targets[0])

        # Helper mode: assist other agents after own work is done
        if allow_help_anywhere:
            if agent.helper_column is not None:
                col = agent.helper_column
                targets = get_cells_needing_work(col)
                if targets:
                    direction = agent.column_sweep_direction.get(col, 'down' if agent.y <= grid_h // 2 else 'up')
                    agent.column_sweep_direction[col] = direction
                    sorted_targets = sorted(targets, key=lambda p: p[1]) if direction == 'down' else sorted(targets, key=lambda p: -p[1])
                    return agent._move_towards_target(*sorted_targets[0])
                else:
                    agent.helper_column = None  # Finished helping in that column

            # Select new column to assist in
            candidate_cols = [
                x for x in range(grid_w)
                if any(a.x == x and a != agent for a in agents)
                and len(get_cells_needing_work(x)) > 0
            ]
            if candidate_cols:
                best_col = max(candidate_cols, key=lambda c: len(get_cells_needing_work(c)))
                agent.helper_column = best_col

                # Choose entry side based on edge proximity
                top_unexplored = (best_col, 0) not in explored
                bottom_unexplored = (best_col, grid_h - 1) not in explored
                if top_unexplored and not bottom_unexplored:
                    entry_y = 0
                    agent.column_sweep_direction[best_col] = 'down'
                elif bottom_unexplored and not top_unexplored:
                    entry_y = grid_h - 1
                    agent.column_sweep_direction[best_col] = 'up'
                else:
                    entry_y = 0 if agent.y <= grid_h // 2 else grid_h - 1
                    agent.column_sweep_direction[best_col] = 'down' if entry_y == 0 else 'up'

                # Move horizontally, then vertically to entry
                if agent.x != best_col:
                    return 'right' if agent.x < best_col else 'left'
                if agent.y != entry_y:
                    return 'down' if agent.y < entry_y else 'up'

        return None


class PreassignedPlanner:
    def select_movement_action(self, agent, perception_data, agents):
        # Assign agent to columns using round-robin method
        if not hasattr(agent, 'assigned_columns'):
            agent_index = agents.index(agent)
            total_agents = len(agents)
            grid_w = agent.grid.size[1]
            agent.assigned_columns = [col for col in range(grid_w) if col % total_agents == agent_index]
            agent.column_sweep_direction = {}

        grid_h = agent.grid.size[0]
        explored = agent.global_explored_cells

        def get_cells_needing_work(col_x):
            return [(col_x, y) for y in range(grid_h) if (col_x, y) not in explored]

        # Sweep assigned columns top-to-bottom or bottom-to-top
        for x in agent.assigned_columns:
            targets = get_cells_needing_work(x)
            if targets:
                if x not in agent.column_sweep_direction:
                    agent.column_sweep_direction[x] = 'down' if agent.y < grid_h // 2 else 'up'
                direction = agent.column_sweep_direction[x]
                sorted_targets = sorted(targets, key=lambda p: p[1]) if direction == 'down' else sorted(targets, key=lambda p: -p[1])
                return agent._move_towards_target(*sorted_targets[0])

        return None  # All assigned columns complete


class PreassignedSweepFromSpawnPlanner:
    def select_movement_action(self, agent, perception_data, agents):
        # Assign a continuous block of columns to each agent
        if not hasattr(agent, 'assigned_columns'):
            agent_index = agents.index(agent)
            total_agents = len(agents)
            grid_w = agent.grid.size[1]
            block_size = grid_w // total_agents
            start_col = agent_index * block_size
            end_col = start_col + block_size
            agent.assigned_columns = list(range(start_col, end_col))
            agent.assigned_columns.sort()
            agent.assigned_columns_set = set(agent.assigned_columns)

            # Sweep order starts at spawn, then spreads outward
            agent.spawn_column = agent.x
            agent.current_column = agent.spawn_column
            center_idx = agent.assigned_columns.index(agent.spawn_column)
            left = agent.assigned_columns[:center_idx][::-1]
            right = agent.assigned_columns[center_idx+1:]
            agent.sweep_order = [agent.spawn_column] + left + right
            agent.sweep_index = 0
            agent.column_sweep_direction = {}

        grid_h = agent.grid.size[0]
        explored = agent.global_explored_cells

        def get_cells_needing_work(col_x):
            return [(col_x, y) for y in range(grid_h) if (col_x, y) not in explored]

        # Follow sweep order one column at a time
        while agent.sweep_index < len(agent.sweep_order):
            col = agent.sweep_order[agent.sweep_index]
            if col not in agent.assigned_columns_set:
                agent.sweep_index += 1
                continue

            targets = get_cells_needing_work(col)
            if not targets:
                agent.sweep_index += 1
                continue

            if col not in agent.column_sweep_direction:
                agent.column_sweep_direction[col] = 'down' if agent.y <= grid_h // 2 else 'up'

            # Move to column
            if agent.x != col:
                return 'right' if agent.x < col else 'left'

            # Then sweep within the column
            direction = agent.column_sweep_direction[col]
            sorted_targets = sorted(targets, key=lambda p: p[1]) if direction == 'down' else sorted(targets, key=lambda p: -p[1])
            return agent._move_towards_target(*sorted_targets[0])

        return None  # All assigned columns complete
