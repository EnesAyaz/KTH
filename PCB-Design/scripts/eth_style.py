"""
Figure style for the papers (after the figure style of ETH Zurich PES publications): serif fonts matching the text,
inward ticks on all sides, light grid, thin frame, MATLAB colour order, units in parentheses, inline curve labels,
bold sub-panel labels (a), (b.i) at the lower left.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

C = dict(blue=(0.0, 0.447, 0.741), red=(0.85, 0.325, 0.098), yellow=(0.929, 0.694, 0.125),
         purple=(0.494, 0.184, 0.556), green=(0.466, 0.674, 0.188), cyan=(0.301, 0.745, 0.933),
         dred=(0.635, 0.078, 0.184), grey=(0.45, 0.45, 0.45))
ORDER = [C[k] for k in ("blue", "red", "yellow", "purple", "green", "cyan", "dred")]
COL_W, TXT_W = 3.45, 7.16          # IEEE two-column widths (in)


def setup():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix", "font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 7.5,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.5,
        "axes.linewidth": 0.6, "axes.edgecolor": "black", "axes.prop_cycle": plt.cycler(color=ORDER),
        "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.minor.size": 1.3, "ytick.minor.size": 1.3,
        "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.pad": 2, "ytick.major.pad": 2,
        "axes.grid": True, "grid.color": "#d4d4d4", "grid.linewidth": 0.4, "grid.linestyle": "-",
        "axes.axisbelow": True, "axes.labelpad": 1.5, "lines.linewidth": 1.1, "lines.markersize": 3.5,
        "legend.frameon": True, "legend.framealpha": 1.0, "legend.edgecolor": "black", "legend.fancybox": False,
        "legend.borderpad": 0.3, "legend.handlelength": 1.6, "legend.labelspacing": 0.25,
        "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    })


def panel(ax, label, dx=-0.20, dy=-0.20):
    """Bold sub-panel label at the lower left, outside the axes, e.g. (a) or (b.i)."""
    ax.text(dx, dy, label, transform=ax.transAxes, fontsize=7.5, fontweight="bold", ha="left", va="top")


def tag(ax, x, y, text, color, ha="left", va="center", **kw):
    """Inline curve label in the curve colour."""
    kw.setdefault("fontsize", 7)
    ax.text(x, y, text, color=color, ha=ha, va=va, **kw)
