# Data Sources

This file documents the datasets used to develop and test the validator, explains why each was chosen, and provides download links so others can reproduce the results.

---

## Reference Genome

**GRCh38 primary assembly (Ensembl release 115)**
https://ftp.ensembl.org/pub/release-115/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz

This is the standard human reference genome used in modern genomics pipelines. All three VCF datasets below were validated against this file. The full assembly covers chromosomes 1 through 22, X, Y, and mitochondrial DNA.

During development, chromosome 1 and chromosome 22 were used for intermediate testing before the full reference was available. Chromosome 1 is the largest chromosome and exercises the most variants. Chromosome 22 is the smallest autosome and is commonly used in genomics testing because it downloads quickly. Final results reported in the paper used the full primary assembly.

Download command:
```bash
curl -O https://ftp.ensembl.org/pub/release-115/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
gunzip Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
mv Homo_sapiens.GRCh38.dna.primary_assembly.fa input/reference/
```

---

## VCF Datasets

### GIAB HG001 (NA12878) v4.2.1 benchmark, GRCh38
https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/NA12878_HG001/NISTv4.2.1/GRCh38/

HG001, also known as NA12878, is the most widely used benchmark sample in human genomics. It was produced by the Genome in a Bottle Consortium at NIST and represents a gold-standard set of high-confidence variant calls. It was chosen as the primary positive control: a well-curated file that a correct validator should pass with zero errors. Result: PASSED, 0 errors, 31,146,729 checks.

Download command:
```bash
curl -O https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/NA12878_HG001/NISTv4.2.1/GRCh38/HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz
gunzip HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz
mv HG001_GRCh38_1_22_v4.2.1_benchmark.vcf input/vcf/
```

### GIAB HG002 (NA24385) v4.2.1 benchmark, GRCh38
https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG002_NA24385_son/NISTv4.2.1/GRCh38/

HG002 is a second GIAB benchmark sample from a different individual. It was included to confirm that the HG001 result was not specific to one sample and that the validator produces consistent results across different benchmark files. Result: PASSED, 0 errors, 32,386,737 checks.

Download command:
```bash
curl -O https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG002_NA24385_son/NISTv4.2.1/GRCh38/HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz
gunzip HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz
mv HG002_GRCh38_1_22_v4.2.1_benchmark.vcf input/vcf/
```

### ClinVar January 2023 archive, GRCh38
https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/archive_2.0/2023/

ClinVar is NCBI's public archive of human genetic variants with clinical interpretations. It was chosen as a real-world negative control: a widely used public database that is known to use extended VCF conventions beyond the base VCFv4.x specification. The validator correctly identified 2 ALT field violations where ClinVar uses non-standard notation for complex structural variants. Result: FAILED, 2 errors, 11,045,908 checks.

Download command:
```bash
curl -O https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/archive_2.0/2023/clinvar_20230107.vcf.gz
gunzip clinvar_20230107.vcf.gz
mv clinvar_20230107.vcf input/vcf/
```

---

## Other suggested sources

| Source | URL |
|---|---|
| 1000 Genomes Project VCFs | https://www.internationalgenome.org/data |
| dbSNP VCF | https://ftp.ncbi.nih.gov/snp/latest_release/VCF/ |
| Plant genomes (Ensembl Plants) | https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/current/fasta/ |
| Any organism reference | https://ftp.ensembl.org/pub/current_fasta/ |
| Raw reads (FASTQ/BAM via SRA) | https://www.ncbi.nlm.nih.gov/sra |
