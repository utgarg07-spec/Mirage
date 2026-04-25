"""Web3 integration layer for MIRAGE threat registry contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Web3Handler:
    def __init__(self):
        self.available = False
        self.reason = ""
        self.w3 = None
        self.contract = None
        self.default_sender = None

        try:
            deployment_path = (
                Path(__file__).resolve().parent.parent.parent
                / "contracts"
                / "deployments"
                / "localhost.json"
            )
            with open(deployment_path, "r", encoding="utf-8") as f:
                deployment = json.load(f)

            self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if not self.w3.is_connected():
                raise RuntimeError("Hardhat node not reachable at 127.0.0.1:8545")

            self.default_sender = self.w3.eth.accounts[0]
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(deployment["address"]),
                abi=deployment["abi"],
            )
            self.available = True
            print("[BLOCKCHAIN] Connected")
        except Exception as e:
            self.reason = str(e)
            self.available = False
            print(f"[BLOCKCHAIN] Not available: {self.reason}")

    def register_threat(self, ip, commands_list, stage, skill_level) -> dict:
        try:
            if not self.available:
                raise RuntimeError(self.reason or "Web3 handler unavailable")

            command_hash = hashlib.sha256(
                json.dumps(commands_list, sort_keys=True).encode("utf-8")
            ).hexdigest()

            tx_hash = self.contract.functions.registerThreat(
                ip, command_hash, stage, int(skill_level)
            ).transact(
                {
                    "from": self.default_sender,
                    "gas": 300000,
                }
            )
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            contract_events = self.contract.events.ThreatRegistered()
            logs = contract_events.process_receipt(receipt)
            actual_fingerprint = logs[0]["args"]["fingerprint"].hex()
            actual_fingerprint = "0x" + actual_fingerprint
            return {
                "success": True,
                "fingerprint": actual_fingerprint,
                "tx_hash": receipt.transactionHash.hex(),
                "block": receipt.blockNumber,
                "stage": stage,
                "skill_level": int(skill_level),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_threat(self, fingerprint_hex: str) -> dict:
        try:
            if not self.available:
                return {"is_known": False, "data": None}

            fingerprint_bytes32 = bytes.fromhex(fingerprint_hex.replace("0x", ""))

            exists, attacker_ip, stage, skill, timestamp = self.contract.functions.checkThreat(
                fingerprint_bytes32
            ).call()
            if not exists:
                return {"is_known": False, "data": None}

            return {
                "is_known": True,
                "data": {
                    "fingerprint": fingerprint_hex,
                    "ip": attacker_ip,
                    "stage": stage,
                    "skill_level": int(skill),
                    "timestamp": int(timestamp),
                },
            }
        except Exception:
            return {"is_known": False, "data": None}

    def broadcast_alert(self, fingerprint_hex, message) -> dict:
        try:
            if not self.available:
                raise RuntimeError(self.reason or "Web3 handler unavailable")

            fingerprint_bytes32 = bytes.fromhex(fingerprint_hex.replace("0x", ""))
            tx_hash = self.contract.functions.broadcastAlert(
                fingerprint_bytes32,
                message,
            ).transact(
                {
                    "from": self.default_sender,
                    "gas": 300000,
                }
            )
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {"success": True, "tx_hash": receipt.transactionHash.hex()}
        except Exception as e:
            return {"success": False, "tx_hash": "", "error": str(e)}

    def get_all_threats(self) -> list:
        if not self.available:
            return []
        try:
            threats = []
            fingerprints = self.contract.functions.getAllThreats().call()
            for fp in fingerprints:
                exists, attacker_ip, stage, skill, timestamp = self.contract.functions.checkThreat(fp).call()
                if exists:
                    threats.append(
                        {
                            "fingerprint": "0x" + fp.hex(),
                            "ip": attacker_ip,
                            "stage": stage,
                            "skill_level": int(skill),
                            "timestamp": int(timestamp),
                        }
                    )
            return threats
        except Exception:
            return []

    def get_threat_count(self) -> int:
        if not self.available:
            return 0
        try:
            return int(self.contract.functions.getThreatCount().call())
        except Exception:
            return 0
