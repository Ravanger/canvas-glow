# AGENTS.md

Rules for agents and contributors working on this repository.

## What this repo is

Build guides for a knob-only LED backlight behind a stretched-canvas
painting. Two dimmer versions, same strip and power: a discrete
two-transistor PWM oscillator and an NE555 version. The guides in
`docs/` are the product; the SVGs in `docs/img/` are their drawings.

## Before you start and before you finish

Run the local checks. There is no CI; this is the only safety net.

    python tools/check.py

Every line must be PASS or WARN, and the exit code 0. A FAIL line
says what is wrong and how to fix it. Fix it; do not edit
`tools/check.py` or `tools/numbers.snapshot` to make a FAIL go away.

Enable the pre-commit hook once per clone. It refuses commits on
`main`, commits touching `docs/reference/`, and commits that fail
the checks:

    git config core.hooksPath .githooks

What the checks enforce:

- `## ` headings in the four docs pages match a frozen list.
- Each page ends with its exact Previous / Contents / Next line.
- Every relative link and `#anchor` resolves.
- `docs/reference/` is byte-identical to the committed copy.
- Every SVG parses as XML.
- No CR line endings.
- Every number-with-unit in the guides and README matches
  `tools/numbers.snapshot`. A FAIL here means a number changed:
  see Numbers below.
- §6 and §11 are identical in both guides. §1, §5, §8 and §10
  print a WARN when they differ; read it and decide if the other
  guide needs the same edit.

## Stop and ask the maintainer

Stop and ask instead of guessing when:

- a task would change a frozen design decision (list below);
- a number looks wrong but you cannot verify it with arithmetic
  you can show, a simulation in `sim/`, or a datasheet value you
  can name;
- a fix seems to need a new page, a renumbered section, or an
  edit in `docs/reference/`;
- you cannot see an SVG rendered and the change is more than a
  label or value;
- the two guides disagree and you do not know which is right.

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

When you change a number: show the arithmetic (or name the sim
file or datasheet parameter) in the commit message, update every
place the same figure appears (both guides, both breadboard pages,
README, `sim/README.md`), then run
`python tools/check.py --update-numbers` and check that the
snapshot diff lists only the numbers you meant to change. A
spelling change (`5V` → `5 V`) also shows up there; that is
expected.

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
- Shared sections (§§1, 5, 6, 10, 11 and the Checks section) must be
  edited in both guides unless the difference is intentional;
  GUIDE-IC §12 lists the intentional ones.
- After any SVG edit, open it rendered (a browser is enough) and
  re-check it against the part tables: every pin, value,
  orientation and connection. The four drawings and the tables
  currently agree on all of them; keep it that way.

## Workflow

- Work on a branch and open a pull request. The maintainer merges
  through the GitHub web UI.
- Return review work as paste-ready text. Do not post comments,
  merge, or close issues on the maintainer's behalf unless asked.
- One change at a time: a fix commit covers one issue, not a bundle
  of unrelated edits.
