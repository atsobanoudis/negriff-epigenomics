import csv

def main():
    csv_file = 'ewas-59-screen.csv'
    identification = 0
    screening_included = 0
    screening_excluded = 0
    excluded_reason = {}
    
    full_text_differentiated = {
        'Open Access': 0,
        'Institutional': 0,
        'Subscription': 0
    }
    
    final_included = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            identification += 1
            screen = row.get('Screen', '').strip().upper()
            category = row.get('Category', '').strip()
            full_text = row.get('Full Text', '').strip()
            explanation = row.get('Explanation', '').strip()
            
            if screen == 'Y':
                # Further check full text availability
                if full_text in full_text_differentiated:
                    full_text_differentiated[full_text] += 1
                else:
                    full_text_differentiated['Subscription'] += 1 # Default or unknown
                
                if full_text != 'Subscription':
                    screening_included += 1
                    final_included += 1
                else:
                    screening_excluded += 1
                    reason = "Subscription-based (could not read)"
                    excluded_reason[reason] = excluded_reason.get(reason, 0) + 1
            else:
                screening_excluded += 1
                reason = category if category else "Other"
                excluded_reason[reason] = excluded_reason.get(reason, 0) + 1
                
    print(f"Identification (Records identified): {identification}")
    print(f"Screening (Total records): {identification}")
    print(f"Excluded: {screening_excluded}")
    for reason, count in excluded_reason.items():
        print(f"  - {reason}: {count}")
    print(f"Eligibility (Full-text articles assessed): {screening_included + full_text_differentiated.get('Subscription', 0)}")
    print(f"Final Included: {final_included}")
    print(f"Full Text Breakdown:")
    for ft, count in full_text_differentiated.items():
        print(f"  - {ft}: {count}")

if __name__ == "__main__":
    main()
