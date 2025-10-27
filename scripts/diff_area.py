import matplotlib.pyplot as plt
import scienceplots
import matplotlib
import csv
import sys

plt.style.use(['science', 'ieee'])
plt.rcParams.update({"font.size": 10})

csv_file = sys.argv[1]

time = []
guest_mem = []
cgroup_mem = []

with open(csv_file, 'r') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for row in reader:
        time.append(float(row[0]))
        guest_mem.append(float(row[1]))
        cgroup_mem.append(float(row[2]))

colors = matplotlib.cm.get_cmap('tab10').colors

fig, ax = plt.subplots()

# Aire Guest OS Memory (en-dessous)
ax.fill_between(time, cgroup_mem, color=colors[1], alpha=0.6, label="Cgroup Memory")
ax.fill_between(time, guest_mem, color=colors[0], alpha=0.5, label="Guest OS Memory")
# Aire Cgroup Memory (au-dessus)

# Courbes par dessus
ax.plot(time, cgroup_mem, color=colors[1], linewidth=1.5)
ax.plot(time, guest_mem, color=colors[0], linewidth=1.5)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Memory (MiB)")
ax.legend()
plt.tight_layout()
plt.savefig("memory_area_plot.pdf")
plt.show()