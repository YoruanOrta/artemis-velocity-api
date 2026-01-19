import requests
import base64
import json
from collections import defaultdict

# API Configuration
API_KEY = "ec_280150d06e6a66c3a4e620c478b6203283a2ec27e0200d1db6779d038ce05603"
EQUIPLY_BASE_URL = "https://challenge.equiply.io/api/v1/c2"
SWAPI_BASE_URL = "https://swapi.info/api"

equiply_headers = {
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def get_all_swapi_people():
    """Fetch all people from SWAPI"""
    print("Fetching all Star Wars characters from SWAPI...")
    all_people = []
    url = f"{SWAPI_BASE_URL}/people"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching from SWAPI: {response.status_code}")
        return []
    
    data = response.json()
    
    # SWAPI.info returns a list directly
    if isinstance(data, list):
        all_people = data
    # Or it might be paginated with 'results'
    elif isinstance(data, dict):
        all_people.extend(data.get('results', []))
        # Handle pagination if needed
        next_url = data.get('next')
        while next_url:
            response = requests.get(next_url)
            if response.status_code == 200:
                data = response.json()
                all_people.extend(data.get('results', []))
                next_url = data.get('next')
            else:
                break
    
    print(f"\nTotal characters from SWAPI: {len(all_people)}")
    return all_people

def get_planet_name(homeworld_url):
    """Get planet name from SWAPI homeworld URL"""
    if not homeworld_url:
        return "Unknown"
    
    try:
        response = requests.get(homeworld_url)
        if response.status_code == 200:
            return response.json().get('name', 'Unknown')
    except:
        pass
    return "Unknown"

def query_equiply_oracle(character_name):
    """Query Equiply oracle about a character"""
    url = f"{EQUIPLY_BASE_URL}/resources-oracle-rolodex"
    params = {"name": character_name}
    
    try:
        response = requests.get(url, headers=equiply_headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def decode_oracle_notes(oracle_notes):
    """Decode Base64 oracle notes"""
    try:
        decoded = base64.b64decode(oracle_notes).decode('utf-8')
        return decoded
    except Exception as e:
        return None

def classify_character(oracle_response):
    """Determine if character belongs to Light Side or Dark Side"""
    if not oracle_response or 'oracle_notes' not in oracle_response:
        return None
    
    decoded = decode_oracle_notes(oracle_response['oracle_notes'])
    if not decoded:
        return None
    
    # Priority: Look for "belongs to" phrase first
    if "belongs to the Light Side" in decoded:
        return "Light"
    elif "belongs to the Dark Side" in decoded:
        return "Dark"
    # Fallback: Check for general keywords
    elif "Light Side" in decoded and "Dark Side" not in decoded:
        return "Light"
    elif "Dark Side" in decoded:
        return "Dark"
    elif "Jedi" in decoded and "Sith" not in decoded:
        return "Light"
    elif "Sith" in decoded:
        return "Dark"
    else:
        return "Unknown"

def analyze_all_characters():
    """Analyze all SWAPI characters with Equiply oracle"""
    # Get all people from SWAPI
    swapi_people = get_all_swapi_people()
    
    # Group by planet
    planet_characters = defaultdict(list)
    
    print("\nGrouping characters by planet...")
    for person in swapi_people:
        name = person.get('name')
        homeworld_url = person.get('homeworld')
        
        if name and homeworld_url:
            planet_name = get_planet_name(homeworld_url)
            planet_characters[planet_name].append(name)
    
    print(f"\nFound {len(planet_characters)} planets")
    
    # Query oracle for each character and calculate FBI
    planet_results = {}
    
    for planet, characters in planet_characters.items():
        if planet == "Unknown":
            continue
            
        print(f"\n{'='*60}")
        print(f"Analyzing planet: {planet}")
        print(f"Characters from SWAPI: {len(characters)}")
        print('-'*60)
        
        light_count = 0
        dark_count = 0
        total_count = 0
        character_data = []
        
        for character in characters:
            print(f"  Querying: {character}...", end=" ")
            oracle_response = query_equiply_oracle(character)
            
            if oracle_response:
                side = classify_character(oracle_response)
                if side == "Light":
                    light_count += 1
                    total_count += 1
                    print(f"✓ Light Side")
                    character_data.append({"name": character, "side": "Light"})
                elif side == "Dark":
                    dark_count += 1
                    total_count += 1
                    print(f"✗ Dark Side")
                    character_data.append({"name": character, "side": "Dark"})
                else:
                    print(f"? Unknown")
            else:
                print(f"✗ Not found in oracle")
        
        if total_count > 0:
            fbi = (light_count - dark_count) / total_count
            
            print(f"\nResults for {planet}:")
            print(f"  Light Side: {light_count}")
            print(f"  Dark Side: {dark_count}")
            print(f"  Total: {total_count}")
            print(f"  FBI: {fbi:.4f}")
            
            planet_results[planet] = {
                "planet": planet,
                "light_side": light_count,
                "dark_side": dark_count,
                "total": total_count,
                "fbi": fbi,
                "characters": character_data
            }
    
    return planet_results

def find_balanced_planet(planet_results):
    """Find the planet where the Force is in balance (FBI = 0)"""
    print("\n" + "="*60)
    print("FINAL RESULTS - ALL PLANETS")
    print("="*60)
    
    # Sort by FBI
    sorted_results = sorted(planet_results.values(), key=lambda x: x['fbi'])
    
    for result in sorted_results:
        print(f"{result['planet']}: FBI = {result['fbi']:.4f} (L:{result['light_side']}, D:{result['dark_side']}, T:{result['total']})")
    
    # Find planet(s) with FBI = 0
    balanced_planets = [r for r in planet_results.values() if r['fbi'] == 0.0]
    
    print("\n" + "="*60)
    if balanced_planets:
        for planet in balanced_planets:
            print(f"Planet with Force in Balance: {planet['planet']}")
            print(f"FBI: {planet['fbi']:.4f}")
            print(f"Light Side: {planet['light_side']}, Dark Side: {planet['dark_side']}")
            print("="*60)
        return balanced_planets[0]['planet']
    else:
        # Return closest to 0
        closest = min(planet_results.values(), key=lambda x: abs(x['fbi']))
        print(f"No perfect balance found. Closest: {closest['planet']} with FBI = {closest['fbi']:.4f}")
        print("="*60)
        return closest['planet']

def submit_solution(planet_name):
    """Submit the solution"""
    url = f"{EQUIPLY_BASE_URL}/solution"
    payload = {"answer": planet_name}
    
    print(f"\nSubmitting solution: {planet_name}")
    response = requests.post(url, headers=equiply_headers, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response

# Main execution
if __name__ == "__main__":
    print("="*60)
    print("EQUIPLY CHALLENGE C2 - SWAPI INTEGRATION")
    print("Finding the planet where the Force is in balance...")
    print("="*60)
    
    # Analyze all characters
    planet_results = analyze_all_characters()
    
    # Find balanced planet
    balanced_planet = find_balanced_planet(planet_results)
    
    # Submit solution
    result = submit_solution(balanced_planet)