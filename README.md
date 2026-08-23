# vcf_validator

Validates VCF files against the VCF specification and optionally checks REF bases against a reference genome, outputting results as JSON, CSV, and graphs.

## Code structure

```
validate.py

  parse_vcf()     reads a VCF file into structured records
  validate_vcf()  checks every field and rule against the spec
  load_fasta()    loads a reference FASTA into memory
  check_ref()     compares VCF REF bases against the reference
  find_inputs()   scans input/ folders for files to run
  write_csv()     writes a summary table to CSV
  write_graphs()  writes error/check charts to a PDF
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

Results are written to `output/` with a timestamp. Three files are created each run: a `.json` with full check-by-check detail, a `.csv` summary table you can open in Excel, and a `.pdf` with graphs.

> Not sure what to expect? Open `test_files/` to see example VCF inputs and sample output before using your own data.

## Requirements

- Python 3.10 or higher
- matplotlib (installed automatically on first run)
- Disk space for your input files — the full GRCh38 reference is ~3GB uncompressed

> **Note:** The reference check against the full GRCh38 genome can take 30+ minutes per VCF file. This is expected. Do not close the terminal while it is running. You will see each file print its result when done, followed by "output/" when everything is saved.
