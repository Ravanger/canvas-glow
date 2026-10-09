# Canvas Glow build guide

A backlit nightlight behind a stretched-canvas painting. A latching switch picks the mode, a knob sets the nightlight brightness, and a hand hovering in front of the painting brings it to full brightness for a few seconds.

| Switch | Idle | Hand hovers |
|---|---|---|
| Latched in (NIGHT) | glows at the knob level (knob fully down = off) | fades to full, holds 3 s, fades back to the knob level |
| Released (HOVER) | dark | fades to full, holds 3 s, fades out |

Bench-test on a breadboard first: [BREADBOARD.md](BREADBOARD.md). Everything runs from one 5 V 2 A adapter. Firmware is in [`../firmware`](../firmware), settings in [`Config.h`](../firmware/include/Config.h).

Contents: [Parts](#1-parts) · [Power budget](#2-power-budget) · [Circuit](#3-circuit) · [Transistors](#4-transistors) · [Light layout](#5-light-layout) · [Hover sensor](#6-hover-sensor) · [Firmware](#7-firmware) · [Build order](#8-build-order) · [Checks](#9-checks) · [Troubleshooting](#10-troubleshooting) · [3D prints](#11-3d-prints-bonus) · [Ideas](#12-ideas) · [Changes from v5](#13-changes-from-the-v5-guide)

---

## 1. Parts

| Part | Qty | Notes | Status |
|---|---|---|---|
| ESP32-C3 SuperMini | 1 | | have |
| 5 V 2 A adapter, barrel plug | 1 | check centre-positive with a meter | have |
| Barrel jack pigtail (+/− wires) | 1 | the power entry on the frame | have |
| 5 V COB strip, 320 LEDs/m, 8 W/m, 3000 K (4 m reel) | ~1.2 m | cut only on the printed cut marks | have |
| NPN driver transistor | 4 | BC337 first choice, see [Transistors](#4-transistors) | have |
| Base resistor 100 Ω / 150 Ω | 2 + 2 | 100 Ω on the long sides, 150 Ω on the short sides | have |
| 10 kΩ resistor | 4 | base-to-GND pulldown, keeps the strip off during boot | have |
| 1 MΩ resistor | 2 | sensor bleed + knob series resistor | have |
| B500K potentiometer | 1 | brightness knob (A500K works, B is smoother) | have |
| Latching push switch (6-pin DPDT) | 1 | mode switch, one pole used | have |
| 100 nF ceramic capacitor | 2 | knob filter + ESP32 supply | have |
| Sensor: telescopic antenna, thin wire, or foil / copper tape | 1 | see [Hover sensor](#6-hover-sensor) | have |
| Schottky diode 1N5819 (or 1N5822) | 1 | stops the adapter backfeeding the PC when USB is plugged in; see [Which diode](#which-diode) | have |
| Electrolytic 470–1000 µF ≥ 10 V | 1 | at the strip power entry | have |
| Electrolytic 100 µF ≥ 10 V | 1 | at the ESP32 5V pin | have |
| Perfboard, 22–24 AWG silicone wire, heat-shrink, solder | — | 20–22 AWG for the main 5 V / GND feed | have |
| Breadboard, jumper wires | — | bench tests without soldering, see [BREADBOARD.md](BREADBOARD.md) | have |
| Crocodile-clip leads | 2 | handy on the bench, not essential | optional |
| White foam board or thick white card | 1 | optional back reflector, see [Light layout](#5-light-layout) | optional |

Tools: multimeter, soldering iron, VS Code with PlatformIO.

## 2. Power budget

The strip is 8 W/m at 5 V, so **1.6 A per metre** at full brightness.

| Item | Current |
|---|---|
| 2 × 0.34 m long sides | 2 × 0.54 A |
| 2 × 0.24 m short sides | 2 × 0.38 A |
| Strip at 100% | 1.86 A |
| ESP32 + base drive | ~0.1 A |
| Adapter | 2.0 A |

1.86 A + 0.1 A is too close to 2 A, so the firmware caps brightness: `STRIP_BUDGET_A = 1.5` makes "full" mean 81% duty and keeps the total near 1.6 A (80% of the adapter). The cap is computed from `LED_SEGMENT_M`, so after cutting the strip enter the real lengths and the cap follows. A nightlight usually sits at 10–40%, well under budget.

Measure the strip once and enter the real figure in `STRIP_AMPS_PER_M` (see [Checks](#9-checks)).

## 3. Circuit

### Pins

| GPIO | Use |
|---|---|
| 3, 4, 5, 10 | strip drivers (one transistor per segment, all driven alike) |
| 0 | hover sensor pad (1 MΩ to GND) |
| 1 | brightness knob wiper (ADC) |
| 7 | mode switch to GND (internal pull-up, closed = NIGHT) |
| 6 | spare: second sensor such as the antenna |
| avoid 2, 8, 9 | boot strapping pins (8 also drives the onboard LED) |
| avoid 18, 19 | USB |

### Power entry

```
5V 2A adapter ── barrel jack ─┬──────────────────── +5V strip rail ──► COB+ of all 4 segments
                              │        [470–1000µF] across +5V/GND right here (mind polarity)
                              │
                              └──►|── Schottky ──┬── SuperMini 5V pin
                                (stripe = this   ├── 100µF to GND
                                 side)           └── 100nF to GND

GND (barrel −) = star point: all 4 emitters, SuperMini GND, all capacitor negatives
```

- The diode stops the adapter feeding the PC's USB port when you plug in USB to flash. The board then runs on about 4.7 V, which is fine. Without a diode, **unplug the barrel jack before connecting USB**.
- Run the emitter ground wires straight back to the barrel jack, not through the SuperMini's GND pin. The strip current then stays off the sensor's ground reference.
- Fuse: optional. Most 2 A adapters shut down on a short, but some only cut out well above 2 A. If you have one, put a 2–2.5 A polyfuse (PTC) or fast fuse in the + lead right after the jack.
- Cover the SuperMini's red power LED with a dab of black paint or tape, or it shows through the canvas.

### Which diode

Read the print on the body (phone camera zoomed in, light at a low angle). If it is worn off, use size plus the meter's diode test (red on the plain end, black on the striped end):

| Diode | Body | Diode test | Use here |
|---|---|---|---|
| **1N5819** | small black (DO-41) | **~0.15–0.3 V** | **first choice** |
| 1N5822 | large black (DO-201, ~5 mm thick) | ~0.15–0.3 V | fine, just bulky |
| 1N4007, FR107 | small black (DO-41) | ~0.5–0.7 V | works; the board runs on ~4.2 V |
| 1N5399, FR207 / 1N5408 | medium / large black | ~0.5–0.7 V | works, bulky |
| 1N4148 | small orange glass | ~0.6 V | no, too small for the supply |

The low reading is what marks a Schottky: among the small black ones, the ~0.2 V diode is the 1N5819. The stripe goes towards the SuperMini.

### One driver channel (build 4)

```
+5V rail ── COB segment + ... COB segment − ── C
                                               │  NPN (BC337)
GPIO ──[100Ω long / 150Ω short]──┬──────────── B
                                 [10kΩ]        │
                                  │            E
GND ──────────────────────────────┴────────────┴── star point
```

### Sensor, knob, switch

```
GPIO0 ──┬── wire to pad (keep ≥ 2 cm from strip wires)
        └──[1MΩ]── GND            (resistor at the board end)

3V3 ──[1MΩ]── knob end A
              knob wiper ──┬── GPIO1
                           └──[100nF]── GND
GND ───────── knob end B

GPIO7 ── switch common ── switch throw (closed when latched in) ── GND
```

The 1 MΩ in series with the knob keeps the wiper under about 1.1 V. The ESP32-C3 ADC reads only up to about 2.5 V. Without the series resistor, wire end A to 3V3, set `KNOB_MAX_MV = 2400` and accept that the last quarter-turn does nothing. If the knob works backwards, swap ends A and B.

## 4. Transistors

Each channel needs an NPN that saturates at up to 0.54 A on a 3.3 V GPIO.

| Part | Max current | Use here |
|---|---|---|
| **BC337** | 800 mA | first choice, any segment |
| 2N2222A | 600 mA | fine on any segment, runs a little warmer on the long sides |
| S8050 | 500 mA | short sides only (0.38 A) |
| 2N3904, C1815 | 200 / 150 mA | no, too small (OK as a pre-driver, see Option B) |
| MPSA13 | Darlington | no, ~1.5 V drop dims and heats |
| 2N6517 | 500 mA | no, low gain at this current |
| 2N7000 | 200 mA | no, too small and not fully on at 3.3 V |
| JFETs (J201, 2N38xx, 2N54xx...) | mA range | no |

**Short of transistors?** Use fewer segments. Two long sides only (2 × 0.34 m) need two transistors, draw 1.09 A at full and need no cap. Set `LED_PINS = { 3, 4 }` and `LED_SEGMENT_M = { 0.34f, 0.34f }`.

**Pin order varies by maker**, so always check. BC337 is often C-B-E and P2N2222A is often E-B-C (flat face towards you, legs down). With a meter on diode test, red lead on one leg and black on each of the others:
- the base is the leg that reads about 0.6–0.7 V to **both** other legs;
- base-to-emitter reads a few mV **higher** than base-to-collector.

A meter with an hFE socket also works.

**Option B: high-side PNP, if the base current is a problem.** Use this if the ESP32 resets, the 3V3 rail sags, or Vce stays above 0.5 V:

```
+5V ──┬───────────── E  BC327 (or 2N2907 / S8550 on short sides)
      [1kΩ]          │
      ├───────────── B
      [150Ω]         C ── COB+ ... COB− ── GND
      │
      C  2N3904 (any small NPN)
GPIO ──[1kΩ]── B
               [10kΩ] to GND
      E ── GND
```

The PNP's base current (~26 mA) now comes from 5 V instead of the GPIO, which only supplies ~2.5 mA. The logic stays the same (GPIO high = on), so the firmware does not change.

## 5. Light layout

Inner opening: 36 × 25.8 cm.

- Fix one segment along the inner face of each stretcher bar: ~34 cm on the long sides and ~24 cm on the short sides, rounded to the nearest cut marks. Enter the real lengths in `LED_SEGMENT_M`.
- **Aim and test before fixing anything.** Strips facing straight across the canvas back leave the centre dim. Two layouts are usually more even:
  - strips angled about 45° towards the canvas (3D-printed clips, [section 11](#11-3d-prints-bonus));
  - **reflector back**: strips aimed at a white foam board that closes the back, so the canvas is lit by the bounce. This is the most even option, and the board also keeps dust out.
- Keep strips, wires and the board at least 1 cm off the canvas. Nothing hard should press into the painting.
- Heat: at nightlight levels the strip barely warms. Hover bursts at full brightness only last seconds. If you ever run it at full for hours, check that the strip stays only finger-warm.

## 6. Hover sensor

The sensor is a conductive pad behind the canvas. A hand in front adds capacitance, which the firmware measures as a slower RC decay on GPIO0.

**Torch test result: solid foil blocks the light completely**, so a foil pad shows as a dark patch unless the paint in front of it is already dark. Pick a sensor:

| Sensor | Sensitivity | Shadow | Notes |
|---|---|---|---|
| Telescopic antenna along the inner bottom bar | weakest, edge only | none | **start here**: "wave near the bottom edge"; solder to the base lug, keep it collapsed (sliding sections give jumpy readings) |
| Thin-wire grid, 1–1.5 cm pitch, ~10 × 10 cm | good | faint lines | thin bare or enamelled wire, scrape the enamel at the joint; torch-test it before fixing |
| Foil / copper tape pad, ~8 × 8 cm | best | dark patch | only behind an area that is dark in the painting anyway |

Bench-test the antenna first (build order step 2). If it only triggers when you nearly touch the frame, add a grid on GPIO6 as a second sensor.

You can run two sensors: put the second one on GPIO6 with its own 1 MΩ and add `6` to `SENSE_PINS`. Either one triggers.

- Keep the pad lead short (under 30 cm), taped down, and at least 2 cm from strip wires.
- Put the 1 MΩ at the board end.
- If people behind or next to the frame cause false triggers, tape grounded foil to the outer side of the back reflector board, without touching the pad or its wire.

## 7. Firmware

### Flash

1. Install the **PlatformIO IDE** extension in VS Code and open this repo folder.
2. Pick an environment in the status bar: `supermini` for normal use, or `supermini-debug` for serial readouts plus a short brightness sweep at boot.
3. Connect the SuperMini by USB (with a diode fitted, or the barrel jack unplugged). Click **Upload**, then **Monitor** (115200 baud).
4. If the port does not appear or the upload fails: hold **BOOT**, tap **RESET** (or plug in while holding BOOT), release BOOT and upload again.

```sh
pio run -e supermini-debug -t upload
pio device monitor
```

The platform is pinned (`espressif32@6.9.0`, Arduino-ESP32 2.0.17), so you don't need to know your installed core version.

At every power-up the board calibrates the sensor for 0.2 s. Keep hands away while you plug it in.

### Debug readout (`supermini-debug`)

```
s0 base=22.4 v=22.6 ----  NIGHT knob=512mV level=32901 duty=363/2047
```

| Field | Meaning |
|---|---|
| `base` / `v` | sensor idle reference / current reading, µs |
| `----` / `HOVER` / `FAULT` | sensor state; FAULT means a pad shorted to GND or its 1 MΩ missing |
| `knob` | wiper voltage; use it to set `KNOB_MAX_MV` |
| `level` / `duty` | perceived brightness 0–65535 / PWM duty after gamma and the power cap |

### Settings (`firmware/include/Config.h`)

| Setting | Default | Change when |
|---|---|---|
| `LED_PINS`, `LED_SEGMENT_M` | 4 segments | you cut different lengths or use fewer transistors |
| `STRIP_AMPS_PER_M` | 1.6 | you measured the strip ([Checks](#9-checks)) |
| `STRIP_BUDGET_A` | 1.5 | keep at or below 1.6 on a 2 A adapter |
| `SENSE_PINS` | `{ 0 }` | you add a second sensor |
| `TRIG_PCT` | 135 | lower towards 125 if a real hover doesn't trigger |
| `TRIG_MARGIN_US` | 12 | raise if it triggers on its own |
| `HOVER_HOLD_MS` | 3000 | you want a longer or shorter glow after the hand leaves |
| `FADE_UP_MS` / `FADE_DOWN_MS` | 800 / 1500 | taste |
| `NIGHT_AUTO_OFF_MIN` | 0 (off) | you want a sleep timer; a hover restarts it, toggling the switch re-arms it |
| `KNOB_MAX_MV` | 1000 | set to ~95% of the debug `knob=` reading at full turn |
| `KNOB_OFF_PCT` | 3 | the bottom of the knob turns the nightlight off |
| `PWM_FREQ_HZ` | 20000 | try 5000 if low brightness looks uneven (Option B drivers) |

The firmware also has a 60 s stuck-hover recovery and a loop watchdog. While the light is fading, the sensor ignores new triggers and lets its baseline follow, because the strip's PWM couples into the pad and shifts the reading.

## 8. Build order

1. **Torch test** (done): foil blocks the light, so start with the antenna.
2. **Bench, sensor only** ([breadboard](BREADBOARD.md)): SuperMini on USB, sensor and 1 MΩ on GPIO0, cardboard between hand and pad. Flash `supermini-debug` and check that `HOVER` appears at 2–4 cm and that `v` sits steady at idle.
3. **Bench, one channel** ([breadboard](BREADBOARD.md)): one transistor, one short strip piece, the barrel supply. Check the switch, the knob and the hover fade.
4. **Light layout test**: tape segments in place temporarily and try angles and the reflector with the painting upright in a dark room.
5. **Build the harness**: 4 channels on perfboard (tape-insulate the underside), the power entry, the knob and switch. Mount everything on the stretcher bars.
6. **Install the sensor** and route its lead away from strip wires.
7. Run every check in section 9.

## 9. Checks

| Check | How | Pass |
|---|---|---|
| Strip current | wire one segment straight to 5 V with the meter (10 A jack) in series | about 1.6 A × length; enter the real A/m in `STRIP_AMPS_PER_M` |
| Transistor drop | hover so it is at full; measure collector to emitter | under 0.4 V good; over 0.6 V → 82 Ω base resistor (not lower: the GPIO limit is 40 mA) or Option B |
| Strip voltage | at full, across the far segment's + and − | 4.5 V or more |
| Total current | meter in series with the barrel + wire, everything at full | at most ~1.6 A |
| PWM coupling | NIGHT, no hand near, turn the knob slowly min → max → min | no `HOVER` in the debug output |
| Heat | 30 min in NIGHT at full | strip, transistors and the board only finger-warm |
| Reboot | unplug and replug in each switch position | comes back in the right mode, no flash at boot |

## 10. Troubleshooting

| Symptom | Try |
|---|---|
| Never triggers | bigger pad, shorter lead, check the 1 MΩ, lower `TRIG_PCT` |
| Triggers by itself | tape down loose wires, move the lead away from strip wires, raise `TRIG_MARGIN_US`, add the grounded foil shield |
| Triggers when the knob turns or the light changes | the PWM coupling check failed: more distance between pad/lead and the strips or their wires |
| Stays bright ~60 s after a hover | the light at full raises the reading above the release level: same fix as above |
| `FAULT` | 1 MΩ open or missing (timeout), or pad shorted to GND (instant). A broken pad wire gives no FAULT, only a weak response |
| One segment dark | transistor pin order, base resistor, the segment's +/− wires |
| All dim | strip voltage under 4.5 V: thicker feed wire, Option B, check the adapter |
| ESP32 resets at full | missing bulk capacitor, too much base current (Option B), feed wire too thin |
| Knob jumpy | 100 nF on the wiper, check the 1 MΩ |
| Knob does nothing for the last part of the turn | lower `KNOB_MAX_MV` to the debug reading |
| Won't boot | disconnect everything, boot bare, reconnect one item at a time; nothing on GPIO 2/8/9 |
| Upload fails | BOOT + RESET (section 7), use a data USB cable |
| PlatformIO `HTTPClientError` or `CERTIFICATE_VERIFY_FAILED` on first build | a work network inspects HTTPS; build once from a home network, or export the Windows root certificates to a `.pem` and set `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` to it |

## 11. 3D prints (bonus)

Print anything near the strip in **PETG**: PLA softens around 55 °C.

- 45° strip clips for the stretcher bars (8 mm strip)
- A box for the SuperMini and driver perfboard, screwed to a bar, with the USB port reachable
- A panel mount for the barrel jack with a cable strain relief
- A bracket for the knob and switch, plus a knob cap
- Wall spacers, if you also want a glow on the wall behind the painting (needs strips facing backwards)

## 12. Ideas

- **Hidden message**: write or paint something on the back of the canvas. It only shows when the light is on.
- **Sleep timer**: set `NIGHT_AUTO_OFF_MIN` (e.g. 45).
- **Halo**: extra strip on the outside back of the frame, facing the wall.
- **Candle or breathing mode** at low brightness (firmware change).
- **Wi-Fi**: phone control, a bedtime schedule, an animation every anniversary. Costs 0.1–0.3 A of the budget; lower `STRIP_BUDGET_A` to match. SuperMini boards often need `WiFi.setTxPower(WIFI_POWER_8_5dBm)` to connect reliably.
- **Auto-on at dark**: a light sensor on GPIO1 instead of the knob, pointed away from the strips.

## 13. Changes from the v5 guide

The original is kept in [`reference/canvas-glow-v5.html`](reference/canvas-glow-v5.html).

- Nightlight first: switch latched = nightlight at the knob level (was 100%); hover is a boost in both modes.
- One sensor instead of four; the strip is split into four segments only so that each transistor stays in its rating.
- One 5 V 2 A adapter for everything (was two USB supplies). Added a Schottky diode and bulk capacitors; dropped the PTC fuse, USB breakout and second cable.
- Firmware power cap from the measured strip length; brightness knob; optional sleep timer; loop watchdog; trigger lockout while fading; no boot flash in the normal build; PlatformIO with a pinned platform instead of the Arduino IDE 2.x/3.x branches.
- Added the foil-shadow warning, a transistor substitution table, and driver Option B.
- Dropped: the 5 mm LED fallback, the BC337 note (now in the table), the PTC section and the old dated schedule.
