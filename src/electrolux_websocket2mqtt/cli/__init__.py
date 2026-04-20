# SPDX-FileCopyrightText: 2026-present Daniel Skowroński <electrolux-websocket2mqtt@skowronski.cloud>
#
# SPDX-License-Identifier: BSD-3-Clause
import click
import coloredlogs
import logging
import asyncio
import json
import aiohttp
from pyelectroluxocp import OneAppApi
from electrolux_websocket2mqtt.__about__ import __version__
from electrolux_websocket2mqtt.config.load import load_config
from electrolux_websocket2mqtt.daemon import load_daemon_config,daemon_run

logger = logging.getLogger(__name__)

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.option(
  "--cfg",
  default="~/.config/electrolux-websocket2mqtt/config.yaml",
  type=click.Path(dir_okay=False),
  help="Path to configuration file.",
  show_default=True,
)
@click.option("--verbosity", "-v", count=True, help="Increase output verbosity (can be used multiple times).")
@click.version_option(version=__version__, prog_name="electrolux-websocket2mqtt")
@click.pass_context
def electrolux_websocket2mqtt(ctx: click.Context, cfg: str, verbosity: int) -> None:
  """Electrolux WebSocket to MQTT utilities."""
  ctx.ensure_object(dict)
  ctx.obj["cfg"] = cfg
  if ctx.invoked_subcommand is None:
    click.echo(ctx.get_help())

  lvl = logging.INFO
  if verbosity := ctx.params.get("verbosity", 0):
    if verbosity == 1:
      lvl = logging.DEBUG
  coloredlogs.install(fmt="[%(asctime)s] %(message)s", level=lvl)
  logging.info(f"Electrolux WebSocket to MQTT CLI v{__version__}")
  
@electrolux_websocket2mqtt.command("check_api")
@click.pass_context
def check_api(ctx: click.Context):
  """Check Electrolux API connectivity."""
  cfg_path = ctx.obj["cfg"]
  cfg = load_config(cfg_path)
  logger.debug(f"Loaded configuration from {cfg_path}")
  async def dump():
    async with OneAppApi(cfg.electrolux.username, cfg.electrolux.password, cfg.electrolux.country) as client:
        appliances = await client.get_appliances_list()
        for a in appliances:
            click.echo(f">> Appliance found with id={a.get('applianceId')} and name={a.get('applianceData').get('applianceName')}")

        def state_update_callback(a):
            click.echo(f">> Appliance state updated: {json.dumps(a)}")
        await client.watch_for_appliance_state_updates([appliances[0].get("applianceId")], state_update_callback)
  asyncio.run(dump())
@electrolux_websocket2mqtt.command("daemon")
@click.pass_context
def daemon(ctx: click.Context):
  """Run the Electrolux WebSocket to MQTT daemon."""
  cfg_path = ctx.obj["cfg"]
  cfg = load_config(cfg_path)
  logger.debug(f"Loaded configuration from {cfg_path}")
  load_daemon_config(cfg)
  while True:
    try:
      asyncio.run(daemon_run())
    except Exception as e:
      logger.exception("Daemon error, restarting...")
      if isinstance(e, aiohttp.ClientResponseError) and e.status == 429:
        logger.warning("Received HTTP 429 Too Many Requests from Electrolux API, likely due to too frequent restarts. Waiting 60 seconds before next restart attempt.")
        asyncio.run(asyncio.sleep(60))
      else:
        logger.info(f"Details: {e}")
        asyncio.run(asyncio.sleep(5))
