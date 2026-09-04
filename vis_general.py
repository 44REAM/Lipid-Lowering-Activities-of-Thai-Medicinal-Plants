import pandas as pd
import plotly.graph_objects as go
import colorsys

# ============================================================================
# CONFIGURATION SECTION - Customize fonts here
# ============================================================================

FONT_CONFIG = {
    'title_size': 32,
    'title_color': '#000000',
    'title_family': 'Times New Roman, serif',  # ← change this
    
    'node_label_size': 24,
    'node_label_color': '#000000',
    'node_label_family': 'Times New Roman, serif',  # ← change this
    
    'header_size': 36,
    'header_color': '#000000',
    'header_family': 'Times New Roman, serif',  # ← change this
    
    'hover_size': 14,
    'hover_color': '#2d3748',
    'hover_family': 'Times New Roman, serif',  # ← change this
}

# Figure dimensions (width and height in pixels):
FIGURE_CONFIG = {
    'width': 1200,
    'height': 1200,
}

# ============================================================================

# 1. Load the dataset
df = pd.read_csv("plant_general.csv")

# 2. Preprocess Data
df['Parts of Use'] = df['Parts of Use'].astype(str).str.split(',')
df = df.explode('Parts of Use')
df['Parts of Use'] = df['Parts of Use'].str.strip()

# 3. Create Node Labels
labels_src = df['Specific Name'].unique().tolist()
labels_mid = df['Family'].unique().tolist()
labels_dst = df['Parts of Use'].unique().tolist()
all_labels = labels_src + labels_mid + labels_dst

label_to_idx = {label: i for i, label in enumerate(all_labels)}

# 4. Define Links
sources = []
targets = []
values = []

# Link Set 1: Specific Name -> Family
flow_1 = df.groupby(['Specific Name', 'Family']).size().reset_index(name='count')
for _, row in flow_1.iterrows():
    sources.append(label_to_idx[row['Specific Name']])
    targets.append(label_to_idx[row['Family']])
    values.append(row['count'])

# Link Set 2: Family -> Parts of Use
flow_2 = df.groupby(['Family', 'Parts of Use']).size().reset_index(name='count')
for _, row in flow_2.iterrows():
    sources.append(label_to_idx[row['Family']])
    targets.append(label_to_idx[row['Parts of Use']])
    values.append(row['count'])

# 5. Create Beautiful Color Palettes

# Generate sophisticated color palette using HSL
def generate_gradient_colors(n, hue_start=150, hue_end=90, saturation=0.65, lightness=0.55):
    """Generate a gradient of colors in HSL space"""
    colors = []
    for i in range(n):
        hue = hue_start + (hue_end - hue_start) * (i / max(n - 1, 1))
        rgb = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
        colors.append(f'rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, 0.9)')
    return colors

# Assign colors to each section
num_src = len(labels_src)
num_mid = len(labels_mid)
num_dst = len(labels_dst)

# Create distinct color schemes for each column
colors_src = generate_gradient_colors(num_src, hue_start=200, hue_end=240, saturation=0.7, lightness=0.6)  # Blue-Purple
colors_mid = generate_gradient_colors(num_mid, hue_start=150, hue_end=180, saturation=0.65, lightness=0.55)  # Green-Cyan
colors_dst = generate_gradient_colors(num_dst, hue_start=30, hue_end=60, saturation=0.75, lightness=0.6)  # Orange-Yellow

node_colors = colors_src + colors_mid + colors_dst

# Create color mapping for links based on source node
link_colors = []
for src_idx in sources:
    # Get the base color and make it more transparent
    if src_idx < num_src:
        base_color = colors_src[src_idx]
    elif src_idx < num_src + num_mid:
        base_color = colors_mid[src_idx - num_src]
    else:
        base_color = colors_dst[src_idx - num_src - num_mid]
    
    # Convert to more transparent version
    link_colors.append(base_color.replace('0.9)', '0.3)'))

# 6. Create Enhanced Sankey Diagram
fig = go.Figure(data=[go.Sankey(
    arrangement='snap',  # Better automatic arrangement
    node=dict(
        pad=20,  # Increased padding for better spacing
        thickness=25,  # Thicker nodes
        line=dict(color="rgba(255, 255, 255, 0.8)", width=1.5),  # Subtle white border
        label=all_labels,
        color=node_colors,
        customdata=[f"<b>{label}</b>" for label in all_labels],
        hovertemplate='%{customdata}<br>Total Flow: %{value}<extra></extra>',
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color=link_colors,  # Color-coded links
        hovertemplate='%{source.label} → %{target.label}<br>Count: %{value}<extra></extra>',
    )
)])

fig_width = FIGURE_CONFIG.get('width', 1400)
fig_height = FIGURE_CONFIG.get('height', 900)

# 7. Enhanced Layout with Beautiful Styling (using FONT_CONFIG and FIGURE_CONFIG)
fig.update_layout(
    title={
        'text': "",
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(
            size=FONT_CONFIG['title_size'],
            color=FONT_CONFIG['title_color'],
            family=FONT_CONFIG['title_family']
        )
    },
    font=dict(
        size=FONT_CONFIG['node_label_size'],
        family=FONT_CONFIG['node_label_family'],
        color=FONT_CONFIG['node_label_color']
    ),
    height=fig_height,
    width=fig_width,
    plot_bgcolor='#f7fafc',  # Soft background
    paper_bgcolor='#ffffff',
    margin=dict(l=30, r=30, t=100, b=50),
    hoverlabel=dict(
        bgcolor="white",
        font_size=FONT_CONFIG['hover_size'],
        font_family=FONT_CONFIG['hover_family'],
        bordercolor="#cbd5e0"
    )
)

# Add annotations for column headers (using FONT_CONFIG)
annotations = [
    dict(
        x=0.05, y=1.05,
        xref='paper', yref='paper',
        text='<b>Specific Names</b>',
        showarrow=False,
        font=dict(
            size=FONT_CONFIG['header_size'],
            color=FONT_CONFIG['header_color'],
            family=FONT_CONFIG['header_family']
        ),
    ),
    dict(
        x=0.5, y=1.05,
        xref='paper', yref='paper',
        text='<b>Families</b>',
        showarrow=False,
        font=dict(
            size=FONT_CONFIG['header_size'],
            color=FONT_CONFIG['header_color'],
            family=FONT_CONFIG['header_family']
        ),
    ),
    dict(
        x=0.95, y=1.05,
        xref='paper', yref='paper',
        text='<b>Parts of Use</b>',
        showarrow=False,
        font=dict(
            size=FONT_CONFIG['header_size'],
            color=FONT_CONFIG['header_color'],
            family=FONT_CONFIG['header_family']
        ),
    ),
]

fig.update_layout(annotations=annotations)


import io
from PIL import Image

# 1. Export the high-res image to bytes (scale=8 gives 11200 x 7200 px)
img_bytes = fig.to_image(format="png", scale=4)

# 2. Open with Pillow and save with 800 DPI metadata
image = Image.open(io.BytesIO(img_bytes))
image.save("sankey_diagram_800dpi.png", dpi=(800, 800))