# Track Specification: Automate Data Extraction and Final Deliverables

## Overview
This track focuses on automating the extraction of structured epigenetic data (CpG sites, gene symbols, tissues, platforms) from existing study summaries (Markdown), cross-referencing these findings with an external list, and generating a final package of scientific deliverables (Excel, PRISMA diagram, and Literature Review).

## Requirements
- **Data Extraction:** Polished Python script to parse 26+ study summaries using Gemini CLI.
- **Output Standardization:** Generate a comprehensive Excel/CSV study sheet with PMID, Title, Sample, Platform, Exposure, CpGs, and Genes.
- **Cross-Referencing:** Develop a method to intersect extracted features with an external list of CpGs/Genes.
- **PRISMA Diagram:** Automated generation of a Mermaid.js flow chart from screening data.
- **Literature Review:** Scientific summary of all included studies in Markdown format.

## Constraints
- Adhere to Nature-style table formatting for reporting.
- Ensure 100% source traceability to PMIDs.
- Follow HGNC gene symbol and standard CpG ID conventions.
