import colorsys
import io
import pandas as pd
from PIL import Image
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION SECTION - Customize fonts here
# ============================================================================

FONT_CONFIG = {
    'title_size': 32,
    'title_color': '#000000',
    'title_family': 'Times New Roman, serif',  # ← change this
    
    # Node label font sizes for each column separately:
    'src_node_size': 20,       # Column 1: Specific Name (Left column)
    'mid_node_size': 14,       # Column 2: Bioactive Compound (Middle column)
    'dst_node_size': 20,       # Column 3: Group (Right column)
    'node_label_size': 12,     # Fallback default if column-specific size is omitted
    'node_label_color': '#000000',
    'node_label_family': 'Times New Roman, serif',  # ← change this
    
    # Column header font sizes (can also be adjusted per column separately):
    'src_header_size': 24,     # Header: Specific Names
    'mid_header_size': 24,     # Header: Bioactive Compound
    'dst_header_size': 24,     # Header: Group
    'header_size': 24,         # Fallback default
    'header_color': '#000000',
    'header_family': 'Times New Roman, serif',  # ← change this
    
    'hover_size': 14,
    'hover_color': '#2d3748',
    'hover_family': 'Times New Roman, serif',  # ← change this
}

# Horizontal positions of columns (normalized from 0.0 to 1.0):
# Default: Left = 0.001, Middle = 0.5, Right = 0.999
# Adjust 'mid_x' to move the middle column (e.g. 0.40 - 0.45 moves it to the left)
POSITION_CONFIG = {
    'src_x': 0.001,   # Column 1: Specific Name (Left)
    'mid_x': 0.5,    # Column 2: Bioactive Compound (Middle) - move left a bit
    'dst_x': 0.999,   # Column 3: Group (Right)
}

# Figure dimensions (width and height in pixels):
FIGURE_CONFIG = {
    'width': 1100,
    'height': 1800,
}

# ============================================================================

# 1. Load the dataset
df = pd.read_csv("plant_compound.csv")

# 2. Preprocess Data
# df['Parts of Use'] = df['Parts of Use'].astype(str).str.split(',')
# df = df.explode('Parts of Use')
# df['Parts of Use'] = df['Parts of Use'].str.strip()

# 3. Create Node Labels
labels_src = df['Specific Name'].unique().tolist()
labels_mid = df['Bioactive Compound'].unique().tolist()
labels_dst = df['Group'].unique().tolist()
all_labels = labels_src + labels_mid + labels_dst

# Separate index mappings for each column stage to prevent collisions when a label
# appears in multiple columns (e.g., 'Polyphenols' as both Bioactive Compound and Group)
src_to_idx = {name: i for i, name in enumerate(labels_src)}
mid_to_idx = {name: len(labels_src) + i for i, name in enumerate(labels_mid)}
dst_to_idx = {name: len(labels_src) + len(labels_mid) + i for i, name in enumerate(labels_dst)}

# 4. Define Links
sources = []
targets = []
values = []

# Link Set 1: Specific Name -> Bioactive Compound
flow_1 = df.groupby(['Specific Name', 'Bioactive Compound']).size().reset_index(name='count')
for _, row in flow_1.iterrows():
    sources.append(src_to_idx[row['Specific Name']])
    targets.append(mid_to_idx[row['Bioactive Compound']])
    values.append(row['count'])

# Link Set 2: Bioactive Compound -> Group
flow_2 = df.groupby(['Bioactive Compound', 'Group']).size().reset_index(name='count')
for _, row in flow_2.iterrows():
    sources.append(mid_to_idx[row['Bioactive Compound']])
    targets.append(dst_to_idx[row['Group']])
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
# Format node labels with column-specific font sizes
src_node_size = FONT_CONFIG.get('src_node_size', FONT_CONFIG.get('col1_node_size', FONT_CONFIG.get('node_label_size', 12)))
mid_node_size = FONT_CONFIG.get('mid_node_size', FONT_CONFIG.get('col2_node_size', FONT_CONFIG.get('node_label_size', 12)))
dst_node_size = FONT_CONFIG.get('dst_node_size', FONT_CONFIG.get('col3_node_size', FONT_CONFIG.get('node_label_size', 12)))

