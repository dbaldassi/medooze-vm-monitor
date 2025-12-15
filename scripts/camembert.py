import matplotlib.pyplot as plt
import scienceplots
import matplotlib
import numpy as np

plt.style.use(['science', 'ieee'])

# plt.rcParams.update({
#     "font.size": 30
# })

# Données principales (en octets)
# data = {
#     "anonymous\nmemory": 1528983552,
#     "files/slabs": 98304 + 1218992,
#     "other": 16492680,
#     # "slabs": 1218992,
# }

data = {
    "Guest\nmemory" : 485268,
    "Guest\nbuff/cache": 524716,
    "Other": 1817927680 / 1024 - (485268 + 524716),
}

labels = []
sizes = []
for k, v in data.items():
    if v > 0:
        labels.append(k)
        sizes.append(v / (1024 * 1024))

colors = matplotlib.cm.get_cmap('tab20').colors

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts = ax.pie(
    sizes,
    labels=None,  # On va placer les labels manuellement
    startangle=140,
    colors=colors[:len(labels)],
)

# Placer les labels à l'extérieur avec des traits
for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = 'left' if x > 0 else 'right'
    connectionstyle = "angle,angleA=0,angleB={}".format(ang)

    pos = (1.35 * np.sign(x), 1.4 * y)
    if labels[i] == "other":
        pos =  (1.25 * np.sign(x), 1 * y)
    elif labels[i] == "Guest\nmemory":
        horizontalalignment = 'right'
        pos =  (1.25 * np.sign(x), 1 * y)
        connectionstyle = None #"angle,angleA=0,angleB=0"# .format(ang)
        # pos =  (1.45 * np.sign(x), 1 * y)

    ax.annotate(
        labels[i],
        xy=(x, y),
        xytext=pos,
        horizontalalignment=horizontalalignment,
        fontsize=26,
        arrowprops=dict(arrowstyle="-", color=colors[i], connectionstyle=connectionstyle)
    )

# plt.title("Répartition mémoire (MiB)")
plt.tight_layout()
plt.savefig("anon_pie.pdf")
# plt.savefig("memory_pie_science.pdf")
plt.show()
