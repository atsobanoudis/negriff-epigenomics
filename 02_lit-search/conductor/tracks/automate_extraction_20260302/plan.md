# Implementation Plan: Automate Data Extraction and Final Deliverables

## Phase 1: Script Polishing & Data Extraction
- [ ] Task: Audit and Refine Extraction Prompt
    - [ ] Review processing/extract_study_data.py prompt for accuracy and standardization rules.
    - [ ] Test extraction on a subset of 3 studies and verify JSON outputs.
- [ ] Task: Execute Batch Extraction
    - [ ] Run the refined extraction script against all 26 Markdown summaries in the pdfs/ directory.
    - [ ] Validate that all JSON outputs are generated and traceable to PMIDs.
- [ ] Task: Generate Master Study Sheet
    - [ ] Aggregate JSON outputs into a consolidated Excel/CSV file (master_study_data.xlsx).
    - [ ] Ensure column formatting aligns with the Product Guide requirements.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Script Polishing & Data Extraction' (Protocol in workflow.md)

## Phase 2: Cross-Referencing & Analysis
- [ ] Task: Develop Cross-Reference Script
    - [ ] Create a Python script to load the master_study_data.xlsx and an external reference list.
    - [ ] Implement intersection logic for CpG IDs and Gene Symbols.
- [ ] Task: Generate Overlap Report
    - [ ] Produce a summary (CSV/Markdown) of all features found in both the literature review and the reference list.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Cross-Referencing & Analysis' (Protocol in workflow.md)

## Phase 3: Final Deliverable Generation
- [ ] Task: Create PRISMA Flow Chart
    - [ ] Generate a Mermaid.js diagram based on ewas-59-screen.xlsx data.
- [ ] Task: Write Scientific Literature Review
    - [ ] Synthesize study summaries into a comprehensive Markdown document.
    - [ ] Include Nature-style tables for study characteristics and findings.
- [ ] Task: Final Quality Audit
    - [ ] Perform a 10% spot-check of extracted data against original summaries.
    - [ ] Verify all deliverable formatting (Nature-style tables, HGNC symbols).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Deliverable Generation' (Protocol in workflow.md)