formatted_labels = (
    [f"<span style='font-size:{src_node_size}px;'>{label}</span>" for label in labels_src] +
    [f"<span style='font-size:{mid_node_size}px;'>{label}</span>" for label in labels_mid] +
    [f"<span style='font-size:{dst_node_size}px;'>{label}</span>" for label in labels_dst]
)

# Column horizontal positions
src_x = POSITION_CONFIG.get('src_x', FONT_CONFIG.get('src_x', 0.001))
mid_x = POSITION_CONFIG.get('mid_x', FONT_CONFIG.get('mid_x', 0.42))
dst_x = POSITION_CONFIG.get('dst_x', FONT_CONFIG.get('dst_x', 0.999))

node_x = [src_x] * num_src + [mid_x] * num_mid + [dst_x] * num_dst

fig = go.Figure(data=[go.Sankey(
    # arrangement='snap',  # Better automatic arrangement
    node=dict(
        pad=10,  # Increased padding for better spacing
        thickness=25,  # Thicker nodes
        line=dict(color="rgba(255, 255, 255, 0.8)", width=1.5),  # Subtle white border
        label=formatted_labels,
        color=node_colors,
        x=node_x,  # Horizontal position for each column
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

max_nodes_in_column = max(len(labels_src), len(labels_mid), len(labels_dst))

# Formula: (Nodes * (Font Size + Padding)) + Top/Bottom Margins
# Allocating ~40px per node ensures labels never overlap vertically
dynamic_height = max(900, max_nodes_in_column * 40)
fig_width = FIGURE_CONFIG.get('width', 1400)
fig_height = FIGURE_CONFIG.get('height', 1200)

# 7. Enhanced Layout with Beautiful Styling (using FONT_CONFIG and FIGURE_CONFIG)
fig.update_layout(
    title={
        'text': "",
        'y': 0.97,
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
src_header_size = FONT_CONFIG.get('src_header_size', FONT_CONFIG.get('col1_header_size', FONT_CONFIG.get('header_size', 24)))
mid_header_size = FONT_CONFIG.get('mid_header_size', FONT_CONFIG.get('col2_header_size', FONT_CONFIG.get('header_size', 24)))
dst_header_size = FONT_CONFIG.get('dst_header_size', FONT_CONFIG.get('col3_header_size', FONT_CONFIG.get('header_size', 24)))

annotations = [
    dict(
        x=0.05, y=1.05,
        xref='paper', yref='paper',
        text='<b>Specific Names</b>',
        showarrow=False,
        font=dict(
            size=src_header_size,
            color=FONT_CONFIG['header_color'],
            family=FONT_CONFIG['header_family']
        ),
    ),
    dict(
        x=mid_x, y=1.05,
        xref='paper', yref='paper',
        xanchor='center',
        text='<b>Bioactive Compound</b>',
        showarrow=False,
        font=dict(
            size=mid_header_size,
            color=FONT_CONFIG['header_color'],
            family=FONT_CONFIG['header_family']
        ),
    ),
    dict(
        x=0.95, y=1.05,
        xref='paper', yref='paper',
        text='<b>Group</b>',
        showarrow=False,
        font=dict(
            size=dst_header_size,
            color=FONT_CONFIG['header_color'],
            family=FONT_CONFIG['header_family']
        ),
    ),
]

fig.update_layout(annotations=annotations)

# 1. Export the high-res image to bytes (scale=8 gives 11200 x 7200 px)
img_bytes = fig.to_image(format="png", scale=5)

# 2. Open with Pillow and save with 800 DPI metadata
image = Image.open(io.BytesIO(img_bytes))
image.save("sankey_diagram2_800dpi.png", dpi=(800, 800))