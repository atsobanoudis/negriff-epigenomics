# Initial Concept
the pdf files in the pdf folder i manually extracted and ran against gemini to produce their respective markdowns. lastly, the goal here is to first polish the automated gemini cli script I have and make sure it functions and that it can generate a comprehensive excel sheet. then develop a method to cross reference to see how we can identify cpgs and genes that overlap with the ones I'll provide. then a final written deliverable that explains all of this with prisma diagram, scientifically written lit review of all the papers, etc, the process of screening etc etc etc

# Product Guide: Epigenomics Literature Search & Extraction

## Vision
To provide a structured, automated extraction and reporting pipeline for completed epigenetic systematic reviews, turning study summaries into standardized scientific deliverables.

## Current State
- 59 studies screened for inclusion in the "ewas-59-screen.xlsx" file.
- Individual PDFs (26 identified) manually processed and summarized into Markdown via Gemini CLI.
- Existing Python scripts (processing/) for abstract screening and data extraction are in development.

## Primary Goal
Automate the extraction of pertinent scientific data (CpG sites, gene symbols, tissues, platforms) from study summaries, cross-reference these features with external lists, and generate a final, publication-ready literature review package.

## Key Features
- **Polished Extraction Script:** Refine and validate the Gemini-based Python extraction scripts to generate a comprehensive, error-free Excel/CSV study sheet.
- **Cross-Referencing Engine:** Develop a method to intersect extracted CpG sites and gene symbols with an external list (to be provided) to identify overlaps.
- **Scientific Deliverable Suite:**
    - **PRISMA Diagram:** Automated generation of a Mermaid.js flow chart depicting the screening and selection process.
    - **Literature Review:** A scientifically written summary in Markdown covering all 26 identified papers, their findings, and the significance of extracted features.
    - **Methodology Summary:** A concise explanation of the screening, summarization, and extraction process used.

## Success Criteria
- A functional, automated extraction script that produces a complete study data CSV.
- A list of overlapping CpG sites and genes between the study results and the external reference list.
- A publication-ready literature review document in Markdown.
- A final PRISMA diagram correctly representing the study flow.
