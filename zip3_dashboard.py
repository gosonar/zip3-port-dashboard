import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# Load your processed data
df = pd.read_excel("zip3s_with_us_canada_ports.xlsx")
zip3_centroids = pd.read_pickle("zip3_centroids.pkl")  # We'll need to save this from your script

# Port regions
region_colors = {
    "West Coast": "orange",
    "East Coast": "green",
    "Gulf Coast": "red",
    "Canada": "purple"
}

# Sidebar filters
st.sidebar.title("ZIP3 Port Dashboard")
states = st.sidebar.multiselect("Filter by State", sorted(df['state'].unique()), default=df['state'].unique())
regions = st.sidebar.multiselect("Filter by Port Region", sorted(df['port_region'].dropna().unique()), default=df['port_region'].dropna().unique())

# Filter data
filtered_df = df[df['state'].isin(states) & df['port_region'].isin(regions)]

# Create Folium Map
m = folium.Map(location=[39.5, -98.35], zoom_start=5, tiles='CartoDB positron')

# Add markers
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
            popup=(
                f"ZIP3: {row['zip3_full']}<br>"
                f"State: {row['state']}<br>"
                f"Nearest Port: {row['nearest_port']}<br>"
                f"Region: {row['port_region']}<br>"
                f"Distance: {row['miles_to_nearest_port']} mi"
            )
        ).add_to(m)

# Optional: Add heatmap
HeatMap([zip3_centroids[z] for z in filtered_df['zip3_full'] if z in zip3_centroids]).add_to(m)

# Display the map
st_data = st_folium(m, width=1000, height=600)

# Show filtered table
st.subheader("Filtered ZIP3 Data")
st.dataframe(filtered_df)



# --------------------------------
# 💾 Add export/download buttons
# --------------------------------

# Convert to CSV and Excel (in-memory)
csv = filtered_df.to_csv(index=False).encode('utf-8')
excel = filtered_df.to_excel(index=False, engine='openpyxl')

st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_zip3s.csv',
    mime='text/csv'
)

st.download_button(
    label="⬇️ Download Filtered Data as Excel",
    data=excel,
    file_name='filtered_zip3s.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)





import pickle
with open("zip3_centroids.pkl", "wb") as f:
    pickle.dump(zip3_centroids, f)
