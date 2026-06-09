# Changelog

All notable changes to this project will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Fixed
- `_conn_errors =+ 1` typo in `mqttclient.py` corrected to `+=1`; the
  "reboot after 10 errors" safeguard now triggers correctly.
- `broker['port']` changed from string `'8883'` to integer `1883` (plain MQTT
  default); passing a string to `MQTTClient` caused a silent type error.
- Duplicate OBIS code entries for `1-0:32.32.0` and `1-0:32.36.0` removed
  from `codetable`; the per-phase voltage sag/swell mappings are now the sole
  entries for those codes.
- `wlan_stable` was imported by value (`from wifi import wlan_stable`); changed
  to `import wifi` so `wifi.wlan_stable` always reflects the current state.
- Misleading log message "repeating on UART1 **RX** Pin" corrected to
  "repeating on UART1 **TX** Pin".
- Duplicate static lines in the `meter2` simulator template removed; only the
  format-placeholder lines remain, preventing stale constant readings appearing
  alongside the randomised ones.

### Added
- `VERSION = "1.3.0"` constant in `config.py`; the startup banner now reads
  the version from there instead of having it hardcoded.
- TLS/SSL support: `MQTTClient2` now reads `ssl` and `ssl_params` from
  `config.broker` and passes them to `umqtt.simple.MQTTClient`.
- Reconnect callbacks: `MQTTClient2.add_reconnect_callback()` allows dependent
  objects (e.g. `P1Meter`) to register a zero-argument function that is called
  after each successful MQTT (re)connection.  `P1Meter` uses this to clear its
  last-sent cache, forcing a full re-publish after reconnect.
- `config_local.py.example` template for local credentials (WiFi password,
  MQTT credentials, WebREPL password); `config_local.py` is now in `.gitignore`.
- Unit test suite in `tests/` runnable on the MicroPython Unix port or a
  connected ESP32 (see `tests/README.md`).

### Changed
- `mqttclient.py`: `connect()` is now an `async` coroutine; on failure it
  `await asyncio.sleep_ms(5000)` before returning so the event loop stays
  responsive between retries.
- `main.py`: `glb_mqtt_client` and `glb_p1_meter` moved inside `run()`;
  coroutine helpers updated to accept them as explicit parameters.
- `lib/logging.py`: `Logger.handlers` moved from class attribute to instance
  attribute, preventing handlers added to one logger from appearing in all
  loggers.
- `VERBOSE` flag and its guards removed from `p1meter.py`, `p1meter_sym.py`,
  and `mqttclient.py`; replaced with unconditional `log.debug()` calls that
  are filtered by the configured log level.
- `dictcopy()` / `import ujson` removed from `p1meter.py`; telegram template
  is now copied with a plain dict literal, saving RAM.
- Default broker port changed from `8883` to `1883` (see **Fixed** above);
  set `'ssl': True` and `'port': 8883` in `config_local.py` to use TLS.
- README updated: firmware requirement raised to MicroPython 1.24+; config
  example synchronised with actual `config.py`; credentials section documents
  the `config_local.py` override pattern.

---

## [1.3.0] — previous release

Initial public release with P1 meter reading, MQTT publish, CRC-16 check,
built-in simulator, and WebREPL/FTP remote access.
