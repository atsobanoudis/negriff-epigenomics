import csv
import json
import subprocess
import sys
import os
import re

def run_gemini_prompt(abstract):
    """Runs a Gemini prompt with the given abstract."""
    query = (
        "You are a biomedical researcher performing a systematic review. Your goal is to screen abstracts to identify Epigenome-Wide Association Studies (EWAS) investigating the effects of child maltreatment, adversity, or abuse (e.g., ACEs) on DNA methylation.\n\n" 
        "Evaluate the provided abstract and determine if it meets the inclusion criteria.\n\n" 
        "Output a JSON object with exactly these keys:\n" 
        "1. \"meets_criteria\": \"Y\" if it is an EWAS on child maltreatment/adversity, otherwise \"N\".\n" 
        "2. \"explanation\": A terse, concise explanation (incomplete sentence ok) justifying your decision.\n" 
        "3. \"category\": Classify the study into ONE of the following exclusive buckets to help populate a PRISMA flow chart:\n" 
        "   - \"Included\": Meets all criteria (EWAS + Child Maltreatment/Adversity).\n" 
        "   - \"Not EWAS\": Focuses on candidate genes, GWAS, or other non-epigenome-wide methods.\n" 
        "   - \"Wrong Exposure\": EWAS but not on child maltreatment, adversity, or abuse (e.g., smoking, diet, other stress).\n" 
        "   - \"Wrong Outcome\": Exposure is correct, but outcome is not DNA methylation (or not EWAS).\n" 
        "   - \"Review/Meta-analysis\": Review articles, meta-analyses, or commentaries.\n" 
        "   - \"Animal/In Vitro\": Study on animals or cell lines, not humans.\n" 
        "   - \"Methodological\": Focuses on methods development rather than biological association.\n" 
        "   - \"Irrelevant\": Completely unrelated topic.\n\n" 
        "Here is the abstract to analyze:\n\n" 
        f"{abstract}"
    )
    
    # Platform specific command adjustment
    # We pass the command as a list of arguments which is safer for quoting.
    command = ["gemini", query, "-m", "gemini-2.5-pro"]
    
    try:
        # shell=True on Windows helps locate the command if it's a batch file/script wrapper
        # On Unix, shell=False is usually preferred for list arguments
        use_shell = (sys.platform == "win32")
        
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', shell=use_shell)
        
        # Print raw output for debugging
        print(f"--- Gemini Raw Output ---\n{result.stdout.strip()}\n-------------------------")
        
        # Robust JSON extraction using Regex
        # This handles cases where Gemini adds conversational text or markdown blocks
        json_match = re.search(r"\{{.*\}}", result.stdout, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            print("Error: No JSON object found in Gemini output.")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Error running Gemini prompt: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def main():
    """Main function to process the CSV file with Gemini."""
    input_csv_path = "03_lit-search/csv-EWASTitleA-set_with_abstracts.csv"
    output_csv_path = "03_lit-search/csv-EWASTitleA-set_processed.csv"

    if not os.path.exists(input_csv_path):
        print(f"Error: Input file '{input_csv_path}' not found. Please run process_abstracts.py first.")
        return

    print(f"Reading from {input_csv_path}...")
    
    rows = []
    with open(input_csv_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            rows.append(row)
    
    if not rows:
        print("No data to process.")
        return

    updated_rows = []
    
    # Define the new Gemini headers
    gemini_headers = [
        "gemini_criteria_met (Y/N)",
        "gemini_explanation",
        "gemini_category"
    ]

    # Get original headers
    first_row_keys = list(rows[0].keys())
    
    # Ensure gemini headers are added if not present
    new_headers = [h for h in first_row_keys if h not in gemini_headers] + gemini_headers
    
    # Initialize new columns for all rows
    for row in rows:
        for header in gemini_headers:
            if header not in row:
                row[header] = ""

    print("Starting Gemini processing...")
    total_processed = 0
    
    for i, row in enumerate(rows):
        pmid = row.get("PMID", "N/A")
        
        # Process ALL rows that have an abstract
        if row.get("Abstract"):
            print(f"Processing row {i+1}/{len(rows)} (PMID: {pmid})...")
            gemini_output = run_gemini_prompt(row["Abstract"])
            if gemini_output:
                print(f"  -> Category: {gemini_output.get('category', 'N/A')}")
                print(f"  -> Meets Criteria: {gemini_output.get('meets_criteria', 'N/A')}")
                row["gemini_criteria_met (Y/N)"] = gemini_output.get("meets_criteria", "")
                row["gemini_explanation"] = gemini_output.get("explanation", "")
                row["gemini_category"] = gemini_output.get("category", "")
                total_processed += 1
            else:
                print(f"  -> Failed to get valid Gemini output for PMID {pmid}")
        else:
            print(f"Skipping row {i+1}/{len(rows)} (PMID: {pmid}) - No Abstract")
        
        updated_rows.append(row)

    print(f"Processed {total_processed} abstracts.")

    # Write the final processed CSV
    print(f"Writing results to {output_csv_path}...")
    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_headers)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Processing complete. The output is saved in {output_csv_path}")

if __name__ == "__main__":
    main()
