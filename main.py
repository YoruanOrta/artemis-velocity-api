from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import math
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Artemis VII Velocity Calculator")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Coordinate(BaseModel):
    x: float
    y: float
    z: float
    timestamp: int

class CoordinateRequest(BaseModel):
    coordinates: List[Coordinate]

class VelocityVector(BaseModel):
    x: float
    y: float
    z: float

class VelocityResponse(BaseModel):
    distance: float
    speed: float
    velocity: VelocityVector

def calculate_3d_distance(p1: Coordinate, p2: Coordinate) -> float:
    """Calculate Euclidean distance between two 3D points"""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dz = p2.z - p1.z
    return math.sqrt(dx**2 + dy**2 + dz**2)

@app.get("/")
async def root():
    return {
        "service": "Artemis VII Velocity Calculator",
        "status": "operational",
        "endpoints": {
            "calculate_velocity": "POST /calculate-velocity"
        }
    }

@app.post("/calculate-velocity", response_model=VelocityResponse)
async def calculate_velocity(request: CoordinateRequest):
    """
    Calculate spacecraft velocity from timestamped 3D coordinates
    
    Returns:
    - distance: Total distance traveled (sum of distances between consecutive points)
    - speed: Average speed (distance / time)
    - velocity: Velocity vector (average change in position per second)
    """
    coordinates = request.coordinates
    
    # Validate input
    if len(coordinates) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 coordinates are required"
        )
    
    # Calculate total distance (sum of distances between consecutive points)
    total_distance = 0.0
    for i in range(len(coordinates) - 1):
        distance = calculate_3d_distance(coordinates[i], coordinates[i + 1])
        total_distance += distance
    
    # Calculate time elapsed
    start_time = coordinates[0].timestamp
    end_time = coordinates[-1].timestamp
    time_elapsed = end_time - start_time
    
    if time_elapsed == 0:
        raise HTTPException(
            status_code=400,
            detail="Time elapsed cannot be zero"
        )
    
    # Calculate average speed (distance per unit time)
    average_speed = total_distance / time_elapsed
    
    # Calculate velocity vector (average change in position per second)
    start_pos = coordinates[0]
    end_pos = coordinates[-1]
    
    velocity_x = (end_pos.x - start_pos.x) / time_elapsed
    velocity_y = (end_pos.y - start_pos.y) / time_elapsed
    velocity_z = (end_pos.z - start_pos.z) / time_elapsed
    
    # Round to 2 decimal places
    response = VelocityResponse(
        distance=round(total_distance, 2),
        speed=round(average_speed, 2),
        velocity=VelocityVector(
            x=round(velocity_x, 2),
            y=round(velocity_y, 2),
            z=round(velocity_z, 2)
        )
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)