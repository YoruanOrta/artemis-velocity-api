import json
import re
import requests

API_KEY = "ec_280150d06e6a66c3a4e620c478b6203283a2ec27e0200d1db6779d038ce05603"
BASE_URL = "https://challenge.equiply.io/api/v1/c8"

headers = {
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def extract_year_from_data(item):
    """Extract manufacturing year using multiple methods"""
    serial = str(item.get('serial_number', ''))
    model = str(item.get('model', ''))
    manufacturer = item.get('manufacturer', '')
    
    # Method 1: Year directly in MODEL number
    match = re.search(r'(19\d{2}|20\d{2})', model)
    if match:
        year = int(match.group(1))
        if 1990 <= year <= 2089:
            return year
    
    # Method 2: Serial starts with YYYY (Philips 747, Stryker, etc.)
    if len(serial) >= 4 and serial[:4].isdigit():
        potential_year = int(serial[:4])
        if 1990 <= potential_year <= 2089:
            return potential_year
    
    # Method 3: Serial format like "SPW12190318PA" or "AF12G431610" 
    # Year encoded as 2-digit in positions 3-4 or 4-5
    match = re.match(r'[A-Z]{2,3}(\d{2})', serial)
    if match:
        two_digit_year = int(match.group(1))
        # Convert 2-digit to 4-digit (assume 20xx for 00-89, 19xx for 90-99)
        if 0 <= two_digit_year <= 89:
            year = 2000 + two_digit_year
        else:
            year = 1900 + two_digit_year
        if 1990 <= year <= 2089:
            return year
    
    # Method 4: Serial starts with 2-digit year like "201107378" (20-11-07378)
    if len(serial) >= 8 and serial[:2].isdigit():
        two_digit_year = int(serial[:2])
        if two_digit_year >= 90:
            year = 1900 + two_digit_year
        else:
            year = 2000 + two_digit_year
        if 1990 <= year <= 2089:
            return year
    
    # Method 5: Look for embedded 4-digit year anywhere
    match = re.search(r'(19\d{2}|20\d{2})', serial)
    if match:
        year = int(match.group(1))
        if 1990 <= year <= 2089:
            return year
    
    # Method 6: Manufacturer-specific patterns
    if manufacturer in ['GE Healthcare', 'GE HEALTHCARE']:
        # GE serials like "RT915093079GA" or "SEW10354778HA"
        # Try extracting 2-digit year after prefix
        match = re.match(r'[A-Z]{2,3}(\d{2})', serial)
        if match:
            two_digit = int(match.group(1))
            year = 2000 + two_digit if two_digit < 90 else 1900 + two_digit
            if 1990 <= year <= 2089:
                return year
    
    return None

def process_equipment_data():
    """Load and process equipment data"""
    print("="*70)
    print("EQUIPMENT ARCHAEOLOGY - Enhanced Year Detection")
    print("="*70)
    
    with open('equipment_data.json', 'r') as f:
        data = json.load(f)
    
    inventory = data['equipment']
    total_equipment = len(inventory)
    
    print(f"\nTotal equipment items: {total_equipment}")
    
    enhanced_inventory = []
    years_found = 0
    year_distribution = {}
    
    for item in inventory:
        year = extract_year_from_data(item)
        
        # Include ALL original fields PLUS manufacture_year
        enhanced_item = {
            "id": item['id'],
            "equipment_name": item['equipment_name'],
            "manufacturer": item['manufacturer'],
            "model": item['model'],
            "serial_number": str(item['serial_number']),
            "manufacture_year": year  # ← "manufacture_year" not "manufacturing_year"
        }
        
        enhanced_inventory.append(enhanced_item)
        
        if year:
            years_found += 1
            year_distribution[year] = year_distribution.get(year, 0) + 1
    
    # Statistics
    print(f"\nYears successfully identified: {years_found}/{total_equipment}")
    print(f"Success rate: {(years_found/total_equipment)*100:.1f}%")
    
    # Year distribution
    print("\nYear distribution:")
    print("-" * 70)
    for year in sorted(year_distribution.keys()):
        count = year_distribution[year]
        bar = "█" * min(50, count)
        print(f"  {year}: {count:3d} {bar}")
    
    # Sample results
    print("\nSample extraction results (first 20):")
    print("-" * 70)
    for i in range(min(20, len(enhanced_inventory))):
        item = inventory[i]
        enhanced = enhanced_inventory[i]
        year = enhanced['manufacture_year']
        status = "✓" if year else "✗"
        print(f"{status} ID {item['id']:3d}: Model {item['model']:20s} Serial {str(item['serial_number']):20s} → {year}")
    
    return enhanced_inventory, years_found, total_equipment

def submit_solution(enhanced_inventory):
    """Submit the enhanced inventory"""
    print("\n" + "="*70)
    print("SUBMITTING SOLUTION")
    print("="*70)
    
    payload = {"equipment": enhanced_inventory}
    
    with open('solution_payload.json', 'w') as f:
        json.dump(payload, f, indent=2)
    
    print(f"\nPayload saved to 'solution_payload.json'")
    print(f"Total records: {len(enhanced_inventory)}")
    
    response = input("\nType 'yes' to submit: ")
    
    if response.lower() == 'yes':
        print("\nSubmitting...")
        api_response = requests.post(
            f"{BASE_URL}/solution",
            headers=headers,
            json=payload
        )
        
        print(f"Status: {api_response.status_code}")
        result = api_response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print("\nCancelled.")
        return None

if __name__ == "__main__":
    enhanced_inventory, years_found, total = process_equipment_data()
    
    success_rate = (years_found / total) * 100
    
    print("\n" + "="*70)
    print("ASSESSMENT")
    print("="*70)
    
    if success_rate >= 50:
        print(f"✅ Success rate: {success_rate:.1f}% (≥50% required)")
        print("\nQualified for points!")
        submit_solution(enhanced_inventory)
    else:
        print(f"❌ Success rate: {success_rate:.1f}% (<50%)")
        print("\nNeed better detection. Saving payload for review...")
        
        payload = {"equipment": enhanced_inventory}
        with open('solution_payload.json', 'w') as f:
            json.dump(payload, f, indent=2)