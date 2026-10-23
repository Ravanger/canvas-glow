#!/usr/bin/env python3
"""Flatten a subcircuit from an ngspice lib file into a standalone fragment.

ngspice 47 cannot print subcircuit-internal node voltages (v(x1:node) reports
"vector not available"), so to probe internal nodes the subcircuit body is
inlined here: internal node names get an `i_` prefix, pin names are left as-is.
`.model` lines inside the subcircuit block pass through unchanged.

Usage:
    flatten_subckt.py LIBFILE SUBCKT_NAME OUTFILE
"""
import sys


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    libpath, name, outpath = sys.argv[1], sys.argv[2], sys.argv[3]
    lib = open(libpath).read().splitlines()
    start = next(i for i, l in enumerate(lib)
                 if l.split()[:2] == [".subckt", name])
    end = next(i for i, l in enumerate(lib) if i > start and l.strip() == ".ends")
    pins = set(lib[start].split()[2:])
    body = []
    for l in lib[start + 1:end]:
        s = l.split(";")[0].strip()      # strip inline ; comments (bug: they corrupt node lists)
        if not s or s.startswith("*"):
            continue
        toks = s.split()
        dev, parts = toks[0], toks[1:]

        def ren(n):
            return n if n in pins else "i_" + n

        if dev[0] == "R":
            body.append(f"{dev} {ren(parts[0])} {ren(parts[1])} {parts[2]}")
        elif dev[0] == "Q":
            body.append(f"{dev} {ren(parts[0])} {ren(parts[1])} {ren(parts[2])} {parts[3]}")
        elif dev[0] == "X":
            body.append(dev + " " + " ".join(ren(n) for n in parts[:-1]) + " " + parts[-1])
        else:
            body.append(l)               # .model etc. pass through
    open(outpath, "w").write("\n".join(body) + "\n")
    print(f"wrote {outpath} ({len(body)} lines)")


if __name__ == "__main__":
    main()
