import csv
import json
import subprocess
import re

def run_gemini_prompt(abstract):
    """Runs gemini command with the abstract."""
    
    # Build the prompt
    prompt = (
        "You are a biomedical researcher performing a systematic review. Your goal is to screen abstracts to identify Epigenome-Wide Association Studies (EWAS) investigating the effects of child maltreatment, adversity, or abuse (e.g., ACEs) on DNA methylation.\n\n" 
        "Evaluate the provided abstract and determine if it meets the inclusion criteria.\n\n" 
        "Output a JSON object with exactly these keys:\n" 
        "1. \"meets_criteria\": \"Y\" if it is an EWAS on child maltreatment/adversity, otherwise \"N\".\n" 
        "2. \"explanation\": must be terse, scientific shorthand/abreviation phrase. no complete sentence; not even a period (e.g., method paper on ...)\n" 
        "3. \"category\": Classify the study into ONE of the following exclusive buckets to help populate a PRISMA flow chart:\n" 
        "   - \"Included\": Meets all criteria (EWAS + Child Maltreatment/Adversity).\n" 
        "   - \"Not EWAS\": Focuses on candidate genes, GWAS, or other non-epigenome-wide methods.\n" 
        "   - \"Wrong Exposure\": EWAS but not on child maltreatment, adversity, or abuse (e.g., smoking, diet, other stress).\n"
        "   - \"Intergenerational\": EWAS but exposure is parent to offspring, not within individual.\n" 
        "   - \"Wrong Outcome\": Exposure is correct, but outcome is not DNA methylation (or not EWAS).\n" 
        "   - \"Review/Meta-analysis\": Review articles, meta-analyses, or commentaries.\n" 
        "   - \"Animal/In Vitro\": Study on animals or cell lines, not humans.\n" 
        "   - \"Methodological\": Focuses on methods development rather than biological association.\n" 
        "   - \"Irrelevant\": Completely unrelated topic.\n\n" 
        "Here is the abstract to analyze:\n\n" 
        f"{abstract}"
    )
#     prompt = f"""RESPOND ONLY WITH JSON. You are a biomedical researcher, screen this abstract:

# Criteria:
# - EWAS on child maltreatment/adversity and DNA methylation; must be within same individual, not paternal/maternal impact = "Y"
# - Anything else = "N"

# Categories: Included, Not EWAS, Wrong Exposure (intergenerational), Wrong Exposure Wrong Outcome, Review/Meta-analysis, Animal/In Vitro, Methodological, Irrelevant

# JSON format:
# {{"meets_criteria": "Y or N", "explanation": "terse, minimally-necessary words, incomplete-sentence brief reason", "category": "one category"}}

# Abstract: {abstract}"""
    
    # Show what we're sending
    print(prompt)
    print("="*80)
    
    # Build command
    cmd = f'gemini "{prompt}" -m gemini-3-pro-preview'
    
    # Run it
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    
    print(result.stdout)
    
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