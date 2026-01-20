import requests
import json

API_KEY = "ec_280150d06e6a66c3a4e620c478b6203283a2ec27e0200d1db6779d038ce05603"
BASE_URL = "https://challenge.equiply.io/api/v1/c6"

headers = {
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def get_radar_data():
    response = requests.get(f"{BASE_URL}/resources-radar", headers=headers)
    return response.json() if response.status_code == 200 else None

def find_the_witness():
    """The Silent Witness - what object is 'watching' the ship"""
    radar_data = get_radar_data()
    
    ship_points = [p for p in radar_data['radar_data'] if p['source'] == 'ship']
    ship_points.sort(key=lambda p: p['timestamp'])
    
    # Get all ship timestamps
    ship_timestamps = set([p['timestamp'] for p in ship_points])
    
    print("="*70)
    print("FINDING THE SILENT WITNESS")
    print("="*70)
    
    # Find objects that appear at EVERY ship timestamp (or most of them)
    all_points = radar_data['radar_data']
    
    # Group by source and check which ones appear consistently
    from collections import defaultdict
    
    objects_by_id = defaultdict(list)
    
    for point in all_points:
        if point['source'] != 'ship':
            # Create a unique ID based on approximate position
            obj_id = f"{point['source']}_{int(point['x']/10)}_{int(point['y']/10)}_{int(point['z']/10)}"
            objects_by_id[obj_id].append(point)
    
    print("\nLooking for objects that appear multiple times (possible witness)...")
    
    for obj_id, detections in objects_by_id.items():
        if len(detections) >= 5:  # Appears 5+ times
            print(f"\n{obj_id}: {len(detections)} detections")
            source = detections[0]['source']
            avg_x = sum(p['x'] for p in detections) / len(detections)
            avg_y = sum(p['y'] for p in detections) / len(detections)
            avg_z = sum(p['z'] for p in detections) / len(detections)
            print(f"  Average position: ({avg_x:.1f}, {avg_y:.1f}, {avg_z:.1f})")
            print(f"  Timestamps: {sorted([p['timestamp'] for p in detections])[:5]}...")
    
    # Check the star at the anomaly timestamp more carefully
    print("\n" + "="*70)
    print("ANALYZING THE STAR AT ANOMALY TIMESTAMP")
    print("="*70)
    
    anomaly_time = 1704067220
    star_at_anomaly = [p for p in all_points if p['timestamp'] == anomaly_time and p['source'] == 'star'][0]
    
    print(f"\nStar detected at anomaly timestamp {anomaly_time}:")
    print(f"Position: ({star_at_anomaly['x']:.2f}, {star_at_anomaly['y']:.2f}, {star_at_anomaly['z']:.2f})")
    
    # Check if this star appears at other timestamps
    similar_stars = [p for p in all_points 
                     if p['source'] == 'star' 
                     and abs(p['x'] - star_at_anomaly['x']) < 10
                     and abs(p['y'] - star_at_anomaly['y']) < 10
                     and abs(p['z'] - star_at_anomaly['z']) < 10]
    
    print(f"\nThis star (or similar position) appears {len(similar_stars)} time(s)")
    
    if len(similar_stars) == 1:
        print("⚠️  This star ONLY appears at the anomaly timestamp!")
        print("⚠️  This is highly suspicious - stars don't just appear once!")
        print("\n🎯 FINDING: This is a GHOST SIGNAL - a false star detection!")
        
        return f"star at ({star_at_anomaly['x']:.2f}, {star_at_anomaly['y']:.2f}, {star_at_anomaly['z']:.2f})"
    
    return None

if __name__ == "__main__":
    answer = find_the_witness()
    
    if answer:
        print("\n" + "="*70)
        print("RECOMMENDED ANSWER:")
        print("="*70)
        print(f"\n{answer}")
        print("\nTry submitting this specific star as the ghost signal/silent witness!")