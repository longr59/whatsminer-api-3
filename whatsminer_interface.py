import base64
import hashlib
import json
import time
from typing import Any, Dict, Optional, Union

from Cryptodome.Cipher import AES


class WhatsminerAPIv3:
    """API interface for Whatsminer API version 3"""

    def __init__(self, account: str, password: str):
        """
        Initialize the API interface.

        Args:
            account: API account (supported: super, user1, user2, user3)
            password: Account password
        """
        self.account = account
        self.password = password
        self.salt = ""

    def set_salt(self, salt: str) -> None:
        """
        Set the salt value for API authentication.

        Args:
            salt: Salt value (should not be empty)
        """
        self.salt = salt

    def _generate_token(self, command: str, ts: int) -> str:
        """
        Generate authentication token.

        Args:
            command: API command
            ts: Timestamp

        Returns:
            Authentication token
        """
        src_buff = f"{command}{self.password}{self.salt}{ts}"
        aes_key = hashlib.sha256(src_buff.encode("utf-8")).digest()
        dst_buff = base64.b64encode(aes_key).decode("utf-8")
        return dst_buff[:8]

    def _encrypt_param(self, param: str, command: str, ts: int) -> str:
        """
        Encrypt parameters using AES-256 encryption.

        Args:
            param: Parameters to encrypt
            command: API command
            ts: Timestamp

        Returns:
            Base64 encoded encrypted parameters
        """
        src_buff = f"{command}{self.password}{self.salt}{ts}"
        aes_key = hashlib.sha256(src_buff.encode("utf-8")).digest()
        pad_len = 16 - (len(param) % 16)
        padded_param = param + (chr(pad_len) * pad_len)
        cipher = AES.new(aes_key, AES.MODE_ECB)  # type: ignore
        encrypted_bytes = cipher.encrypt(padded_param.encode())
        return base64.b64encode(encrypted_bytes).decode()

    def get_request_cmds(self, cmd: str, param: Optional[Any] = None) -> str:
        """
        Generate request command without authentication.

        Args:
            cmd: API command
            param: Command parameters

        Returns:
            JSON formatted command string
        """
        payload = {"cmd": cmd, "param": param}
        return json.dumps(payload)

    def set_request_cmds(self, cmd: str, param: Optional[Any] = None) -> str:
        """
        Generate authenticated request command.

        Args:
            cmd: API command
            param: Command parameters

        Returns:
            JSON formatted command string with authentication
        """
        payload: Dict[str, Any] = {"cmd": cmd, "param": param}
        ts = int(time.time())
        token = self._generate_token(cmd, ts)
        payload["ts"] = ts
        payload["token"] = token
        payload["account"] = self.account
        return json.dumps(payload)

    def set_fan_poweroff_cool(self, param: Any) -> str:
        """Set fan power-off cooling mode."""
        return self.set_request_cmds("set.fan.poweroff_cool", param)

    def set_fan_temp_offset(self, param: Any) -> str:
        """Set fan temperature offset."""
        return self.set_request_cmds("set.fan.temp_offset", param)

    def set_fan_zero_speed(self, param: Any) -> str:
        """Set fan zero speed mode."""
        return self.set_request_cmds("set.fan.zero_speed", param)

    def set_log_upload(self, server_ip: str, server_port: str) -> str:
        """
        Configure log upload settings.

        Args:
            server_ip: Log server IP address
            server_port: Log server port (as string, e.g. "9990")
        """
        payload = {"ip": server_ip, "port": server_port, "proto": "udp"}
        return self.set_request_cmds("set.log.upload", json.dumps(payload))

    def set_miner_cointype(self, cointype: str) -> str:
        """Set miner coin type."""
        payload = {"cointype": cointype}
        return self.set_request_cmds("set.miner.cointype", json.dumps(payload))

    def set_miner_fastboot(self, param: str) -> str:
        """
        Set miner fast boot.

        Args:
            param: 'enable' or 'disable'
        """
        return self.set_request_cmds("set.miner.fastboot", param)

    def set_miner_heat_mode(self, param: str) -> str:
        """
        Set miner heat mode.

        Args:
            param: 'heating', 'normal' or 'anti-icing'
        """
        return self.set_request_cmds("set.miner.heat_mode", param)

    def set_miner_pools(
        self,
        pool_url1: str,
        work_user1: str,
        work_passwd1: str,
        pool_url2: str,
        work_user2: str,
        work_passwd2: str,
        pool_url3: str,
        work_user3: str,
        work_passwd3: str,
    ) -> str:
        """Set mining pool configuration."""
        command = "set.miner.pools"
        param_data = [
            {
                "pool": pool_url1,
                "worker": work_user1,
                "passwd": work_passwd1,
            },
            {
                "pool": pool_url2,
                "worker": work_user2,
                "passwd": work_passwd2,
            },
            {
                "pool": pool_url3,
                "worker": work_user3,
                "passwd": work_passwd3,
            },
        ]

        payload: Dict[str, Any] = {"cmd": command}
        ts = int(time.time())
        token = self._generate_token(command, ts)

        payload.update(
            {
                "ts": ts,
                "token": token,
                "account": self.account,
                "param": self._encrypt_param(json.dumps(param_data), command, ts),
            }
        )

        return json.dumps(payload)

    def set_miner_power(self, param: Any) -> str:
        """Set miner power settings."""
        return self.set_request_cmds("set.miner.power", param)

    def set_miner_power_percent(self, mode: str, percent: Union[str, int]) -> str:
        """Set miner power percentage."""
        percent_str = str(percent)
        payload = {"percent": percent_str, "mode": mode}
        return self.set_request_cmds("set.miner.power_percent", json.dumps(payload))

    def set_miner_power_limit(self, param: Any) -> str:
        """Set miner power limit."""
        return self.set_request_cmds("set.miner.power_limit", param)

    def set_miner_power_mode(self, param: str) -> str:
        """
        Set miner power mode.

        Args:
            param: 'low', 'normal' or 'high'
        """
        return self.set_request_cmds("set.miner.power_mode", param)

    def set_miner_report(self, gap: int) -> str:
        """Set miner reporting interval."""
        payload = {"gap": gap}
        return self.set_request_cmds("set.miner.report", json.dumps(payload))

    def set_miner_restore_setting(self) -> str:
        """Restore miner to default settings."""
        return self.set_request_cmds("set.miner.restore_setting")

    def set_miner_service(self, param: str) -> str:
        """Control miner service."""
        return self.set_request_cmds("set.miner.service", param)

    def set_miner_target_freq(self, param: Any) -> str:
        """Set miner target frequency."""
        return self.set_request_cmds("set.miner.target_freq", param)

    def set_miner_upfreq_speed(self, param: Any) -> str:
        """Set miner frequency ramp-up speed."""
        return self.set_request_cmds("set.miner.upfreq_speed", param)

    def set_system_hostname(self, hostname: str) -> str:
        """Set system hostname."""
        payload = {"hostname": hostname}
        return self.set_request_cmds("set.system.hostname", json.dumps(payload))

    def set_system_factory_reset(self) -> str:
        """Reset system to factory defaults."""
        return self.set_request_cmds("set.system.factory_reset")

    def set_system_reboot(self) -> str:
        """Reboot the system."""
        return self.set_request_cmds("set.system.reboot")

    def set_system_timezone(self, timezone: str, zonename: str) -> str:
        """Set system timezone."""
        payload = {"timezone": timezone, "zonename": zonename}
        return self.set_request_cmds("set.system.timezone", json.dumps(payload))

    def set_user_passwd(self, username: str, old_passwd: str, new_passwd: str) -> str:
        """Change user password."""
        cmd = "set.user.change_passwd"
        param_data = {"account": username, "new": new_passwd, "old": old_passwd}

        payload: Dict[str, Any] = {"cmd": cmd}
        ts = int(time.time())
        token = self._generate_token(cmd, ts)

        payload.update(
            {
                "ts": ts,
                "token": token,
                "account": self.account,
                "param": self._encrypt_param(json.dumps(param_data), cmd, ts),
            }
        )

        return json.dumps(payload)
