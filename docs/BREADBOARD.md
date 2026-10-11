# Canvas Glow breadboard test

Bench steps 1 and 2 of the [build guide](GUIDE.md#7-build-order), on a breadboard with jumper wires and no soldering. Everything runs from the 5 V 2 A adapter. Crocodile leads help but are not needed. The finished light is built as in the [build guide](GUIDE.md).

## Setup

- Barrel jack + to the + rail, barrel jack − to the GND rail.
- Check the pin order of every transistor first ([Transistors](GUIDE.md#5-transistors)): 2N3904 E-B-C, 2N7000 S-G-D, BC337 and BC327 C-B-E.
- Breadboard contacts carry about 1 A. That covers the bench, not the finished light.
- Stranded wires (barrel pigtail, connector leads) bend in the breadboard holes. Twist them tight, or wrap them round a jumper pin and tape it.

![Breadboard wiring](img/breadboard.svg)

## Step 1: oscillator + LED

| From | To |
|---|---|
| + rail | RC1 10 kΩ to Q1 C |
| + rail | RC2 10 kΩ to Q2 C |
| + rail | pot wiper (middle leg) |
| pot end A | 4.7 kΩ to Q2 B |
| pot end B | 120 kΩ to Q1 B |
| Q1 C | C1 2.2 nF to Q2 B |
| Q2 C | C2 2.2 nF to Q1 B |
| Q1 E, Q2 E | GND rail |
| Q2 C | Q3 gate |
| Q3 source | GND rail |
| + rail | 220 Ω to LED anode (long leg) |
| LED cathode (short leg, flat side) | Q3 drain |
| 100 µF | across + rail and GND rail near Q1/Q2, stripe (−) to GND |
| 100 nF | across + rail and GND rail next to the 100 µF |

Pass: the knob dims the LED from off (or a faint glow) to bright, with no flicker. If it works backwards, swap the pot's end legs. If it is stuck on or off, the oscillator is not running: recheck the pin orders and C1/C2.

## Step 2: power stage

Remove the LED from Q3, then add:

| From | To |
|---|---|
| Q3 drain | 1 kΩ to Q4 B |
| Q4 B | 10 kΩ to + rail |
| Q4 E | + rail |
| Q4 C | DRIVE RAIL |
| DRIVE RAIL | 180 Ω to BC337 base |
| BC337 base | 10 kΩ to GND rail |
| BC337 E | GND rail |
| BC337 C | load −: strip −, or LED cathode |
| load + | + rail: strip +, or LED anode through 220 Ω |
| 470–1000 µF | across + rail and GND rail, stripe (−) to GND |

- Load, pick one:
  - **COB strip piece**, cut at the marks (10–20 cm, 0.16–0.32 A). Never put the whole reel on one transistor: 4 m at full is over 6 A. No solder: an 8 mm 2-pin COB clip connector, or a jumper pin laid flat on each copper pad at a cut mark and taped down hard (or crocodile clips). Tests the transistor at real current.
  - **Plain LED** (any 3 or 5 mm), no strip cutting: + rail → 220 Ω → anode (long leg); cathode (short leg, flat side) → collector. About 13 mA, so it tests the switching and the knob, but not the transistor drop under load.

Pass: the load dims smoothly, BC337 and BC327 stay cool, and the DC voltage on the DRIVE RAIL tracks the knob.
