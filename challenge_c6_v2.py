import requests
import json

# API Configuration
API_KEY = "ec_280150d06e6a66c3a4e620c478b6203283a2ec27e0200d1db6779d038ce05603"
BASE_URL = "https://challenge.equiply.io/api/v1/c6"

headers = {
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def get_radar_data():
    """Fetch radar data from the API"""
    print("Fetching radar data...")
    response = requests.get(f"{BASE_URL}/resources-radar", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def analyze_anomaly(radar_data):
    """Deep analysis of the radar data for anomalies"""
    print("\n" + "="*70)
    print("DEEP ANOMALY ANALYSIS")
    print("="*70)
    
    ship_points = [point for point in radar_data['radar_data'] if point['source'] == 'ship']
    ship_points.sort(key=lambda p: p['timestamp'])
    
    # Check for duplicate positions
    print("\nChecking for duplicate/near-duplicate positions...")
    for i in range(len(ship_points)):
        for j in range(i+1, len(ship_points)):
            dx = ship_points[i]['x'] - ship_points[j]['x']
            dy = ship_points[i]['y'] - ship_points[j]['y']
            dz = ship_points[i]['z'] - ship_points[j]['z']
            distance = (dx**2 + dy**2 + dz**2)**0.5
            
            if distance < 5:  # Very close positions
                print(f"\n⚠️  ANOMALY DETECTED:")
                print(f"   Point {i+1} and Point {j+1} are suspiciously close!")
                print(f"   Distance: {distance:.2f} units")
                print(f"   Point {i+1}: ({ship_points[i]['x']:.2f}, {ship_points[i]['y']:.2f}, {ship_points[i]['z']:.2f})")
                print(f"   Point {j+1}: ({ship_points[j]['x']:.2f}, {ship_points[j]['y']:.2f}, {ship_points[j]['z']:.2f})")
    
    # Check for hidden objects at specific coordinates
    print("\n" + "="*70)
    print("CHECKING FOR HIDDEN OBJECTS AT KEY COORDINATES")
    print("="*70)
    
    all_data = radar_data['radar_data']
    
    # Check what's at the duplicate position
    duplicate_x, duplicate_y, duplicate_z = 211.27, 1.42, 133.26  # Average of points 19 and 21
    
    print(f"\nSearching for objects near the anomaly point ({duplicate_x:.2f}, {duplicate_y:.2f}, {duplicate_z:.2f})...")
    
    nearby_objects = []
    for point in all_data:
        dx = point['x'] - duplicate_x
        dy = point['y'] - duplicate_y
        dz = point['z'] - duplicate_z
        distance = (dx**2 + dy**2 + dz**2)**0.5
        
        if distance < 10 and point['source'] != 'ship':
            nearby_objects.append({
                'distance': distance,
                'source': point['source'],
                'coords': (point['x'], point['y'], point['z']),
                'timestamp': point['timestamp']
            })
    
    if nearby_objects:
        print(f"\n🎯 Found {len(nearby_objects)} objects near the anomaly:")
        nearby_objects.sort(key=lambda x: x['distance'])
        for obj in nearby_objects[:5]:  # Show top 5 closest
            print(f"   - {obj['source']:10s} at ({obj['coords'][0]:7.2f}, {obj['coords'][1]:7.2f}, {obj['coords'][2]:7.2f}) - Distance: {obj['distance']:.2f}")
    
    # Check all timestamps
    print("\n" + "="*70)
    print("ANALYZING ALL RADAR CONTACTS")
    print("="*70)
    
    sources_count = {}
    for point in all_data:
        source = point['source']
        sources_count[source] = sources_count.get(source, 0) + 1
    
    print("\nRadar contacts by type:")
    for source, count in sorted(sources_count.items()):
        print(f"   {source:10s}: {count:3d} contacts")
    
    # Look for unusual patterns
    print("\n" + "="*70)
    print("SEARCHING FOR HIDDEN MESSAGES IN THE PATTERN")
    print("="*70)
    
    # The engineer said "specific pattern" - let's look at the XY projection
    # which shows letters
    print("\nAnalyzing the flight pattern letters...")
    print("Based on the XY plane visualization, the pattern appears to spell:")
    print("\n   >>> Checking for spelled message in flight path <<<")
    
    # The pattern looks like it might spell "SOS" or similar
    # Let's also check if there's a hidden object the engineer is pointing to
    
    return ship_points

def submit_solution(answer):
    """Submit the finding to Mission Control"""
    print("\n" + "="*70)
    print("SUBMITTING FINDINGS TO MISSION CONTROL")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/solution",
        headers=headers,
        json={"answer": answer}
    )
    
    print(f"\nResponse: {response.status_code}")
    print(response.json())
    
    return response.json()

def main():
    radar_data = get_radar_data()
    
    if not radar_data:
        return
    
    ship_points = analyze_anomaly(radar_data)
    
    print("\n" + "="*70)
    print("CONCLUSIONS")
    print("="*70)
    print("\nThe engineer's 'careful review' request makes sense now:")
    print("1. The ship returned to nearly the same position twice (points 19 & 21)")
    print("2. This creates an anomaly that wouldn't occur in normal calibration")
    print("3. The engineer is deliberately pointing to something at these coordinates")
    print("\nPossible findings to report:")
    print("- Duplicate position anomaly")
    print("- Specific coordinates being highlighted")
    print("- Hidden object at the anomaly location")
    print("- Pattern in the flight path itself")
    
    # Try different answers
    print("\n" + "="*70)
    print("What should we report? Let me try a few possibilities...")
    print("="*70)

if __name__ == "__main__":
    main()