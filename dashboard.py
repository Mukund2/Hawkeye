import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(page_title="Hawkeye - Defense Intelligence", layout="wide")

# Define threat zones with coordinates
THREAT_ZONES = {
    "Taiwan Strait": {
        "bounds": [[23.5, 118.0], [26.0, 122.0]],  # [lat_min, lon_min], [lat_max, lon_max]
        "center": [24.75, 120.0],
        "description": "Critical strait between Taiwan and mainland China. High-value for monitoring cross-strait military activity and potential conflict escalation."
    },
    "Korean Peninsula": {
        "bounds": [[33.0, 124.0], [43.0, 131.0]],
        "center": [38.0, 127.5],
        "description": "Monitoring zone for North Korean missile activity, US-ROK joint operations, and regional military posture."
    },
    "Black Sea": {
        "bounds": [[41.0, 27.0], [47.0, 42.0]],
        "center": [44.0, 34.5],
        "description": "Active conflict zone. Tracking Russian naval activity, NATO reconnaissance, and Ukraine-related military operations."
    }
}

# Military callsign patterns
MILITARY_PATTERNS = {
    'US': ['RCH', 'USAF', 'CNV', 'NAVY', 'ARMY', 'COAST', 'EVAC', 'FFAB', 'HOUND', 'SPAR'],
    'NATO': ['NAF', 'BAF', 'GAF', 'RAF', 'RRR', 'FAF', 'IAF'],
    'RUSSIA': ['RSD', 'RFF', 'RA', 'AFL']
}

def is_military_aircraft(callsign):
    """Check if callsign matches military patterns"""
    if not callsign or pd.isna(callsign):
        return False, None
    
    callsign = str(callsign).strip().upper()
    
    for country, patterns in MILITARY_PATTERNS.items():
        for pattern in patterns:
            if callsign.startswith(pattern):
                return True, country
    return False, None

def point_in_zone(lat, lon, zone_bounds):
    """Check if a point is within a threat zone"""
    lat_min, lon_min = zone_bounds[0]
    lat_max, lon_max = zone_bounds[1]
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

def detect_loitering(df, icao24, time_window_minutes=30, distance_threshold_km=10):
    """Detect if an aircraft is loitering (staying in same area)"""
    # Get aircraft's positions over time
    aircraft_data = df[df['icao24'] == icao24].sort_values('timestamp')
    
    if len(aircraft_data) < 3:
        return False
    
    # Check if positions are within threshold distance
    positions = aircraft_data[['latitude', 'longitude']].values
    
    # Simple distance check (rough approximation)
    lat_range = positions[:, 0].max() - positions[:, 0].min()
    lon_range = positions[:, 1].max() - positions[:, 1].min()
    
    # Rough conversion: 1 degree ≈ 111km
    distance_moved = np.sqrt((lat_range * 111)**2 + (lon_range * 111)**2)
    
    return distance_moved < distance_threshold_km

def detect_clustering(df, lat, lon, radius_km=50):
    """Detect if multiple aircraft are clustered near a position"""
    # Rough distance calculation
    df['dist'] = np.sqrt(
        ((df['latitude'] - lat) * 111)**2 + 
        ((df['longitude'] - lon) * 111)**2
    )
    
    nearby = df[df['dist'] < radius_km]
    return len(nearby) >= 3  # 3+ aircraft within radius

