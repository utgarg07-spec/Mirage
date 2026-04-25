const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying MirageRegistry...");
  const MirageRegistry = await hre.ethers.getContractFactory("MirageRegistry");
  const registry = await MirageRegistry.deploy();
  await registry.waitForDeployment();
  const address = await registry.getAddress();
  console.log(`MirageRegistry deployed to: ${address}`);

  // Save address and ABI for Python backend
  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) fs.mkdirSync(deploymentsDir);

  const artifactPath = path.join(
    __dirname,
    "../artifacts/contracts/MirageRegistry.sol/MirageRegistry.json"
  );
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

  const deployment = {
    address: address,
    abi: artifact.abi,
    network: "localhost",
    deployedAt: new Date().toISOString()
  };

  fs.writeFileSync(
    path.join(deploymentsDir, "localhost.json"),
    JSON.stringify(deployment, null, 2)
  );
  console.log("Deployment info saved to deployments/localhost.json");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
