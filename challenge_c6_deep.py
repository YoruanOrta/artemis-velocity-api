import requests
import json
from collections import defaultdict

# API Configuration
API_KEY = "ec_280150d06e6a66c3a4e620c478b6203283a2ec27e0200d1db6779d038ce05603"
BASE_URL = "https://challenge.equiply.io/api/v1/c6"

headers = {
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def get_radar_data():
    response = requests.get(f"{BASE_URL}/resources-radar", headers=headers)
    return response.json() if response.status_code == 200 else None

def deep_analysis(radar_data):
    """Analyze EVERYTHING in the radar data"""
    print("\n" + "="*70)
    print("COMPLETE RADAR ANALYSIS - LOOKING AT EVERYTHING")
    print("="*70)
    
    all_points = radar_data['radar_data']
    
    # Group by source
    by_source = defaultdict(list)
    for point in all_points:
        by_source[point['source']].append(point)
    
    print("\n1. ANALYZING EACH SOURCE TYPE:")
    print("-" * 70)
    
    for source in sorted(by_source.keys()):
        points = by_source[source]
        print(f"\n{source.upper()} ({len(points)} total):")
        
        # Look for anomalies in each source type
        # Check for duplicates
        coords_seen = {}
        for i, point in enumerate(points):
            coord_key = f"{point['x']:.1f},{point['y']:.1f},{point['z']:.1f}"
            if coord_key in coords_seen:
                print(f"  ⚠️  DUPLICATE: Point {i} is at same location as point {coords_seen[coord_key]}")
                print(f"      Location: ({point['x']:.2f}, {point['y']:.2f}, {point['z']:.2f})")
            coords_seen[coord_key] = i
        
        # Check for suspicious timestamps
        timestamps = [p['timestamp'] for p in points]
        if len(set(timestamps)) != len(timestamps):
            print(f"  ⚠️  DUPLICATE TIMESTAMPS found in {source}")
    
    print("\n2. CHECKING FOR IMPOSSIBLE OBJECTS:")
    print("-" * 70)
    
    # Stars and planets shouldn't move, but let's check timestamps
    for source in ['star', 'planet']:
        if source in by_source:
            points = by_source[source]
            timestamps = [p['timestamp'] for p in points]
            unique_times = set(timestamps)
            
            if len(unique_times) < len(timestamps):
                print(f"\n⚠️  {source.upper()} has multiple readings at same timestamp!")
                
                # Find which ones
                time_count = {}
                for t in timestamps:
                    time_count[t] = time_count.get(t, 0) + 1
                
                for t, count in time_count.items():
                    if count > 1:
                        print(f"   Timestamp {t}: {count} {source}s detected")
                        matching = [p for p in points if p['timestamp'] == t]
                        for p in matching:
                            print(f"      - ({p['x']:.2f}, {p['y']:.2f}, {p['z']:.2f})")
    
    print("\n3. ANALYZING METADATA:")
    print("-" * 70)
    metadata = radar_data['metadata']
    print(f"Reported point count: {metadata['point_count']}")
    print(f"Actual point count: {len(all_points)}")
    print(f"Time range in metadata: {metadata['time_range']['start']} to {metadata['time_range']['end']}")
    
    # Check actual time range
    all_timestamps = [p['timestamp'] for p in all_points]
    actual_min = min(all_timestamps)
    actual_max = max(all_timestamps)
    print(f"Actual time range in data: {actual_min} to {actual_max}")
    
    if metadata['time_range']['start'] != actual_min or metadata['time_range']['end'] != actual_max:
        print("\n⚠️⚠️⚠️  METADATA DISCREPANCY DETECTED! ⚠️⚠️⚠️")
        print("The metadata time range does NOT match the actual data!")
        print(f"Metadata says: {metadata['time_range']['start']} to {metadata['time_range']['end']}")
        print(f"Actual range: {actual_min} to {actual_max}")
        print(f"Difference: {actual_max - metadata['time_range']['end']} seconds")
    
    print("\n4. LOOKING FOR PATTERNS IN SPECIFIC TIMESTAMPS:")
    print("-" * 70)
    
    # Check what happened at specific times
    ship_points = by_source['ship']
    ship_times = sorted(set([p['timestamp'] for p in ship_points]))
    
    print(f"\nShip timestamps: {ship_times[0]} to {ship_times[-1]}")
    print(f"That's {ship_times[-1] - ship_times[0]} seconds of flight")
    
    # Check what's detected at the SAME time as ship positions
    print("\n5. OBJECTS DETECTED AT SAME TIME AS SHIP POSITIONS:")
    print("-" * 70)
    
    for ship_time in ship_times[:3] + ship_times[-3:]:  # First 3 and last 3
        ship_pos = [p for p in ship_points if p['timestamp'] == ship_time][0]
        same_time = [p for p in all_points if p['timestamp'] == ship_time and p['source'] != 'ship']
        
        if same_time:
            print(f"\nAt t={ship_time} (Ship at {ship_pos['x']:.1f}, {ship_pos['y']:.1f}, {ship_pos['z']:.1f}):")
            for obj in same_time:
                print(f"  - {obj['source']:10s} at ({obj['x']:.1f}, {obj['y']:.1f}, {obj['z']:.1f})")

def find_the_witness(radar_data):
    """The challenge is called 'The Silent Witness' - find what's witnessing"""
    print("\n" + "="*70)
    print("SEARCHING FOR 'THE SILENT WITNESS'")
    print("="*70)
    
    ship_points = [p for p in radar_data['radar_data'] if p['source'] == 'ship']
    ship_points.sort(key=lambda p: p['timestamp'])
    
    # The anomaly point where ship returned
    anomaly_point = ship_points[20]  # Point 21 (index 20)
    
    print(f"\nAnomaly location: ({anomaly_point['x']:.2f}, {anomaly_point['y']:.2f}, {anomaly_point['z']:.2f})")
    print(f"Timestamp: {anomaly_point['timestamp']}")
    
    # Find what was there at that exact moment
    all_points = radar_data['radar_data']
    at_same_time = [p for p in all_points if p['timestamp'] == anomaly_point['timestamp'] and p['source'] != 'ship']
    
    print(f"\nObjects detected at the EXACT SAME timestamp as the anomaly:")
    if at_same_time:
        for obj in at_same_time:
            dist_x = obj['x'] - anomaly_point['x']
            dist_y = obj['y'] - anomaly_point['y']
            dist_z = obj['z'] - anomaly_point['z']
            distance = (dist_x**2 + dist_y**2 + dist_z**2)**0.5
            
            print(f"  - {obj['source']:10s} at ({obj['x']:.1f}, {obj['y']:.1f}, {obj['z']:.1f}) - {distance:.1f} units away")
    else:
        print("  No other objects at that exact timestamp!")

def main():
    radar_data = get_radar_data()
    
    if not radar_data:
        return
    
    deep_analysis(radar_data)
    find_the_witness(radar_data)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nLook for:")
    print("1. Metadata discrepancies")
    print("2. Duplicate detections")
    print("3. Objects at the anomaly timestamp")
    print("4. Patterns in the 'complete picture'")

if __name__ == "__main__":
    main()