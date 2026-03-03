import csv
import os

def intersect(list1, list2):
    """Return a sorted list of elements present in both lists."""
    return sorted(list(set(list1) & set(list2)))

def load_master_data(file_obj):
    """
    Load master study data from a file-like object and parse cpgs/genes lists.
    Expected format: pmid,title,sample,ewas_platform,exposure,cpgs,genes,filename
    """
    data = []
    reader = csv.DictReader(file_obj)
    for row in reader:
        # Split semicolon-newline separated strings back into lists
        if 'cpgs' in row and row['cpgs']:
            row['cpgs'] = [x.strip() for x in row['cpgs'].split(';') if x.strip()]
        else:
            row['cpgs'] = []
            
        if 'genes' in row and row['genes']:
            row['genes'] = [x.strip() for x in row['genes'].split(';') if x.strip()]
        else:
            row['genes'] = []
            
        data.append(row)
    return data

def load_reference_list(filepath):
    """Load a reference list from a text file (one ID per line)."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    master_file = "master_study_data.csv"
    ref_cpgs_file = "ref_cpgs.txt"
    ref_genes_file = "ref_genes.txt"
    output_file = "overlap_report.csv"
    
    if not os.path.exists(master_file):
        print(f"Error: {master_file} not found.")
        return
        
    ref_cpgs = load_reference_list(ref_cpgs_file)
    ref_genes = load_reference_list(ref_genes_file)
    
    with open(master_file, 'r', encoding='utf-8-sig') as f:
        studies = load_master_data(f)
        
    report = []
    for study in studies:
        overlap_cpgs = intersect(study['cpgs'], ref_cpgs)
        overlap_genes = intersect(study['genes'], ref_genes)
        
        if overlap_cpgs or overlap_genes:
            report.append({
                'pmid': study['pmid'],
                'title': study['title'],
                'overlap_cpgs': "; ".join(overlap_cpgs),
                'overlap_genes': "; ".join(overlap_genes),
                'num_cpgs': len(overlap_cpgs),
                'num_genes': len(overlap_genes)
            })
            
    if report:
        headers = ['pmid', 'title', 'overlap_cpgs', 'overlap_genes', 'num_cpgs', 'num_genes']
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(report)
        print(f"✅ Overlap report saved to {output_file} ({len(report)} studies with overlaps)")
    else:
        print("ℹ️ No overlaps found between studies and reference lists.")

if __name__ == "__main__":
    main()
