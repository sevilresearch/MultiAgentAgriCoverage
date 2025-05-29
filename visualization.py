import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import time
import signal
import sys
import os
from PIL import Image
import shutil
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

simulation_time = round(0.00, 2)
time_step = round(0.1, 2)

# Number of visualization frames (iterations) required per action
MOVEMENT_FRAMES = 1     
PLANTING_FRAMES = 10    
WATERING_FRAMES = 4    
viz_while_loop_counter = 0

# Load the Twemoji font for emojis
emoji_font_path = "/home/isr-lab/.local/share/fonts/TwitterColorEmoji-SVGinOT.ttf"
# emoji_font_path = "D:/UWF Study/Spring 2025/Foundations of IS/Project3_LP/TwitterColorEmoji-SVGinOT-15.1.0/TwitterColorEmoji-SVGinOT-15.1.0/TwitterColorEmoji-SVGinOT.ttf"

emoji_font = fm.FontProperties(fname=emoji_font_path)

# standard font for non-emoji text
standard_font = "DejaVu Sans"

# def display_grid(grid, agents):
def display_grid(grid, agents, state_estimator, behavior_planner, record=False):


    """Displays the grid with an animated Matplotlib plot."""
    size = grid.size
    fig, ax = plt.subplots(figsize=(15, 6))

    if record:
        os.makedirs("sim_videos/frames", exist_ok=True)

    frame_dir = "sim_videos/frames"
    video_path = "sim_videos/1_agent_15x7.gif"

    if record:
        if os.path.exists(frame_dir):
            shutil.rmtree(frame_dir)
        os.makedirs(frame_dir)


    # Define colors for different cell types
    color_map = {
        "dry": "chocolate",     # Dry soil 
        "empty": "lightgray",   # Empty plot 
        "planted": "limegreen", # Planted crop 
        "robot": "royalblue"    # Agent
    }
    # Ensure agents is iterable
    if not isinstance(agents, list):
        agents = [agents]


    def check_all_cells_visited(grid, global_explored_cells):
        """Stops only when all cells have been visited at least once."""
        total_cells = grid.size[0] * grid.size[1]
        return len(global_explored_cells) >= total_cells



    def update_grid(simulation_time, frame_id=None):
        """Updates the grid visualization."""
        ax.clear()  # Clear the axis for the new frame

        # Go over each cell
        for y in range(size[0]):
            for x in range(size[1]):
                cell = grid.get_cell_info(x, y)
                
                # Background color for each cell
                if cell["soil_type"] == 2:  # Obstacle cell
                    color = "#4a4a4a"  # Dark gray barriers
                elif cell["moisture_level"] == 0:  # Dry soil
                    color = color_map["dry"]
                elif cell["crop_status"] == 1 and cell["moisture_level"] > 0:  # Planted & hydrated
                    color = color_map["planted"]
                else:  # Empty cell
                    color = color_map["empty"]

                # Draw the background color for the cell
                ax.add_patch(plt.Rectangle((x, size[0] - y - 1), 1, 1, color=color))

                # Overlay the robot emoji with a circular highlight
                for agent in agents:
                    if (x, y) == (agent.x, agent.y):  # If the agent is in this cell
                        ax.add_patch(plt.Circle((x + 0.5, size[0] - y - 0.5), 0.4, color=agent.color, alpha=0.6))
                        ax.text(x + 0.5, size[0] - y - 0.5, "🤖", fontsize=16, ha="center", va="center", fontproperties=emoji_font)

                # Overlay the plant emoji if crop status is planted
                if cell["crop_status"] == 1:  # If the plant is in this cell
                    ax.text(x + 0.5, size[0] - y - 0.5, "🌱", fontsize=16, ha="center", va="center", fontproperties=emoji_font)

        # Draw boundaries
        for y in range(1, size[0] - 1):  # Exclude first and last row
            for x in range(size[1] - 1):  # Exclude last column
                if grid.boundaries[y, x]:  # Check if boundary exists between columns
                    ax.plot([x + 1, x + 1], [y, y + 1], color="#4a4a4a", linewidth=3.5, linestyle="-")


        # Draw trail
        for agent in agents:
            if agent.agents_actual_visited_cells:
                trail_arr = np.array(agent.agents_actual_visited_cells)
                xs = trail_arr[:, 0]
                ys = size[0] - trail_arr[:, 1] - 1  # Flip vertically for display
                ax.scatter(xs + 0.5, ys + 0.5, s=25, c=agent.color, alpha=0.8, edgecolors='none', marker='s')

        # Set grid lines and limits
        ax.set_xticks(range(size[1] + 1))
        ax.set_yticks(range(size[0] + 1))
        # ax.grid(True, color="black", linewidth=0.5)
        ax.grid(True, which="both", color="black", linewidth=0.8, linestyle="--")  # Default gridlines

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xlim(0, size[1])
        ax.set_ylim(0, size[0])
        fig.tight_layout(pad=0.9, rect=[0, 0, 1, 1])  # Minimize white space without cutting text
        
        plt.pause(0.001)
        if record and frame_id is not None:
            fig.savefig(os.path.join(frame_dir, f"frame_{frame_id:04d}.png"), dpi=100)

    def stitch_frames_to_gif():
        frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".png")])
        if not frames:
            print("[WARN] No frames to stitch.")
            return
        images = [Image.open(os.path.join(frame_dir, f)) for f in frames]
        images[0].save(video_path, save_all=True, append_images=images[1:], duration=100, loop=0)
        print(f"[VIDEO] Saved simulation to {video_path}")
        shutil.rmtree(frame_dir)


    def signal_handler(sig, frame):
        """Handles Ctrl+C to exit cleanly."""
        print("\nSimulation stopped by user.")
        plt.close(fig)  # Close the Matplotlib figure properly
        sys.exit(0)  # Exit the program safely

    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

    # Initial grid display
    import visualization 
    visualization.simulation_time = 0.00   
    frame_counter = 0
    
    visualization.viz_while_loop_counter = 0

    update_grid(visualization.simulation_time, frame_counter if record else None)

    plt.ion()  
    sim_time_while_loop = 0
    try:
        while True:
            plt.savefig("7x15grid.eps", dpi=300)

            for agent in agents:
                time.sleep(4)    
                action = agent.select_action()
                step_time = agent.execute_action(action)  # ← pass it in
                update_grid(visualization.simulation_time, frame_counter if record else None)

            visualization.viz_while_loop_counter +=1
            visualization.simulation_time = visualization.viz_while_loop_counter * time_step
            
            sim_time_while_loop += 1

            if check_all_cells_visited(grid, agents[0].global_explored_cells):
                if all(agent.done or agent.is_frozen for agent in agents):
                    print("[SIM] Grid fully explored. All agents completed final tasks.")
                    print(f"sim_time_while_loop: \033[92m'{sim_time_while_loop:.2f}\033[0m' units")

                    time.sleep(2)
                    break
    except KeyboardInterrupt:
        print("\nSimulation stopped manually.")

    plt.close(fig)
    if record:
        stitch_frames_to_gif()

    return visualization.simulation_time

def check_all_cells_visited(grid, global_explored_cells):
    """Stops only when all cells have been visited at least once."""
    total_cells = grid.size[0] * grid.size[1]
    return len(global_explored_cells) >= total_cells


def run_simulation(grid, agents, state_estimator, behavior_planner):
    """Displays the grid with an animated Matplotlib plot."""
    size = grid.size

    if not isinstance(agents, list):
        agents = [agents]


    def signal_handler(sig, frame):
        """Handles Ctrl+C to exit cleanly."""
        print("\nSimulation stopped by user.")
        sys.exit(0)  # Exit the program safely

    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    import visualization
    visualization.simulation_time = 0
    visualization.time_step = 1  # in seconds or arbitrary units

    try:
        while True:
            visualization.simulation_time += visualization.time_step

            for agent in agents:
                agent.execute_action(agent.select_action())  # Execute each agent's action
            
            if check_all_cells_visited(grid, agents[0].global_explored_cells):  # Stop if all cells are planted
                if all(agent.done or agent.is_frozen for agent in agents):
                    print("[SIM] Grid fully explored. All agents have completed final tasks.")
                    time.sleep(2)
                    break
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    return visualization.simulation_time
