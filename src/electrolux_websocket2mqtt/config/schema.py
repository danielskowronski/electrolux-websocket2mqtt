# SPDX-FileCopyrightText: 2026-present Daniel Skowroński <electrolux-websocket2mqtt@skowronski.cloud>
#
# SPDX-License-Identifier: BSD-3-Clause
import platform
from typing import Optional
from pydantic import BaseModel

class ElectroluxConfig(BaseModel):
  username: str
  password: str
  country: str
class MQTTConfig(BaseModel):
  host: str
  port: int
  username: str
  password: str
  topic_prefix: str
class ApplianceConfig(BaseModel):
  device_id: str
  selected_properties: list[str]
class Config(BaseModel):
  electrolux: ElectroluxConfig
  mqtt: MQTTConfig
  appliances: dict[str, ApplianceConfig]
