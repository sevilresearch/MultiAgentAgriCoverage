import matplotlib.pyplot as plt
import numpy as np
import re
import matplotlib.ticker as ticker

# ---------------------- Data Extraction Function ----------------------
def extract_data(file_path):
    runs = []
    cells_travelled = {1: [], 2: [], 3: []}
    revisits = {1: [], 2: [], 3: []}
    percent_revisits = {1: [], 2: [], 3: []}
    run_times = []

    with open(file_path, 'r') as file:
        content = file.read()

    run_pattern = re.compile(r"--- [Rr]un (\d+) ---")
    agent_pattern = re.compile(r"Agent (\d) \(\w+\) stats:")
    cells_pattern = re.compile(r"Total cells travelled: (\d+)")
    revisits_pattern = re.compile(r"Total revisits: (\d+)")
    percent_pattern = re.compile(r"Percentage of revisited cells: ([\d\.]+)%")
    time_pattern = re.compile(r"Sim time: ['\"]?([\d\.]+)['\"]? units")

    run_matches = list(re.finditer(run_pattern, content))
    run_indices = [match.start() for match in run_matches] + [len(content)]

    for i, run_match in enumerate(run_matches):
        run_num = int(run_match.group(1))
        runs.append(run_num)
        run_start = run_match.start()
        run_end = run_indices[i + 1] if i + 1 < len(run_indices) else len(content)
        run_content = content[run_start:run_end]

        agent_matches = list(re.finditer(agent_pattern, run_content))
        for j, agent_match in enumerate(agent_matches):
            agent_num = int(agent_match.group(1))
            agent_start = agent_match.start()
            agent_end = agent_matches[j + 1].start() if j + 1 < len(agent_matches) else len(run_content)
            agent_content = run_content[agent_start:agent_end]

            cells = re.search(cells_pattern, agent_content)
            rev = re.search(revisits_pattern, agent_content)
            perc = re.search(percent_pattern, agent_content)

            if cells and rev and perc:
                cells_travelled[agent_num].append(int(cells.group(1)))
                revisits[agent_num].append(int(rev.group(1)))
                percent_revisits[agent_num].append(float(perc.group(1)))

        time_match = re.search(time_pattern, run_content)
        if time_match:
            run_times.append(float(time_match.group(1)))

    all_cells = [val for agent_data in cells_travelled.values() for val in agent_data]
    all_revisits = [val for agent_data in revisits.values() for val in agent_data]
    all_percent = [val for agent_data in percent_revisits.values() for val in agent_data]

    return runs, cells_travelled, revisits, percent_revisits, run_times, all_cells, all_revisits, all_percent

# ---------------------- Load Both LP and PCP ----------------------
lp_path = 'IMECE_LP_20grids.txt'
pcp_path = 'IMECE_PCP_20grids.txt'

lp_runs, lp_cells, lp_revisits, lp_percent, lp_times, lp_all_cells, lp_all_revisits, lp_all_percent = extract_data(lp_path)
pcp_runs, pcp_cells, pcp_revisits, pcp_percent, pcp_times, pcp_all_cells, pcp_all_revisits, pcp_all_percent = extract_data(pcp_path)

# ---------------------- Averages ----------------------
lp_avg_travel = np.mean(lp_all_cells)
lp_avg_revisit = np.mean(lp_all_revisits)
lp_avg_time = np.mean(lp_times)

pcp_avg_travel = np.mean(pcp_all_cells)
pcp_avg_revisit = np.mean(pcp_all_revisits)
pcp_avg_time = np.mean(pcp_times)

# ---------------------- Plot Settings ----------------------
plt.rcParams.update({
    'font.size': 13,
    'axes.labelweight': 'bold',
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'lines.linewidth': 2,
    'legend.fontsize': 13  # Increased for better visibility
})

tick_locator = ticker.MultipleLocator(base=2)
agent_colors = {1: 'b', 2: 'y', 3: 'm'}

# ---------------------- Plot Function ----------------------
def plot_metric(runs, values, avg, title, ylabel, filename, is_multi_agent=False):
    plt.figure(figsize=(9, 4))
    if is_multi_agent:
        for agent, data in values.items():
            plt.plot(runs, data, marker='o',
                     color=agent_colors[agent],
                     markerfacecolor=agent_colors[agent],
                    #  markeredgecolor='black',
                     label=f"Agent {agent}")
    else:
        plt.plot(runs, values, marker='o', color='g', label=title.split(" per")[0])
    plt.axhline(y=avg, color='r', linestyle='--', linewidth=2, label=f"Avg: {avg:.2f}")
    plt.xlabel('Grid Environment')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(runs)
    plt.gca().xaxis.set_major_locator(tick_locator)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, format='eps')
    plt.close()

# ---------------------- LP Plots ----------------------
# plot_metric(lp_runs, lp_times, lp_avg_time,
#             'Simulation Time per Grid Environment (Local Planner)',
#             'Simulation Time (units)', 'IMECE_LP_simtime.eps')

# plot_metric(lp_runs, lp_cells, lp_avg_travel,
#             'Total Cells Travelled per Grid Environment (Local Planner)',
#             'Total Cells Travelled', 'IMECE_LP_cells_travelled.eps', is_multi_agent=True)

# plot_metric(lp_runs, lp_revisits, lp_avg_revisit,
#             'Revisits per Grid Environment (Local Planner)',
#             'Total Revisits', 'IMECE_LP_revisits.eps', is_multi_agent=True)

# # ---------------------- PCP Plots ----------------------
# plot_metric(pcp_runs, pcp_times, pcp_avg_time,
#             'Simulation Time per Grid Environment (Preassigned Columns Planner)',
#             'Simulation Time (units)', 'IMECE_PCP_simtime.eps')

# plot_metric(pcp_runs, pcp_cells, pcp_avg_travel,
#             'Total Cells Travelled per Grid Environment (Preassigned Columns Planner)',
#             'Total Cells Travelled', 'IMECE_PCP_cells_travelled.eps', is_multi_agent=True)

# plot_metric(pcp_runs, pcp_revisits, pcp_avg_revisit,
#             'Revisits per Grid Environment (Preassigned Columns Planner)',
#             'Total Revisits', 'IMECE_PCP_revisits.eps', is_multi_agent=True)


# ---------------------- Combined Simulation Time Plot ----------------------
plt.figure(figsize=(9, 4))

# Plot LP simulation times
plt.plot(lp_runs, lp_times, marker='o', color='blue', label='LP Simulation Time')
plt.axhline(y=lp_avg_time, color='blue', linestyle='--', linewidth=2, label=f'LP Avg: {lp_avg_time:.2f}')

# Plot PCP simulation times
plt.plot(pcp_runs, pcp_times, marker='s', color='orange', label='PCP Simulation Time')
plt.axhline(y=pcp_avg_time, color='orange', linestyle='--', linewidth=2, label=f'PCP Avg: {pcp_avg_time:.2f}')

# Labels and formatting
plt.xlabel('Grid Environment')
plt.ylabel('Simulation Time (units)')
plt.title('Simulation Time per Grid Environment (LP vs. PCP)')
plt.xticks(lp_runs)
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(base=2))
plt.grid(True)
plt.legend(loc='upper right')  # <-- Legend position set here
plt.tight_layout()
plt.savefig('IMECE_combined_simtime.eps', format='eps')
plt.show()
plt.close()
