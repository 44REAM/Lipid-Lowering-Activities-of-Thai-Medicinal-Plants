import pandas as pd
import math
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import BytesIO
from PIL import Image

# ── 1. Load data ──────────────────────────────────────────────────────────────
df = pd.read_csv("Bioactive_Analysis_Full.csv")
df = df.dropna(subset=["SMILES", "Bioactive Compounds"])
df = df[df["SMILES"].str.strip() != ""]

# Build mapping: Bioactive Compound → Specific Name (plant name)
pc = pd.read_csv("plant_compound.csv")
pc["Bioactive Compound"] = pc["Bioactive Compound"].str.strip()
pc["Specific Name"] = pc["Specific Name"].str.strip()
specific_name_map = pc.drop_duplicates("Bioactive Compound").set_index("Bioactive Compound")["Specific Name"].to_dict()

# ── 2. Parse molecules ─────────────────────────────────────────────────────────
mols, names = [], []
for _, row in df.iterrows():
    mol = Chem.MolFromSmiles(row["SMILES"].strip())
    if mol is not None:
        mols.append(mol)
        names.append(row["Bioactive Compounds"].strip())
    else:
        print(f"⚠  Could not parse SMILES for: {row['Bioactive Compounds']}")

print(f"✔  {len(mols)} molecules loaded successfully.")

# ── 3. Layout parameters ──────────────────────────────────────────────────────
N_COLS = 5                              # fixed number of columns
N_ROWS = math.ceil(len(mols) / N_COLS)  # rows computed from column count
IMG_W, IMG_H = 140, 100                 # pixels per cell

# ── 4. Build one PIL image per molecule ───────────────────────────────────────
def mol_to_pil(mol, width=IMG_W, height=IMG_H):
    drawer = rdMolDraw2D.MolDraw2DCairo(width, height)
    drawer.drawOptions().addStereoAnnotation = True
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    bio = BytesIO(drawer.GetDrawingText())
    return Image.open(bio).convert("RGB")

images = [mol_to_pil(m) for m in mols]

# ── 5. Compose subplot figure ─────────────────────────────────────────────────
fig, axes = plt.subplots(
    N_ROWS, N_COLS,
    figsize=(N_COLS * IMG_W / 96, N_ROWS * (IMG_H + 30) / 96),  # ~96 dpi
    dpi=130,
)

# Make axes always a 2D array
if N_ROWS == 1:
    axes = [axes]
axes_flat = [ax for row in axes for ax in (row if hasattr(row, "__iter__") else [row])]

TNR = "Times New Roman"                  # shorthand for font family

for i, ax in enumerate(axes_flat):
    if i < len(images):
        ax.imshow(images[i])
        compound = names[i]
        plant    = specific_name_map.get(compound, "")
        kw = dict(transform=ax.transAxes, ha="center", va="bottom",
                  clip_on=False, fontfamily=TNR)
        if plant:
            # Scientific name – italic, above compound name
            ax.text(0.5, 1.13, plant, fontsize=8,
                    fontstyle="italic", fontweight="normal", **kw)
        # Compound name – bold
        ax.text(0.5, 1.00, compound, fontsize=8,
                fontweight="bold", fontstyle="normal", **kw)
    ax.axis("off")

# fig.suptitle("Bioactive Compounds – 2D Structures", fontsize=14, fontweight="bold", y=1.005)
plt.tight_layout(pad=0.5, h_pad=3.5)

out_path = "bioactive_structures.png"
plt.savefig(out_path, bbox_inches="tight", dpi=800)
print(f"✔  Saved → {out_path}")
plt.show()
