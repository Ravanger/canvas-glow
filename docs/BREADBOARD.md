# Canvas Glow breadboard test

Bench steps 1 and 2 of the [build guide](GUIDE.md#7-build-order), on a breadboard with jumper wires and no soldering. Crocodile leads help but are not needed. The finished light is built as in the [build guide](GUIDE.md).

## Setup

- **SuperMini headers**: if they came loose, push the header strips into the breadboard (long pins down), set the board on top and press it down with a rubber band or tape. Contact is unreliable this way, so if readings jump, press the board and see if they settle. Soldering the two headers is the one joint worth doing early.
- Place the SuperMini across the centre gap, USB-C towards the board edge. Pin names are on the silkscreen; check them rather than counting.
- Breadboard contacts carry about 1 A. That covers the bench, not the finished light.

![Breadboard wiring](img/breadboard.svg)

Pin positions vary between makers, so follow the silkscreen labels, not the drawing's positions.

## Step A: knob only

USB power, nothing else.

| From | To |
|---|---|
| 3V3 | 1 MΩ to knob end A |
| knob wiper | GPIO1, plus 100 nF to the GND rail |
| knob end B | GND rail |
| SuperMini GND | GND rail |

Flash `supermini-debug` ([Flash](GUIDE.md#flash)), open the monitor and turn the knob ([Debug readout](GUIDE.md#debug-readout-supermini-debug)). Note `knob=` at full turn and set `KNOB_MAX_MV` to about 95% of it.

Pass: `knob=` and `level=` change smoothly with the knob and read 0 at the bottom of the turn.

## Step B: add one channel

| From | To |
|---|---|
| Barrel jack − | GND rail (the star point on the bench) |
| Barrel jack + | + rail (load only, **not** the SuperMini 5V pin) |
| GPIO3 row | 100 Ω to the BC337 base row |
| BC337 base row | 10 kΩ to the GND rail |
| BC337 emitter | GND rail |
| BC337 collector | load −: strip −, or LED cathode |
| load + | + rail: strip +, or LED anode through 220 Ω |
| 470–1000 µF | across + rail and GND rail, stripe (−) to GND |

- Keep the SuperMini on USB and leave its 5V pin unconnected. The adapter powers only the load, and the shared GND rail is enough. No diode needed on the bench.
- Load, pick one:
  - **COB strip piece**, cut at the marks (10–20 cm, 0.16–0.32 A). Never put the whole reel on one transistor: 4 m at full is over 6 A. No solder: an 8 mm 2-pin COB clip connector, or a jumper pin laid flat on each copper pad at a cut mark and taped down hard (or crocodile clips). Tests the transistor at real current.
  - **Plain LED** (any 3 or 5 mm), no strip cutting: + rail → 220 Ω → anode (long leg); cathode (short leg, flat side) → collector. About 13 mA, so it tests the switching, fades and knob, but not the transistor drop under load.
- Stranded wires (barrel pigtail, connector leads) bend in the breadboard holes. Twist them tight, or wrap them round a jumper pin and tape it.
- Check the BC337 pin order first ([Transistors](GUIDE.md#4-transistors)).

Pass: the knob dims the load smoothly from off to full.
