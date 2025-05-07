import json
import socket
import struct
from typing import Any, Dict, Optional


class WhatsminerTCP:
    """TCP client for Whatsminer communication protocol"""

    def __init__(self, ip: str, port: int, account: str, password: str):
        """
        Initialize the TCP client for Whatsminer.

        Args:
            ip: The IP address of the Whatsminer device
            port: The port number to connect to
            account: The account name for authentication
            password: The password for authentication
        """
        self.ip = ip
        self.port = port
        self.account = account
        self.password = password
        self.sock: Optional[socket.socket] = None

    def connect(self) -> None:
        """Connect to the Whatsminer device."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))

    def close(self) -> None:
        """Close the connection to the Whatsminer device."""
        if self.sock:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()

    def send(self, message: str, message_length: int) -> Dict[str, Any]:
        """
        Send a message to the Whatsminer device.

        Args:
            message: The message to send
            message_length: The length of the message

        Returns:
            The JSON response from the device
        """
        if not self.sock:
            raise RuntimeError("Not connected. Call connect() first.")

        length_bytes = struct.pack("<I", message_length)
        self.sock.sendall(length_bytes)
        self.sock.sendall(message.encode())
        response = self._receive_response()

        if response is None:
            raise RuntimeError("Failed to receive response")

        return json.loads(response)

    def _receive_response(self) -> Optional[str]:
        """
        Receive the response from the TCP connection.

        Returns:
            The response as a string or None if an error occurred
        """
        if not self.sock:
            return None

        buffer = b""

        # Read the first 4 bytes for response json length
        length_data = self.sock.recv(4)
        if len(length_data) < 4:
            print("Failed to receive the full length information")
            return None

        rsp_len = struct.unpack("<I", length_data)[0]
        if rsp_len > 8192:
            print("Invalid response length:", rsp_len)
            return None

        # Receive the rest of the data
        while len(buffer) < rsp_len:
            more_data = self.sock.recv(rsp_len - len(buffer))
            if not more_data:
                break
            buffer += more_data

        return buffer.decode()
