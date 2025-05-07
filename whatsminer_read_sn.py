#!/usr/bin/env python3
"""
WhatsMiner Serial Number Reader

This script connects to a WhatsMiner device and reads its serial numbers.
"""

import json
from typing import Any, Dict, Optional

from whatsminer_interface import WhatsminerAPIv3
from whatsminer_trans import WhatsminerTCP


def whatsminer_read_sn(worker_ip: str, port: int = 4433) -> Optional[Dict[str, Any]]:
    """
    Connect to a WhatsMiner device and retrieve its serial numbers.

    Args:
        worker_ip: IP address of the WhatsMiner device
        port: Port number (default: 4433)

    Returns:
        Dictionary containing the IP and serial numbers or None if an error occurs
    """
    # Default credentials - you may need to change these
    account = "super"
    password = "super"

    # Initialize API and TCP connection
    whatsminer_api = WhatsminerAPIv3(account, password)
    whatsminer_tcp = WhatsminerTCP(worker_ip, port, account, password)

    try:
        # Connect to the miner
        whatsminer_tcp.connect()

        # Get device info
        req_info = whatsminer_api.get_request_cmds("get.device.info")
        req_length = len(req_info)
        response = whatsminer_tcp.send(req_info, req_length)

        if response["code"] != 0:
            print(f"Error retrieving device info: {response}")
            return None

        # Get salt and set it
        salt = response["msg"]["salt"]
        whatsminer_api.set_salt(salt)

        # Extract miner information
        device_info = response.get("msg", {})
        miner_info = device_info.get("miner", {})

        # Create result dictionary
        result = {
            "ip": worker_ip,
            "miner_sn": miner_info.get("miner-sn"),
            "pcb_sn_0": miner_info.get("pcbsn0"),
            "pcb_sn_1": miner_info.get("pcbsn1"),
            "pcb_sn_2": miner_info.get("pcbsn2"),
            "pcb_sn_3": miner_info.get("pcbsn3"),
        }

        return result

    except Exception as error:
        print(f"Error connecting to {worker_ip}: {error}")
        return None

    finally:
        whatsminer_tcp.close()


def main() -> None:
    """
    Main function to demonstrate WhatsMiner serial number reading.
    """
    worker_ip = "192.13.1.165"
    result = whatsminer_read_sn(worker_ip)

    if result:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
