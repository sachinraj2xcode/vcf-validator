---
title: 'vcf_validator: A Layered, Rule-by-Rule VCF Validation Tool'
tags:
  - Python
  - bioinformatics
  - genomics
  - VCF
  - variant calling
  - data validation
authors:
  - name: Sachin Raj
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 23 August 2026
bibliography: paper.bib
---

# Summary

`vcf_validator` is a lightweight, dependency-free Python tool that validates Variant Call Format (VCF) files against the VCF specification and optionally checks REF bases against a supplied reference genome. It produces a structured, rule-by-rule report in JSON, CSV, and graphical form, explicitly identifying each check that passed, warned, or failed — along with the line number and reason. The tool is implemented as a single Python script with no required third-party dependencies for its core logic.

# Statement of Need

The VCF format is the standard output of genomic variant calling pipelines, but existing tools that process VCF files (such as bcftools, pysam, and cyvcf2) are optimised for analysis and are often lenient by design, silently tolerating malformed input. A dedicated validation tool needs the opposite behaviour: surface every deviation from the specification rather than papering over it. Crucially, such a tool must be explicit about the boundary between format validity and biological correctness — a VCF file can be structurally valid and still contain scientifically misleading calls.

`vcf_validator` addresses this gap by separating validation into four independently testable layers: structural conformance with the VCF specification, internal consistency of field values and genotypes, REF-base consistency against a reference FASTA, and read-level evidence from aligned reads. Each layer produces discrete, attributable check results rather than a single pass/fail verdict. The tool automatically handles the common chromosome naming mismatch between VCF files that use `chr` prefixes and reference FASTA files that do not, which is a practical issue that commonly produces spurious errors in other validation workflows.

The tool was evaluated against 47 automated tests covering all implemented rules, and then run against three publicly available real-world datasets: the GIAB HG001 (NA12878) v4.2.1 benchmark VCF [@zook2016], the GIAB HG002 (NA24385) v4.2.1 benchmark VCF [@zook2016], and the ClinVar January 2023 archive VCF [@landrum2016], all validated against the GRCh38 primary assembly reference FASTA [@cunningham2022]. The two GIAB benchmark files passed with zero errors across a combined 63 million checks. ClinVar was correctly classified as failed due to two genuine ALT field violations reflecting its use of extended VCF conventions for complex structural variants.

# Similar Tools

`bcftools stats` and `bcftools check` provide some VCF validation functionality but are primarily designed for analysis rather than validation, and do not produce structured per-rule reports. `vcf-validator` by EBI (a separate tool) performs specification checking but does not integrate reference-genome consistency or read-evidence corroboration. The Picard `ValidateSamFile` tool validates SAM/BAM files but not VCF. `vcf_validator` differs from these in its explicit four-layer separation, its structured JSON/CSV output, its automatic chromosome naming resolution, and its dependency-free core.

# Acknowledgements

The GIAB benchmark data used to evaluate this tool was produced by the Genome in a Bottle Consortium at NIST [@zook2016]. The reference genome used was the GRCh38 primary assembly from Ensembl release 115 [@cunningham2022].

# References
