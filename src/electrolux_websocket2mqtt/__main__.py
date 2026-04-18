# SPDX-FileCopyrightText: 2026-present Daniel Skowroński <electrolux-websocket2mqtt@skowronski.cloud>
#
# SPDX-License-Identifier: BSD-3-Clause
import sys

if __name__ == "__main__":
    from electrolux_websocket2mqtt.cli import electrolux_websocket2mqtt

    sys.exit(electrolux_websocket2mqtt())
