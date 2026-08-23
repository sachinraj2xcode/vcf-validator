import re, json, csv, os, sys, subprocess
from datetime import datetime

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    except ImportError:
    print("installing matplotlib...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    
VALID = set("ACGTNacgtn")
ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("output", exist_ok=True)


def parse_vcf(path):
    hdr = {"fileformat": None, "info": {}, "format": {}, "filter": {}, "samples": []}
    recs = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line:
                continue
            if line.startswith("##"):
                if line.startswith("##fileformat="):
                    hdr["fileformat"] = line.split("=", 1)[1].strip()
                m = re.match(r"##(INFO|FORMAT|FILTER)=<.*?ID=([^,>]+)", line, re.I)
                if m:
                    hdr[m.group(1).lower()][m.group(2)] = True
                continue
            if line.startswith("#CHROM"):
                cols = line.lstrip("#").split("\t")
                hdr["samples"] = cols[9:] if len(cols) > 9 else []
                continue
            fields = line.split("\t")
            if len(fields) < 8:
                recs.append({"line": i, "parse_error": f"only {len(fields)} fields"})
                continue
            chrom, pos_raw, id_, ref, alt, qual, filt, info, *rest = fields
            try:
                pos = int(pos_raw)
            except ValueError:
                pos = None
            recs.append({
                "line": i, "chrom": chrom, "pos_raw": pos_raw, "pos": pos,
                "ref": ref, "alt": alt,
                "alts": [] if alt in (".", "") else alt.split(","),
                "qual": qual, "filter": filt, "info": info,
                "format": rest[0] if rest else None,
                "samples": rest[1:] if len(rest) > 1 else [],
            })
    return hdr, recs


def validate_vcf(path):
    checks = []

    def add(sev, rule, msg, line=None):
        checks.append({"severity": sev, "rule": rule, "line": line, "message": msg})

    hdr, recs = parse_vcf(path)

    if hdr["fileformat"]:
        if re.match(r"^VCFv4\.\d+$", hdr["fileformat"]):
            add("PASS", "FILEFORMAT", f"version {hdr['fileformat']}")
        else:
            add("WARNING", "FILEFORMAT", f"unusual version: {hdr['fileformat']}")
    else:
        add("ERROR", "FILEFORMAT", "missing ##fileformat line")

    if not recs:
        add("WARNING", "NO_RECORDS", "no data records found")

    last_pos = {}
    seen_chroms = []

    for r in recs:
        ln = r["line"]

        if "parse_error" in r:
            add("ERROR", "FIELD_COUNT", r["parse_error"], ln)
            continue

        if not r["chrom"] or not re.match(r"^[A-Za-z0-9_.\-]+$", r["chrom"]):
            add("ERROR", "CHROM", f"invalid chrom '{r['chrom']}'", ln)
        else:
            add("PASS", "CHROM", f"chrom '{r['chrom']}' ok", ln)

        if r["pos"] is None:
            add("ERROR", "POS", f"pos '{r['pos_raw']}' not an integer", ln)
        elif r["pos"] < 1:
            add("ERROR", "POS", f"pos {r['pos']} must be >= 1", ln)
        else:
            add("PASS", "POS", f"pos {r['pos']} ok", ln)

        if not r["ref"] or any(b not in VALID for b in r["ref"]):
            add("ERROR", "REF", f"ref '{r['ref']}' has invalid bases", ln)
        else:
            add("PASS", "REF", f"ref '{r['ref']}' ok", ln)

        if not r["alt"]:
            add("ERROR", "ALT", "alt is empty", ln)
        elif r["alt"] == ".":
            add("PASS", "ALT", "alt is '.' ok", ln)
        else:
            bad = [a for a in r["alts"]
                   if a != "*"
                   and not re.match(r"^<[A-Za-z0-9:_.\-]+>$", a)
                   and not re.search(r"[\[\]]", a)
                   and any(b not in VALID for b in a)]
            if bad:
                add("ERROR", "ALT", f"invalid alt: {bad}", ln)
            else:
                add("PASS", "ALT", f"{len(r['alts'])} alt(s) ok", ln)

        if not r["qual"]:
            add("ERROR", "QUAL", "qual is empty", ln)
        elif r["qual"] == ".":
            add("PASS", "QUAL", "qual is '.'", ln)
        else:
            try:
                q = float(r["qual"])
                if q < 0:
                    add("ERROR", "QUAL", f"qual {q} is negative", ln)
                else:
                    add("PASS", "QUAL", f"qual {q} ok", ln)
            except ValueError:
                add("ERROR", "QUAL", f"qual '{r['qual']}' not a number", ln)

        if not r["filter"]:
            add("ERROR", "FILTER", "filter is empty", ln)
        else:
            vals = r["filter"].split(";")
            if "PASS" in vals and len(vals) > 1:
                add("ERROR", "FILTER", "PASS must appear alone", ln)
            else:
                undeclared = [v for v in vals if v not in ("PASS", ".") and v not in hdr["filter"]]
                if undeclared:
                    add("WARNING", "FILTER", f"undeclared filter values: {undeclared}", ln)
                else:
                    add("PASS", "FILTER", f"filter '{r['filter']}' ok", ln)

        if r["info"] in (None, ""):
            add("ERROR", "INFO", "info is empty, use '.' if absent", ln)

        if r["format"]:
            keys = r["format"].split(":")
            if "GT" in keys and keys[0] != "GT":
                add("ERROR", "FORMAT_GT_ORDER", "GT must be first in FORMAT", ln)
            missing = [k for k in keys if k not in hdr["format"]]
            if missing:
                add("WARNING", "FORMAT", f"undeclared format keys: {missing}", ln)
            if "GT" in keys:
                gt_i = keys.index("GT")
                for si, sv in enumerate(r["samples"]):
                    sub = sv.split(":")
                    if gt_i >= len(sub):
                        add("ERROR", "GT", f"sample {si} missing GT", ln)
                        continue
                    gt = sub[gt_i]
                    alleles = re.split(r"[/|]", gt)
                    bad_tok = [a for a in alleles if not re.match(r"^(\d+|\.)$", a)]
                    if bad_tok:
                        add("ERROR", "GT", f"sample {si} gt '{gt}' bad tokens {bad_tok}", ln)
                    else:
                        oor = [a for a in alleles if a != "." and int(a) > len(r["alts"])]
                        if oor:
                            add("ERROR", "GT", f"sample {si} gt '{gt}' allele index {oor} out of range", ln)
                        else:
                            add("PASS", "GT", f"sample {si} gt '{gt}' ok", ln)

        if r["chrom"] and r["pos"] is not None:
            c = r["chrom"]
            if seen_chroms and seen_chroms[-1] != c and c in seen_chroms:
                add("WARNING", "SORT", f"chrom '{c}' reappears after another chrom", ln)
                last_pos.pop(c, None)
            if c not in seen_chroms:
                seen_chroms.append(c)
            if c not in last_pos:
                last_pos[c] = r["pos"]
            elif r["pos"] < last_pos[c]:
                add("ERROR", "SORT", f"pos {r['pos']} on '{c}' out of order (prev {last_pos[c]})", ln)
            else:
                last_pos[c] = r["pos"]

    nerr  = sum(1 for c in checks if c["severity"] == "ERROR")
    nwarn = sum(1 for c in checks if c["severity"] == "WARNING")
    npass = sum(1 for c in checks if c["severity"] == "PASS")
    return {
        "file": path,
        "status": "FAILED" if nerr else ("PASSED_WITH_WARNINGS" if nwarn else "PASSED"),
        "errors": nerr, "warnings": nwarn, "passed": npass, "checks": checks,
    }


def load_fasta(path):
    seqs = {}
    name = None
    chunks = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(">"):
                if name:
                    seqs[name] = "".join(chunks)
                name = line[1:].split()[0]
                chunks = []
            else:
                chunks.append(line)
    if name:
        seqs[name] = "".join(chunks)
    return seqs


def check_ref(result, vcf_path, fa_path):
    seqs = load_fasta(fa_path)
    hdr, recs = parse_vcf(vcf_path)
    for r in recs:
        if "parse_error" in r or not r["chrom"] or r["pos"] is None or not r["ref"]:
            continue
        if any(b not in VALID for b in r["ref"]):
            continue
        chrom, pos, ref_allele = r["chrom"], r["pos"], r["ref"]

        # handle chr prefix mismatch between vcf and fasta
        ref_chrom = chrom
        if chrom not in seqs:
            alt = chrom.lstrip("chr") if chrom.startswith("chr") else f"chr{chrom}"
            ref_chrom = alt if alt in seqs else None

        if ref_chrom is None:
            result["checks"].append({"severity": "ERROR", "rule": "REF_CONTIG",
                "line": r["line"], "message": f"chrom '{chrom}' not in reference"})
            result["errors"] += 1
            continue

        actual = seqs[ref_chrom][pos-1 : pos-1+len(ref_allele)].upper()
        if not actual:
            result["checks"].append({"severity": "ERROR", "rule": "REF_BOUNDS",
                "line": r["line"], "message": f"{chrom}:{pos} out of bounds"})
            result["errors"] += 1
        elif actual != ref_allele.upper():
            result["checks"].append({"severity": "ERROR", "rule": "REF_MISMATCH",
                "line": r["line"], "message": f"ref '{ref_allele}' != fasta '{actual}' at {chrom}:{pos}"})
            result["errors"] += 1
            result["status"] = "FAILED"
        else:
            result["checks"].append({"severity": "PASS", "rule": "REF_MATCH",
                "line": r["line"], "message": f"ref '{ref_allele}' matches at {chrom}:{pos}"})
            result["passed"] += 1


def find_inputs():
    vcf_dir = "input/vcf"
    ref_dir = "input/reference"
    runs = []

    vcf_files = sorted([f for f in os.listdir(vcf_dir) if f.endswith(".vcf")]) if os.path.isdir(vcf_dir) else []

    for vcf_file in vcf_files:
        stem = vcf_file.replace(".vcf", "")
        vcf_path = os.path.join(vcf_dir, vcf_file)
        ref_path = None

        if os.path.isdir(ref_dir):
            refs = [f for f in os.listdir(ref_dir) if f.endswith((".fa", ".fasta"))]
            exact = [f for f in refs if f.split(".")[0] == stem]
            if exact:
                ref_path = os.path.join(ref_dir, exact[0])
            elif len(refs) == 1:
                ref_path = os.path.join(ref_dir, refs[0])

        runs.append({"id": stem, "vcf": vcf_path, "ref": ref_path})

    return runs


def write_csv(results, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["run_id", "file", "status", "errors", "warnings", "passed"])
        w.writeheader()
        for r in results:
            w.writerow({"run_id": r["run_id"], "file": r["file"], "status": r["status"],
                        "errors": r["errors"], "warnings": r["warnings"], "passed": r["passed"]})


def write_graphs(results, out_dir):
    ids      = [r["run_id"] for r in results]
    errors   = [r["errors"]   for r in results]
    warnings = [r["warnings"] for r in results]
    passed   = [r["passed"]   for r in results]
    x = range(len(ids))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, errors,   label="errors",   color="#f44336", alpha=0.85)
    ax.bar(x, warnings, label="warnings", color="#ff9800", alpha=0.85, bottom=errors)
    ax.set_xticks(list(x))
    ax.set_xticklabels(ids, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("count")
    ax.set_title("errors and warnings per run")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "errors_per_run.png"), dpi=150)
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, passed,   label="passed",   color="#4caf50", alpha=0.85)
    ax.bar(x, warnings, label="warnings", color="#ff9800", alpha=0.85, bottom=passed)
    ax.bar(x, errors,   label="errors",   color="#f44336", alpha=0.85,
           bottom=[p+w for p, w in zip(passed, warnings)])
    ax.set_xticks(list(x))
    ax.set_xticklabels(ids, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("checks")
    ax.set_title("check results per run")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "check_results.png"), dpi=150)
    plt.close()

    rule_errs = {}
    for r in results:
        for c in r["checks"]:
            if c["severity"] == "ERROR":
                rule_errs[c["rule"]] = rule_errs.get(c["rule"], 0) + 1
    if rule_errs:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(rule_errs.keys(), rule_errs.values(), color="#f44336", alpha=0.85)
        ax.set_ylabel("total errors")
        ax.set_title("errors by rule")
        plt.xticks(rotation=30, ha="right", fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "errors_by_rule.png"), dpi=150)
        plt.close()


