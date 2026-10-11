# Canvas Glow

Backlit nightlight behind a stretched-canvas painting, a dimmable halo with a brightness knob. Discrete transistor PWM dimmer (no microcontroller), 5 V COB strip, one 5 V 2 A adapter.

- Build guide: [docs/GUIDE.md](docs/GUIDE.md)
- Breadboard test, no soldering: [docs/BREADBOARD.md](docs/BREADBOARD.md)

A two-transistor oscillator makes ~1 kHz PWM, the knob sets the duty, and a 2N7000 and a BC327 drive four BC337 transistors that switch the four strip segments.
