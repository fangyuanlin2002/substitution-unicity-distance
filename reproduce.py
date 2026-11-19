"""Print saved experiment results, generate two figures, and display them."""
from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent


def main():
    with (ROOT / 'results.csv').open(newline='') as f:
        rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]
    n = [int(r['n']) for r in rows]

    def values(key):
        return [100 * r[key] for r in rows]

    print('Saved experiment results; probabilities in percent.')
    print('Communication theory based formula: two-letter-context model.')
    print('Uniform: deterministic evaluation of the same formula under uniform letters.')
    print('This script plots saved results; it does not rerun the experiments.\n')
    print(f"{'N':>3} {'Candidates':>11} {'Actual':>9} {'Uniform':>9} "
          f"{'Comm. theory':>13} {'Codebook check':>15} {'Threshold':>11}")
    for r in rows:
        print(f"{int(r['n']):3d} {int(r['M']):11d} {100*r['actual']:9.4f} "
              f"{100*r['uniform_formula']:9.4f} {100*r['formula']:13.4f} "
              f"{100*r['two_context_RC']:15.4f} {100*r['threshold']:11.4f}")
    error = max(abs(r['formula'] - r['actual']) for r in rows) * 100
    print(f'\nLargest absolute formula error: {error:.3f} percentage points.')
    for key, name in [('actual', 'Actual corpus'), ('formula', 'Communication theory based formula')]:
        crossing = next((int(r['n']) for r in rows if r[key] >= .99), None)
        print(f'{name}: first tested length reaching 99% = {crossing}.')
    print('The uncertainty band is ±2 Monte Carlo SE; it does not bound model error or numerical bias.')

    plt.rcParams.update({'font.family': 'serif', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig1, ax1 = plt.subplots(figsize=(8, 4.8))
    for key, label, style in [
        ('uniform_formula', 'Uniform letters (deterministic formula)', ':'),
        ('iid_RC', 'English letter frequencies', '--'),
        ('one_context_RC', 'One-letter context', '-.'),
        ('two_context_RC', 'Two-letter context', '-')
    ]:
        ax1.plot(n, values(key), style, label=label, linewidth=1.7)
    ax1.set_title('Communication theory based predictions')

    fig2, ax2 = plt.subplots(figsize=(8, 4.8))
    prediction = values('formula')
    se = values('formula_se')
    ax2.fill_between(n, [max(0, v-2*s) for v, s in zip(prediction, se)],
                     [min(100, v+2*s) for v, s in zip(prediction, se)],
                     color='C0', alpha=.15, label='Formula: ±2 Monte Carlo SE')
    ax2.plot(n, prediction, 'C0-', label='Communication theory based formula')
    ax2.plot(n, values('two_context_RC'), 'C1x', label='Whole-codebook check')
    ax2.plot(n, values('threshold'), 'C2--', label='Information-density threshold')
    ax2.set_title('Two-letter-context English model')

    output = ROOT / 'figures'
    output.mkdir(exist_ok=True)
    for fig, ax, name in [(fig1, ax1, 'models'), (fig2, ax2, 'formula')]:
        ax.plot(n, values('actual'), 'ko-', markersize=4, label='Actual corpus')
        ax.axhline(99, color='.65', linewidth=.7)
        ax.set(xlabel='Plaintext length (letters)', ylabel='Unique recovery (%)',
               ylim=(-2, 103), xticks=n)
        ax.legend(frameon=False, fontsize=9, loc='upper left')
        fig.tight_layout()
        fig.savefig(output / f'{name}.pdf')
        fig.savefig(output / f'{name}.png', dpi=200)
    print(f'\nFigures saved to {output}')
    plt.show()


if __name__ == '__main__':
    main()
