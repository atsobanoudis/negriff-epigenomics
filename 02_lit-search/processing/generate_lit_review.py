import json
import os

def load_all_json(json_dir):
    data = []
    for filename in sorted(os.listdir(json_dir)):
        if filename.endswith('.json'):
            with open(os.path.join(json_dir, filename), 'r', encoding='utf-8') as f:
                data.append(json.load(f))
    return data

def generate_markdown(studies, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Systematic Literature Review: Childhood Maltreatment and DNA Methylation\n\n")
        f.write("## Overview\n")
        f.write(f"This review synthesizes findings from {len(studies)} epigenome-wide association studies (EWAS) investigating the biological embedding of childhood adversity.\n\n")
        
        f.write("## Study Characteristics and Key Findings\n\n")
        f.write("| PMID | Title | Sample | Platform | Exposure | Key Genes/Loci |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for s in studies:
            pmid = s.get('pmid', 'N/A')
            title = s.get('title', 'N/A')
            sample = s.get('sample', 'N/A')
            platform = s.get('ewas_platform', 'N/A')
            exposure = s.get('exposure', 'N/A')
            
            # Show top 5 genes to keep table readable
            genes = s.get('genes', [])
            if isinstance(genes, list):
                genes_str = ", ".join(genes[:5])
                if len(genes) > 5:
                    genes_str += "..."
            else:
                genes_str = str(genes)
                
            f.write(f"| {pmid} | {title} | {sample} | {platform} | {exposure} | {genes_str} |\n")
        
        f.write("\n## Detailed Study Summaries\n\n")
        for s in studies:
            f.write(f"### PMID: {s.get('pmid')} - {s.get('title')}\n\n")
            f.write(f"- **Sample Type:** {s.get('sample')}\n")
            f.write(f"- **Platform:** {s.get('ewas_platform')}\n")
            f.write(f"- **Exposure:** {s.get('exposure')}\n")
            
            cpgs = s.get('cpgs', [])
            if cpgs:
                f.write(f"- **Significant CpGs:** {', '.join(cpgs)}\n")
            
            genes = s.get('genes', [])
            if genes:
                f.write(f"- **Associated Genes:** {', '.join(genes)}\n")
            f.write("\n---\n\n")

def main():
    json_dir = "processing/json_store"
    output_file = "literature_review.md"
    
    if not os.path.exists(json_dir):
        print(f"Error: {json_dir} not found.")
        return
        
    studies = load_all_json(json_dir)
    generate_markdown(studies, output_file)
    print(f"✅ Literature review generated: {output_file}")

if __name__ == "__main__":
    main()
