# Tech Stack: Epigenomics Literature Search & Extraction

## Programming Language
- **Python:** The primary language for all scripts, data processing, and automation.

## Core Libraries & Tools
- **Gemini CLI:** The main engine for study summarization and scientific feature extraction from Markdown and PDF summaries.
- **Biopython (Bio.Entrez):** Used for querying PubMed and fetching study metadata.
- **Pandas / Openpyxl:** For generating and manipulating Excel (.xlsx) and CSV (.csv) summaries.
- **JSON & CSV Modules:** For structured metadata storage and intermediate data serialization.
- **Regular Expressions (re):** For pattern matching CpG IDs and gene symbols during extraction.
- **Subprocess:** For programmatic invocation of the Gemini CLI from within Python scripts.

## Visualization & Documentation
- **Mermaid.js:** For generating PRISMA-compliant flowcharts in Markdown.
- **Markdown:** The primary format for final literature review summaries and documentation.
- **Nature-Style HTML Tables:** For scientific reporting of extracted features.

## Data Infrastructure
- **File-Based Storage:** Study-specific PDFs and summaries are stored in the pdfs/ directory, named by their PMID.
- **JSON Metadata Store:** Study-specific JSON files generated from Gemini extraction will be stored for audit and audit trail purposes.
- **Consolidated Excel/CSV:** The final product of the extraction pipeline, aggregating data across all identified studies.
