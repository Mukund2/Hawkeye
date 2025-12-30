import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Page config
st.set_page_config(page_title="Hawkeye - Defense Intelligence", layout="wide")

# Title
st.title("Hawkeye - Real-Time Aircraft Intelligence")

# Load the most recent data
@st.cache_data
def load_data():
    df = pd.read_csv('aircraft_data.csv')
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    # Get data from the last collection (within last 2 minutes)
    latest_time = df['timestamp'].max()
    cutoff_time = latest_time - pd.Timedelta(minutes=2)
    recent_df = df[df['timestamp'] >= cutoff_time]
    # Remove duplicates - keep most recent position for each aircraft
    recent_df = recent_df.sort_values('timestamp').drop_duplicates(subset=['icao24'], keep='last')
    return recent_df

# Load data
df = load_data()

# Sidebar stats
st.sidebar.header("📊 Current Status")
st.sidebar.metric("Total Aircraft Tracked", len(df))
st.sidebar.metric("Countries", df['origin_country'].nunique())
st.sidebar.metric("Last Updated", df['timestamp'].iloc[0].strftime("%H:%M:%S"))

# Top countries
st.sidebar.subheader("Top 5 Countries")
top_countries = df['origin_country'].value_counts().head(5)
for country, count in top_countries.items():
    st.sidebar.write(f"🌍 {country}: {count}")

# Main map
st.subheader("🗺️ Global Aircraft Positions")

# Create the map centered on US (you can change this)
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Add aircraft to map
for idx, row in df.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        # Create popup text
        popup_text = f"""
        <b>Callsign:</b> {row['callsign']}<br>
        <b>Country:</b> {row['origin_country']}<br>
        <b>Altitude:</b> {row['altitude']:.0f}m<br>
        <b>Speed:</b> {row['velocity']:.1f} m/s<br>
        <b>Heading:</b> {row['heading']:.0f}°
        """
        
        # Add marker
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            popup=folium.Popup(popup_text, max_width=200),
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.6
        ).add_to(m)

# Display map
st_folium(m, width=1400, height=600)

# Data table at bottom
st.subheader("📋 Recent Aircraft Data")
# Show only relevant columns
display_df = df[['callsign', 'origin_country', 'altitude', 'velocity', 'heading']].head(20)
st.dataframe(display_df, use_container_width=True)