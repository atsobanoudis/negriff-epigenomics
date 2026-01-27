import csv
import json
import subprocess
import re

def run_gemini_prompt(abstract):
    """Runs gemini command with the abstract."""
    
    # Build the prompt
    prompt = f"""RESPOND ONLY WITH JSON. You are a biomedical researcher, screen this abstract:

Criteria:
- EWAS on child maltreatment/adversity and DNA methylation = "Y"
- Anything else = "N"

Categories: Included, Not EWAS, Wrong Exposure, Wrong Outcome, Review/Meta-analysis, Animal/In Vitro, Methodological, Irrelevant

JSON format:
{{"meets_criteria": "Y or N", "explanation": "brief reason", "category": "one category"}}

Abstract: {abstract}"""
    
    # Show what we're sending
    print("\n" + "="*80)
    print("SENDING TO GEMINI:")
    print("="*80)
    print(prompt)
    print("="*80)
    
    # Build command
    cmd = f'gemini "{prompt}" -m gemini-2.5-pro'
    
    print("\nCOMMAND:")
    print(cmd)
    print("="*80)
    
    # Run it
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    
    print("\nGEMINI OUTPUT:")
    print("="*80)
    print(result.stdout)
    print("="*80)
    
    if result.stderr:
        print("\nERRORS:")
        print(result.stderr)
    
    # Try to extract JSON
    # Look for ```json blocks first
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result.stdout, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Try raw JSON
        match = re.search(r'\{.*?\}', result.stdout, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            print("\n❌ NO JSON FOUND")
            return None
    
    try:
        data = json.loads(json_str)
        print("\n✓ PARSED JSON:")
        print(json.dumps(data, indent=2))
        return data
    except:
        print(f"\n❌ FAILED TO PARSE: {json_str}")
        return None


def main():
    input_csv = "02_lit-search/csv-EWASTitleA-set_with_abstracts.csv"
    output_csv = "02_lit-search/csv-EWASTitleA-set_processed.csv"
    
    with open(input_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"\nFound {len(rows)} rows\n")
    
    for i, row in enumerate(rows, 1):
        print(f"\n{'#'*80}")
        print(f"ROW {i}/{len(rows)} - PMID: {row.get('PMID', 'N/A')}")
        print(f"{'#'*80}")
        
        if not row.get("Abstract"):
            print("⚠ No abstract, skipping")
            row["gemini_criteria_met (Y/N)"] = ""
            row["gemini_explanation"] = ""
            row["gemini_category"] = ""
            continue
        
        result = run_gemini_prompt(row["Abstract"])
        
        if result:
            row["gemini_criteria_met (Y/N)"] = result.get("meets_criteria", "")
            row["gemini_explanation"] = result.get("explanation", "")
            row["gemini_category"] = result.get("category", "")
        else:
            row["gemini_criteria_met (Y/N)"] = "ERROR"
            row["gemini_explanation"] = "Failed to parse"
            row["gemini_category"] = "ERROR"
    
    # Write output
    headers = list(rows[0].keys())
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Done. Saved to {output_csv}")

if __name__ == "__main__":
    main()