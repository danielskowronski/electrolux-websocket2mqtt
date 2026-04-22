# SPDX-FileCopyrightText: 2026-present Daniel Skowroński <electrolux-websocket2mqtt@skowronski.cloud>
#
# SPDX-License-Identifier: BSD-3-Clause
import logging
import asyncio
import json
import time
from pyelectroluxocp import OneAppApi
from electrolux_websocket2mqtt.__about__ import __version__
from electrolux_websocket2mqtt.config.schema import Config
from dataclasses import dataclass
import aiomqtt

@dataclass
class ReportingAppliance:
  alias: str
  device_id: str
  property_topics: dict[str, str]

logger = logging.getLogger(__name__)
_cfg: Config
_dev_map: dict[str, ReportingAppliance] = {}
_last_ws_message_time: float

def load_daemon_config(cfg: Config) -> None:
  global _cfg
  _cfg = cfg
  prepare_device_mapping(cfg)
def prepare_device_mapping(cfg: Config) -> None:
  global _dev_map
  for appliance_alias, appliance_cfg in cfg.appliances.items():
    ra = ReportingAppliance(
      alias=appliance_alias,
      device_id=appliance_cfg.device_id,
      property_topics={}
    )
    for prop in appliance_cfg.selected_properties:
      topic = f"{cfg.mqtt.topic_prefix}/{appliance_alias}/{prop}"
      ra.property_topics[prop] = topic
    _dev_map[appliance_cfg.device_id] = ra
def should_report_property(device_id: str, property_name: str) -> bool:
  appliance = _dev_map.get(device_id)
  if not appliance:
    return False
  return property_name in appliance.property_topics

async def safe_publish(mqtt_client: aiomqtt.Client, topic: str, payload: str, fatal_error: asyncio.Future) -> None:
  try:
    await mqtt_client.publish(topic, payload, qos=1, retain=True)
  except asyncio.CancelledError:
    raise
  except Exception as e:
    logger.exception("MQTT publish failed for topic=%s", topic)
    if not fatal_error.done():
      fatal_error.set_exception(e)
    raise

def appliance_update_callback(mqtt_client: aiomqtt.Client, appliance_data: dict, fatal_error: asyncio.Future) -> None:
  global _last_ws_message_time
  _last_ws_message_time = time.monotonic()
  for appliance_id, appliance_updates in appliance_data.items():
    if appliance_id not in _dev_map:
      logger.debug(f"Received update for appliance with id={appliance_id} which is not in config, skipping")
      continue
    appliance = _dev_map[appliance_id]
    logger.info(f"Received update for appliance with id={appliance_id} and name={appliance.alias}: {json.dumps(appliance_updates)}")
    for prop, value in appliance_updates.items():
      if should_report_property(appliance_id, prop):
        topic = appliance.property_topics[prop]
        payload = json.dumps(value)
        logger.debug(f"Publishing update for appliance with id={appliance_id} and property={prop} to topic={topic} with payload={payload}")
        task = asyncio.create_task(safe_publish(mqtt_client, topic, payload, fatal_error))
        task.add_done_callback(lambda t: t.exception())
      else:
        pass

async def watchdog_task() -> None:
  global _last_ws_message_time
  if not _cfg.electrolux.watchdog or not _cfg.electrolux.watchdog.enabled:
    return
  while True:
    await asyncio.sleep(_cfg.electrolux.watchdog.timeout_seconds/100)
    elapsed = time.monotonic() - _last_ws_message_time
    logger.debug(f"Watchdog check: elapsed={elapsed:.1f} seconds")
    if elapsed > _cfg.electrolux.watchdog.timeout_seconds:
      logger.warning(f"No WebSocket messages received for {elapsed:.1f} seconds, triggering daemon restart")
      raise Exception("WebSocket connection appears to be stalled")

async def daemon_run():
  global _cfg, _last_ws_message_time
  loop = asyncio.get_running_loop()
  fatal_error = loop.create_future()

  async with aiomqtt.Client(
    hostname=_cfg.mqtt.host,
    port=_cfg.mqtt.port,
    username=_cfg.mqtt.username,
    password=_cfg.mqtt.password,
  ) as mqtt_client, \
  OneAppApi(
    _cfg.electrolux.username,
    _cfg.electrolux.password,
    _cfg.electrolux.country
  ) as electrolux_client:
    appliances = await electrolux_client.get_appliances_list(include_metadata=True)
    _last_ws_message_time = time.monotonic()
    tasks = [ asyncio.create_task(watchdog_task()) ]
    for appliance in appliances:
      device_id = appliance.get("applianceId")
      if device_id in _dev_map:
        logger.info(f"Monitoring appliance with id={device_id} and name={appliance.get('applianceData').get('applianceName')}")
        tasks.append(
          asyncio.create_task(
            electrolux_client.watch_for_appliance_state_updates(
              [device_id],
              lambda appliance_data, mqtt_client=mqtt_client, fatal_error=fatal_error:
                appliance_update_callback(mqtt_client, appliance_data, fatal_error),
            )
          )
        )
      else:
        logger.info(f"Skipping appliance with id={device_id} and name={appliance.get('applianceData').get('applianceName')} (not in config)")
    if not tasks:
      logger.warning("No appliances to monitor, exiting")
      return
    logger.info("Daemon is running, waiting for appliance updates...")
    done, pending = await asyncio.wait(
      [*tasks, fatal_error],
      return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
      if isinstance(task, asyncio.Task):
        task.cancel()
    await asyncio.gather(
      *(t for t in pending if isinstance(t, asyncio.Task)),
      return_exceptions=True,
    )
    for task in done:
      task.result()
