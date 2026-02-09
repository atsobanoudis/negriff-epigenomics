import csv
import subprocess
import sys
import re
import html

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


def clean_text(text):
    """Cleans text by removing HTML tags and unescaping entities."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    text = html.unescape(text)
    # Normalize whitespace
    text = " ".join(text.split())
    return text


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
                            raw_text = " ".join([str(x) for x in abstract_data])
                        else:
                            raw_text = str(abstract_data)
                        results[pmid] = clean_text(raw_text)
    except Exception as e:
        print(f"Error fetching abstracts batch: {e}")
    return results


def main():
    """Main function to process the CSV file."""
    input_csv_path = "03_lit-search/csv-EWASTitleA-set.csv"
    # Output path for the file with abstracts
    output_csv_path = "03_lit-search/csv-EWASTitleA-set_with_abstracts.csv"
    email = "alex.tsobanoudis@kp.org"

    # Step 1: Read CSV and identify PMIDs to fetch
    rows = []
    pmids_to_fetch = []
    
    # Check if input file exists
    try:
        with open(input_csv_path, "r", newline="", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                pmid = row.get("PMID")
                if not row.get("Abstract") and pmid:
                    pmids_to_fetch.append(pmid)
                rows.append(row)
    except FileNotFoundError:
        print(f"Error: Input file '{input_csv_path}' not found.")
        return
    
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

    # Save CSV with abstracts
    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as midfile:
        writer = csv.DictWriter(midfile, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved file with abstracts to {output_csv_path}")

if __name__ == "__main__":
    main()
