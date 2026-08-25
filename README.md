# vcf_validator

Validates VCF files against the VCF specification and optionally checks REF bases against a reference genome, outputting results as JSON, CSV, and graphs.

## Citation

If you use this tool, please cite the associated paper:

Raj, S. (2026). VCF Validation Through Structural, Reference, and Genotype Checks: A Layered Approach to Variant Call Format Quality Control. Zenodo. https://doi.org/ZENODO_DOI

## Code structure

```
validate.py

  parse_vcf()     reads a VCF file into structured records
  validate_vcf()  checks every field and rule against the spec
  check_ref()     compares VCF REF bases against the reference

  load_fasta()    loads a reference FASTA into memory
  find_inputs()   scans input/ folders for files to run
  write_csv()     writes a summary table to CSV
  write_graphs()  writes error/check charts to PNG files
```

## File system

```
input/
  vcf/            put your .vcf files here
  reference/      put your reference .fa file here
output/           results appear here after each run, timestamped
test_files/       sample VCF and output files for viewing and testing only
validate.py       the script
DATA_SOURCES.md   where to get real data, with download commands
```

## How to use

**Step 1 — add a VCF file**

Put any `.vcf` file into `input/vcf/`. This can be your own file, a public benchmark, or one of the samples in `test_files/`. You can add as many VCF files as you like and they will all be validated in one run.

**Step 2 — optionally add a reference genome**

Put a `.fa` reference FASTA into `input/reference/`. This enables REF base consistency checking. It is optional — the validator will still run without it and check everything else. See `DATA_SOURCES.md` for where to download one.

**Step 3 — run and view results**

```bash
python validate.py
```

Results are written to `output/` with a timestamp. Five files are created each run:

| File | Contents |
|---|---|
| `errors_TIMESTAMP.json` | Every ERROR and WARNING with rule, line number, and message |
| `results_TIMESTAMP.csv` | Summary table (status, error count, passed checks per file) |
| `errors_per_run.png` | Bar chart of errors and warnings per run |
| `check_results.png` | Stacked bar of passed / warning / error checks per run |
| `errors_by_rule.png` | Error count broken down by rule category |

**Results from the paper datasets (GRCh38 full reference):**

| Dataset | Status | Errors | Warnings | Passed Checks |
|---|---|---|---|---|
| HG001 GRCh38 v4.2.1 | PASSED | 0 | 0 | 31,146,729 |
| HG002 GRCh38 v4.2.1 | PASSED | 0 | 0 | 32,386,737 |
| ClinVar 2023-01-07 | FAILED | 2 | 0 | 11,045,908 |

ClinVar errors: one ALT field violation (`YT` at line 845,115) and one REF_CONTIG violation (chromosome `NW_009646201.1` not in GRCh38 primary assembly, at line 1,578,015).

> Not sure what to expect? Open `test_files/` to see example VCF inputs and sample output before using your own data.

## Requirements

- Python 3.10 or higher
- Disk space for your input files — the full GRCh38 reference is ~3GB uncompressed

The core validation logic has no third-party dependencies. Matplotlib is used for graph output only and is installed automatically on first run if not already present.

> **Note:** The reference check against the full GRCh38 genome can take 30+ minutes per VCF file. This is expected. Do not close the terminal while it is running. You will see each file print its result when done, followed by "output/" when everything is saved. No PDF is produced — graphs are saved as PNG files.
