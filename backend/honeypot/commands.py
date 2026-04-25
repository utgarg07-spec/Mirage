"""Trie-based command resolver and convincing fake shell responses."""

from __future__ import annotations

import os
import shlex
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelligence.honey_file_generator import generate_honey_file

from .fake_filesystem import read_fake_file, register_fake_file


PROMPT_USER = "root"
PROMPT_HOST = "fintech-prod-01"

DEFAULT_CWD = "/root"


@dataclass
class SessionState:
    cwd: str = DEFAULT_CWD
    history: list[str] = field(default_factory=list)
    is_root: bool = True


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.value: str | None = None


class CommandTrie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, command: str, value: str) -> None:
        node = self.root
        for char in command:
            node = node.children.setdefault(char, TrieNode())
        node.value = value

    def longest_prefix_value(self, text: str) -> str | None:
        node = self.root
        best: str | None = None
        for char in text:
            if char not in node.children:
                break
            node = node.children[char]
            if node.value is not None:
                best = node.value
        return best


class CommandEngine:
    """Resolve commands using a Trie and dynamic handlers."""

    def __init__(self) -> None:
        self.lookup = CommandTrie()
        self.static_responses = self._build_static_responses()
        self.planted_files: set[str] = set()
        for command in self.static_responses:
            self.lookup.insert(command, command)

    @staticmethod
    def _build_static_responses() -> dict[str, str]:
        return {
            "ls": (
                "transactions_2026.csv  customer_pii_backup.tar.gz  .ssh/  logs/  "
                "config/  payment_api_keys.env"
            ),
            "pwd": "/root",
            "whoami": "root",
            "id": "uid=0(root) gid=0(root) groups=0(root),27(sudo),999(payments)",
            "uname -a": (
                "Linux fintech-prod-01 5.15.0-1023-aws #27-Ubuntu SMP Fri Mar 15 "
                "12:03:17 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux"
            ),
            "cat /etc/passwd": (
                "root:x:0:0:root:/root:/bin/bash\n"
                "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                "sys:x:3:3:sys:/dev:/usr/sbin/nologin\n"
                "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
                "ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n"
                "postgres:x:113:121:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash\n"
                "paymentsvc:x:1002:1002:Payment Processing Service:/opt/paymentsvc:/bin/false"
            ),
            "cat /etc/hostname": PROMPT_HOST,
            "ps aux": (
                "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
                "root         1  0.0  0.2 169184 11872 ?        Ss   Apr22   0:04 /sbin/init\n"
                "root       612  0.1  1.1 152904 45120 ?        Ssl  Apr22   3:12 /usr/bin/python3 /opt/paymentsvc/api.py\n"
                "postgres   844  0.0  0.9 219740 37716 ?        Ss   Apr22   1:05 /usr/lib/postgresql/14/bin/postgres\n"
                "root      1021  0.0  0.4  99520 17520 ?        Ssl  Apr22   0:31 /usr/sbin/sshd -D\n"
                "root      1448  0.2  2.4 423400 98512 ?        Ssl  Apr22   6:59 /usr/bin/dockerd -H fd://\n"
                "root      2974  0.0  0.1  13948  6928 pts/0    Ss+  00:04   0:00 -bash"
            ),
            "ifconfig": (
                "ens5: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9001\n"
                "        inet 10.42.17.83  netmask 255.255.240.0  broadcast 10.42.31.255\n"
                "        inet6 fe80::9cf1:68ff:fea0:8f12  prefixlen 64  scopeid 0x20<link>\n"
                "        ether 9e:f1:68:a0:8f:12  txqueuelen 1000  (Ethernet)\n"
                "        RX packets 2004115  bytes 1789923410 (1.7 GB)\n"
                "        TX packets 1958834  bytes 2388204411 (2.3 GB)\n"
                "\n"
                "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536\n"
                "        inet 127.0.0.1  netmask 255.0.0.0\n"
                "        inet6 ::1  prefixlen 128  scopeid 0x10<host>"
            ),
            "netstat": (
                "Active Internet connections (only servers)\n"
                "Proto Recv-Q Send-Q Local Address           Foreign Address         State\n"
                "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN\n"
                "tcp        0      0 10.42.17.83:5432         0.0.0.0:*               LISTEN\n"
                "tcp        0      0 10.42.17.83:443          0.0.0.0:*               LISTEN\n"
                "tcp6       0      0 :::22                   :::*                    LISTEN\n"
                "unix  2      [ ACC ]     STREAM     LISTENING     32094    /run/docker.sock"
            ),
            "env": (
                "SHELL=/bin/bash\n"
                "PWD=/root\n"
                "LOGNAME=root\n"
                "HOME=/root\n"
                "LANG=en_US.UTF-8\n"
                "TERM=xterm-256color\n"
                "USER=root\n"
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
                "PAYMENT_ENV=production\n"
                "REGION=us-east-1\n"
                "DB_HOST=10.42.17.21\n"
                "K8S_NODE=fintech-node-a3"
            ),
            "cat /etc/shadow": "cat: /etc/shadow: Permission denied",
            "sudo su": "root@fintech-prod-01:~# ",
        }

    def plant_honey_files(self, honey_files: list[str], stage: str = "collection") -> None:
        """Add files to ls output and register readable fake contents."""
        for filename in honey_files:
            clean_name = filename.strip()
            if not clean_name:
                continue
            self.planted_files.add(clean_name)
            register_fake_file(clean_name, generate_honey_file(clean_name, stage))

    def _resolve_cd(self, command: str, state: SessionState) -> str:
        parts = shlex.split(command)
        target = parts[1] if len(parts) > 1 else "/root"
        if target in ("~", "/root"):
            state.cwd = "/root"
        elif target.startswith("/"):
            state.cwd = target.rstrip("/") or "/"
        else:
            base = state.cwd.rstrip("/")
            state.cwd = f"{base}/{target}".replace("//", "/")
        return ""

    def _resolve_echo(self, command: str) -> str:
        return command[len("echo") :].strip()

    def _resolve_history(self, state: SessionState) -> str:
        if not state.history:
            return ""
        return "\n".join(f"{idx + 1}  {cmd}" for idx, cmd in enumerate(state.history))

    def _resolve_cat(self, command: str) -> str | None:
        parts = shlex.split(command)
        if len(parts) < 2:
            return "cat: missing file operand"
        file_name = parts[1]
        contents = read_fake_file(file_name)
        if contents is None:
            return f"cat: {file_name}: No such file or directory"
        return contents

    def is_known_command(self, raw_command: str) -> bool:
        """Return True when command is handled by local honeypot logic."""
        command = raw_command.strip()
        if not command:
            return True
        if command.startswith(("cd", "echo", "cat ")):
            return True
        if command == "history":
            return True
        token = self.lookup.longest_prefix_value(command)
        return bool(token and token == command)

    def execute(self, raw_command: str, state: SessionState) -> str:
        command = raw_command.strip()
        if not command:
            return ""

        state.history.append(command)

        token = self.lookup.longest_prefix_value(command)
        if token and token == command:
            if token == "sudo su":
                state.is_root = True
            if token == "pwd":
                return state.cwd
            if token == "ls":
                base = self.static_responses["ls"]
                if self.planted_files:
                    extras = "  ".join(sorted(self.planted_files))
                    return f"{base}  {extras}".strip()
                return base
            return self.static_responses[token]

        if command.startswith("cd"):
            return self._resolve_cd(command, state)
        if command.startswith("echo"):
            return self._resolve_echo(command)
        if command == "history":
            return self._resolve_history(state)
        if command.startswith("cat "):
            dynamic_cat = self._resolve_cat(command)
            if dynamic_cat is not None:
                return dynamic_cat

        return f"bash: {command}: command not found"


def get_prompt(state: SessionState) -> str:
    """Keep prompt fixed as requested while retaining session cwd state."""
    suffix = "#" if state.is_root else "$"
    return f"{PROMPT_USER}@{PROMPT_HOST}:~{suffix} "
