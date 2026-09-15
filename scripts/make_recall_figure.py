import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = json.load(open("data/recall_curve_data.json"))
citation = data["citation"]
rcr = data["rcr"]
ks_citation = list(range(1, len(citation) + 1))
ks_rcr = list(range(1, len(rcr) + 1))

fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(ks_citation, [v * 100 for v in citation], label="Raw citation count", color="#1f4e79", linewidth=1.8)
ax.plot(ks_rcr, [v * 100 for v in rcr], label="Relative Citation Ratio (RCR)", color="#c0504d", linewidth=1.8, linestyle="--")
ax.set_xlabel("Rank cutoff $k$ (papers examined, ranked by signal)")
ax.set_ylabel("Recall of guideline-matched papers (%)")
ax.set_xlim(0, 753)
ax.set_ylim(0, 100)
ax.axhline(100, color="gray", linewidth=0.5, linestyle=":")
ax.legend(loc="lower right", frameon=False, fontsize=9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("figures/recall_at_k.pdf")
fig.savefig("figures/recall_at_k.png", dpi=200)
print("saved recall_at_k.pdf and .png")
