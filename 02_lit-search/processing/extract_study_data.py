import os
import json
import subprocess
import csv
import re
import sys

# Configuration
MODEL = "gemini-3-flash-preview" 
INPUT_DIR = "pdfs"
OUTPUT_CSV = "master_study_data.csv"
JSON_DIR = "processing/json_store"

# Standardization targets
SAMPLE_TYPES = ["Blood", "Saliva", "Buccal", "Brain", "Cord Blood", "Other"]
PLATFORMS = ["450k", "EPIC", "EPICv2", "RRBS", "WGBS", "Other"]

PROMPT_TEMPLATE = r"""
<system_role>
You are a biomedical data scientist specializing in epigenetics. Your task is to extract structured variables from study summaries for a systematic review on childhood maltreatment and DNA methylation.
</system_role>

<instructions>
Analyze the provided study summary and extract the following information. Ensure all data is standardized according to the guidelines.

1. **PMID**: The PubMed Identifier.
2. **Title**: The full, exact title of the publication.
3. **Sample**: The tissue or cell type used for DNA extraction.
4. **EWAS Platform**: The specific array or sequencing technology used.
5. **Exposure**: A terse (max 10 words) but descriptive summary of the specific maltreatment or adversity studied.
6. **CpGs**: A list of all significant CpG site IDs (e.g., cg00000000).
7. **Genes**: A list of official HGNC gene symbols associated with the findings.
</instructions>

<standardization_rules>
- **Sample**: Map to one of: {sample_types}. Use "Other (Specific Type)" if it doesn't fit.
- **Platform**: Map to one of: {platforms}. Be specific (e.g., "EPICv2" if version is noted).
- **List Formatting**: Return 'cpgs' and 'genes' as a JSON list of strings. If no data is found for a field, return an empty list [].
- **Gene Validation**: Differentiate between actual HGNC gene symbols (e.g., NR3C1, SLC6A4) and study abbreviations (e.g., BPD, CTQ, ACE). Exclude abbreviations.
- **CpG Validation**: Ensure all CpG IDs follow the cgXXXXXXXX format.
</standardization_rules>

<study_summary>
{content}
</study_summary>

<output_format>
Return ONLY a valid JSON object with these exact keys:
"pmid", "title", "sample", "ewas_platform", "exposure", "cpgs", "genes"
</output_format>
""".strip()

def run_gemini(content, filename):
    """
    Format the prompt, invoke Gemini CLI, and parse the JSON output.
    """
    prompt = PROMPT_TEMPLATE.format(
        sample_types=", ".join(SAMPLE_TYPES),
        platforms=", ".join(PLATFORMS),
        content=content
    )
    
    print("\n" + "="*80)
    print(f"SENT TO GEMINI ({filename}):")
    print("-"*80)
    print(prompt)
    print("="*80)
    
    command = ["gemini", "-p", prompt, "-m", MODEL]
    
    try:
        use_shell = (sys.platform == "win32")
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', shell=use_shell)
        
        print("\n" + "="*80)
        print(f"GEMINI RAW OUTPUT ({filename}):")
        print("-"*80)
        print(result.stdout)
        if result.stderr:
            print(f"DEBUG/ERROR: {result.stderr}")
        print("="*80)

        json_match = re.search(r"\{.*\}", result.stdout, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            print(f"❌ Error: No JSON found in output for {filename}")
            return None
    except Exception as e:
        print(f"❌ Unexpected error processing {filename}: {e}")
        return None

def main():
    """
    Main execution loop: list files, extract data via Gemini, and save to CSV.
    """
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Directory '{INPUT_DIR}' not found.")
        return

    if not os.path.exists(JSON_DIR):
        os.makedirs(JSON_DIR)
        print(f"📁 Created JSON store: {JSON_DIR}")

    files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.md')])
    all_data = []
    
    print(f"🚀 Starting extraction for {len(files)} files using {MODEL}...\n")
    
    for i, filename in enumerate(files):
        filepath = os.path.join(INPUT_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        data = run_gemini(content, filename)
        
        if data:
            # Save raw JSON to store
            json_filename = filename.replace('.md', '.json')
            json_path = os.path.join(JSON_DIR, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Saved JSON: {json_filename}")

            # Post-process lists for CSV storage
            if isinstance(data.get('cpgs'), list):
                data['cpgs'] = "; \n".join(data['cpgs'])
            if isinstance(data.get('genes'), list):
                data['genes'] = "; \n".join(data['genes'])
                
            data['filename'] = filename
            all_data.append(data)
            print(f"✅ Successfully parsed {filename}")
        else:
            print(f"⚠️ Failed to extract data for {filename}")

    if all_data:
        headers = ["pmid", "title", "sample", "ewas_platform", "exposure", "cpgs", "genes", "filename"]
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n📊 Successfully saved {len(all_data)} records to {OUTPUT_CSV}")
    else:
        print("\n❌ No data was successfully extracted.")

if __name__ == "__main__":
    main()
