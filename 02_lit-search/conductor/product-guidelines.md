# Product Guidelines: Epigenomics Literature Search & Extraction

## Content & Tone
- **Professional/Semi-formal:** The final literature review and summaries should be objective and scientifically accurate while remaining accessible to a broad academic audience. Avoid overly dense jargon where possible, but use correct biological and bioinformatic terminology.
- **Terse and Focused:** Summaries of papers and methodologies should be concise, focusing on the core findings (CpGs, genes, samples, and results) without unnecessary filler.

## Visual Standards
- **Nature-Style Tables:** Follow the Nature-style HTML table formatting as specified in the project’s global context:
    - Bold, left-aligned titles.
    - 1px solid black borders (top, bottom, and under headers).
    - No vertical borders.
    - Collapsed borders.
    - Footnotes in 0.9em font size with italicized gene symbols.
- **Mermaid.js Flowcharts:** Use Mermaid.js to generate publication-quality PRISMA flow diagrams. Ensure clear labeling of study screening phases (Identification, Screening, Eligibility, and Inclusion).

## Data Integrity & Traceability
- **Source Traceability:** Every extracted data point (CpG, gene, platform, etc.) must be linked back to its source PMID or DOI. Extracted data from the Gemini CLI must always be cross-referenced with the source filename (PMID.md) to ensure correct attribution.
- **Standardized Naming:** 
    - CpG sites must follow the cgXXXXXXXX format.
    - Gene symbols should follow HGNC standards (e.g., *NR3C1*, *SLC6A4*).
- **Study Variables:** Consistently extract and report key variables: PMID, Title, Sample Type (Tissue), EWAS Platform (e.g., 450k, EPIC), Exposure Type, CpG IDs, and Gene Symbols.

## Quality Control & Verification
- **Standard Audit:** Perform a manual spot-check of approximately 10-20% of the automated extractions against the source PDFs/Markdowns to ensure consistency and identify potential systematic extraction errors.
- **JSON Metadata:** Use structured JSON for all intermediate extraction outputs to facilitate validation and programmatic conversion to final deliverables (CSV/Excel/Markdown).
