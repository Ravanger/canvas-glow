# Canvas Glow

Backlit nightlight behind a stretched-canvas painting, a dimmable halo with a brightness knob. 5 V COB strip, one 5 V 2 A adapter. Two dimmer versions, same strip and power:

- Discrete version (no ICs): transistor PWM dimmer, no microcontroller.
  - Build guide: [docs/GUIDE.md](docs/GUIDE.md)
  - Breadboard test, no soldering: [docs/BREADBOARD.md](docs/BREADBOARD.md)
- IC version: NE555 PWM dimmer, same four BC337 output channels.
  - Build guide: [docs/GUIDE-IC.md](docs/GUIDE-IC.md)
  - Breadboard test, no soldering: [docs/BREADBOARD-IC.md](docs/BREADBOARD-IC.md)

The discrete version makes ~1 kHz PWM with a two-transistor oscillator; the IC version uses a 555 for the same job. Either way the knob sets the duty, and four BC337 transistors switch the four strip segments.
