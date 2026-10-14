"""Plot top-plate FEA results (von Mises stress on the underside, vertical deflection on the top face).

Input : fea_6mm_nodes.csv  (exported from EquiSense_TopPlate_FEA_6mm.FCStd -> CCX_Results)
Output: fea_plot.png

Usage : python plot_fea.py [nodes.csv] [out.png]
"""
import sys

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
import pandas as pd

matplotlib.use("Agg")

src = sys.argv[1] if len(sys.argv) > 1 else "fea_6mm_nodes.csv"
out = sys.argv[2] if len(sys.argv) > 2 else "fea_plot.png"

d = pd.read_csv(src)
bottom = d[np.isclose(d.z, 0)]  # underside: peak tensile bending stress
top = d[d.z > 5.99].sort_values("z").drop_duplicates(["x", "y"], keep="last")

fig, axs = plt.subplots(1, 2, figsize=(12, 5.4), constrained_layout=True)
panels = [
    (axs[0], bottom, "vm", "turbo", "von Mises stress, underside (MPa)", (0, 120)),
    (axs[1], top, "dz", "viridis", "Vertical deflection (mm)", None),
]
for ax, df, col, cmap, label, lim in panels:
    tri = mtri.Triangulation(df.x, df.y)
    values = df[col].clip(upper=lim[1]) if lim else df[col]
    levels = np.linspace(lim[0], lim[1], 25) if lim else 25
    cs = ax.tricontourf(tri, values, levels=levels, cmap=cmap, extend="max" if lim else "neither")
    fig.colorbar(cs, ax=ax, shrink=0.9).set_label(label)
    for sx in (-1, 1):  # Z-mount spacer contact faces
        for sy in (-1, 1):
            ax.add_patch(plt.Rectangle((sx * 200 - 12, sy * 200 - 15), 24, 30, fill=False, ec="w", lw=1.5))
    for x in (-100, 100):  # foot pads
        ax.add_patch(plt.Rectangle((x - 50, -125), 100, 250, fill=False, ec="w", ls="--", lw=1.2))
    ax.set_aspect("equal")
    ax.set_xlim(-225, 225)
    ax.set_ylim(-225, 225)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")

axs[0].set_title("Stress, capped at 120 MPa for legibility\n(276 MPa peak = sharp spacer-edge singularity)", fontsize=11)
axs[1].set_title("Deflection, max %.2f mm at plate centre" % -d.dz.min(), fontsize=11)
fig.savefig(out, dpi=170, facecolor="white")
print("saved", out)
