import sys
import os
# Add backend/ directory to path so 'blockchain' package is found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> None:
    print("[TEST] Initializing Web3Handler...")
    from blockchain.web3_handler import Web3Handler

    handler = Web3Handler()
    if not handler.available:
        print(f"[TEST] Blockchain unavailable: {handler.reason}")
        return

    print(f"[TEST] Current threat count: {handler.get_threat_count()}")

    result = handler.register_threat(
        "192.168.1.100",
        ["whoami", "cat /etc/passwd", "sudo su", "cat transactions_2026.csv"],
        "collection",
        3,
    )
    print(f"[TEST] Register result: {result}")
    if not result.get("success"):
        return

    print(f"[TEST] New threat count: {handler.get_threat_count()}")

    check = handler.check_threat(result["fingerprint"])
    print(f"[TEST] Check result: {check}")

    alert = handler.broadcast_alert(
        result["fingerprint"],
        "Advanced attacker detected - collection stage reached",
    )
    print(f"[TEST] Alert result: {alert}")

    all_threats = handler.get_all_threats()
    print(f"[TEST] All threats count: {len(all_threats)}")
    if all_threats:
        print(f"[TEST] First threat: {all_threats[0]}")


if __name__ == "__main__":
    main()
