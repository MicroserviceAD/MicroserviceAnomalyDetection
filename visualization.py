import networkx as nx
from matplotlib import pyplot as plt

G = nx.read_gml("benign_graph/graph-t0000.gml")
print(type(G))

nodePairs = []
weights = []
for u, v, weight in G.edges.data("weight"):
    print(u, v, weight)
    nodePairs.append(u + " - " + v)
    weights.append(weight)
#https://www.geeksforgeeks.org/bar-plot-in-matplotlib/
# Figure Size
fig, ax = plt.subplots(figsize=(25, 16))

# Horizontal Bar Plot
ax.barh(nodePairs, weights)

# Remove axes splines
for s in ['top', 'bottom', 'left', 'right']:
    ax.spines[s].set_visible(False)

# Remove x, y Ticks
ax.xaxis.set_ticks_position('none')
ax.yaxis.set_ticks_position('none')

# Add padding between axes and labels
ax.xaxis.set_tick_params(pad=5)
ax.yaxis.set_tick_params(pad=10)

# Add x, y gridlines
ax.grid(b=True, color='grey',
        linestyle='-.', linewidth=0.5,
        alpha=0.2)

# Show top values
ax.invert_yaxis()

# Add annotation to bars
for i in ax.patches:
    plt.text(i.get_width()+0.2, i.get_y()+0.5,
             str(round((i.get_width()), 2)),
             fontsize=10, fontweight='bold',
             color='grey')

# Add Plot Title
ax.set_title('Network traffic of Microservices',
             loc='left', )
# Show Plot

plt.xlabel('Traffic Volume')
plt.ylabel('Node Connections')
plt.savefig('simplepythondet.jpg')


