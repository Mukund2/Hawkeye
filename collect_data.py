import requests
import pandas as pd
import time
from datetime import datetime

def fetch_aircraft_data():
    """Fetch current aircraft states from OpenSky API"""
    url = "https://opensky-network.org/api/states/all"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['states']
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def process_aircraft_data(states):
    """Convert raw API data into pandas DataFrame"""
    aircraft_list = []
    
    for state in states:
        # Skip if missing critical data
        if state[5] is None or state[6] is None:
            continue
            
        aircraft = {
            'timestamp': datetime.now(),
            'icao24': state[0],
            'callsign': state[1].strip() if state[1] else None,
            'origin_country': state[2],
            'longitude': state[5],
            'latitude': state[6],
            'altitude': state[7],
            'on_ground': state[8],
            'velocity': state[9],
            'heading': state[10],
            'vertical_rate': state[11]
        }
        aircraft_list.append(aircraft)
    
    return pd.DataFrame(aircraft_list)

def save_data(df, filename='aircraft_data.csv'):
    """Save data to CSV, appending if file exists"""
    try:
        # Try to read existing data
        existing_df = pd.read_csv(filename)
        # Append new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(filename, index=False)
    except FileNotFoundError:
        # File doesn't exist yet, create it
        df.to_csv(filename, index=False)
    
    print(f"Saved {len(df)} aircraft records to {filename}")

# Main execution
if __name__ == "__main__":
    print("Starting aircraft data collection...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Fetch data
            states = fetch_aircraft_data()
            
            if states:
                # Process into DataFrame
                df = process_aircraft_data(states)
                
                # Save to CSV
                save_data(df)
                
                print(f"Collected data at {datetime.now()}")
            
            # Wait 60 seconds before next collection
            # (OpenSky has rate limits, don't call too frequently)
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nData collection stopped.")