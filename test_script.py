import pandas as pd
import pgeocode
from geopy.distance import geodesic

# Load your Excel file (adjust the filename if needed)
df = pd.read_excel("C:/Users/kirkp/OneDrive/API SCRIPTS/Test stuff/ZIP3s.xlsx")  # adjust if needed


# Format ZIP3s
df['zip3_full'] = df['zip3'].astype(str).str.zfill(3)

# Approximate lat/lon for major U.S. and Canadian container ports
port_locations = {
    # U.S. Ports
    "Los Angeles/Long Beach": (33.75, -118.2),
    "Oakland/SF Bay": (37.8, -122.3),
    "Seattle/Tacoma": (47.6, -122.3),
    "Portland": (45.5, -122.7),
    "Houston": (29.75, -95.3),
    "New Orleans": (29.95, -90.1),
    "Savannah": (32.1, -81.1),
    "Charleston": (32.8, -79.95),
    "Norfolk": (36.85, -76.3),
    "Baltimore": (39.25, -76.6),
    "NY/NJ": (40.67, -74.17),
    "Miami": (25.77, -80.18),
    "Jacksonville": (30.4, -81.6),
    "Boston": (42.35, -71.05),

    # Canadian Ports
    "Vancouver": (49.3, -123.1),
    "Montreal": (45.5, -73.55),
    "Halifax": (44.65, -63.57)
}

# Use pgeocode for U.S. and Canada
nomi_us = pgeocode.Nominatim('us')
nomi_ca = pgeocode.Nominatim('ca')

# Build ZIP3 centroids
unique_zip3s = df['zip3_full'].unique()
zip3_centroids = {}

for zip3 in unique_zip3s:
    # Try US first
    sub_df = nomi_us.query_postal_code([f"{zip3}{i:02}" for i in range(100)])
    sub_df = sub_df.dropna(subset=['latitude', 'longitude'])
    if not sub_df.empty:
        zip3_centroids[zip3] = (sub_df['latitude'].mean(), sub_df['longitude'].mean())
    else:
        # Try Canadian postal prefixes (ZIP3s assumed to be valid in input)
        sub_df = nomi_ca.query_postal_code([f"{zip3}"])
        sub_df = sub_df.dropna(subset=['latitude', 'longitude'])
        if not sub_df.empty:
            zip3_centroids[zip3] = (sub_df['latitude'].mean(), sub_df['longitude'].mean())

# Determine ports within 250 miles of each ZIP3
def find_nearby_ports(zip3):
    coord = zip3_centroids.get(zip3)
    if not coord:
        return []
    return [name for name, port_coord in port_locations.items() if geodesic(coord, port_coord).miles <= 250]

df['nearby_ports'] = df['zip3_full'].apply(find_nearby_ports)
df['ports_within_250_miles'] = df['nearby_ports'].apply(lambda ports: ', '.join(ports) if ports else '')

# Flag if any ports are within 250 miles
df['within_250_miles'] = df['nearby_ports'].apply(bool)

# Save the results to Excel
output_path = "C:/Users/kirkp/OneDrive/API SCRIPTS/Test stuff/zip3s_with_us_canada_ports.xlsx"
df.to_excel(output_path, index=False)

# Print confirmation
import os
print("✅ File saved successfully.")
print("📁 Full path:", os.path.abspath(output_path))


# -----------------------------
# 📍 Add distance to nearest port
# -----------------------------
def nearest_port_info(zip3):
    coord = zip3_centroids.get(zip3)
    if not coord:
        return ('', None)
    
    closest_port = None
    min_distance = float('inf')
    for port_name, port_coord in port_locations.items():
        distance = geodesic(coord, port_coord).miles
        if distance < min_distance:
            min_distance = distance
            closest_port = port_name
    return (closest_port, round(min_distance, 2))

# Apply to each ZIP3
df[['nearest_port', 'miles_to_nearest_port']] = df['zip3_full'].apply(
    nearest_port_info
).apply(pd.Series)



# Save the results to Excel
output_path = "C:/Users/kirkp/OneDrive/API SCRIPTS/Test stuff/zip3s_with_us_canada_ports.xlsx"


# Assign regions to ports
port_regions = {
    "Los Angeles/Long Beach": "West Coast",
    "Oakland/SF Bay": "West Coast",
    "Seattle/Tacoma": "West Coast",
    "Portland": "West Coast",
    "NY/NJ": "East Coast",
    "Boston": "East Coast",
    "Norfolk": "East Coast",
    "Baltimore": "East Coast",
    "Charleston": "East Coast",
    "Savannah": "East Coast",
    "Miami": "East Coast",
    "Jacksonville": "East Coast",
    "Houston": "Gulf Coast",
    "New Orleans": "Gulf Coast",
    "Vancouver": "Canada",
    "Montreal": "Canada",
    "Halifax": "Canada"
}

# Add the region column
df['port_region'] = df['nearest_port'].map(port_regions)



df.to_excel(output_path, index=False)

# Print confirmation
import os
print("✅ File saved successfully.")
print("📁 Full path:", os.path.abspath(output_path))





import folium

# ----------------------------
# 🗂️ Assign regions to ports
# ----------------------------
port_regions = {
    "Los Angeles/Long Beach": "West Coast",
    "Oakland/SF Bay": "West Coast",
    "Seattle/Tacoma": "West Coast",
    "Portland": "West Coast",
    "NY/NJ": "East Coast",
    "Boston": "East Coast",
    "Norfolk": "East Coast",
    "Baltimore": "East Coast",
    "Charleston": "East Coast",
    "Savannah": "East Coast",
    "Miami": "East Coast",
    "Jacksonville": "East Coast",
    "Houston": "Gulf Coast",
    "New Orleans": "Gulf Coast",
    "Vancouver": "Canada",
    "Montreal": "Canada",
    "Halifax": "Canada"
}

# Add port_region to DataFrame
df['port_region'] = df['nearest_port'].map(port_regions)

# ----------------------------
# 🗺️ Create a map
# ----------------------------
# Center map on US roughly
map_center = [39.5, -98.35]
m = folium.Map(location=map_center, zoom_start=5, tiles='CartoDB positron')

# Add port markers
for port_name, coords in port_locations.items():
    folium.Marker(
        location=coords,
        popup=f"Port: {port_name}",
        icon=folium.Icon(color='blue', icon='anchor', prefix='fa')
    ).add_to(m)

# Add ZIP3 centroids
for idx, row in df.iterrows():
    zip_coord = zip3_centroids.get(row['zip3_full'])
    if zip_coord:
        folium.CircleMarker(
            location=zip_coord,
            radius=4,
            color='green' if row['within_250_miles'] else 'gray',
            fill=True,
            fill_opacity=0.6,
            popup=f"ZIP3: {row['zip3_full']}\nNearest Port: {row['nearest_port']}\nDistance: {row['miles_to_nearest_port']} mi"
        ).add_to(m)




import pickle
with open("C:/Users/kirkp/OneDrive/API SCRIPTS/Test stuff/zip3_centroids.pkl", "wb") as f:
    pickle.dump(zip3_centroids, f)




# Save map
map_path = "C:/Users/kirkp/OneDrive/API SCRIPTS/Test stuff/zip3_port_map.html"
m.save(map_path)

print("🗺️ Map saved to:", map_path)
