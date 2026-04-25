"""Paramiko-based fake SSH honeypot server for MIRAGE."""

from __future__ import annotations

import sys
import os
import socket
import threading
import traceback
from contextlib import suppress

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paramiko

from honeypot.commands import CommandEngine, SessionState, get_prompt
from honeypot.session_logger import create_session, end_session, log_command
from intelligence.mitre_predictor import MitrePredictor
from intelligence.groq_handler import get_llm_response

HOST = "0.0.0.0"
PORT = 2222
BANNER = "Ubuntu 22.04.4 LTS \\n \\l\n"


class AcceptAllServer(paramiko.ServerInterface):
    def __init__(self) -> None:
        self.event = threading.Event()
        self.username = ""
        self.password = ""

    def check_auth_password(self, username: str, password: str) -> int:
        self.username = username
        self.password = password
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel: paramiko.Channel) -> bool:
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                   pixelwidth, pixelheight, modes) -> bool:
        return True


def _recv_line(channel: paramiko.Channel) -> str | None:
    buffer = []
    while True:
        data = channel.recv(1)
        if not data:
            return None
        ch = data.decode(errors="ignore")
        if ch in ("\r", "\n"):
            channel.send("\r\n")
            return "".join(buffer).strip()
        if ch == "\x03":
            return "exit"
        if ch in ("\x08", "\x7f"):
            if buffer:
                buffer.pop()
                channel.send("\b \b")
            continue
        if ch.isprintable():
            buffer.append(ch)
            channel.send(ch)


def _fire(func_name: str, *args):
    """Safely call a broadcaster function by name."""
    try:
        from api.event_broadcaster import (
            fire_new_session, fire_new_command,
            fire_stage_change, fire_session_ended,
            fire_threat_registered, fire_network_alert
        )
        funcs = {
            "fire_new_session": fire_new_session,
            "fire_new_command": fire_new_command,
            "fire_stage_change": fire_stage_change,
            "fire_session_ended": fire_session_ended,
            "fire_threat_registered": fire_threat_registered,
            "fire_network_alert": fire_network_alert,
        }
        if func_name in funcs:
            funcs[func_name](*args)
            print(f"[BROADCASTER] {func_name} fired OK")
    except Exception as e:
        print(f"[BROADCASTER ERROR] {func_name}: {e}")
        traceback.print_exc()


def _handle_client(client_socket: socket.socket, client_ip: str,
                   host_key: paramiko.RSAKey) -> None:
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)
    server = AcceptAllServer()
    session_id: str | None = None
    predictor = MitrePredictor()
    session_commands: list[str] = []
    current_stage = "reconnaissance"

    try:
        transport.start_server(server=server)
        channel = transport.accept(timeout=20)
        if channel is None:
            return
        if not server.event.wait(10):
            return

        session_id = create_session(client_ip, server.username, server.password)
        print(f"[HONEYPOT] New session {session_id} from {client_ip}")

        # Fire session started event
        _fire("fire_new_session", session_id, client_ip, server.username)

        engine = CommandEngine()
        state = SessionState()

        channel.send(BANNER)
        channel.send(get_prompt(state))

        while True:
            command = _recv_line(channel)
            if command is None:
                break
            if command == "":
                channel.send(get_prompt(state))
                continue
            if command.lower() in {"exit", "logout", "quit"}:
                log_command(session_id, command, "logout")
                channel.send("logout\r\nConnection to fintech-prod-01 closed.\r\n")
                break

            # Get response
            response = engine.execute(command, state)
            if not response or "command not found" in response:
                response = get_llm_response(command, session_commands[-5:])

            log_command(session_id, command, response)

            # Update prediction
            session_commands.append(command)
            prediction = predictor.predict(session_commands)
            new_stage = prediction.get("current_stage", "reconnaissance")

            # Fire stage change if changed
            if new_stage != current_stage:
                _fire("fire_stage_change", session_id, current_stage,
                      new_stage, prediction.get("confidence", 0))
                current_stage = new_stage

            # Fire command event
            _fire("fire_new_command",
                  session_id,
                  command,
                  response,
                  prediction.get("current_stage", "reconnaissance"),
                  prediction.get("confidence", 0),
                  prediction.get("next_stage", "unknown"),
                  prediction.get("skill_level", 1),
                  prediction.get("technique_tags", []))

            if response:
                channel.send(f"{response}\r\n")
            channel.send(get_prompt(state))

    except Exception as e:
        print(f"[HONEYPOT ERROR] {e}")
        traceback.print_exc()
    finally:
        if session_id:
            with suppress(Exception):
                end_session(session_id)
            _fire("fire_session_ended", session_id, current_stage,
                  predictor.predict(session_commands).get("skill_level", 1)
                  if session_commands else 1)
            print(f"[HONEYPOT] Session {session_id} ended")
        with suppress(Exception):
            transport.close()
        with suppress(Exception):
            client_socket.close()


def start_server(host: str = HOST, port: int = PORT) -> None:
    host_key = paramiko.RSAKey.generate(2048)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(100)
        print(f"[MIRAGE] SSH honeypot listening on {host}:{port}")
        while True:
            client, addr = sock.accept()
            thread = threading.Thread(
                target=_handle_client,
                args=(client, addr[0], host_key),
                daemon=True,
            )
            thread.start()


if __name__ == "__main__":
    start_server()