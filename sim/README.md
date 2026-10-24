# SPICE verification of the guide circuits

SPICE checks of the circuits in `docs/GUIDE.md` and `docs/GUIDE-IC.md`.
The supply-current, saturation and start-up figures the guides quote come
from the **Recheck** section at the end (`recheck.py`, vendor transistor
models). The earlier runs above it (generic models, `*.cir` files) are kept
for the timing and duty results and as history.

## Installing ngspice

- Windows: `scoop bucket add extras`, then `scoop install extras/ngspice`
  (the binary is `ngspice_con`).
- Debian/Ubuntu: `sudo apt install ngspice`. macOS: `brew install ngspice`.

Any ngspice from 42 on works; 44.2, 46 and 47 were used.

## Files

| File | What | Status |
|---|---|---|
| `555a.lib` | Pure-analog NE555 model (genopa1 comparators + cross-coupled NPN SR latch at 1 k scale + real discharge/output transistors; follower high side so it can represent the ~90 mA pin-3 source load) | sanity-passed |
| `sanity.cir` | Standard astable: RA=1 k→DISCH, RB=5 k→node, C=0.5 µF, TRIG=THR=node | **PASS**: ~255 Hz / 3.92 ms period (expected ~247–262 Hz), clean 40 ms window, no aborts |
| `models.lib` | Generic 1N4148 / 2N3904 / BC327 / BC337 models for the real-circuit sims | ready |
| `parse_tran.py` | Merges ngspice's paginated print tables and analyzes a column (freq, duty, levels) | ready |
| `flatten_subckt.py` | Inlines a subcircuit with `i_`-prefixed internal nodes (ngspice 47 can't print `v(x1:node)`) | ready |
| `probe.cir` | Internal-node probe for the 555a VOH sag | known t=0 convergence issue, see header |
| `ic_pwm_{endA,mid,endB}.cir` | GUIDE-IC PWM at three knob positions (realistic 1N4148 + full BC337 load) | run clean, results below |
| `disc_{endA,mid,endB}.cir` | GUIDE.md discrete astable at three knob positions (full Q3/Q4/BC337 load) | run clean, results below |
| `ic_tmpl.cir`, `d_tmpl.cir` | Templates for the above; regenerate with `sed s/__RA__/<val>/g` etc. | ready |
| `diag_discrete_q2c.cir` | F1 mechanism diagnostic (endB): extra v(q1b)/v(q3b) probes to show the q2c plateau + collapse step; mathematically identical to `disc_endB.cir`; expected values in its header | verified: q2c plateau 4.243 V, step onto q1b −4.17 V |

Run the earlier netlists from this directory, then parse the print table:

```sh
ngspice -b disc_mid.cir > log 2>&1        # ngspice_con on Windows
python parse_tran.py log --col "v(rail)"
```

Quote vector names: zsh glob-expands the parentheses.

Without root on Debian/Ubuntu, extract the packages instead of installing
them: `apt-get download ngspice libngspice0`, `dpkg -x` each into a folder,
point `LD_LIBRARY_PATH` at its `usr/lib/x86_64-linux-gnu` and run its
`usr/bin/ngspice`.

## ngspice gotchas learned the hard way

- **Line 1 of a netlist is consumed as the circuit title.** A device line on
  line 1 is silently not parsed. Always put a comment / `.title` / blank
  first. (Root-caused with dedicated f1/f2/f3 test netlists.)
- `uic` goes **last** in `.tran tstep tstop uic`.
- `print all` prints a *parameter* named "all" — use explicit
  `print time v(node) ...`.
- Wide print tables **paginate two ways**: (a) every ~57 rows the same
  `Index ...` header is reprinted; (b) when the requested vectors exceed one
  page width, ngspice emits a *continuation table* with the remaining vectors
  that **repeats the time column**. Merging by row index must skip that
  repeated time or every later column shifts (`parse_tran.py` handles both).
- Subcircuit-internal probes fail: `v(x1:nout)` → "vector not available".
  Flatten instead (`flatten_subckt.py`). Caveat: the flattened 555a fails to
  converge at t=0 in ngspice 47 while the subcircuit form runs fine.
- `gnd` is a **ground alias** in ngspice (like `0`, `vss`) — a zero-voltage
  source from `gnd` to `0` is a fatal "shorted VSRC".
- `.tran ... method=trap` → "Undefined parameter [trap]" in this build.
- The genopa1 clamp diode was softened `N=0.01 → N=0.05` for t=0 robustness
  (output rails shift by <30 mV; negligible).

## 555a model — known limitation

No-load VOH in the sim is ~2.6 V, not the ~4.3–4.6 V an ideal follower would
give (latch node sags under the follower's base drive through the 1 k/1 k
path; internal probe pending). A real NE555 delivers ~3.3–3.5 V at the
guide's ~90 mA pin-3 load, and the external behavioral-model sim measured
3.53 V — so **pin-3 level claims rely on datasheet + external
sim, not this model**. Timing (comparators, latch switching, discharge) is
verified correct by `sanity.cir`, and the sagged VOH still drives the BC337
base resistors into deep saturation in load sims (19 mA forced vs 9 mA
minimum), so load conclusions hold.

## Circuit facts used by the netlists

- COB strip modeled as constant-current loads linearized at 5 V: long side
  0.544 A → 9.19 Ω, short side 0.384 A → 13.02 Ω (per segment).
- IC PWM: charge Vcc→10 k→pin7/wiper→RpotA→endA→D1→cap node; discharge
  node→D2→100 k→endB→RpotB→wiper→DISCH; TRIG=THR=cap node; pin5 100 nF.
- Discrete astable: RC1=RC2=10 k pull-ups, C1/C2=2.2 nF cross-coupling,
  pot wiper to Vcc with Ra=4.7 k (→Q2B) and Rb=100 k (→Q1B), Q3 2N3904
  (47 k from Q2C) driving Q4 BC327 PNP; rail → 180 Ω/270 Ω → BC337 bases
  (+10 k pulldowns).

## Results (ngspice 47, this machine)

Superseded for the supply-current figures by the recheck below: these runs
use generic BJT models with no collector resistance, so the BC337 saturation
drop and the strip current are off, and they report strip plus base current
rather than the adapter current.

IC PWM (`ic_pwm_*`), steady state:

| Knob | f | duty (pin 3 high) | cap swing | strip avg + base @ full |
|---|---|---|---|---|
| endA | ~901 Hz | 1.6 % | 1.65–3.34 V | 45 mA |
| mid | ~893 Hz | 44.1 % | 1.66–3.34 V | 798 mA |
| endB | ~907 Hz | 81.0 % | 1.65–3.34 V | 1468 mA + ~33 mA ≈ **1.50 A** |

Discrete (`disc_*`), steady state:

| Knob | rail peak | rail DC avg | duty | period (long pulses) | strip avg @ full |
|---|---|---|---|---|---|
| endA | 4.90 V | 0.074 V | 0.33 % (faint-glow blips, ~2–4 kHz) | — | 40 mA |
| mid | 4.92 V | 2.29 V | ~48 % | ~0.87 ms | 860 mA |
| endB | 4.92 V | 3.87 V | 85.4 % | ~0.78–0.85 ms | 1449 mA + ~66 mA ≈ **1.52 A** |

Caveats: the discrete runs are numerically noisy near BJT cutoff
(step-to-step convergence oscillation produces spurious 1–2 µs rail blips);
duty and DC averages are time-averaged and robust, period needs the
long-pulse pairing shown above. The 555a VOH sag (1.8 V under full load)
does not affect any timing or saturation conclusion — see "known limitation".

EndB duty is also **trajectory-sensitive in this generic BJT model**: two
mathematically identical netlists (`disc_endB.cir` and `diag_discrete_q2c.cir`)
give different sample-count duties (85.4 % vs 78.4 %) while their long-pulse
pairing agrees at ~82–86 % per cycle in both. The cleaner external sim's
85.6–85.9 % is taken as the best estimate; this model's band
(78–86 %) is noted as a caveat.

## Recheck: supply current and start-up (vendor models)

`recheck.py` builds each netlist, runs ngspice and time-averages the
adapter current from `wrdata` output, so no print-table parsing is involved.
It uses `vendor.lib`: Philips 2N3904, BC327-25, BC337-25 and BC337-16 models
from the KiCad SPICE library (source and commit in its header). Run from this
directory with `ngspice_con` on PATH (on Windows: `scoop install extras/ngspice`):

    python recheck.py current
    python recheck.py startup
    python recheck.py knob

The supply is an ideal source with an optional series resistance for the feed,
then 1000 µF bulk (50 mΩ ESR), 100 µF and 100 nF. The strip is the same
linearized load as above (9.19 Ω / 13.02 Ω per segment at 5 V). In the IC runs
the 555 is replaced by an ideal PWM source at the duty the 555a runs measured
(81 %) and at 83 %, with pin 3 as 3.6 V behind 3 Ω (≈3.3 V at the ~90 mA load,
the datasheet typical) or behind 8.5 Ω (≈3.0 V, toward the datasheet minimum),
plus 4 mA for the 555 and its timing network. The current pin 3 sources is
drawn from the supply, as in the real chip.

Adapter current at the top of the knob (ngspice 47, 2026-10-24):

| Case | Discrete (85.5 % duty, as simulated) | IC at 81 % duty (set) | IC at 83 % duty (set) |
|---|---|---|---|
| 5.00 V, BC337-25 | 1.588 A | 1.507 A | 1.544 A |
| 5.00 V, BC337-16 | 1.587 A | 1.508 A | 1.545 A |
| 5.00 V + 0.1 Ω feed | 1.540 A | 1.459 A | 1.495 A |
| 5.25 V adapter | 1.669 A | 1.585 A | 1.624 A |
| 4.75 V adapter | 1.506 A | — | — |

The IC figures include the base drive pin 3 sources from the supply (~0.07 A).
The weaker pin-3 drive (8.5 Ω) lowers the IC total by under 10 mA: the BC337s
stay saturated. BC337 Vce when on is 0.23–0.25 V in every case, so the strip
sees ~4.76 V from a 5.00 V supply and its ON current is ~1.77 A, not 1.856 A.
The discrete drive rail sits at 4.93 V when on and averages 4.22 V DC at full.
Knob at the bottom draws 2 mA (discrete): the strip is off.

Discrete start-up (`startup`, `knob`): the supply ramps 0 → 5 V in 10 µs,
1 ms, 10 ms, 100 ms and 1 s. At mid and top the oscillator starts on every
ramp (~1.1 kHz). At the bottom stop Q1 and Q2 both stay on (q1c 0.08 V,
q2c 0.01 V), so the strip is off; turning the knob up releases it. With a
100 ms power-up at the bottom and a 1 s turn to mid, oscillation starts about
10 % of the way into the turn and runs at 44.8 % duty at mid.

Limits: the strip is a linear load, not an LED model; no noise source, so a
start-up failure that needs noise or part asymmetry would not show; the 555
itself is not in the IC current runs.