@st.cache_data
def load_data():
    df = pd.read_csv('aircraft_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    
    # Get data from last 2 minutes
    latest_time = df['timestamp'].max()
    cutoff_time = latest_time - pd.Timedelta(minutes=2)
    recent_df = df[df['timestamp'] >= cutoff_time]
    
    # Remove duplicates - keep most recent position
    recent_df = recent_df.sort_values('timestamp').drop_duplicates(subset=['icao24'], keep='last')
    
    # Add military classification
    recent_df[['is_military', 'military_country']] = recent_df['callsign'].apply(
        lambda x: pd.Series(is_military_aircraft(x))
    )
    
    # Add threat zone classification
    for zone_name, zone_data in THREAT_ZONES.items():
        recent_df[f'in_{zone_name.replace(" ", "_")}'] = recent_df.apply(
            lambda row: point_in_zone(row['latitude'], row['longitude'], zone_data['bounds'])
            if pd.notna(row['latitude']) and pd.notna(row['longitude']) else False,
            axis=1
        )
    
    return recent_df

# Load data
df = load_data()

# Calculate threat levels for each zone
threat_levels = {}
for zone_name, zone_data in THREAT_ZONES.items():
    zone_col = f'in_{zone_name.replace(" ", "_")}'
    aircraft_in_zone = df[df[zone_col] == True]
    military_in_zone = aircraft_in_zone[aircraft_in_zone['is_military'] == True]
    
    # Threat level calculation
    total_aircraft = len(aircraft_in_zone)
    military_count = len(military_in_zone)
    
    if military_count >= 5:
        level = "HIGH"
        color = "red"
    elif military_count >= 2:
        level = "ELEVATED"
        color = "orange"
    elif total_aircraft > 20:
        level = "MODERATE"
        color = "yellow"
    else:
        level = "NORMAL"
        color = "green"
    
    threat_levels[zone_name] = {
        'level': level,
        'color': color,
        'total_aircraft': total_aircraft,
        'military_aircraft': military_count,
        'military_details': military_in_zone[['callsign', 'military_country', 'altitude', 'velocity']].to_dict('records') if military_count > 0 else []
    }

# Title
st.title("Hawkeye - Defense Intelligence Platform")
st.markdown("*Open-source intelligence aggregation and threat assessment for strategic regions*")

# Sidebar - Intelligence Summary
st.sidebar.header("Intelligence Summary")
st.sidebar.metric("Total Aircraft Tracked", len(df))
st.sidebar.metric("Military Aircraft Detected", len(df[df['is_military'] == True]))
st.sidebar.metric("Active Threat Zones", sum(1 for z in threat_levels.values() if z['level'] != 'NORMAL'))

st.sidebar.markdown("---")
st.sidebar.subheader("Threat Zone Status")

for zone_name, threat_data in threat_levels.items():
    status_color = {
        'HIGH': '🔴',
        'ELEVATED': '🟠',
        'MODERATE': '🟡',
        'NORMAL': '🟢'
    }[threat_data['level']]
    
    st.sidebar.markdown(f"**{status_color} {zone_name}**")
    st.sidebar.markdown(f"Status: **{threat_data['level']}**")
    st.sidebar.markdown(f"Military: {threat_data['military_aircraft']} | Total: {threat_data['total_aircraft']}")
    
    if threat_data['military_aircraft'] > 0:
        with st.sidebar.expander("View Military Aircraft"):
            for aircraft in threat_data['military_details']:
                st.write(f"**{aircraft['callsign']}** ({aircraft['military_country']})")
                st.write(f"Alt: {aircraft['altitude']:.0f}m | Speed: {aircraft['velocity']:.1f}m/s")
    st.sidebar.markdown("---")

# Top countries
st.sidebar.subheader("Top 5 Countries")
top_countries = df['origin_country'].value_counts().head(5)
for country, count in top_countries.items():
    st.sidebar.write(f"{country}: {count}")

# Main map
st.subheader("Global Threat Assessment Map")

# Create map centered on Pacific (to see all threat zones)
m = folium.Map(location=[35, 120], zoom_start=3)

# Add threat zones as rectangles
for zone_name, zone_data in THREAT_ZONES.items():
    threat_info = threat_levels[zone_name]
    
    # Create rectangle for threat zone
    folium.Rectangle(
        bounds=zone_data['bounds'],
        color=threat_info['color'],
        fill=True,
        fillColor=threat_info['color'],
        fillOpacity=0.2,
        weight=3,
        popup=folium.Popup(f"""
            <div style='width: 300px'>
            <h4>{zone_name}</h4>
            <p><b>Threat Level:</b> {threat_info['level']}</p>
            <p><b>Total Aircraft:</b> {threat_info['total_aircraft']}</p>
            <p><b>Military Aircraft:</b> {threat_info['military_aircraft']}</p>
            <hr>
            <p style='font-size: 12px'>{zone_data['description']}</p>
            </div>
        """, max_width=300)
    ).add_to(m)
    
    # Add zone label
    folium.Marker(
        location=zone_data['center'],
        icon=folium.DivIcon(html=f"""
            <div style='font-size: 12pt; color: {threat_info['color']}; font-weight: bold; 
                        text-shadow: 1px 1px 2px white, -1px -1px 2px white;'>
                {zone_name}<br>{threat_info['level']}
            </div>
        """)
    ).add_to(m)

# Add aircraft to map
for idx, row in df.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        
        # Determine icon color based on military status
        if row['is_military']:
            color = 'darkred'
            icon_symbol = '✈'
            size = 5
        else:
            color = 'blue'
            icon_symbol = '•'
            size = 3
        
        # Create popup
        popup_text = f"""
        <b>{'⚠️ MILITARY ' if row['is_military'] else ''}Callsign:</b> {row['callsign']}<br>
        <b>Country:</b> {row['origin_country']}<br>
        <b>Altitude:</b> {row['altitude']:.0f}m<br>
        <b>Speed:</b> {row['velocity']:.1f} m/s<br>
        <b>Heading:</b> {row['heading']:.0f}°
        """
        
        if row['is_military']:
            popup_text += f"<br><b>Military Origin:</b> {row['military_country']}"
        
        # Add marker
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=size,
            popup=folium.Popup(popup_text, max_width=200),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)

