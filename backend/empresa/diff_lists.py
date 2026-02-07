import re
from decimal import Decimal

def parse_dre(filename):
    items = []
    try:
        with open(filename, 'r', encoding='utf-16') as f:
            for line in f:
                match = re.search(r'Valor:\s*([\d\.]+)', line)
                if match:
                    items.append(Decimal(match.group(1)))
    except UnicodeError:
        # Fallback to default if not utf-16
        with open(filename, 'r') as f:
            for line in f:
                match = re.search(r'Valor:\s*([\d\.]+)', line)
                if match:
                    items.append(Decimal(match.group(1)))
    return items

def parse_receipts(filename):
    items = []
    try:
        with open(filename, 'r', encoding='utf-16') as f:
            for line in f:
                match = re.search(r'Val:\s*([\d\.]+)', line)
                if match:
                    items.append(Decimal(match.group(1)))
    except UnicodeError:
        with open(filename, 'r') as f:
            for line in f:
                match = re.search(r'Val:\s*([\d\.]+)', line)
                if match:
                    items.append(Decimal(match.group(1)))
    return items

def main():
    dre_items = parse_dre('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa\\dre_values.txt')
    receipt_items = parse_receipts('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa\\receipt_values.txt')
    
    dre_items.sort()
    receipt_items.sort()
    
    start_dre_total = sum(dre_items)
    start_receipt_total = sum(receipt_items)
    
    print(f"DRE Total Loaded: {start_dre_total}")
    print(f"Receipt Total Loaded: {start_receipt_total}")
    print(f"Target Diff: {start_dre_total - start_receipt_total}")
    
    # Simple matching: remove match from receipt if found in dre
    unmatched_dre = []
    receipt_copy = list(receipt_items)
    
    for val in dre_items:
        try:
            receipt_copy.remove(val)
        except ValueError:
            unmatched_dre.append(val)
            
    # Remaining in receipt copy are extra receipts? (Should be none ideally if DRE is encompassing)
    
    print("\n--- Unmatched in DRE (Invoiced but not Received in Jan) ---")
    total_unmatched = Decimal(0)
    for val in unmatched_dre:
        print(val)
        total_unmatched += val
        
    print(f"\nTotal Unmatched: {total_unmatched}")
    
    print("\n--- Unmatched in Receipts (Received but not Invoiced in Jan?) ---")
    for val in receipt_copy:
        print(val)

if __name__ == "__main__":
    main()
