import matplotlib.pyplot as plt
import numpy as np

# Define the function to generate a 5x1 demo grid with key cell types
def generate_demo_grid_array():
    """Create a 5x1 demo grid with specific cell types."""
    grid = np.zeros((1, 5), dtype=[('moisture_level', 'i4'), ('crop_status', 'i4')])
    grid[0, 0] = (1, 1)  # Green: wet + planted
    grid[0, 1] = (1, 0)  # Gray: wet + empty
    grid[0, 2] = (0, 1)  # Red with 🌱: dry + planted
    grid[0, 3] = (0, 0)  # Dark red: dry + empty
    grid[0, 4] = (1, 0)  # Robot cell: wet + empty
    return grid

# Function to draw and save the visual demo grid
def save_demo_grid_image(grid, save_path):
    color_map = {
        "dry": "chocolate",
        "empty": "lightgray",
        "planted": "limegreen",
        "robot": "royalblue"
    }

    fig, ax = plt.subplots(figsize=(7, 2))

    for x in range(grid.shape[1]):
        cell = grid[0, x]
        crop_status = cell['crop_status']
        moisture_level = cell['moisture_level']

        # Background color logic
        if crop_status == 1 and moisture_level == 1:
            color = color_map["planted"]
        elif crop_status == 1 and moisture_level == 0:
            color = "red"
        elif crop_status == 0 and moisture_level == 0:
            color = "firebrick"
        else:
            color = color_map["empty"]

        # Draw the cell
        ax.add_patch(plt.Rectangle((x, 0), 1, 1, color=color))

        # Add robot on cell 4
        if x == 4:
            ax.add_patch(plt.Circle((x + 0.5, 0.5), 0.3, color=color_map["robot"], alpha=0.7))
            ax.text(x + 0.5, 0.5, "🤖", fontsize=16, ha="center", va="center")

        # Add plant icon if planted
        if crop_status == 1:
            ax.text(x + 0.5, 0.5, "🌱", fontsize=16, ha="center", va="center")

    # Layout and save
    ax.set_xlim(0, grid.shape[1])
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis("off")
    ax.set_title("Demo Grid: Cell Types in 7×15 Farm", fontsize=12, pad=10)
    plt.tight_layout()
    plt.savefig("grid_demo_legend.png", dpi=300)
    plt.show()
    plt.close()

# Run everything
demo_grid = generate_demo_grid_array()
save_demo_grid_image(demo_grid, "grid_demo_legend.png")
