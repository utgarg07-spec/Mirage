// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract MirageRegistry {
    struct AttackerRecord {
        bytes32 fingerprintHash;
        string attackerIP;
        string attackStage;
        uint8 skillLevel;
        uint256 timestamp;
        bool isActive;
    }

    mapping(bytes32 => AttackerRecord) public fingerprints;
    bytes32[] public allFingerprints;

    event ThreatRegistered(
        bytes32 indexed fingerprint,
        string ip,
        string stage,
        uint8 skill,
        uint256 timestamp
    );
    event NetworkAlert(
        bytes32 indexed fingerprint,
        string message,
        uint256 timestamp
    );

    function registerThreat(
        string memory ip,
        string memory commandHash,
        string memory stage,
        uint8 skill
    ) public returns (bytes32) {
        bytes32 fingerprint = keccak256(
            abi.encodePacked(ip, commandHash, block.timestamp)
        );
        fingerprints[fingerprint] = AttackerRecord({
            fingerprintHash: fingerprint,
            attackerIP: ip,
            attackStage: stage,
            skillLevel: skill,
            timestamp: block.timestamp,
            isActive: true
        });
        allFingerprints.push(fingerprint);
        emit ThreatRegistered(fingerprint, ip, stage, skill, block.timestamp);
        return fingerprint;
    }

    function checkThreat(bytes32 fp) public view returns (
        bool exists,
        string memory ip,
        string memory stage,
        uint8 skill,
        uint256 timestamp
    ) {
        AttackerRecord memory r = fingerprints[fp];
        return (
            r.timestamp > 0,
            r.attackerIP,
            r.attackStage,
            r.skillLevel,
            r.timestamp
        );
    }

    function broadcastAlert(
        bytes32 fingerprint,
        string memory message
    ) public {
        require(fingerprints[fingerprint].timestamp > 0, "Unknown fingerprint");
        emit NetworkAlert(fingerprint, message, block.timestamp);
    }

    function getAllThreats() public view returns (bytes32[] memory) {
        return allFingerprints;
    }

    function getThreatCount() public view returns (uint256) {
        return allFingerprints.length;
    }
}
