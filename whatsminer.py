#!/usr/bin/env python3
"""
WhatsMiner Control Script

This script demonstrates how to use the WhatsminerAPIv3 interface
to communicate with and control a WhatsMiner device.
"""

import json

from whatsminer_interface import WhatsminerAPIv3
from whatsminer_trans import WhatsminerTCP


def main() -> None:
    """
    Main function to demonstrate WhatsMiner API usage.
    """
    # Configuration
    miner_ip = "192.168.2.128"
    miner_port = 4433
    miner_account = "super"
    miner_passwd = "super"

    # Initialize API and TCP connection
    whatsminer_api = WhatsminerAPIv3(miner_account, miner_passwd)
    whatsminer_tcp = WhatsminerTCP(miner_ip, miner_port, miner_account, miner_passwd)

    try:
        # Connect to the miner
        whatsminer_tcp.connect()

        # Get device info and salt
        req_info = whatsminer_api.get_request_cmds("get.device.info")
        req_length = len(req_info)
        rsp_info = whatsminer_tcp.send(req_info, req_length)

        if rsp_info["code"] == 0:
            miner_salt = rsp_info["msg"]["salt"]
            whatsminer_api.set_salt(miner_salt)
            print(f"Device info: {json.dumps(rsp_info, indent=2)}")
        else:
            print(f"Error: {json.dumps(rsp_info, indent=2)}")
            return

        # Example: Restart miner service
        req_info = whatsminer_api.set_miner_service("restart")
        req_length = len(req_info)
        rsp_info = whatsminer_tcp.send(req_info, req_length)
        print(f"Service restart response: {json.dumps(rsp_info, indent=2)}")

        # Example: Change user password (commented out for safety)
        # req_info = whatsminer_api.set_user_passwd("user1", "user1", "abcde1")
        # req_length = len(req_info)
        # rsp_info = whatsminer_tcp.send(req_info, req_length)
        # print(f"Password change response: {json.dumps(rsp_info, indent=2)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        whatsminer_tcp.close()


if __name__ == "__main__":
    main()
