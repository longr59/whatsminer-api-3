# WhatsMiner API Python Client

A Python library for interacting with WhatsMiner devices via API v3.

## Basic Usage

```python
from whatsminer_interface import WhatsminerAPIv3
from whatsminer_trans import WhatsminerTCP

# Initialize connection
miner_ip = "192.168.1.100"
miner_port = 4433
account = "super"  # Default admin account
password = "super"  # Default password

# Create API and TCP instances
api = WhatsminerAPIv3(account, password)
tcp = WhatsminerTCP(miner_ip, miner_port, account, password)

# Connect to miner
tcp.connect()

try:
    # Get device info and salt
    req = api.get_request_cmds("get.device.info")
    response = tcp.send(req, len(req))

    # Set salt for authentication
    if response["code"] == 0:
        salt = response["msg"]["salt"]
        api.set_salt(salt)

        # Now you can send authenticated commands
        # Example: Restart miner service
        req = api.set_miner_service("restart")
        response = tcp.send(req, len(req))
        print(response)
finally:
    tcp.close()
```

## Reading Serial Numbers

```python
from whatsminer_read_sn import whatsminer_read_sn

# Get miner serial numbers
result = whatsminer_read_sn("192.168.1.100")
if result:
    print(f"Miner SN: {result['miner_sn']}")
    print(f"PCB SNs: {result['pcb_sn_0']}, {result['pcb_sn_1']}, {result['pcb_sn_2']}, {result['pcb_sn_3']}")
```

## Key Features

- Full API v3 support with AES-256 encryption
- Pool configuration management
- Power and performance control
- System management (reboot, factory reset)
- Fan and temperature control
- Password management

## API Reference

### Core Methods

- `get_request_cmds(cmd, param)` - Generate unauthenticated request
- `set_request_cmds(cmd, param)` - Generate authenticated request

### Pool Configuration

```python
api.set_miner_pools(
    "stratum+tcp://pool1.example.com:3333",
    "worker1",
    "password1",
    "stratum+tcp://pool2.example.com:3333",
    "worker2",
    "password2",
    "stratum+tcp://pool3.example.com:3333",
    "worker3",
    "password3"
)
```

### Power Management

```python
# Set power mode (low, normal, high)
api.set_miner_power_mode("normal")

# Set power percentage
api.set_miner_power_percent("auto", 90)  # Use 90% of available power
```

### System Control

```python
# Reboot device
api.set_system_reboot()

# Factory reset
api.set_system_factory_reset()

# Change user password
api.set_user_passwd("user1", "old_password", "new_password")
```
