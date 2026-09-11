"""Illustrative resistor loss calculation; currents are RMS values."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    resistance = 0.1  # ohm, assumed constant with temperature
    current = np.linspace(0, 20, 101)
    loss = current**2 * resistance
    assert np.isclose(loss[-1], 40.0)
    with (output / "loss_sweep.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["current_rms_A", "loss_W"])
        writer.writerows(zip(current, loss))
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(current, loss, linewidth=2)
    ax.set(xlabel="RMS current (A)", ylabel="Conduction loss (W)",
           title="Resistive conduction loss (R = 0.1 ohm)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output / "loss_plot.png", dpi=180)
    fig.savefig(output / "loss_plot.pdf")
    plt.close(fig)
    (output / "results.tex").write_text(
        rf"\newcommand{{\Resistance}}{{{resistance:.2f}}}" + "\n" +
        rf"\newcommand{{\MaxCurrent}}{{{current[-1]:.0f}}}" + "\n" +
        rf"\newcommand{{\MaxLoss}}{{{loss[-1]:.1f}}}" + "\n",
        encoding="utf-8")
    print(f"At {current[-1]:.0f} A RMS: {loss[-1]:.1f} W; outputs in {output}")


if __name__ == "__main__":
    main()
