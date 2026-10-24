# Canvas Glow

A backlit nightlight behind a stretched-canvas painting: a dimmable
halo with a brightness knob. One 5 V COB strip, one 5 V 2 A adapter,
two dimmer versions with the same strip and power.

The knob sets the duty of a PWM signal at about 1 kHz (0.9 kHz on
the IC version), and four BC337 transistors switch the four strip
segments. Bench-test on a breadboard first, with no soldering, then
build the finished light on perfboard behind the painting.

**Status:** the circuits are worked out on paper and in SPICE
simulations (`sim/`), but no one has built and measured one yet. Every
current and voltage in the guides is a calculation or a simulation,
and the checks in each guide's section 8 are how you confirm them on
your build.

## Features

- Knob-only brightness
- ~1 kHz PWM
- Breadboard test
- One 5 V 2 A adapter for everything
- Strip split into four segments, one transistor each, so every
  transistor stays inside its rating
- Optional polyfuse at the power entry
- Optional white back reflector behind the strip
- Optional 3D-printed mounts (strip clips, perfboard box, jack
  mount, knob bracket, wall spacers) in PETG

## The two versions

| Version | PWM source | Build guide | Breadboard test |
| ------- | ---------- | ----------- | --------------- |
| Discrete | Two-transistor oscillator (~1 kHz), no ICs | [docs/GUIDE.md](docs/GUIDE.md) | [docs/BREADBOARD.md](docs/BREADBOARD.md) |
| IC | NE555 timer (~0.9 kHz), same four BC337 output channels | [docs/GUIDE-IC.md](docs/GUIDE-IC.md) | [docs/BREADBOARD-IC.md](docs/BREADBOARD-IC.md) |

Both versions use the same strip, power entry, light layout, and
output stage. The only change is what makes the PWM: the discrete
version uses a Q1/Q2 astable with a Q3 buffer and a Q4 high-side
switch; the IC version replaces all of that with one NE555 driving
the BC337 bases directly.

### Which version?

- **IC (NE555)** if you want the fewest parts and the simplest
  wiring: one chip and two diodes make the PWM, and a latching switch
  on its RESET pin can add a real off switch. The bottom of the knob
  is a faint glow (about 2% duty).
- **Discrete** if you have no 555 or want to see how a PWM
  oscillator works from transistors: three 2N3904s and a BC327 more,
  and no off switch (unplug the adapter). The bottom of the knob is
  off or a faint glow, depending on the parts.

Pick one and follow only its two pages; either guide works on its
own, and the IC guide repeats the shared sections.

### How to follow a build

1. Read your version's build guide sections 1–3: parts, power
   budget, and how it works.
2. Buy the parts in section 1 and check the adapter polarity and
   transistor pin orders (section 5).
3. Do the breadboard test, steps 1 and 2. No soldering yet.
4. Follow the build order in section 7, one step at a time.
5. Run every check in section 8 before leaving the light on
   unattended.
6. If something is off, look it up in section 9.

## Hardware

See the build guide for the full parts table. In short: 5 V COB
strip, 320 LEDs/m, 8 W/m, 3000 K (about 1.2 m total); B500K
potentiometer with a knob cap; BC337 × 4; 2N3904 × 3 and BC327 × 1
(discrete) or NE555 and 1N4148 × 2 (IC); 5 V 2 A adapter with a
barrel jack pigtail; perfboard, wire, and solder for the finished
light; a breadboard and jumper wires for the bench test.

You need basic through-hole soldering, a multimeter with a 10 A
range, and the patience to check transistor pin orders: they vary
by maker, and the guides show how to find them with the meter.

## Safety

- It is a 5 V circuit, but the strip feed carries up to about 1.6 A: use
  the wire gauges in the parts table and heat-shrink every joint.
- Check the adapter is centre-positive before connecting anything.
  Nothing protects the board from a reversed adapter, and a reversed
  electrolytic capacitor can overheat or burst.
- Keep strips, wires and the board at least 1 cm off the canvas, and
  run the 30-minute heat check in section 8 before leaving it on
  unattended.
- If the light ever jumps to full and the knob does nothing, unplug
  it: that draws more than the adapter budget (section 9 of each
  guide).

## Configuration

The values below are the configuration the guides are worked out for.
Changing the strip length changes the power budget, so re-check
[the power budget](docs/GUIDE.md#2-power-budget) before going longer.

- Strip layout: 2 × 0.34 m long sides, 2 × 0.24 m short sides
  (about 1.2 m total, cut only on the printed cut marks)
- Brightness knob: B500K linear potentiometer
- Polyfuse 2–2.5 A at the power entry: optional
- IC version only, real off switch: optional latching switch on
  the NE555 RESET pin (pin 4), with a 10 kΩ pull-up
- Discrete version: no off switch — unplug the adapter to switch off
- Back reflector: optional white foam board or thick white card
- 3D prints: optional, PETG only (PLA softens around 55 °C)

The values shipped in the guides are worked out for one painting,
not a recommendation for every painting: a different frame size needs
its own strip lengths and its own power-budget check. Cut pitch and
rated W/m vary between strips — use your strip's (current = W/m ÷ 5 V
× length) and recompute [the power budget](docs/GUIDE.md#2-power-budget)
with your actual cut lengths.

## Limitations

- No true off: the bottom of the knob leaves a faint glow — unplug
  the adapter to switch off. The IC version can add a real off
  switch on the NE555 RESET pin ([GUIDE-IC, Troubleshooting](docs/GUIDE-IC.md#9-troubleshooting)).

## Documentation

Documentation lives in `docs/`, next to the build it describes.
Each file in `docs/` is written as a standalone page, and every page
ends with Previous / Contents / Next links where one exists, in the
order below, so you can read straight through or jump to a single
page:

1. [Discrete build guide](docs/GUIDE.md) — parts, power budget,
   how it works, circuit, build order, checks, troubleshooting
2. [Discrete breadboard test](docs/BREADBOARD.md) — bench steps 1
   and 2, no soldering
3. [IC build guide](docs/GUIDE-IC.md) — the NE555 version
4. [IC breadboard test](docs/BREADBOARD-IC.md) — bench steps 1 and
   2 for the IC version

The original v5 guide is kept for history:
[canvas-glow-v5.html](docs/reference/canvas-glow-v5.html).

### Terms used in the guides

- **PWM, duty**: the strip is switched fully on and off about a
  thousand times a second; the duty is the fraction of each cycle it
  is on, and the eye sees it as brightness.
- **Saturated**: a transistor switched fully on, with only a few
  tenths of a volt across it.
- **VEBO, hFE**: a transistor's maximum reverse base-emitter voltage,
  and its current gain.
- **Low-ESR**: an electrolytic capacitor with a low internal
  resistance, made for supplies that switch current.
- **PTC / polyfuse**: a resettable fuse that goes high-resistance
  when too much current heats it.
- **Star point**: the one spot (the barrel jack's −) where every
  ground wire meets, so heavy strip current does not flow through
  the oscillator's ground.

The simulation figures in the guides come from `sim/` — SPICE
netlists and run notes; see [sim/README.md](sim/README.md) for what
was run and how to reproduce them.

## License

Public domain: [CC0 1.0 Universal](LICENSE). Use, copy, modify and
sell any of it, no attribution needed. One exception:
`sim/vendor.lib` is copied from the GPL-3.0
[KiCad-Spice-Library](https://github.com/kicad-spice-library/KiCad-Spice-Library)
and stays under GPL-3.0.

---

[Next: Discrete build guide →](docs/GUIDE.md)

