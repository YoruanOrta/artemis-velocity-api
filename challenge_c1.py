import requests
import json

# API Key
API_KEY = "ec_280150d06e6a66c3a4e620c478b6203283a2ec27e0200d1db6779d038ce05603"

# Base URL
BASE_URL = "https://challenge.equiply.io/api/v1/c1"

# Headers
headers = {
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def get_all_stars():
    """Fetches all stars from all available pages"""
    all_stars = []
    page = 1
    
    print("Fetching stars...")
    
    while True:
        url = f"{BASE_URL}/resources-stars?page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error on page {page}: {response.status_code}")
            break
        
        stars = response.json()
        
        # If no stars returned, we've reached the end
        if not stars:
            print(f"No more stars after page {page-1}")
            break
        
        all_stars.extend(stars)
        print(f"Page {page}: {len(stars)} stars fetched")
        page += 1
    
    return all_stars

def calculate_average_resonance(stars):
    """Calculates the average resonance of all stars"""
    if not stars:
        return 0
    
    total_resonance = sum(star['resonance'] for star in stars)
    average = total_resonance / len(stars)
    
    return average

def submit_solution(average):
    """Submits the solution to the server"""
    url = f"{BASE_URL}/solution"
    
    payload = {
        "answer": average
    }
    
    print(f"\nSubmitting solution: {average}")
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response

# Main execution
if __name__ == "__main__":
    # Step 1: Fetch all stars
    stars = get_all_stars()
    print(f"\nTotal stars fetched: {len(stars)}")
    
    # Step 2: Calculate average resonance
    average_resonance = calculate_average_resonance(stars)
    print(f"Average resonance: {average_resonance}")
    
    # Step 3: Submit solution
    result = submit_solution(average_resonance)