"""Re-check of the full-knob supply current and the discrete start-up case.

Builds each netlist, runs ngspice in batch mode, reads the wrdata output and
reports time-weighted averages, so no print-table parsing is involved.

    python recheck.py current     # supply current at both knob ends, both designs
    python recheck.py startup     # discrete oscillator on slow supply ramps
    python recheck.py knob        # discrete: power up at the bottom, then turn the knob up

Needs ngspice_con (or ngspice) on PATH. Netlists and data land in ./out/.
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NGSPICE = shutil.which("ngspice_con") or shutil.which("ngspice")

STRIP = {"l": 9.19, "s": 13.02}

DISCRETE = """* discrete astable (GUIDE.md), recheck: {tag}
.include {lib}
Vs src 0 PWL(0 0 {ramp} {vs})
Rsrc src vcc {rsrc}
Cbulk vcc bulk 1000u
Resr bulk 0 0.05
Cdec vcc 0 100u
Cdec2 vcc 0 100n
RC1 vcc q1c 10k
RC2 vcc q2c 10k
C1 q1c q2b 2.2n
C2 q2c q1b 2.2n
RpotA vcc endA {ra}
RpotB vcc endB {rb}
Ra endA q2b 4.7k
Rb endB q1b 100k
Q1 q1c q1b 0 {q_small}
Q2 q2c q2b 0 {q_small}
Rq3b q2c q3b 47k
Q3 q3c q3b 0 {q_small}
Rq3c q3c q4b 1k
Rpq4 q4b vcc 10k
Q4 rail q4b vcc {q_pnp}
Rd1 rail b_l1 180
Rd2 rail b_l2 180
Rd3 rail b_s1 270
Rd4 rail b_s2 270
Rpl1 b_l1 0 10k
Rpl2 b_l2 0 10k
Rpl3 b_s1 0 10k
Rpl4 b_s2 0 10k
Ql1 c_l1 b_l1 0 {q_pow}
Ql2 c_l2 b_l2 0 {q_pow}
Qs1 c_s1 b_s1 0 {q_pow}
Qs2 c_s2 b_s2 0 {q_pow}
RsL1 vcc c_l1 {l}
RsL2 vcc c_l2 {l}
RsS1 vcc c_s1 {s}
RsS2 vcc c_s2 {s}
.options reltol=1e-4
.tran {step} {stop}
.control
run
wrdata {data} i(Vs) v(vcc) v(rail) v(q2c) v(c_l1) v(q1c)
quit
.endc
"""

# The 555 is replaced by an ideal PWM source at the duty the 555a sims measured;
# its pin-3 high level is a Thevenin source fitted to the datasheet VOH figures.
IC = """* IC PWM output stage (GUIDE-IC), recheck: {tag}
.include {lib}
Vs src 0 dc {vs}
Rsrc src vcc {rsrc}
Cbulk vcc bulk 1000u
Resr bulk 0 0.05
Vpwm pin3o 0 PULSE(0 {voc} 0 50n 50n {ton} {period})
Rout pin3o out {rout}
Iq vcc 0 {iq}
Rb1 out b1 100
Rb2 out b2 100
Rb3 out b3 150
Rb4 out b4 150
Q1l c1 b1 0 {q_pow}
Q2l c2 b2 0 {q_pow}
Q3l c3 b3 0 {q_pow}
Q4l c4 b4 0 {q_pow}
Rs1 vcc c1 {l}
Rs2 vcc c2 {l}
Rs3 vcc c3 {s}
Rs4 vcc c4 {s}
.tran {step} {stop}
.control
run
wrdata {data} i(Vs) v(vcc) v(out) v(c1)
quit
.endc
"""


def run(text, tag):
    OUT.mkdir(exist_ok=True)
    cir = OUT / f"{tag}.cir"
    data = OUT / f"{tag}.dat"
    cir.write_text(text.replace("{data}", data.name), encoding="utf-8", newline="\n")
    log = subprocess.run([NGSPICE, "-b", cir.name], cwd=OUT, capture_output=True, text=True)
    if not data.exists():
        sys.exit(f"ngspice produced no data for {tag}:\n{log.stdout[-2000:]}\n{log.stderr[-2000:]}")
    rows = []
    for line in data.read_text().splitlines():
        parts = line.split()
        try:
            vals = [float(x) for x in parts]
        except ValueError:
            continue
        rows.append(vals[0::2][:1] + vals[1::2])
    return rows


def avg(rows, col, t0, t1):
    acc = 0.0
    for a, b in zip(rows, rows[1:]):
        lo, hi = max(a[0], t0), min(b[0], t1)
        if hi > lo:
            acc += 0.5 * (a[col] + b[col]) * (hi - lo)
    return acc / (t1 - t0)


def crossings(rows, col, level, t0):
    n = 0
    for a, b in zip(rows, rows[1:]):
        if a[0] >= t0 and (a[col] - level) * (b[col] - level) < 0:
            n += 1
    return n


def duty(rows, col, level, t0, t1):
    on = 0.0
    for a, b in zip(rows, rows[1:]):
        lo, hi = max(a[0], t0), min(b[0], t1)
        if hi > lo and 0.5 * (a[col] + b[col]) > level:
            on += hi - lo
    return on / (t1 - t0)


POT = {"endA": ("1", "500k"), "mid": ("250k", "250k"), "endB": ("500k", "1")}
PARTS = {
    "bc337-25": {"q_small": "2N3904", "q_pnp": "BC327-25", "q_pow": "BC337-25"},
    "bc337-16": {"q_small": "2N3904", "q_pnp": "BC327-25", "q_pow": "BC337-16"},
}


def discrete(tag, pos, vs=5.0, rsrc=0.0, ramp="10u", stop=30e-3, parts="bc337-25"):
    ra, rb = POT[pos] if isinstance(pos, str) else pos[1:]
    text = DISCRETE.format(tag=tag, lib="../vendor.lib", ramp=ramp, vs=vs, rsrc=rsrc or 1e-6,
                           ra=ra, rb=rb, step="2u" if stop > 0.2 else "0.2u", stop=stop, data="{data}", **STRIP, **PARTS[parts])
    return run(text, tag)


def ic(tag, d, vs=5.0, rsrc=0.0, voc=3.6, rout=3.0, iq=4e-3, parts="bc337-25"):
    period = 1.11e-3
    text = IC.format(tag=tag, lib="../vendor.lib", vs=vs, rsrc=rsrc or 1e-6, voc=voc, rout=rout, iq=iq,
                     ton=d * period, period=period, step="0.5u", stop=12e-3, data="{data}",
                     **STRIP, **PARTS[parts])
    return run(text, tag)


def knob():
    print("Discrete: power up at endA (slow ramp), then turn the knob to mid over 50 ms.")
    for ramp in ["10u", "100m"]:
        t_ramp = {"10u": 10e-6, "100m": 0.1}[ramp]
        t0, t1 = t_ramp + 10e-3, t_ramp + 60e-3
        ra = f"r={{1+249k*min(max((time-{t0})/{t1 - t0},0),1)}}"
        rb = f"r={{500k-249k*min(max((time-{t0})/{t1 - t0},0),1)}}"
        tag = f"knob_endA_to_mid_{ramp}"
        r = discrete(tag, ("x", ra, rb), ramp=ramp, stop=t1 + 30e-3)
        q1 = [x[6] for x in r if t_ramp + 5e-3 < x[0] < t0]
        q2 = [x[4] for x in r if t_ramp + 5e-3 < x[0] < t0]
        n = crossings(r, 4, 2.5, t1)
        print(f"{tag:26s} at endA: q1c {min(q1):5.3f}..{max(q1):5.3f} V, q2c {min(q2):5.3f}..{max(q2):5.3f} V; "
              f"after the turn: {n} q2c crossings in 30 ms, duty {duty(r, 3, 2.5, t1, t1 + 30e-3)*100:4.1f} %")


def current():
    print("Supply current, time-averaged over the last 20 ms (discrete) / 10 ms (IC).")
    print("Columns: case | supply A | duty | board V min | strip-on collector V")
    for parts in PARTS:
        for vs, rsrc in [(5.0, 0.0), (5.0, 0.1), (5.25, 0.0), (4.75, 0.0)]:
            for pos in ["endA", "endB"]:
                tag = f"disc_{pos}_{parts}_{vs}V_{rsrc}R"
                r = discrete(tag, pos, vs=vs, rsrc=rsrc, parts=parts)
                i = -avg(r, 1, 10e-3, 30e-3)
                d = duty(r, 3, 2.5, 10e-3, 30e-3)
                vmin = min(x[2] for x in r if x[0] > 10e-3)
                von = min(x[5] for x in r if x[0] > 10e-3)
                print(f"{tag:34s} {i:6.3f} A  duty {d*100:5.1f} %  Vboard {vmin:5.3f}  Vce(on) {von:5.3f}")
    for parts in PARTS:
        for d in [0.81, 0.83]:
            for vs, rsrc, voc, rout in [(5.0, 0.0, 3.6, 3.0), (5.0, 0.0, 3.6, 8.5), (5.25, 0.0, 3.85, 3.0),
                                        (5.0, 0.1, 3.6, 3.0)]:
                tag = f"ic_{int(d*100)}_{parts}_{vs}V_{rsrc}R_rout{rout}"
                r = ic(tag, d, vs=vs, rsrc=rsrc, voc=voc, rout=rout, parts=parts)
                i = -avg(r, 1, 2e-3, 12e-3)
                voh = max(x[3] for x in r if x[0] > 2e-3)
                von = min(x[4] for x in r if x[0] > 2e-3)
                print(f"{tag:34s} {i:6.3f} A  duty {d*100:5.1f} %  VOH {voh:5.3f}  Vce(on) {von:5.3f}")


def startup():
    print("Discrete start-up: supply ramps 0 -> 5 V; count q2c crossings of 2.5 V after the ramp.")
    for pos in ["endA", "mid", "endB"]:
        for ramp, stop in [("10u", 20e-3), ("1m", 20e-3), ("10m", 40e-3), ("100m", 130e-3), ("1", 1.03)]:
            tag = f"start_{pos}_{ramp}"
            t_ramp = {"10u": 10e-6, "1m": 1e-3, "10m": 10e-3, "100m": 0.1, "1": 1.0}[ramp]
            r = discrete(tag, pos, ramp=ramp, stop=stop)
            n = crossings(r, 4, 2.5, t_ramp + 5e-3)
            q2c = [x[4] for x in r if x[0] > t_ramp + 5e-3]
            print(f"{tag:22s} crossings in last {(stop - t_ramp - 5e-3)*1e3:5.1f} ms: {n:4d}   "
                  f"q2c {min(q2c):5.3f}..{max(q2c):5.3f} V")


if __name__ == "__main__":
    if not NGSPICE:
        sys.exit("ngspice not found on PATH")
    {"current": current, "startup": startup, "knob": knob}[sys.argv[1]]()
