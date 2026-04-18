# Electrolux Websocket To MQTT - `electrolux-websocket2mqtt`

Simple daemon republishing data from unofficial Electrolux WebSocket API to MQTT.

## Usage

TBD

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
- [ ] debug mode
- [ ] HA auto discovery payloads
- [ ] operations on raw data
- [ ] support for sending commands
