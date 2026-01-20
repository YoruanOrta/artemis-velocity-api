import requests
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
        print(response.text)
        return None

def analyze_ship_pattern(radar_data):
    """Extract and analyze ship coordinates"""
    print("\n" + "="*60)
    print("ANALYZING SHIP FLIGHT PATTERN")
    print("="*60)
    
    # Extract ship coordinates
    ship_points = [point for point in radar_data['radar_data'] if point['source'] == 'ship']
    
    # Sort by timestamp
    ship_points.sort(key=lambda p: p['timestamp'])
    
    print(f"\nFound {len(ship_points)} ship position readings")
    print("\nShip coordinates (ordered by time):")
    print("-" * 60)
    
    for i, point in enumerate(ship_points):
        print(f"Point {i+1}: ({point['x']:7.2f}, {point['y']:7.2f}, {point['z']:7.2f}) at t={point['timestamp']}")
    
    return ship_points

def plot_ship_path_3d(ship_points):
    """Plot the ship's path in 3D space"""
    print("\nGenerating 3D visualization...")
    
    # Extract coordinates
    x = [p['x'] for p in ship_points]
    y = [p['y'] for p in ship_points]
    z = [p['z'] for p in ship_points]
    
    # Create 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the path
    ax.plot(x, y, z, 'b-', linewidth=2, label='Ship Path')
    ax.scatter(x, y, z, c='red', s=100, marker='o', label='Position Points')
    
    # Mark start and end
    ax.scatter(x[0], y[0], z[0], c='green', s=200, marker='*', label='START')
    ax.scatter(x[-1], y[-1], z[-1], c='purple', s=200, marker='*', label='END')
    
    # Labels
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.set_title('Ship Flight Pattern - 3D View')
    ax.legend()
    
    plt.savefig('ship_path_3d.png', dpi=300, bbox_inches='tight')
    print("3D plot saved as 'ship_path_3d.png'")
    
    return fig

def plot_2d_projections(ship_points):
    """Plot 2D projections of the ship's path"""
    print("\nGenerating 2D projections...")
    
    x = [p['x'] for p in ship_points]
    y = [p['y'] for p in ship_points]
    z = [p['z'] for p in ship_points]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # XY plane
    axes[0, 0].plot(x, y, 'b-o', linewidth=2)
    axes[0, 0].scatter(x[0], y[0], c='green', s=200, marker='*', label='START')
    axes[0, 0].scatter(x[-1], y[-1], c='purple', s=200, marker='*', label='END')
    axes[0, 0].set_xlabel('X')
    axes[0, 0].set_ylabel('Y')
    axes[0, 0].set_title('XY Plane (Top View)')
    axes[0, 0].grid(True)
    axes[0, 0].legend()
    axes[0, 0].axis('equal')
    
    # XZ plane
    axes[0, 1].plot(x, z, 'r-o', linewidth=2)
    axes[0, 1].scatter(x[0], z[0], c='green', s=200, marker='*', label='START')
    axes[0, 1].scatter(x[-1], z[-1], c='purple', s=200, marker='*', label='END')
    axes[0, 1].set_xlabel('X')
    axes[0, 1].set_ylabel('Z')
    axes[0, 1].set_title('XZ Plane (Front View)')
    axes[0, 1].grid(True)
    axes[0, 1].legend()
    axes[0, 1].axis('equal')
    
    # YZ plane
    axes[1, 0].plot(y, z, 'g-o', linewidth=2)
    axes[1, 0].scatter(y[0], z[0], c='green', s=200, marker='*', label='START')
    axes[1, 0].scatter(y[-1], z[-1], c='purple', s=200, marker='*', label='END')
    axes[1, 0].set_xlabel('Y')
    axes[1, 0].set_ylabel('Z')
    axes[1, 0].set_title('YZ Plane (Side View)')
    axes[1, 0].grid(True)
    axes[1, 0].legend()
    axes[1, 0].axis('equal')
    
    # Time vs Distance
    distances = [0]
    for i in range(1, len(ship_points)):
        dx = x[i] - x[i-1]
        dy = y[i] - y[i-1]
        dz = z[i] - z[i-1]
        dist = (dx**2 + dy**2 + dz**2)**0.5
        distances.append(distances[-1] + dist)
    
    axes[1, 1].plot(range(len(ship_points)), distances, 'm-o', linewidth=2)
    axes[1, 1].set_xlabel('Point Number')
    axes[1, 1].set_ylabel('Cumulative Distance')
    axes[1, 1].set_title('Distance Traveled Over Time')
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('ship_path_2d.png', dpi=300, bbox_inches='tight')
    print("2D projections saved as 'ship_path_2d.png'")
    
    return fig

def check_for_message(ship_points):
    """Check if coordinates spell out a message"""
    print("\n" + "="*60)
    print("CHECKING FOR HIDDEN MESSAGES")
    print("="*60)
    
    # Check if coordinates form ASCII characters
    print("\nChecking if coordinates could be ASCII values...")
    
    # Try different interpretations
    x_vals = [int(p['x']) for p in ship_points]
    y_vals = [int(p['y']) for p in ship_points]
    z_vals = [int(p['z']) for p in ship_points]
    
    print("\nX coordinates as potential ASCII:", x_vals)
    print("Y coordinates as potential ASCII:", y_vals)
    print("Z coordinates as potential ASCII:", z_vals)
    
    # Check if any are in printable ASCII range (32-126)
    for coord_name, coords in [('X', x_vals), ('Y', y_vals), ('Z', z_vals)]:
        if all(32 <= abs(c) <= 126 for c in coords):
            try:
                message = ''.join(chr(abs(c)) for c in coords)
                print(f"\n✓ {coord_name} coordinates decode to: '{message}'")
            except:
                pass

def main():
    # Get radar data
    radar_data = get_radar_data()
    
    if not radar_data:
        print("Failed to retrieve radar data")
        return
    
    # Analyze ship pattern
    ship_points = analyze_ship_pattern(radar_data)
    
    if len(ship_points) == 0:
        print("No ship coordinates found!")
        return
    
    # Check for hidden messages
    check_for_message(ship_points)
    
    # Generate visualizations
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)
    
    plot_ship_path_3d(ship_points)
    plot_2d_projections(ship_points)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nCheck the generated images:")
    print("- ship_path_3d.png")
    print("- ship_path_2d.png")
    print("\nLook for patterns, messages, or anomalies in the flight path!")

if __name__ == "__main__":
    main()