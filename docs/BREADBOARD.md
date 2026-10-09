# Canvas Glow breadboard test

Bench steps 2 and 3 of the [build guide](GUIDE.md#8-build-order), on a breadboard with jumper wires and no soldering. Crocodile leads help but are not needed. The finished light is built as in the [build guide](GUIDE.md).

## Setup

- **SuperMini headers**: if they came loose, push the header strips into the breadboard (long pins down), set the board on top and press it down with a rubber band or tape. Contact is unreliable this way, so if readings jump, press the board and see if they settle. Soldering the two headers is the one joint worth doing early.
- Place the SuperMini across the centre gap, USB-C towards the board edge. Pin names are on the silkscreen; check them rather than counting.
- Breadboard contacts carry about 1 A. That covers the bench, not the finished light.

## Step 2: sensor only

USB power, nothing else.

| From | To |
|---|---|
| GPIO0 row | 1 MΩ to the GND rail |
| GPIO0 row | jumper to the antenna's base lug (antenna collapsed): pin through the lug hole, bent over and taped, or a crocodile lead |
| SuperMini GND | GND rail |

Leave GPIO7 open: the internal pull-up puts it in hover mode, so the unconnected knob is ignored. Lay the antenna flat on the table, away from the USB cable, with cardboard over it. Flash `supermini-debug` ([Flash](GUIDE.md#flash)), open the monitor, then read `v` ([Debug readout](GUIDE.md#debug-readout-supermini-debug)) with the hand away and at 2–4 cm.

Pass: `HOVER` appears at 2–4 cm and `v` sits steady at idle. If it only triggers when you nearly touch the antenna, try a wire grid ([Hover sensor](GUIDE.md#6-hover-sensor)).

## Step 3: one channel, knob and switch

| From | To |
|---|---|
| Barrel jack − | GND rail (the star point on the bench) |
| Barrel jack + | + rail (strip only, **not** the SuperMini 5V pin) |
| GPIO3 row | 100 Ω to the BC337 base row |
| BC337 base row | 10 kΩ to the GND rail |
| BC337 emitter | GND rail |
| BC337 collector | strip − |
| strip + | + rail |
| 470–1000 µF | across + rail and GND rail, stripe (−) to GND |
| 3V3 | 1 MΩ to knob end A |
| knob wiper | GPIO1, plus 100 nF to the GND rail |
| knob end B | GND rail |
| GPIO7 | switch common; the throw that closes when latched to the GND rail |

- Keep the SuperMini on USB and leave its 5V pin unconnected. The adapter powers only the strip, and the shared GND rail is enough. No diode needed on the bench.
- Use a **short strip piece**, cut at the marks (10–20 cm, 0.16–0.32 A). Never put the whole reel on one transistor: 4 m at full is over 6 A.
- No solder on the strip: an 8 mm 2-pin COB clip connector, or a jumper pin laid flat on each copper pad at a cut mark and taped down hard (or crocodile clips).
- Stranded wires (barrel pigtail, connector leads) bend in the breadboard holes. Twist them tight, or wrap them round a jumper pin and tape it.
- If the switch does not fit the breadboard, use a jumper instead: GPIO7 to GND = NIGHT, open = hover.
- Check the BC337 pin order first ([Transistors](GUIDE.md#4-transistors)).

Pass: the switch changes mode, the knob dims the strip in NIGHT, and a hover fades it up and back.
