
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pathlib import Path

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="DV Lab 7 | Interactive World Maps",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    letter-spacing: -0.4px;
}
[data-testid="stMetric"] {
    background: #f3f6fb;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e5eaf2;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD NATURAL EARTH DATASET
# =====================================================

# Corrected path: shapefile is in the SAME folder as app.py

DATA_PATH = (
    Path(__file__).parent
    / "ne_110m_admin_0_countries.shp"
)

@st.cache_data
def load_data():

    gdf = gpd.read_file(DATA_PATH)

    # Identify country name column
    country_columns = ["ADMIN", "NAME", "name", "NAME_EN"]

    country_col = next(
        (col for col in country_columns if col in gdf.columns),
        None
    )

    if country_col is None:
        raise ValueError("Country name column not found.")

    gdf["country"] = gdf[country_col].astype(str)

    # Identify population column
    population_columns = ["POP_EST", "pop_est"]

    pop_col = next(
        (col for col in population_columns if col in gdf.columns),
        None
    )

    if pop_col is not None:
        gdf["population"] = pd.to_numeric(
            gdf[pop_col], errors="coerce"
        )
        population_source = "Natural Earth population estimates"

    else:
        rng = np.random.default_rng(0)
        gdf["population"] = rng.integers(
            1000000, 1000000000, size=len(gdf)
        )
        population_source = "Simulated population data"

    # Set geographic coordinate system if missing
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    # Calculate country area in square kilometers
    area_gdf = gdf.to_crs("EPSG:6933")

    gdf["area_km2"] = area_gdf.geometry.area / 1000000

    # Calculate population density
    gdf["pop_density"] = (
        gdf["population"] / gdf["area_km2"]
    )

    gdf["pop_density"] = gdf["pop_density"].replace(
        [np.inf, -np.inf], np.nan
    )

    return gdf, population_source


if not DATA_PATH.exists():
    st.error(
        "Shapefile not found. Please check that "
        "ne_110m_admin_0_countries.shp is inside "
        "your DV Lab 7 folder."
    )
    st.code(str(DATA_PATH))
    st.stop()

try:
    gdf, population_source = load_data()
except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("Map Visualization Lab")
st.sidebar.write("TFB3133/TEB3133 Data Visualization")

st.sidebar.divider()

map_type = st.sidebar.radio(
    "Choose a Map Type",
    [
        "Map Cosmetics",
        "Map Visual Hierarchy",
        "Choropleth Map",
        "Geo Projection"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Dataset Information")

st.sidebar.write("Source: Natural Earth")
st.sidebar.write(f"Countries/regions: {len(gdf)}")
st.sidebar.caption(population_source)

# =====================================================
# MAIN DASHBOARD HEADER
# =====================================================

st.title("Interactive World Map Visualization")

st.write(
    "Explore geographical data through map styling, "
    "visual hierarchy, population density, and "
    "geographic projections."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries / Regions", len(gdf))

with col2:
    st.metric("Map Techniques", 4)

with col3:
    st.metric("Current View", map_type)

st.divider()

# =====================================================
# TASK 1: MAP COSMETICS
# =====================================================

if map_type == "Map Cosmetics":

    st.header("Task 1: Map Cosmetics")

    st.write(
        "Customize the appearance of the world map "
        "using different colors, borders, and backgrounds."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        country_color = st.color_picker(
            "Country Color", "#87CEEB"
        )

    with col2:
        border_color = st.color_picker(
            "Border Color", "#202020"
        )

    with col3:
        background_color = st.color_picker(
            "Background Color", "#E5E5E5"
        )

    border_width = st.slider(
        "Border Thickness",
        min_value=0.0,
        max_value=2.0,
        value=0.5,
        step=0.1
    )

    fig, ax = plt.subplots(figsize=(13, 7))

    gdf.plot(
        ax=ax,
        color=country_color,
        edgecolor=border_color,
        linewidth=border_width
    )

    ax.set_title(
        "Customized World Map",
        fontsize=16,
        fontweight="bold",
        pad=15
    )

    ax.set_facecolor(background_color)
    ax.set_axis_off()

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "Observation: Changing map colors, border "
        "thickness, and background improves the "
        "visual appearance and readability of the map."
    )

# =====================================================
# TASK 2: MAP VISUAL HIERARCHY
# =====================================================

elif map_type == "Map Visual Hierarchy":

    st.header("Task 2: Map Visual Hierarchy")

    st.write(
        "Highlight selected countries while keeping "
        "the remaining countries in a neutral color."
    )

    all_countries = sorted(gdf["country"].unique().tolist())

    default_countries = [
        "Brazil",
        "India",
        "China",
        "Australia",
        "South Africa",
        "Russia"
    ]

    available_defaults = [
        country for country in default_countries
        if country in all_countries
    ]

    highlighted_countries = st.multiselect(
        "Select Countries to Highlight",
        options=all_countries,
        default=available_defaults
    )

    highlight_color = st.color_picker(
        "Highlight Color",
        "#E63946"
    )

    neutral_color = st.color_picker(
        "Other Countries Color",
        "#87CEEB"
    )

    gdf_display = gdf.copy()

    gdf_display["map_color"] = gdf_display["country"].apply(
        lambda x: (
            highlight_color
            if x in highlighted_countries
            else neutral_color
        )
    )

    fig, ax = plt.subplots(figsize=(13, 7))

    gdf_display.plot(
        ax=ax,
        color=gdf_display["map_color"].tolist(),
        edgecolor="black",
        linewidth=0.4
    )

    ax.set_title(
        "World Map: Selected Countries Highlighted",
        fontsize=16,
        fontweight="bold",
        pad=15
    )

    legend_items = [
        mpatches.Patch(
            color=highlight_color,
            label="Selected Countries"
        ),
        mpatches.Patch(
            color=neutral_color,
            label="Other Countries"
        )
    ]

    ax.legend(
        handles=legend_items,
        loc="lower left"
    )

    ax.set_axis_off()
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.metric(
        "Number of Highlighted Countries",
        len(highlighted_countries)
    )

    if highlighted_countries:
        st.subheader("Selected Countries")
        st.write(", ".join(highlighted_countries))

    st.info(
        "Observation: Highlighting selected countries "
        "creates a visual hierarchy, allowing users "
        "to focus on important geographical regions."
    )

# =====================================================
# TASK 3: CHOROPLETH MAP
# =====================================================

elif map_type == "Choropleth Map":

    st.header("Task 3: Choropleth Map")

    st.write(
        "Visualize population density across countries "
        "using different color schemes and optional "
        "logarithmic transformation."
    )

    col1, col2 = st.columns(2)

    with col1:
        color_choice = st.selectbox(
            "Choose Color Scheme",
            [
                "OrRd",
                "YlGn",
                "Blues",
                "Purples",
                "Greens"
            ]
        )

    with col2:
        use_log_scale = st.checkbox(
            "Use Log Transformation",
            value=True
        )

    gdf_display = gdf.copy()

    if use_log_scale:
        gdf_display["display_density"] = np.log1p(
            gdf_display["pop_density"].clip(lower=0)
        )
        legend_label = "log(1 + Population Density)"

    else:
        gdf_display["display_density"] = (
            gdf_display["pop_density"]
        )
        legend_label = "People per km²"

    fig, ax = plt.subplots(figsize=(13, 7))

    gdf_display.plot(
        column="display_density",
        cmap=color_choice,
        edgecolor="black",
        linewidth=0.3,
        legend=True,
        legend_kwds={
            "label": legend_label,
            "shrink": 0.6
        },
        missing_kwds={
            "color": "lightgrey",
            "label": "No data"
        },
        ax=ax
    )

    ax.set_title(
        f"Population Density by Country ({color_choice})",
        fontsize=16,
        fontweight="bold",
        pad=15
    )

    ax.set_axis_off()
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Population Density Data")

    density_table = gdf[
        ["country", "population", "area_km2", "pop_density"]
    ].copy()

    density_table.columns = [
        "Country",
        "Population",
        "Area (km²)",
        "Density (people/km²)"
    ]

    st.dataframe(
        density_table.sort_values(
            "Density (people/km²)",
            ascending=False
        ).round(2),
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Population source: {population_source}")

    st.info(
        "Observation: Choropleth maps represent "
        "population density using color intensity. "
        "Log transformation reduces differences "
        "between extreme values, making patterns "
        "easier to compare."
    )

# =====================================================
# TASK 4: GEO PROJECTION
# =====================================================

elif map_type == "Geo Projection":

    st.header("Task 4: Geo Projection")

    st.write(
        "Explore how different geographic projections "
        "affect the appearance of the world map."
    )

    # Corrected: Define missing projection options

    projection_options = {
        "WGS84 (Geographic)": "EPSG:4326",
        "Robinson": (
            "+proj=robin +lon_0=0 +datum=WGS84 "
            "+units=m +no_defs"
        ),
        "Mollweide": (
            "+proj=moll +lon_0=0 +datum=WGS84 "
            "+units=m +no_defs"
        ),
        "Equal Earth": "EPSG:8857"
    }

    col1, col2 = st.columns(2)

    with col1:
        proj_choice = st.selectbox(
            "Select a Projection",
            list(projection_options.keys())
        )

    with col2:
        color_choice = st.selectbox(
            "Choose Color Scheme",
            [
                "OrRd",
                "YlGn",
                "Blues",
                "Purples",
                "Greens"
            ]
        )

    use_log_scale = st.checkbox(
        "Use Log Transformation for Population Density",
        value=True
    )

    gdf_display = gdf.copy()

    if use_log_scale:
        gdf_display["display_density"] = np.log1p(
            gdf_display["pop_density"].clip(lower=0)
        )
        legend_label = "log(1 + Population Density)"

    else:
        gdf_display["display_density"] = (
            gdf_display["pop_density"]
        )
        legend_label = "People per km²"

    # Convert coordinates to selected projection
    gdf_proj = gdf_display.to_crs(
        projection_options[proj_choice]
    )

    fig, ax = plt.subplots(figsize=(13, 7))

    gdf_proj.plot(
        column="display_density",
        cmap=color_choice,
        edgecolor="black",
        linewidth=0.3,
        legend=True,
        legend_kwds={
            "label": legend_label,
            "shrink": 0.6
        },
        missing_kwds={
            "color": "lightgrey"
        },
        ax=ax
    )

    ax.set_title(
        f"World Map in {proj_choice} Projection",
        fontsize=16,
        fontweight="bold",
        pad=15
    )

    ax.set_axis_off()
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Projection Information")

    projection_description = {
        "WGS84 (Geographic)":
            "Uses latitude and longitude coordinates. "
            "It is commonly used for geographic data.",

        "Robinson":
            "A compromise projection designed to "
            "provide a visually balanced world map.",

        "Mollweide":
            "An equal-area projection that preserves "
            "relative areas but distorts shapes.",

        "Equal Earth":
            "An equal-area projection that preserves "
            "relative land areas across the world."
    }

    st.write(projection_description[proj_choice])

    st.info(
        "Observation: Different map projections "
        "change the shapes, sizes, and arrangement "
        "of geographical features. Each projection "
        "has different strengths and limitations."
    )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "TFB3133/TEB3133 Data Visualization | "
    "Lab 7: Interactive Map Visualization Examples "
    "using Streamlit"
)
