# SPDX-FileCopyrightText: 2026-present Daniel Skowroński <electrolux-websocket2mqtt@skowronski.cloud>
#
# SPDX-License-Identifier: BSD-3-Clause
from .schema import Config
import yaml
from pathlib import Path
import os


def load_config(path: str) -> Config:
  path_expanded = Path(path).expanduser()
  with open(path_expanded, "r", encoding="utf-8") as f:
    raw_cfg = yaml.safe_load(f)
  _cfg = Config.model_validate(raw_cfg)
  return _cfg
