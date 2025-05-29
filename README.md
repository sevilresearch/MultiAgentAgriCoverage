# MultiAgentAgriCoverage
# Multi-Agent Behavior Planning for Agricultural Grid Tasks

This repository contains the simulation framework and analysis code for our ASME IMECE 2025 paper:  
**"Multi-Agent Coverage for Agricultural Robotics-Based Soil and Crops Monitoring"**  
📍 Designed and implemented by [Bhaavin Jogeshwar](mailto:bj83@students.uwf.edu)

## 📜 Project Overview

This simulation demonstrates decentralized behavior planning for multi-agent robotic systems performing planting and watering tasks in a constrained farm grid. It features:

- **Local perception and decision-making**
- **Dynamic helper logic for idle agents**
- **A* rerouting in the presence of obstacles**
- **Preassigned vs. Local planner comparisons**
- **Agent freezing and fault tolerance analysis**

The code is modular, fault-resilient, and ideal for replicating real-world agricultural field conditions.

---

## 🚀 Quick Start

### 1. Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/your-repo-name.git
cd your-repo-name
```

### 2. Install requirements

The project does not use a `requirements.txt`, but it assumes you have:
- Python ≥ 3.10
- `numpy`
- `matplotlib`

You can install them using:
```bash
pip install numpy matplotlib
```

### 3. (Optional but Recommended) Install Emoji Font for Icons

To enable emoji-like visuals in simulation icons, install the Twitter Color Emoji SVG font:

🔗 [Download Twemoji TTF](https://sourceforge.net/projects/twitt-c-emoji-svg-font.mirror/)

Once downloaded, install the TTF file based on your operating system:
- **Windows**: Right-click the `.ttf` file → Install
- **Mac**: Double-click the `.ttf` file → Install Font
- **Linux**: Copy the `.ttf` to `~/.fonts/` and run `fc-cache -fv`

---

## 🧠 Run the Simulation

```bash
python main.py
```

---

## 📂 Project Structure

```
📁 core simulation files:
├── main.py                   # Entry point – run simulations
├── agent.py                 # Agent class with movement, task logic, and rerouting
├── behavior_planning.py     # Three planner strategies: LP, PCP, and Block-based
├── grid.py                  # Grid logic with cell types and environment boundaries
├── state_estimation.py      # Perception logic for task identification
├── visualization.py         # Frame-based visual simulation and logging
├── generatinggrid.py        # (Optional) Generate or edit grid layouts

📁 analysis & results:
├── project3analysis.py       # Script for post-run analysis and plotting
├── IMECE_LP_20grids.txt     # Simulation log files
├── IMECE_PCP_20grids.txt
├── *.eps, *.png, *.psd      # Figures for paper and visualizations

📁 assets:
├── images/                  # Contains all plot snapshots and debug visuals
├── rerouting/               # Diagrams of reroute behavior
├── startposdiff/            # Grid variations and experiments

📁 others:
├── __pycache__/             # Python cache files
```

---

## 🧪 Reproducibility Notes

- Each simulation grid is 7×15 cells.
- Actions are frame-based: 
  - Move: 1 frame (0.05s)
  - Plant: 10 frames (0.5s)
  - Water: 4 frames (0.2s)
- Results include runtime, revisits, and distance metrics, used in Tables 1–3 and Figures 4–6 of the [ASME paper](./IMECE_2025_ASME_conference_paper_draft1%20BKJ%2005-10.pdf).

---

## 📊 Citation (APA)
Jogeshwar, B. K., Sevil, H. E., & Haghshenas-Jaryani, M. (2025). Multi-Agent Coverage for Agricultural Robotics-Based Soil and Crops Monitoring. _Proceedings of the ASME International Mechanical Engineering Congress & Exposition (IMECE)_, Memphis, TN.
