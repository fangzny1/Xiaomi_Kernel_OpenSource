import json, sys

# kernel_crcs.txt: "<symbol> <crc>" (hex), one per line
kernel_crcs = {}
for line in open('kernel_crcs.txt'):
    parts = line.split()
    if len(parts) == 2:
        try:
            kernel_crcs[parts[0]] = int(parts[1], 16)
        except ValueError:
            pass

modules = json.load(open('module_crcs.json'))
print(f"kernel exports {len(kernel_crcs)} versioned symbols")

ml = kernel_crcs.get('module_layout')
print(f"module_layout kernel CRC: {hex(ml) if ml is not None else 'MISSING'}")

report = {}
ok_modules = 0
for name, wanted in sorted(modules.items()):
    bad = []
    missing = []
    for sym, crc in wanted.items():
        if sym not in kernel_crcs:
            missing.append(sym)
        elif kernel_crcs[sym] != crc:
            bad.append(sym)
    if not bad and not missing:
        ok_modules += 1
    report[name] = {'mismatched': bad, 'missing': missing}

print(f"\n=== VERDICT: {ok_modules}/{len(modules)} modules fully compatible ===\n")
for name, r in sorted(report.items()):
    if r['mismatched'] or r['missing']:
        print(f"{name}: {len(r['mismatched'])} mismatched, {len(r['missing'])} missing")
        for s in r['mismatched'][:5]:
            print(f"    MISMATCH {s}: want {hex(modules[name][s])} got {hex(kernel_crcs[s]) if s in kernel_crcs else '?'}")
        for s in r['missing'][:5]:
            print(f"    MISSING  {s}")
json.dump(report, open('crc_report.json', 'w'), indent=1)
