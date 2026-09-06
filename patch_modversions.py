"""Relax MODVERSIONS symbol CRC checks in kernel/module.c.

The device's 187 first-stage vendor modules are prebuilt (Xiaomi 5.10.168/198
trees) and their genksyms CRCs do not textually match any rebuildable tree.
The GKI KABI discipline keeps the actual struct layouts compatible (the
device's working kernel proves it), so mismatched CRCs are safe to accept.
Layout-breaking config changes are still forbidden; kABI padding patches must
be used for task_struct additions (see droidspaces_ksu.fragment).
"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'kernel/module.c'
src = open(path).read()

if 'yunluo-ksu relax' in src:
    print('already patched')
    sys.exit(0)

marker = 'static int check_version(const struct load_info *info,'
i = src.index(marker)
j = src.index('{', i)
patched = src[:j + 1] + (
    '\n\t/* yunluo-ksu relax: accept prebuilt vendor modules despite CRC diffs;\n'
    '\t * struct layouts stay KMI-compatible, see droidspaces_ksu.fragment */\n'
    '\treturn 1;\n'
) + src[j + 1:]

# check_modstruct_version routes through check_version, so it is covered.
open(path, 'w').write(patched)
print('patched', path)

# arch/arm64: force the global stack-protector guard. STACKPROTECTOR_PER_TASK
# is def_bool y (no prompt, so a config fragment cannot disable it) and newer
# clang meets CC_HAVE_STACKPROTECTOR_SYSREG, which stops exporting
# __stack_chk_guard — imported by 139 prebuilt vendor modules.
kpath = 'arch/arm64/Kconfig'
ksrc = open(kpath).read()
old = 'config STACKPROTECTOR_PER_TASK\n\tdef_bool y'
new = 'config STACKPROTECTOR_PER_TASK\n\tdef_bool n'
if old in ksrc:
    open(kpath, 'w').write(ksrc.replace(old, new))
    print('patched', kpath)
elif new in ksrc:
    print(kpath, 'already patched')
else:
    print('WARNING: STACKPROTECTOR_PER_TASK pattern not found in', kpath)
    sys.exit(1)
