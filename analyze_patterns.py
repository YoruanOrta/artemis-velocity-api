import json

def analyze_correct_vs_incorrect():
    """Analizar qué detectamos bien vs mal"""
    
    with open('equipment_data.json', 'r') as f:
        data = json.load(f)
    
    inventory = data['equipment']
    
    print("="*70)
    print("ANALYZING PATTERNS - What did we get RIGHT?")
    print("="*70)
    
    # Mostrar ejemplos de cada manufacturer
    by_mfr = {}
    for item in inventory[:100]:  # Primeros 100 para muestra
        mfr = item['manufacturer']
        if mfr not in by_mfr:
            by_mfr[mfr] = []
        by_mfr[mfr].append(item)
    
    for mfr, items in by_mfr.items():
        print(f"\n{mfr}:")
        print("-" * 70)
        for item in items[:5]:
            print(f"  Model: {item['model']:20s} Serial: {item['serial_number']}")
    
    # Analizar Stryker específicamente
    print("\n" + "="*70)
    print("STRYKER SERIAL ANALYSIS")
    print("="*70)
    
    stryker_items = [item for item in inventory if 'stryker' in item['manufacturer'].lower()]
    
    print(f"\nTotal Stryker items: {len(stryker_items)}")
    print("\nStryker serials and models:")
    print("-" * 70)
    
    for item in stryker_items[:20]:
        serial = str(item['serial_number'])
        model = item['model']
        print(f"Model {model:10s} | Serial: {serial:15s} | First 4: {serial[:4] if len(serial) >= 4 else 'N/A'}")
    
    # Buscar patrones en seriales que comienzan con números
    print("\n" + "="*70)
    print("SERIAL PATTERNS - First characters analysis")
    print("="*70)
    
    numeric_start = []
    alpha_start = []
    
    for item in inventory[:200]:
        serial = str(item['serial_number'])
        if serial and serial[0].isdigit():
            numeric_start.append((item['manufacturer'], item['model'], serial))
        elif serial and serial[0].isalpha():
            alpha_start.append((item['manufacturer'], item['model'], serial))
    
    print(f"\nSerials starting with NUMBERS: {len(numeric_start)}")
    for mfr, model, serial in numeric_start[:15]:
        print(f"  {mfr:20s} | Model: {model:15s} | Serial: {serial}")
    
    print(f"\nSerials starting with LETTERS: {len(alpha_start)}")
    for mfr, model, serial in alpha_start[:15]:
        print(f"  {mfr:20s} | Model: {model:15s} | Serial: {serial}")

if __name__ == "__main__":
    analyze_correct_vs_incorrect()