# Display map
st_folium(m, width=1400, height=700)

# Intelligence Briefing Section
st.subheader("Intelligence Briefing")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Military Activity")
    military_df = df[df['is_military'] == True]
    
    if len(military_df) > 0:
        # Group by country
        military_by_country = military_df.groupby('military_country').size().sort_values(ascending=False)
        
        for country, count in military_by_country.items():
            st.write(f"**{country}:** {count} aircraft")
        
        # Show military aircraft in threat zones
        st.markdown("#### Military in Threat Zones")
        for zone_name in THREAT_ZONES.keys():
            zone_col = f'in_{zone_name.replace(" ", "_")}'
            mil_in_zone = military_df[military_df[zone_col] == True]
            if len(mil_in_zone) > 0:
                st.warning(f"⚠️ **{len(mil_in_zone)} military aircraft in {zone_name}**")
    else:
        st.info("No military aircraft currently detected")

with col2:
    st.markdown("### Pattern Detection")
    
    # Clustering detection
    clusters_detected = []
    for zone_name, zone_data in THREAT_ZONES.items():
        center = zone_data['center']
        if detect_clustering(df, center[0], center[1], radius_km=100):
            clusters_detected.append(zone_name)
    
    if clusters_detected:
        for zone in clusters_detected:
            st.warning(f"🔍 **Clustering detected in {zone}**")
    else:
        st.info("No unusual clustering detected")
    
    # High-value observations
    st.markdown("#### Notable Activity")
    
    # High altitude aircraft
    high_alt = df[df['altitude'] > 12000]  # Above 40,000 feet
    if len(high_alt) > 0:
        st.write(f"{len(high_alt)} aircraft above 12,000m (likely surveillance/recon)")
    
    # Low speed (loitering)
    slow = df[(df['velocity'] < 100) & (df['altitude'] > 1000)]
    if len(slow) > 0:
        st.write(f"{len(slow)} aircraft with low velocity (potential loitering)")

# Detailed data table
st.subheader("Detailed Aircraft Data")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    show_military_only = st.checkbox("Show Military Only", value=False)

with col2:
    selected_zone = st.selectbox("Filter by Threat Zone", ["All Zones"] + list(THREAT_ZONES.keys()))

with col3:
    selected_country = st.selectbox("Filter by Country", ["All Countries"] + sorted(df['origin_country'].unique().tolist()))

# Apply filters
filtered_df = df.copy()

if show_military_only:
    filtered_df = filtered_df[filtered_df['is_military'] == True]

if selected_zone != "All Zones":
    zone_col = f'in_{selected_zone.replace(" ", "_")}'
    filtered_df = filtered_df[filtered_df[zone_col] == True]

if selected_country != "All Countries":
    filtered_df = filtered_df[filtered_df['origin_country'] == selected_country]

# Display filtered data
display_cols = ['callsign', 'origin_country', 'altitude', 'velocity', 'heading', 'is_military']
st.dataframe(
    filtered_df[display_cols].head(50),
    use_container_width=True,
    hide_index=True
)

st.caption(f"Showing {len(filtered_df)} of {len(df)} total aircraft")