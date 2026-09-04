import sys
import pandas as pd
import math
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Enable CoordGen for cleaner, publication-grade 2D coordinate generation
rdDepictor.SetPreferCoordGen(True)

# ============================================================================
# CONFIGURATION SECTION - Customize fonts, positions, resolution & layout here
# ============================================================================

FONT_CONFIG = {
    'font_family': 'Times New Roman',
    'plant_size': 18,           # Scientific name (plant) font size (italic)
    'compound_size': 18,        # Compound name font size (bold)
}

# Text vertical positions (relative to axes coordinates):
# Adjust these to control vertical spacing and avoid text overlap
TEXT_POSITION = {
    'plant_y': 1.18,            # Y position of scientific name (plant)
    'compound_y': 1.03,         # Y position of compound name (when plant is present)
    'single_name_y': 1.08,      # Y position of compound name (when plant is absent)
}

# ============================================================================
# MOLECULE CONFIG - ปรับความหนาของเส้นพันธะและขนาดตัวอักษรของอะตอมในโมเลกุล
# ============================================================================
MOLECULE_CONFIG = {
    'bond_line_width': 5.0,     # ความหนาของเส้นโมเลกุล (แนะนำ: 3.5 - 5.0 ยิ่งมากยิ่งหนาเข้ม)
    'atom_label_min_font': 30,  # ขนาดตัวอักษรของอะตอม (เช่น OH, O, N) ให้หนาและชัดสมส่วนกับเส้น
}

FIGURE_CONFIG = {
    'n_cols': 5,                # Number of columns in grid
    'col_width_inch': 3.2,      # Width per grid cell in inches (DO NOT ADJUST PLOT SIZE)
    'row_height_inch': 2.8,     # Height per grid cell in inches
    'mol_img_width': 1000,      # RDKit drawing canvas width (pixels) - prevents blurriness
    'mol_img_height': 750,      # RDKit drawing canvas height (pixels)
    'dpi': 600,                 # Output PNG resolution (600 DPI publication standard)
    'out_path': 'bioactive_structures.png',
}

# ============================================================================
# 1. Load data
# ============================================================================
df = pd.read_csv("Bioactive_Analysis_Full.csv")
df = df.dropna(subset=["SMILES", "Bioactive Compounds"])
df = df[df["SMILES"].str.strip() != ""]

# Build mapping: Bioactive Compound → Specific Name (plant name)
pc = pd.read_csv("plant_compound.csv")
pc["Bioactive Compound"] = pc["Bioactive Compound"].str.strip()
pc["Specific Name"] = pc["Specific Name"].str.strip()
specific_name_map = pc.drop_duplicates("Bioactive Compound").set_index("Bioactive Compound")["Specific Name"].to_dict()

# ============================================================================
# 2. Parse molecules
# ============================================================================
mols, names = [], []
for _, row in df.iterrows():
    mol = Chem.MolFromSmiles(row["SMILES"].strip())
    if mol is not None:
        mols.append(mol)
        names.append(row["Bioactive Compounds"].strip())
    else:
        print(f"⚠  Could not parse SMILES for: {row['Bioactive Compounds']}")

print(f"✔  {len(mols)} molecules loaded successfully.")

# ============================================================================
# 3. Layout parameters
# ============================================================================
N_COLS = FIGURE_CONFIG['n_cols']
N_ROWS = math.ceil(len(mols) / N_COLS)

# ============================================================================
# 4. Build one PIL image per molecule (High Resolution)
# ============================================================================
def mol_to_pil(mol, width=FIGURE_CONFIG['mol_img_width'], height=FIGURE_CONFIG['mol_img_height']):
    drawer = rdMolDraw2D.MolDraw2DCairo(width, height)
    opts = drawer.drawOptions()
    opts.addStereoAnnotation = True
    opts.bondLineWidth = MOLECULE_CONFIG['bond_line_width']
    if MOLECULE_CONFIG.get('atom_label_min_font', 0) > 0:
        opts.minFontSize = MOLECULE_CONFIG['atom_label_min_font']
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    bio = BytesIO(drawer.GetDrawingText())
    return Image.open(bio).convert("RGB")

print(f"Rendering {len(mols)} molecules at {FIGURE_CONFIG['mol_img_width']}×{FIGURE_CONFIG['mol_img_height']} px...")
images = [mol_to_pil(m) for m in mols]

# ============================================================================
# 5. Compose subplot figure
# ============================================================================
fig_w = N_COLS * FIGURE_CONFIG['col_width_inch']
fig_h = N_ROWS * FIGURE_CONFIG['row_height_inch']

fig, axes = plt.subplots(
    N_ROWS, N_COLS,
    figsize=(fig_w, fig_h),
    dpi=100,  # Screen preview DPI
)

if N_ROWS == 1:
    axes = [axes]
axes_flat = [ax for row in axes for ax in (row if hasattr(row, "__iter__") else [row])]

font_family = FONT_CONFIG['font_family']
plant_size = FONT_CONFIG['plant_size']
compound_size = FONT_CONFIG['compound_size']

plant_y = TEXT_POSITION['plant_y']
compound_y = TEXT_POSITION['compound_y']
single_name_y = TEXT_POSITION['single_name_y']

for i, ax in enumerate(axes_flat):
    if i < len(images):
        ax.imshow(images[i], interpolation='antialiased')
        compound = names[i]
        plant = specific_name_map.get(compound, "")
        kw = dict(transform=ax.transAxes, ha="center", va="bottom",
                  clip_on=False, fontfamily=font_family)
        if plant:
            # Scientific name – italic, above compound name
            ax.text(0.5, plant_y, plant, fontsize=plant_size,
                    fontstyle="italic", fontweight="normal", **kw)
            ax.text(0.5, compound_y, compound, fontsize=compound_size,
                    fontweight="bold", fontstyle="normal", **kw)
        else:
            # Compound name only
            ax.text(0.5, single_name_y, compound, fontsize=compound_size,
                    fontweight="bold", fontstyle="normal", **kw)
    ax.axis("off")

plt.tight_layout(pad=0.8, h_pad=4.0, w_pad=1.0)

out_path = FIGURE_CONFIG['out_path']
out_dpi = FIGURE_CONFIG['dpi']
print(f"Saving high-resolution figure to {out_path} ({out_dpi} DPI)...")
plt.savefig(out_path, bbox_inches="tight", dpi=out_dpi)
print(f"✔  Saved → {out_path}")
