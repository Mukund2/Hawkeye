# Hawkeye - Defense Intelligence Platform
## Open-source threat detection and assessment for geopolitically tense regions
### Overview
Defense intelligence tool that demonstrates how open-source aircraft tracking data can be used for threat detection. Platform monitors global airspace with a focus on contested regions, automatically detecting military clustering and potential threat escalation.
### Key Features
Threat Zone Monitoring
- Taiwan Strait, Korean Peninsula, Black Sea
- color-coded zones based on military activity levels
- visual threat heatmap with clickable details
### Military Aircraft Detection
- automatic identification through US, NATO, and Russian callsigns
- real-time global tracking
### Pattern Detection
- clustering detection in contested areas
- loitering aircraft identified and risk of conflict increased
## Data Pipeline
OpenSky Network API → Python Data Collection → Pandas Processing → 
Threat Assessment Logic → Streamlit Dashboard → Intelligence Visualization
## Tech Stack
Data Source: OpenSky Network (public ADS-B aircraft tracking)
Backend: Python (pandas for data processing, requests for API calls)
Visualization: Streamlit + Folium (interactive maps)
Pattern Detection: Custom algorithms for clustering, loitering, and anomaly detection
Threat Assessment: Rule-based system for zone monitoring and alert generation
### Use Cases
- defense operations - real-time situational awareness of contested regions
- OSINT - publicly available data used for analysis
- geopolitical risk assessment
# Installation and Setup
## Prerequisites
Python 3.8+
pip package manager
## Installation

git clone https://github.com/yourusername/Hawkeye.git
cd Hawkeye

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install streamlit pandas folium streamlit-folium requests numpy

python3 collect_data.py
- Let run for 3-5 minutes, then Ctrl+C to stop

streamlit run dashboard.py
# Project Structure
Hawkeye/
├── dashboard.py          # Main Streamlit application
├── collect_data.py       # Data collection script
├── aircraft_data.csv     # Local data storage
├── requirements.txt      # Python dependencies
└── README.md            # This file

### Current capabilities
- 9,800+ aircraft tracked globally
- 28 military aircraft identified
- 3 active threat zones flagged