# --- run ---
print("=" * 50)
print("  VCF Validator")
print("=" * 50)

runs = find_inputs()
if not runs:
    print("no vcf files found in input/vcf/")
    sys.exit(1)

print(f"\nfound {len(runs)} vcf file(s) to validate\n")
all_results = []

for run in runs:
    print(f"  validating {os.path.basename(run['vcf'])} ...")
    result = validate_vcf(run["vcf"])
    print(f"    structural checks done")
    if run["ref"]:
        print(f"    checking against reference, please wait ...")
        check_ref(result, run["vcf"], run["ref"])
        print(f"    reference check done")
    result["run_id"] = run["id"]
    all_results.append(result)
    print(f"    result: {result['status']}  errors={result['errors']}  warnings={result['warnings']}  passed={result['passed']}")
    print()

json_path = f"output/results_{ts}.json"
csv_path  = f"output/results_{ts}.csv"
graphs_dir = f"output"

print("writing results ...")
print("  saving JSON, please wait ...")
with open(json_path, "w") as f:
    json.dump({"timestamp": ts, "total": len(all_results),
               "passed":   sum(1 for r in all_results if r["status"] == "PASSED"),
               "warnings": sum(1 for r in all_results if r["status"] == "PASSED_WITH_WARNINGS"),
               "failed":   sum(1 for r in all_results if r["status"] == "FAILED"),
               "runs": all_results}, f, indent=2)
print("  JSON done")

print("  saving CSV, please wait ...")
write_csv(all_results, csv_path)
print("  CSV done")

print("  generating graphs, please wait ...")
write_graphs(all_results, graphs_dir)
print("  graphs done")

passed  = sum(1 for r in all_results if r["status"] == "PASSED")
warned  = sum(1 for r in all_results if r["status"] == "PASSED_WITH_WARNINGS")
failed  = sum(1 for r in all_results if r["status"] == "FAILED")

print()
print("=" * 50)
print(f"  done.  {len(all_results)} run(s)  |  passed={passed}  warnings={warned}  failed={failed}")
print("=" * 50)
print()
print("output files:")
print(f"  {json_path}")
print(f"  {csv_path}")
print(f"  output/errors_per_run.png")
print(f"  output/check_results.png")
print(f"  output/errors_by_rule.png")
