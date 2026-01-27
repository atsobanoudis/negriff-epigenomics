import csv
import json
import subprocess
import sys

def install_biopython():
    """Installs the biopython package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "biopython"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing biopython: {e}")
        sys.exit(1)

try:
    from Bio import Entrez
except ImportError:
    print("biopython is not installed. Installing...")
    install_biopython()
    from Bio import Entrez


def fetch_abstracts_batch(pmids, email):
    """Fetches abstracts for a list of PMIDs from PubMed in batch."""
    Entrez.email = email
    pmids_str = ",".join(pmids)
    results = {}
    try:
        handle = Entrez.efetch(db="pubmed", id=pmids_str, rettype="abstract", retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        
        if "PubmedArticle" in records:
            for article in records["PubmedArticle"]:
                pmid = str(article["MedlineCitation"].get("PMID", ""))
                if "MedlineCitation" in article and "Article" in article["MedlineCitation"]:
                    if "Abstract" in article["MedlineCitation"].get("Article", {}):
                        abstract_data = article["MedlineCitation"].get("Article", {}).get("Abstract", {}).get("AbstractText", "")
                        # Join list elements if structured abstract, otherwise return string
                        if isinstance(abstract_data, list):
                            results[pmid] = " ".join([str(x) for x in abstract_data])
                        else:
                            results[pmid] = str(abstract_data)
    except Exception as e:
        print(f"Error fetching abstracts batch: {e}")
    return results

def run_gemini_prompt(abstract):
    """Runs a Gemini prompt with the given abstract."""
    query = (
        "You are an biomedical researcher evaluating if a paper is about EWAS on child maltreatment, adversity, or abuse (e.g., ACEs). "
        "Based on the provided abstract, determine if the study meets the criteria of being an EWAS study on this topic. "
        "The output should be a JSON object with the following fields: "
        '"meets_criteria" (Y/N), "exposure_bucket" (direct, intergenerational, or non-exposure), ' 
        '"non_exposure_bucket" (methodological or irrelevant, if applicable), and "explanation" ' 
        "(a terse, minimum-word, incomplete-sentence explanation for non-exposure, if applicable). "
        "Here is the abstract to analyze:\n\n"
        f"{abstract}"
    )
    
    command = ["gemini", query, "-m", "gemini-2.5-pro"]
    print(f"Executing Gemini command: {' '.join(command)}") # Debug print
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Gemini stdout: {result.stdout}") # Debug print
        print(f"Gemini stderr: {result.stderr}") # Debug print
        # Clean the output from markdown formatting
        cleaned_stdout = result.stdout.strip()
        if cleaned_stdout.startswith("```json") and cleaned_stdout.endswith("```"):
            cleaned_stdout = cleaned_stdout[len("```json"):-len("```")].strip()
        
        return json.loads(cleaned_stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error running Gemini prompt: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            print(f"Stderr: {e.stderr}")
        return None


def main():
    """Main function to process the CSV file."""
    input_csv_path = "02_lit-search/csv-EWASTitleA-set.csv"
    output_csv_path = "02_lit-search/csv-EWASTitleA-set_processed.csv"
    email = "alex.tsobanoudis@kp.org"

    # Step 1: Read CSV and identify PMIDs to fetch
    rows = []
    pmids_to_fetch = []
    with open(input_csv_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            pmid = row.get("PMID")
            if not row.get("Abstract") and pmid:
                pmids_to_fetch.append(pmid)
            rows.append(row)
    
    if not rows:
        print("No data to process.")
        return

    # Step 1.5: Batch fetch abstracts
    fetched_abstracts = {}
    if pmids_to_fetch:
        print(f"Fetching {len(pmids_to_fetch)} abstracts in batches of 100...")
        batch_size = 100
        for i in range(0, len(pmids_to_fetch), batch_size):
            batch = pmids_to_fetch[i:i + batch_size]
            print(f"Fetching batch {i // batch_size + 1} ({len(batch)} PMIDs)...")
            batch_results = fetch_abstracts_batch(batch, email)
            fetched_abstracts.update(batch_results)

    # Update rows with fetched abstracts
    for row in rows:
        pmid = row.get("PMID")
        if pmid in fetched_abstracts:
            row["Abstract"] = fetched_abstracts[pmid]

    # Save intermediate CSV with abstracts
    with open("02_lit-search/csv-EWASTitleA-set_with_abstracts.csv", "w", newline="", encoding="utf-8-sig") as midfile:
        writer = csv.DictWriter(midfile, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    print("Saved intermediate file with abstracts to 02_lit-search/csv-EWASTitleA-set_with_abstracts.csv")

    # Step 2: Process rows with 'Y' and run Gemini
    updated_rows = []
    
    # Define the new Gemini headers
    gemini_headers = [
        "gemini_criteria_met (Y/N)",
        "gemini_exposure_bucket",
        "gemini_non_exposure_bucket",
        "gemini_explanation",
    ]

    # Get original headers safely, in case rows is empty
    first_row_keys = []
    if rows:
        first_row_keys = list(rows[0].keys())

    new_headers = first_row_keys + gemini_headers
    
    # Initialize new columns for all rows to prevent KeyError if not all rows are processed by Gemini
    for row in rows:
        for header in gemini_headers:
            row.setdefault(header, "")

    for row in rows:
        # Check if "Abstract" key exists before accessing it
        if row.get("criteria_met (Y/N)") == "Y" and row.get("Abstract"):
            print(f"Processing row with PMID: {row.get('PMID', 'N/A')}")
            gemini_output = run_gemini_prompt(row["Abstract"])
            if gemini_output:
                row["gemini_criteria_met (Y/N)"] = gemini_output.get("meets_criteria", "")
                row["gemini_exposure_bucket"] = gemini_output.get("exposure_bucket", "")
                row["gemini_non_exposure_bucket"] = gemini_output.get("non_exposure_bucket", "")
                row["gemini_explanation"] = gemini_output.get("explanation", "")
        updated_rows.append(row)

    print(f"new_headers: {new_headers}") # Debug print
    print(f"Length of updated_rows: {len(updated_rows)}") # Debug print
    if updated_rows:
        print(f"Sample updated_row[0]: {updated_rows[0]}") # Debug print

    # Step 3: Write the final processed CSV
    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_headers)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Processing complete. The output is saved in {output_csv_path}")

if __name__ == "__main__":
    main()