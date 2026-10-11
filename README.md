# Canvas Glow

Backlit nightlight behind a stretched-canvas painting, a dimmable halo with a brightness knob. ESP32-C3 SuperMini, 5 V COB strip, one 5 V 2 A adapter.

- Build guide: [docs/GUIDE.md](docs/GUIDE.md)
- Breadboard test, no soldering: [docs/BREADBOARD.md](docs/BREADBOARD.md)
- Settings: [firmware/include/Config.h](firmware/include/Config.h)

```sh
pio run -e supermini -t upload        # normal
pio run -e supermini-debug -t upload  # serial readout + boot sweep
pio device monitor                    # 115200
```

| GPIO | Use |
|---|---|
| 3, 4, 5, 10 | strip drivers |
| 1 | brightness knob |
