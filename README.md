# Electrolux Websocket To MQTT - `electrolux-websocket2mqtt`

**work in progress**

Simple daemon republishing data from unofficial Electrolux WebSocket API to MQTT.

## Usage

### Electrolux API

You must enter username and password used for the app, as well as country code of registration. Those can be validated at [https://developer.electrolux.one](https://developer.electrolux.one).

List of appliances in config requires three things:

1. device alias - this will be used in logs and MQTT topic; it doesn't have to correspond to device name in Electrolux app and it must be MQTT-topic friendly
2. device ID - numeric ID (but entered as string) assigned by Electrolux, it's very likely to be 24-digit long and start with 95
3. selected properties - list of exposed device properties to retransmit over MQTT

### MQTT

This tool requires MQTT broker with auth and permission to publish to prefix specified in config, by default it's `electrolux/#`.

Each property is published as message with QoS=1 and retain flag (for use with IoT devices that do not persist state and require KV-like data access) to topic `topic_prefix/appliance_alias/property`.

Property name is 1:1 from Electrolux API and is device-dependent, so you must first run `check_api` to see what your device is exposing. For now, both keys and values are taken straight from JSON data sent by API.

### Config

It's read from disk, by default from `~/.config/electrolux-websocket2mqtt/config.yaml`. See example in [examples/config.yaml](./examples/config.yaml).

### CLI

```
Usage: electrolux-websocket2mqtt [OPTIONS] COMMAND [ARGS]...

  Electrolux WebSocket to MQTT utilities.

Options:
  --cfg FILE       Path to configuration file.  [default:
                   ~/.config/electrolux-websocket2mqtt/config.yaml]
  -v, --verbosity  Increase output verbosity (can be used multiple times).
  --version        Show the version and exit.
  -h, --help       Show this message and exit.

Commands:
  check_api  Check Electrolux API connectivity.
  daemon     Run the Electrolux WebSocket to MQTT daemon.
```

---

## Why?

### What I want to achive

My own [HumidifierWaterRefillTerminal](https://github.com/danielskowronski/HumidifierWaterRefillTerminal) relies on relatively timely updates from MQTT about water tank status. I don't want to run client code on edge IoT, so I'm writing simple relay daemon which runs on a separate infra server and updates MQTT topics. That way, both edge IoT and HomeAssistant can consume the data. 

### What other options were dropped

- Electrolux IoT appliances do not expose any local API
- they transmit over MQTTS only to Electrolux servers with cert pinning in firmware
- official "Electrolux One" API has rate-limit for 5k requests per day amounting in fetch every 18 seconds and is very easy to hit it accidentally (reloading integration triggers extra initial poll)
- even though said API supports live-streaming for few months:
  - it can return false info about what will trigger update - some devices list several properties but only send `event:ping`
  - properties that are live updated may not be enough (e.g. they may lack device alerts like water shortage) for certain applications
- those issues propagate to all HomeAssistant integrations using Electrolux One API
- https://github.com/Woyken/homeassistant_electrolux_status doesn't support my device

## References

- https://developer.electrolux.one/documentation/reference#getLivestreamConfigurations
- https://github.com/Woyken/py-electrolux-ocp

## Status

- [.] MVP: Electrolux API client getting initial and updated properties filtered by config and republishing to MQTT - just script
- [ ] proper k8s integrations incl. Helm chart
- [ ] proper error handling in WebSocket (better than watchdog)
- [ ] debug mode
- [ ] HA auto discovery payloads
- [ ] operations on raw data
- [ ] support for sending commands
