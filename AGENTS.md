# AGENTS.md

Rules for agents and contributors working on this repository.

## What this repo is

Build guides for a knob-only LED backlight behind a stretched-canvas
painting. Two dimmer versions, same strip and power: a discrete
two-transistor PWM oscillator and an NE555 version. The guides in
`docs/` are the product; the SVGs in `docs/img/` are their drawings.

## Frozen design decisions

Do not change these without the maintainer's say-so:

- No microcontroller, no firmware, no flashing. Knob-only.
- One 5 V 2 A adapter for everything (oscillator and strip).
- The strip is split into four segments, one BC337 each, so every
  transistor stays inside its rating.
- No mode switch, hover sensor, or Wi-Fi control.
- The discrete version's oscillator and the IC version's 555 circuit
  are separate designs; a fix to one does not automatically apply
  to the other.

## Numbers

Never change a number in a guide from memory. Every duty, frequency,
current, and voltage figure in the guides comes from the guide's own
arithmetic, a simulation, or a bench measurement. Changing one needs
a re-check against the circuit, not an edit from recall. If a number
looks wrong, verify it first and say what the check showed.

## Docs structure

- Each file in `docs/` is a standalone page. Keep section numbering
  stable: other work references sections by number.
- Every docs page ends with Previous / Contents / Next links where
  one exists, in the README's reading order: GUIDE → BREADBOARD →
  GUIDE-IC → BREADBOARD-IC.
- Do not split a guide into more pages without asking: section
  references across the guides would break.
- The `reference/` directory holds the original v5 guide for
  history. Do not edit it.

## Workflow

- Work on a branch and open a pull request. The maintainer merges
  through the GitHub web UI.
- Return review work as paste-ready text. Do not post comments,
  merge, or close issues on the maintainer's behalf unless asked.
- One change at a time: a fix commit covers one issue, not a bundle
  of unrelated edits.
