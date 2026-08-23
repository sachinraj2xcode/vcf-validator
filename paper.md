---
title: 'vcf_validator: A Layered, Rule-by-Rule Validator for Variant Call Format Files'
tags:
  - Python
  - bioinformatics
  - genomics
  - VCF
  - variant calling
  - data validation
  - reference genome
authors:
  - name: Sachin Raj
    orcid: 0009-0005-6249-416X
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 23 August 2026
bibliography: paper.bib
---

# Summary

`vcf_validator` is a lightweight, dependency-free Python tool that validates Variant Call Format (VCF) files against the VCF specification and optionally checks REF bases against a supplied reference genome. It produces a structured, rule-by-rule report in JSON, CSV, and graphical form, explicitly identifying every check that passed, warned, or failed along with the line number and reason. The tool is implemented as a single Python script with no required third-party dependencies.

The current release implements three independently testable validation layers: (1) structural conformance with the VCF specification [@danecek2011]; (2) internal consistency of field values and genotypes; and (3) REF-base consistency against a reference FASTA. A fourth layer providing read-level evidence corroboration from BAM and FASTQ files is planned as a separate tool and a separate publication, as its scope and dependencies warrant independent treatment.

The tool was run against three publicly available real-world datasets: the GIAB HG001 (NA12878) v4.2.1 benchmark VCF [@zook2016], the GIAB HG002 (NA24385) v4.2.1 benchmark VCF [@zook2016], and the ClinVar January 2023 archive VCF [@landrum2016], all validated against the GRCh38 primary assembly reference FASTA [@cunningham2022]. The two GIAB benchmark files passed with zero errors across a combined 63 million checks. ClinVar was correctly classified as FAILED due to two genuine ALT field violations reflecting its use of extended VCF conventions for complex structural variants.

# Statement of Need

The VCF format is the standard output of genomic variant calling pipelines, but existing tools such as bcftools, pysam, and cyvcf2 are optimised for analysis and are lenient by design, silently tolerating malformed input so that downstream analysis can proceed. A dedicated validation tool needs the opposite behaviour: surface every deviation from the specification rather than papering over it.

The motivation for this tool comes from direct professional experience: in genomic data pipelines, VCF files are the primary file type requiring validation prior to ingestion into downstream curation and analysis systems. In practice, existing tools would silently accept malformed files, passing errors downstream where they were difficult to trace.

A practical issue that commonly produces spurious errors in other validation workflows is the chromosome naming convention mismatch between VCF files that use `chr` prefixes (e.g. chr1) and reference FASTA files that do not (e.g. Ensembl's convention of 1, 2). The tool resolves this automatically, ensuring naming differences do not produce false errors.

# Implementation

The tool is implemented as a single Python script (`validate.py`) containing three core functions:

- `parse_vcf()` reads VCF text into structured records
- `validate_vcf()` performs structural, field, genotype, and sort checks
- `check_ref()` checks REF base consistency against a reference FASTA file

Seventeen distinct rule categories are implemented across the three layers, covering file structure and header conformance, per-field syntax validation for all eight fixed VCF columns, genotype token syntax and allele index range checking, coordinate sort order, and reference-genome REF-base consistency. The core logic has zero third-party dependencies and uses only the Python standard library.

# Results

The validator was run against three real-world datasets producing over 74 million individual validation checks. Results are shown in Table 1.

| Dataset | Status | Errors | Warnings | Passed Checks |
|---|---|---|---|---|
| HG001 GRCh38 v4.2.1 | PASSED | 0 | 0 | 31,146,729 |
| HG002 GRCh38 v4.2.1 | PASSED | 0 | 0 | 32,386,737 |
| ClinVar 2023-01-07 | FAILED | 2 | 0 | 11,045,908 |

Table 1: Validation results across three real-world VCF datasets against the full GRCh38 primary assembly reference.

Both GIAB benchmark files passed with zero errors, confirming that the validator does not produce false positives on well-curated gold-standard data. ClinVar was correctly identified as containing two genuine ALT field violations reflecting its documented use of extended VCF conventions for complex structural variants.

# Future Work

A fourth validation layer is planned as a separate tool and will be the subject of a separate publication. This layer will extend the validation framework to incorporate BAM and FASTQ files, providing read-level evidence corroboration for variant calls. The decision to treat this as an independent contribution reflects the distinct dependencies, file formats, and analytical scope that read-level validation introduces. The current tool establishes the VCF structural and reference consistency foundation upon which that evidence layer will build.

# Acknowledgements

The GIAB benchmark data used to evaluate this tool was produced by the Genome in a Bottle Consortium at NIST [@zook2016]. The reference genome used was the GRCh38 primary assembly from Ensembl release 115 [@cunningham2022].

# References
