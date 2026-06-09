# Unit Tests — MicroPython P1 Meter

The `tests/` directory contains a suite of MicroPython-compatible unit tests
that can be run on:

* the **MicroPython Unix port** (e.g. inside the official Docker image), or
* a **connected ESP32** board via `mpremote`.

---

## Directory layout

```
tests/
  mocks/            Hardware mocks for the Unix port (machine, esp32, neopixel, …)
  test_crc16.py            CRC-16/ARC algorithm (utilities.crc16)
  test_parsereadings.py    OBIS line parser (P1Meter.parsereadings)
  test_replace_codes.py    OBIS→topic translation (replace_codes + codetable)
  test_simulator.py        Fake telegram generator (P1MeterSIM.fake_message)
  test_config.py           Config value regression tests (config.py)
  run_tests.sh             Convenience runner script
```

---

## Running on the MicroPython Unix port (Docker)

```bash
# Pull the official image
docker pull micropython/unix

# Run the full suite (from repo root)
docker run --rm -v "$PWD":/code -w /code micropython/unix \
    sh tests/run_tests.sh /usr/local/bin/micropython

# Or run a single test
docker run --rm -v "$PWD":/code -w /code micropython/unix \
    micropython tests/test_crc16.py
```

If you have MicroPython installed locally:

```bash
./tests/run_tests.sh              # uses 'micropython' on $PATH
micropython tests/test_crc16.py  # single test
```

---

## Running on a connected ESP32

```bash
# Install mpremote if needed
pip install mpremote

# Copy only what's needed (mocks are not required on real hardware)
mpremote cp -r src/ :
mpremote cp -r tests/ :

# Run a test
mpremote run tests/test_crc16.py
mpremote run tests/test_parsereadings.py
```

---

## How the mocks work

When tests run on the Unix port, `tests/mocks/` is prepended to `sys.path`
**before** `src/`.  This means that `import machine` resolves to
`tests/mocks/machine.py` (a pure-Python mock) rather than the real hardware
module, allowing hardware-independent logic to be tested without an ESP32.

On an actual ESP32 the real modules take precedence from MicroPython's frozen
modules — the mocks are never loaded.

---

## Adding new tests

1. Create `tests/test_<feature>.py` using the standard `unittest.TestCase` API.
2. Add the path-setup block at the top (copy from an existing test file).
3. Import only the module you need; the mocks will handle hardware dependencies.
4. Run with `micropython tests/test_<feature>.py`.
