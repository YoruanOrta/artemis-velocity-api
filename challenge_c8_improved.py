import json
import re
import requests

API_KEY = "ec_280150d06e6a66c3a4e620c478b6203283a2ec27e0200d1db6779d038ce05603"
BASE_URL = "https://challenge.equiply.io/api/v1/c8"

headers = {
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def extract_year_welch_allyn(serial):
    """Welch Allyn: Format YY-MM-XXXXX where YY is 2-digit year"""
    serial = str(serial)
    if len(serial) >= 4 and serial[:4].isdigit():
        # First 2 digits = year, next 2 = month
        yy = int(serial[:2])
        mm = int(serial[2:4])
        
        # Validate month (01-12)
        if 1 <= mm <= 12:
            # Convert 2-digit to 4-digit year
            year = 2000 + yy if yy < 90 else 1900 + yy
            if 1990 <= year <= 2089:
                return year
    return None

def extract_year_stryker_747(serial):
    """Stryker 747: Format YYYY-MM-XXX"""
    serial = str(serial)
    if len(serial) >= 4 and serial[:4].isdigit():
        year = int(serial[:4])
        if 1990 <= year <= 2089:
            return year
    return None

def extract_year_from_model(model):
    """Extract year from model number"""
    match = re.search(r'(19\d{2}|20\d{2})', str(model))
    if match:
        year = int(match.group(1))
        if 1990 <= year <= 2089:
            return year
    return None

def extract_year_ge_healthcare(item):
    """GE Healthcare: Year in model number"""
    # Try model first
    year = extract_year_from_model(item['model'])
    if year:
        return year
    
    # GE serials like "RT915093079GA" or "SEW10354778HA"
    serial = str(item['serial_number'])
    
    # Pattern: [A-Z]{2,3} + YY + rest
    match = re.match(r'[A-Z]{2,3}(\d{2})', serial)
    if match:
        yy = int(match.group(1))
        year = 2000 + yy if yy < 90 else 1900 + yy
        if 1990 <= year <= 2089:
            return year
    
    return None

def extract_year_from_data(item):
    """Extract year using manufacturer-specific logic"""
    manufacturer = item.get('manufacturer', '').lower()
    serial = str(item.get('serial_number', ''))
    model = str(item.get('model', ''))
    
    # Priority 1: Check model for year (works for GE and others)
    year = extract_year_from_model(model)
    if year:
        return year
    
    # Priority 2: Manufacturer-specific patterns
    if 'welch allyn' in manufacturer:
        year = extract_year_welch_allyn(serial)
        if year:
            return year
    
    elif 'stryker' in manufacturer:
        # Stryker 747 and similar models
        if model in ['747', '1105']:
            year = extract_year_stryker_747(serial)
            if year:
                return year
    
    elif 'ge' in manufacturer or 'ge healthcare' in manufacturer:
        year = extract_year_ge_healthcare(item)
        if year:
            return year
    
    # Priority 3: Generic patterns
    # Try YYYY at start
    if len(serial) >= 4 and serial[:4].isdigit():
        potential_year = int(serial[:4])
        if 2000 <= potential_year <= 2089:
            return potential_year
    
    # Try YY-MM format (2 digit year + month validation)
    if len(serial) >= 4 and serial[:4].isdigit():
        yy = int(serial[:2])
        mm = int(serial[2:4])
        if 1 <= mm <= 12:
            year = 2000 + yy if yy < 50 else 1900 + yy
            if 1990 <= year <= 2030:
                return year
    
    # Try embedded YYYY
    match = re.search(r'(20\d{2})', serial)
    if match:
        year = int(match.group(1))
        if 2000 <= year <= 2089:
            return year
    
    # Try letter prefix + YY pattern
    match = re.match(r'[A-Z]{2,3}(\d{2})', serial)
    if match:
        yy = int(match.group(1))
        year = 2000 + yy if yy < 90 else 1900 + yy
        if 1990 <= year <= 2089:
            return year
    
    return None

def process_equipment_data():
    """Process with improved logic"""
    print("="*70)
    print("IMPROVED EQUIPMENT ARCHAEOLOGY")
    print("="*70)
    
    with open('equipment_data.json', 'r') as f:
        data = json.load(f)
    
    inventory = data['equipment']
    total = len(inventory)
    
    enhanced_inventory = []
    years_found = 0
    
    for item in inventory:
        year = extract_year_from_data(item)
        
        enhanced_item = {
            "id": item['id'],
            "equipment_name": item['equipment_name'],
            "manufacturer": item['manufacturer'],
            "model": item['model'],
            "serial_number": str(item['serial_number']),
            "manufacture_year": year
        }
        
        enhanced_inventory.append(enhanced_item)
        
        if year:
            years_found += 1
    
    print(f"\nYears found: {years_found}/{total} ({(years_found/total)*100:.1f}%)")
    
    # Show samples
    print("\nSample results by manufacturer:")
    print("-" * 70)
    
    for mfr in ['Welch Allyn', 'Stryker', 'GE Healthcare']:
        items = [item for item in enhanced_inventory if mfr.lower() in item['manufacturer'].lower()][:5]
        if items:
            print(f"\n{mfr}:")
            for item in items:
                print(f"  {item['model']:15s} | {item['serial_number']:15s} → {item['manufacture_year']}")
    
    return enhanced_inventory, years_found, total

def submit_solution(enhanced_inventory):
    """Submit solution"""
    payload = {"equipment": enhanced_inventory}
    
    with open('solution_payload.json', 'w') as f:
        json.dump(payload, f, indent=2)
    
    print("\n" + "="*70)
    print("SUBMITTING")
    print("="*70)
    print(f"Records: {len(enhanced_inventory)}")
    
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
    
    return None

if __name__ == "__main__":
    enhanced_inventory, years_found, total = process_equipment_data()
    
    success_rate = (years_found / total) * 100
    print(f"\n{'='*70}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 50:
        print("✅ Qualified!")
        submit_solution(enhanced_inventory)
    else:
        print("❌ Below 50%")