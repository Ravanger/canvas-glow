# SPICE verification of the guide circuits

Simulation scratch for scrutinizing `docs/GUIDE.md` / `docs/GUIDE-IC.md`
(discrete + NE555 PWM versions). Investigation only — nothing here changes
the guides. The results below come from these sims plus an independent
external sim (ngspice 42, behavioral 555) and analytic derivations.

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

Run from this directory (`cd sim && $NGSPICE -b disc_mid.cir > log 2>&1`,
then `python3 parse_tran.py log --col "v(rail)"`). Note: quote vector names —
zsh glob-expands the parentheses.

## Running ngspice without root

The .debs (Debian/Ubuntu pool packages, cached in `/tmp/opencode/spice/` —
ephemeral) are extracted, not installed:

```sh
mkdir -p /tmp/opencode/spice/root
dpkg -x ngspice0_47+ds-1_amd64.deb        /tmp/opencode/spice/root
dpkg -x libngspice0_47+ds-1_amd64.deb     /tmp/opencode/spice/root
export LD_LIBRARY_PATH=/tmp/opencode/spice/root/usr/lib/x86_64-linux-gnu
NGSPICE=/tmp/opencode/spice/root/usr/bin/ngspice

$NGSPICE -b sanity.cir > sanity.log 2>&1
python3 parse_tran.py sanity.log --col 1          # v(out)
```

Re-download the .debs with `apt-get download ngspice libngspice0` (or from
the Debian pool). ngspice 44.2 and 46 were also tested; behavior notes below
apply to all of them.

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
