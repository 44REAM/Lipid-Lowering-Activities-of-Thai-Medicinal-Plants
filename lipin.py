import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import pandas as pd
import numpy as np

TABLE3_FILE = 'Bioactive_Analysis_Full.csv'
SORTED_TABLE3_FILE = 'Bioactive_Analysis_Full_Lipinski_Sorted.csv'
COMPOUND_COLUMN = 'Bioactive Compounds'
RULES_PASSED_COLUMN = 'Lipinski_Rules_Passed'

# Histogram bin-width configuration. Adjust these values to change the width
# of each numeric histogram bin (in the unit used by that measurement).
BIN_WIDTHS = {
    'MW': 25,
    'LogP': 1,
    'HBA': 1,
    'HBD': 1,
}

# Table 3 is ordered from the highest to the lowest number of Lipinski rules
# passed. Compound names are alphabetized within each group for easy lookup.
df_final = pd.read_csv(TABLE3_FILE)
df_final = (
    df_final.assign(_compound_sort=df_final[COMPOUND_COLUMN].str.casefold())
    .sort_values(
        [RULES_PASSED_COLUMN, '_compound_sort'],
        ascending=[False, True],
        kind='stable',
    )
    .drop(columns='_compound_sort')
    .reset_index(drop=True)
)
df_final.to_csv(SORTED_TABLE3_FILE, index=False)

# Set style
sns.set_style("white")
plt.rcParams.update({
    'figure.max_open_warning': 0,
    'text.color': '#1a1a1a',
    'axes.labelcolor': '#1a1a1a',
    'xtick.color': '#1a1a1a',
    'ytick.color': '#1a1a1a',
    'axes.edgecolor': '#1a1a1a',
    'font.size': 11,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'font.family': 'serif',           # ← use serif family
    'font.serif': 'Times New Roman',  # ← set to Times New Roman
})

fig = plt.figure(figsize=(7, 7))
gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.35)

ax_A = fig.add_subplot(gs[0, 0])
ax_B = fig.add_subplot(gs[0, 1])
ax_C = fig.add_subplot(gs[1, 0])
ax_D = fig.add_subplot(gs[1, 1])
ax_E = fig.add_subplot(gs[2, :])

bar_color = '#3a7abf'
ref_color = '#c0392b'
label_bg  = '#ffffff'

def add_panel_label(ax, letter, x=0.95, ha='right'):
    ax.text(x, 0.95, letter, transform=ax.transAxes,
            fontsize=14, fontweight='bold', va='top', ha=ha,
            color='#1a1a1a',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=label_bg,
                      edgecolor='none', alpha=0.85))


def bins_for(data, width):
    """Return bin edges aligned to multiples of a chosen bin width."""
    if width <= 0:
        raise ValueError('Histogram bin widths must be greater than zero.')

    start = np.floor(data.min() / width) * width
    end = np.ceil(data.max() / width) * width
    return np.arange(start, end + width, width)

# --- Panel A: Molecular Weight ---
mw = df_final['MW'].dropna()
ax_A.hist(mw, bins=bins_for(mw, BIN_WIDTHS['MW']), color=bar_color, edgecolor='white', linewidth=0.6)
ax_A.axvline(500, color=ref_color, linewidth=1.8, linestyle='--', label='MW = 500')
ax_A.set_xlabel('Molecular weight (MW)', fontweight='semibold')
ax_A.set_ylabel('Number of compounds', fontweight='semibold')
add_panel_label(ax_A, 'A')
sns.despine(ax=ax_A)

# --- Panel B: LogP ---
logp = df_final['LogP'].dropna()
ax_B.hist(logp, bins=bins_for(logp, BIN_WIDTHS['LogP']), color=bar_color, edgecolor='white', linewidth=0.6)
ax_B.axvline(5, color=ref_color, linewidth=1.8, linestyle='--', label='LogP = 5')
ax_B.set_xlabel('Partition coefficient (LogP)', fontweight='semibold')
ax_B.set_ylabel('Number of compounds', fontweight='semibold')
add_panel_label(ax_B, 'B')
sns.despine(ax=ax_B)

# --- Panel C: Hydrogen Bond Acceptors ---
hba = df_final['HBA'].dropna()
ax_C.hist(hba, bins=bins_for(hba, BIN_WIDTHS['HBA']), color=bar_color, edgecolor='white', linewidth=0.6)
ax_C.axvline(10, color=ref_color, linewidth=1.8, linestyle='--', label='HBA = 10')
ax_C.set_xlabel('Hydrogen bond acceptors (HBAs)', fontweight='semibold')
ax_C.set_ylabel('Number of compounds', fontweight='semibold')
add_panel_label(ax_C, 'C')
sns.despine(ax=ax_C)

# --- Panel D: Hydrogen Bond Donors ---
hbd = df_final['HBD'].dropna()
ax_D.hist(hbd, bins=bins_for(hbd, BIN_WIDTHS['HBD']), color=bar_color, edgecolor='white', linewidth=0.6)
ax_D.axvline(5, color=ref_color, linewidth=1.8, linestyle='--', label='HBD = 5')
ax_D.set_xlabel('Hydrogen bond donors (HBDs)', fontweight='semibold')
ax_D.set_ylabel('Number of compounds', fontweight='semibold')
add_panel_label(ax_D, 'D')
sns.despine(ax=ax_D)

# --- Panel E: Lipinski Pass Count ---
lipinski_counts = df_final['Lipinski_Rules_Passed'].value_counts().sort_index()
bars = ax_E.bar(lipinski_counts.index.astype(str), lipinski_counts.values,
                color=bar_color, edgecolor='white', linewidth=0.6, width=0.5)

for bar, count in zip(bars, lipinski_counts.values):
    ax_E.text(bar.get_x() + bar.get_width() / 2,
              bar.get_height() + max(lipinski_counts.values) * 0.01,
              str(count), ha='center', va='bottom',
              fontsize=11, fontweight='bold', color='#1a1a1a')

ax_E.set_xlabel('Number of Lipinski rules passed', fontweight='semibold')
ax_E.set_ylabel('Number of compounds', fontweight='semibold')
add_panel_label(ax_E, 'E', x=0.02, ha='left')
sns.despine(ax=ax_E)

plt.savefig('Bioactive_Analysis_Charts_Fixed.png', dpi=800, bbox_inches='tight')

print(
    "Table 3 sorted by Lipinski rules passed and saved as "
    f"'{SORTED_TABLE3_FILE}'. Visualization saved as "
    "'Bioactive_Analysis_Charts_Fixed.png'."
)
