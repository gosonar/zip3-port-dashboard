import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import io


# 🔧 Optional: Reduce default padding

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Remove spacing between components */
        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0rem;
        }

        /* Specifically reduce margin after folium map */
        iframe {
            margin-bottom: -40px;
        }

        /* Optional: tighter spacing on the table itself */
        .stDataFrame {
            margin-top: -20px;
        }
    </style>
""", unsafe_allow_html=True)




# --- Load Data ---
df = pd.read_excel("zip3s_with_us_canada_ports.xlsx")
zip3_centroids = pd.read_pickle("zip3_centroids.pkl")  # Pre-saved from your data pipeline

# --- Region Coloring ---
region_colors = {
    "West Coast": "orange",
    "East Coast": "green",
    "Gulf Coast": "red",
    "Canada": "purple"
}

# --- Sidebar Filters ---
st.sidebar.title("ZIP3 Port Dashboard")
states = st.sidebar.multiselect("Filter by State", sorted(df['state'].unique()), default=df['state'].unique())
regions = st.sidebar.multiselect("Filter by Port Region", sorted(df['port_region'].dropna().unique()), default=df['port_region'].dropna().unique())

# --- Filter Dataset ---
filtered_df = df[df['state'].isin(states) & df['port_region'].isin(regions)]

# --- Folium Map ---
m = folium.Map(location=[39.5, -98.35], zoom_start=5, tiles='CartoDB positron')

for _, row in filtered_df.iterrows():
    coord = zip3_centroids.get(row['zip3_full'])
    if coord:
        folium.CircleMarker(
            location=coord,
            radius=5,
            color=region_colors.get(row['port_region'], "gray"),
            fill=True,
            fill_color=region_colors.get(row['port_region'], "gray"),
            fill_opacity=0.7,
            popup=folium.Popup(
                f"ZIP3: {row['zip3_full']}<br>"
                f"State: {row['state']}<br>"
                f"Nearest Port: {row['nearest_port']}<br>"
                f"Region: {row['port_region']}<br>"
                f"Distance: {row['miles_to_nearest_port']} mi",
                max_width=250
            )
        ).add_to(m)

# --- Heatmap Layer ---
HeatMap([zip3_centroids[z] for z in filtered_df['zip3_full'] if z in zip3_centroids]).add_to(m)


# --- Display Map ---
# Display Map (no extra columns or wrappers)
from streamlit.components.v1 import html

map_html = m.get_root().render()

# Wrap it in a responsive container with forced size
html(f"""
    <div style="width: 100%; height: 800px;">
        {map_html}
    </div>
""", height=800)




# Minimize heading size to avoid default spacing
st.markdown("#### Filtered ZIP3 Data")

# Show the table
st.dataframe(filtered_df)



# --- Export Buttons ---

# CSV
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📄 Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_zip3s.csv',
    mime='text/csv'
)

# Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='ZIP3 Data')
excel_buffer.seek(0)

st.download_button(
    label="📥 Download Filtered Data as Excel",
    data=excel_buffer,
    file_name='filtered_zip3s.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)



