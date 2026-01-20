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
    response = requests.get(f"{BASE_URL}/resources-radar", headers=headers)
    return response.json() if response.status_code == 200 else None

def decode_flight_pattern(ship_points):
    """Try to decode what the flight pattern spells"""
    print("\n" + "="*70)
    print("DECODING FLIGHT PATTERN")
    print("="*70)
    
    # Group points that might form letters
    # Looking at the XY coordinates, let's analyze the pattern
    
    x_coords = [p['x'] for p in ship_points]
    y_coords = [p['y'] for p in ship_points]
    
    print("\nFlight path segments:")
    print("-" * 70)
    
    # Analyze movement patterns
    for i in range(len(ship_points) - 1):
        x1, y1 = ship_points[i]['x'], ship_points[i]['y']
        x2, y2 = ship_points[i+1]['x'], ship_points[i+1]['y']
        
        dx = x2 - x1
        dy = y2 - y1
        
        movement = ""
        if abs(dx) > abs(dy):
            movement = "RIGHT" if dx > 0 else "LEFT"
        else:
            movement = "UP" if dy > 0 else "DOWN"
        
        print(f"Point {i+1:2d} → {i+2:2d}: {movement:5s} (Δx={dx:6.1f}, Δy={dy:6.1f})")
    
    # Check for the anomaly points specifically
    print("\n" + "="*70)
    print("ANOMALY ANALYSIS")
    print("="*70)
    print("\nPoints 19 and 21 are nearly identical:")
    print(f"Point 19: ({ship_points[18]['x']:.2f}, {ship_points[18]['y']:.2f}, {ship_points[18]['z']:.2f})")
    print(f"Point 20: ({ship_points[19]['x']:.2f}, {ship_points[19]['y']:.2f}, {ship_points[19]['z']:.2f})")
    print(f"Point 21: ({ship_points[20]['x']:.2f}, {ship_points[20]['y']:.2f}, {ship_points[20]['z']:.2f})")
    print(f"Point 22: ({ship_points[21]['x']:.2f}, {ship_points[21]['y']:.2f}, {ship_points[21]['z']:.2f})")
    
    print("\nThe ship went: 19 → 20 → 21 (back to ~19)")
    print("This creates a LOOP or marks a specific location!")

def try_solutions():
    """Try different possible answers"""
    print("\n" + "="*70)
    print("POSSIBLE SOLUTIONS TO TRY")
    print("="*70)
    
    possible_answers = [
        "duplicate position",
        "anomaly at (211, 1, 133)",
        "ship returned to same position",
        "hidden contact",
        "ghost signal",
        "phantom contact",
        "false reading",
        "sensor malfunction",
        "cloaked object"
    ]
    
    print("\nBased on the challenge title 'Ghost Signal: The Silent Witness'")
    print("and the anomaly detected, the answer is likely related to:")
    print("\n1. A 'ghost' or phantom radar contact")
    print("2. Something hidden at the duplicate position")
    print("3. The pattern itself spelling something")
    
    return possible_answers

def submit_solution(answer):
    """Submit answer"""
    print(f"\nTrying: '{answer}'")
    response = requests.post(
        f"{BASE_URL}/solution",
        headers=headers,
        json={"answer": answer}
    )
    
    result = response.json()
    print(f"Response: {result}")
    return result

def main():
    radar_data = get_radar_data()
    
    if not radar_data:
        return
    
    ship_points = [p for p in radar_data['radar_data'] if p['source'] == 'ship']
    ship_points.sort(key=lambda p: p['timestamp'])
    
    decode_flight_pattern(ship_points)
    
    possible_answers = try_solutions()
    
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    print("\nGiven the challenge name 'Ghost Signal: The Silent Witness'")
    print("and the duplicate position anomaly, I suggest trying:")
    print("\n  1. 'ghost signal' (matches the challenge title)")
    print("  2. 'phantom contact'")
    print("  3. 'cloaked object'")
    
    print("\nWhich answer should we try first?")
    print("Enter the answer to submit, or type 'all' to try multiple:")

if __name__ == "__main__":
    main()