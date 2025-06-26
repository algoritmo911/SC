// SPDX-License-Identifier: MIT
// Пример простого скрипта развертывания для Hardhat

async function main() {
  // Получаем аккаунт для развертывания
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Компилируем и развертываем SystemCoin
  const SystemCoin = await ethers.getContractFactory("SystemCoin");
  const systemCoin = await SystemCoin.deploy();
  await systemCoin.deployed();
  console.log("SystemCoin deployed to:", systemCoin.address);

  // Компилируем и развертываем KnowledgeNFT
  const KnowledgeNFT = await ethers.getContractFactory("KnowledgeNFT");
  const knowledgeNFT = await KnowledgeNFT.deploy();
  await knowledgeNFT.deployed();
  console.log("KnowledgeNFT deployed to:", knowledgeNFT.address);

  console.log("Deployment complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
