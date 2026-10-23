# Canvas Glow

A backlit nightlight behind a stretched-canvas painting: a dimmable
halo with a brightness knob. One 5 V COB strip, one 5 V 2 A adapter,
two dimmer versions with the same strip and power.

The knob sets the duty of a ~1 kHz PWM signal, and four BC337
transistors switch the four strip segments. Bench-test on a
breadboard first, with no soldering, then build the finished light
on perfboard behind the painting.

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

## Hardware

See the build guide for the full parts table. In short: 5 V COB
strip, 320 LEDs/m, 8 W/m, 3000 K (about 1.2 m total); B500K
potentiometer with a knob cap; BC337 × 4; 5 V 2 A adapter with a
barrel jack pigtail; perfboard, wire, and solder for the finished
light; a breadboard and jumper wires for the bench test.

## Getting started

1. [Discrete build guide](docs/GUIDE.md) — parts, power budget, how
   it works, circuit, build order, checks, troubleshooting
2. [Discrete breadboard test](docs/BREADBOARD.md) — bench steps 1
   and 2 of the build order, no soldering
3. [IC build guide](docs/GUIDE-IC.md) — the same light with an NE555
   making the PWM
4. [IC breadboard test](docs/BREADBOARD-IC.md) — bench steps 1 and 2
   of the IC build order, no soldering

Either guide works on its own; the IC guide repeats the shared
sections.

## Configuration

The values below are the tested configuration from the guides.
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

The values shipped in the guides are the tested configuration, not
a recommendation for every painting: a different frame size needs
its own strip lengths and its own power-budget check.

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

---

[Next: Discrete build guide →](docs/GUIDE.md)

