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

`vcf_validator` is a lightweight, dependency-free Python tool that validates Variant Call Format (VCF) files against the VCF specification and optionally checks REF bases against a supplied reference genome. It produces a structured, rule-by-rule report in JSON, CSV, and graphical form, explicitly identifying every check that passed, warned, or failed along with the line number and reason. The tool is implemented as a single Python script with no required third-party dependencies for its core validation logic.

The tool separates validation into four independently testable layers: (1) structural conformance with the VCF specification [@danecek2011]; (2) internal consistency of field values and genotypes; (3) REF-base consistency against a reference FASTA; and (4) read-level evidence from aligned reads. Each layer produces discrete, attributable check results rather than a single pass/fail verdict.

The tool was evaluated against 47 automated tests covering all implemented rules, and then run against three publicly available real-world datasets: the GIAB HG001 (NA12878) v4.2.1 benchmark VCF [@zook2016], the GIAB HG002 (NA24385) v4.2.1 benchmark VCF [@zook2016], and the ClinVar January 2023 archive VCF [@landrum2016], all validated against the GRCh38 primary assembly reference FASTA [@cunningham2022]. The two GIAB benchmark files passed with zero errors across a combined 63 million checks. ClinVar was correctly classified as FAILED due to two genuine ALT field violations reflecting its use of extended VCF conventions for complex structural variants.

# Statement of Need

The VCF format is the standard output of genomic variant calling pipelines, but existing tools that process VCF files such as bcftools, pysam, and cyvcf2 are optimised for analysis and are lenient by design, silently tolerating malformed input so that downstream analysis can proceed. This is the correct behaviour for an analysis tool, but it means format and consistency errors can pass through a pipeline unreported. A dedicated validation tool needs the opposite behaviour: surface every deviation from the specification rather than papering over it.

Crucially, such a tool must be explicit about the boundary between format validity and biological correctness. A VCF file can be structurally valid and still contain scientifically misleading calls, for example if it was generated against the wrong reference build or if genotype calls reference alleles never declared at that site. `vcf_validator` addresses this gap by making each validation layer independently testable and by constraining read-evidence checks to WARNING-or-PASS severity only, reflecting that absence of read support in a single alignment file is not proof that a call is incorrect.

A practical issue that commonly produces spurious errors in other validation workflows is the chromosome naming convention mismatch between VCF files that use `chr` prefixes (e.g. chr1) and reference FASTA files that do not (e.g. Ensembl's convention of 1, 2). The tool resolves this automatically by trying both conventions, ensuring naming differences do not produce false errors.

# Implementation

The tool is implemented as a single Python script (`validate.py`) containing five functions:

- `parse_vcf()` reads VCF text into structured records
- `validate_vcf()` performs structural, field, genotype, and sort checks
- `check_ref()` checks REF base consistency against a FASTA file
- `check_sam()` checks read-level evidence from a plain-text SAM file
- `validate_fastq()` performs standalone FASTQ structural checks

Seventeen distinct rule categories are implemented across the four layers. These cover file structure and header conformance, per-field syntax validation for all eight fixed VCF columns, genotype token syntax and allele index range checking, coordinate sort order, and reference-genome REF-base consistency. The FASTQ validator checks four-line record structure, sequence character validity, sequence/quality length equality, and Phred+33 encoding [@ewing1998a].

The core logic has zero third-party dependencies and uses only the Python standard library. Read-level BAM/CRAM evidence requires pysam for binary files; a dependency-free plain-text SAM reader is provided as a fallback. Real BAM/CRAM files follow the SAM specification [@li2009].

# Results

All 47 automated tests passed on execution. The validator was then run against three real-world datasets producing over 74 million individual validation checks. Results are shown in Table 1.

| Dataset | Status | Errors | Warnings | Passed Checks |
|---|---|---|---|---|
| HG001 GRCh38 v4.2.1 | PASSED | 0 | 0 | 31,146,729 |
| HG002 GRCh38 v4.2.1 | PASSED | 0 | 0 | 32,386,737 |
| ClinVar 2023-01-07 | FAILED | 2 | 0 | 11,045,908 |

Table 1: Validation results across three real-world VCF datasets against the full GRCh38 primary assembly reference.

Both GIAB benchmark files passed with zero errors, confirming that the validator does not produce false positives on well-curated gold-standard data. ClinVar was correctly identified as containing two genuine ALT field violations reflecting its documented use of extended VCF conventions for complex structural variants.

# Acknowledgements

The GIAB benchmark data used to evaluate this tool was produced by the Genome in a Bottle Consortium at NIST [@zook2016]. The reference genome used was the GRCh38 primary assembly from Ensembl release 115 [@cunningham2022].

# References
