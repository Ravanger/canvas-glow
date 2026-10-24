# Canvas Glow breadboard test — IC version (NE555)

Bench steps 1 and 2 of the [IC build guide](GUIDE-IC.md#7-build-order), on a breadboard with jumper wires and no soldering. Everything runs from the 5 V 2 A adapter. Crocodile leads help but are not needed. The finished light is built as in the [IC build guide](GUIDE-IC.md).

## Setup

- Barrel jack + to the + rail, barrel jack − to the GND rail.
- Check the pin order of every part first ([Transistors](GUIDE-IC.md#5-transistors)): NE555 DIP-8, notch at the top, pins counter-clockwise from the top left — 1 GND, 2 TRIG, 3 OUT, 4 RESET on the left; 8 VCC, 7 DISCH, 6 THR, 5 CTRL on the right. BC337 pins C-B-E.
- Stranded wires (barrel pigtail, connector leads) bend in the breadboard holes. Twist them tight, or wrap them round a jumper pin and tape it.
- Before fitting anything else, plug in and measure the rails: + rail to GND rail must read about +5 V, not −5 V. Unplug before wiring, and unplug before every change.
- Long breadboards often split each power rail in the middle (a gap in the printed red or blue line). Bridge the halves with jumpers, or keep everything on one half.
- Seat the 555 across the breadboard's centre channel, notch towards the top, so each pin has its own row.
- Polarity: a diode's banded end is the cathode; an electrolytic's stripe marks − and its longer lead is +; an LED's long leg is +. Pot legs, shaft towards you and legs down: usually end A, wiper, end B.
- The drawing shows the connections, not a hole-by-hole layout.

![Breadboard wiring, IC version](img/breadboard-ic.svg)

## Step 1: 555 + LED

| From | To |
|---|---|
| + rail | pin 8 (VCC) |
| + rail | pin 4 (RESET) |
| GND rail | pin 1 (GND) |
| pins 2 + 6 tied | 2.2 nF to GND rail |
| pin 5 (CTRL) | 100 nF to GND rail |
| + rail | 100 nF to GND rail next to the chip (decoupling) |
| + rail | 10 kΩ to pin 7 (DISCH) |
| pin 7 (DISCH) | pot wiper |
| pot end A | D1 anode |
| D1 cathode (banded end) | pins 2 + 6 |
| pot end B | 100 kΩ to D2 cathode (banded end) |
| D2 anode | pins 2 + 6 |
| + rail | 10–47 µF (≥ 16 V) to GND rail next to the chip, + lead to + rail |
| + rail | 470–1000 µF (≥ 16 V) to GND rail at the jack, + lead to + rail |
| pin 3 (OUT) | 220 Ω to LED anode (long leg) |
| LED cathode (short leg, flat side) | GND rail |

**Pass:** the knob dims the LED from a faint glow to bright, with no flicker and no dead zone — it must brighten continuously through the whole travel. End A is the counter-clockwise end, end B the clockwise end, so clockwise brightens.

**If not:**

- Works backwards: swap the pot's end legs.
- Stuck on or off: the 555 is not oscillating. Recheck the pinout (pins 2 + 6 tied, pin 4 to +5V, wiper to pin 7 with the 10 kΩ pull-up and good contact), that the diodes are not swapped, and that the 2.2 nF is on pins 2 + 6.
- Dark for most of the travel, lit only near one end: the pot ends or diodes are miswired. Rewire to the table above.
- Never lights, even at full: check adapter polarity and that the 5 V rail is actually ~5 V.

## Step 2: power stage

Remove the step-1 220 Ω and LED from pin 3, then add:

| From | To |
|---|---|
| pin 3 (OUT) | 100 Ω to BC337 base |
| BC337 E | GND rail |
| BC337 C | LED cathode (short leg, flat side) |
| + rail | 220 Ω to LED anode (long leg) |

Any 3 or 5 mm LED, about 13 mA for a red LED (white/blue run lower, ~8 mA). It tests the switching and the knob. The BC337 drop at real strip current is checked on the finished light ([Checks](GUIDE-IC.md#8-checks)).

**Pass:** the LED dims smoothly, and the DC voltage on pin 3 tracks the knob (about 0.06 V at the bottom; higher than ~2.7 V at full — one BC337 loads pin 3 with about 26 mA through the 100 Ω instead of the four channels' ~87 mA, so pin 3 sits higher under load). The finished-light figure is in [Checks](GUIDE-IC.md#8-checks).

---

[← Previous: IC build guide](GUIDE-IC.md) · [Contents](../README.md#documentation)
