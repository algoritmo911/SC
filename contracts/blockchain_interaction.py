# contracts/blockchain_interaction.py

from typing import Any, Dict, Optional, List, Union
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware # For PoA networks like Polygon, Rinkeby
from web3.contract import Contract

# Assuming TokenizationInterface is defined in core.interfaces
# from core.interfaces import TokenizationInterface
# Assuming KnowledgeUnit is defined in core.knowledge_units (or its relevant parts for NFT metadata)
# from core.knowledge_units import KnowledgeUnit

# Placeholder for the actual TokenizationInterface from core.interfaces
class TokenizationInterface: # Placeholder
    async def mint_sc_tokens(self, recipient_address: str, amount: float, ku_id: str) -> str: pass
    async def mint_ku_nft(self, owner_address: str, ku_data: Any, token_uri: str) -> str: pass # ku_data could be KnowledgeUnit
    async def transfer_sc_tokens(self, from_address: str, to_address: str, amount: float) -> str: pass
    async def get_sc_balance(self, address: str) -> float: pass
    async def get_ku_nft_owner(self, token_id: Union[str, int]) -> Optional[str]: pass
    async def get_ku_nft_token_uri(self, token_id: Union[str, int]) -> Optional[str]: pass


class BlockchainService(TokenizationInterface):
    """
    Service class for interacting with blockchain networks (e.g., Ethereum-compatible).
    Manages contract instances and provides methods for token operations.
    This is a basic implementation and would need significant enhancements for production.
    """

    def __init__(self, rpc_url: str, private_key: Optional[str] = None,
                 sc_token_address: Optional[str] = None, sc_token_abi: Optional[List[Dict]] = None,
                 ku_nft_address: Optional[str] = None, ku_nft_abi: Optional[List[Dict]] = None,
                 chain_id: Optional[int] = None, gas_limit: int = 500000, max_priority_fee_per_gas_gwei: int = 2, max_fee_per_gas_gwei: int = 50):
        """
        Initializes the BlockchainService.
        Args:
            rpc_url: URL of the Ethereum JSON-RPC endpoint.
            private_key: Private key of the account used to send transactions (operator/minter).
                         Required for operations that modify state (mint, transfer).
            sc_token_address: Address of the deployed SC ERC20 token contract.
            sc_token_abi: ABI of the SC ERC20 token contract.
            ku_nft_address: Address of the deployed KU ERC721 NFT contract.
            ku_nft_abi: ABI of the KU ERC721 NFT contract.
            chain_id: Network Chain ID (e.g., 1 for Ethereum Mainnet, 4 for Rinkeby). Auto-detected if None.
            gas_limit: Default gas limit for transactions.
            max_priority_fee_per_gas_gwei: Max priority fee per gas (for EIP-1559 txns).
            max_fee_per_gas_gwei: Max fee per gas (for EIP-1559 txns).
        """
        self.w3 = Web3(HTTPProvider(rpc_url))

        # Inject PoA middleware if connecting to a PoA network (e.g., Rinkeby, Goerli, Polygon)
        # This might need to be conditional based on the network.
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to blockchain RPC at {rpc_url}")

        self.private_key = private_key
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.w3.eth.default_account = self.account.address # Optional: sets default sender
        else:
            self.account = None # Read-only operations possible without private key

        self.chain_id = chain_id if chain_id else self.w3.eth.chain_id
        self.gas_limit = gas_limit
        self.max_priority_fee_per_gas_gwei = max_priority_fee_per_gas_gwei
        self.max_fee_per_gas_gwei = max_fee_per_gas_gwei


        self.sc_token_contract: Optional[Contract] = None
        if sc_token_address and sc_token_abi:
            self.sc_token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(sc_token_address),
                abi=sc_token_abi
            )

        self.ku_nft_contract: Optional[Contract] = None
        if ku_nft_address and ku_nft_abi:
            self.ku_nft_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(ku_nft_address),
                abi=ku_nft_abi
            )

    def _get_nonce(self) -> int:
        if not self.account:
            raise ValueError("Account not set. Private key is required for transactions.")
        return self.w3.eth.get_transaction_count(self.account.address)

    def _build_transaction_options(self, value_wei: int = 0) -> Dict[str, Any]:
        """Builds common transaction options, handling EIP-1559 or legacy gas pricing."""
        options = {
            "chainId": self.chain_id,
            "nonce": self._get_nonce(),
            "gas": self.gas_limit, # This is the gas limit, not gas price
            "value": value_wei,
        }
        # EIP-1559 gas pricing (preferred)
        try:
            # Ensure base_fee_per_gas is available (usually is on EIP-1559 networks)
            # latest_block = self.w3.eth.get_block('latest')
            # base_fee = latest_block.get('baseFeePerGas', None)

            options['maxPriorityFeePerGas'] = self.w3.to_wei(self.max_priority_fee_per_gas_gwei, 'gwei')
            options['maxFeePerGas'] = self.w3.to_wei(self.max_fee_per_gas_gwei, 'gwei')
            # If base_fee is available and you want more dynamic maxFeePerGas:
            # options['maxFeePerGas'] = base_fee + self.w3.to_wei(self.max_priority_fee_per_gas_gwei, 'gwei')

        except Exception: # Fallback to legacy gas pricing if EIP-1559 fields cause issues or not supported
            print("Warning: Falling back to legacy gas pricing (gasPrice).")
            options['gasPrice'] = self.w3.eth.gas_price # Let Web3.py determine current gas price

        return options

    async def _send_transaction(self, transaction) -> str:
        if not self.private_key:
            raise ValueError("Private key not provided. Cannot sign transactions.")
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return tx_hash.hex()

    # --- TokenizationInterface Implementation ---

    async def mint_sc_tokens(self, recipient_address: str, amount: float, ku_id: str, reason: str = "KU Contribution") -> str:
        if not self.sc_token_contract:
            raise ConnectionError("SC Token contract not initialized.")
        if not self.account:
            raise ValueError("Operator account not set for minting.")

        # Assuming SC token has 18 decimals
        # TODO: Fetch decimals from contract or make configurable
        amount_in_wei = self.w3.to_wei(amount, 'ether')
        recipient_checksum_address = Web3.to_checksum_address(recipient_address)

        tx_options = self._build_transaction_options()
        transaction = self.sc_token_contract.functions.mint(
            recipient_checksum_address,
            amount_in_wei,
            ku_id, # Pass KU ID for on-chain tracking if contract supports it
            reason
        ).build_transaction(tx_options)

        tx_hash = await self._send_transaction(transaction)
        print(f"Minting {amount} SC to {recipient_address} for KU {ku_id}. Tx Hash: {tx_hash}")
        return tx_hash

    async def mint_ku_nft(self, owner_address: str, ku_system_id: str, token_uri: str) -> str:
        if not self.ku_nft_contract:
            raise ConnectionError("KU NFT contract not initialized.")
        if not self.account:
            raise ValueError("Operator account not set for NFT minting.")

        owner_checksum_address = Web3.to_checksum_address(owner_address)

        tx_options = self._build_transaction_options()
        # Assuming contract has a 'safeMint(address to, string memory kuSystemId, string memory tokenURI_)' function
        transaction = self.ku_nft_contract.functions.safeMint(
            owner_checksum_address,
            ku_system_id, # System's internal ID for the KU
            token_uri     # URI to metadata (e.g., IPFS CID for JSON metadata)
        ).build_transaction(tx_options)

        tx_hash = await self._send_transaction(transaction)
        print(f"Minting KU-NFT for KU {ku_system_id} to {owner_address} with URI {token_uri}. Tx Hash: {tx_hash}")
        return tx_hash

    async def transfer_sc_tokens(self, from_address: str, to_address: str, amount: float) -> str:
        # This assumes the `self.account` (operator) has approval or is the `from_address`.
        # For user-to-user transfers initiated by the user, they'd sign with their own private key.
        # If this service acts as a relayer or uses its own funds, `from_address` might be `self.account.address`.
        if not self.sc_token_contract:
            raise ConnectionError("SC Token contract not initialized.")
        if not self.account or self.account.address.lower() != from_address.lower():
             # This check might be too restrictive depending on the use case.
             # If the service's account is meant to transfer on behalf of others, it needs approval.
            raise ValueError("Transfer 'from_address' must be the operator's address for this implementation, or operator needs approval.")


        amount_in_wei = self.w3.to_wei(amount, 'ether') # Assuming 18 decimals
        to_checksum_address = Web3.to_checksum_address(to_address)
        # from_checksum_address = Web3.to_checksum_address(from_address) # Already self.account.address

        tx_options = self._build_transaction_options()
        transaction = self.sc_token_contract.functions.transfer(
            to_checksum_address,
            amount_in_wei
        ).build_transaction(tx_options) # `from` is implicitly `self.account.address`

        tx_hash = await self._send_transaction(transaction)
        print(f"Transferring {amount} SC from {from_address} to {to_address}. Tx Hash: {tx_hash}")
        return tx_hash

    async def get_sc_balance(self, address: str) -> float:
        if not self.sc_token_contract:
            raise ConnectionError("SC Token contract not initialized.")
        checksum_address = Web3.to_checksum_address(address)
        balance_wei = self.sc_token_contract.functions.balanceOf(checksum_address).call()
        # TODO: Fetch decimals from contract or make configurable
        balance_ether = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_ether)

    async def get_ku_nft_owner(self, token_id: Union[str, int]) -> Optional[str]:
        if not self.ku_nft_contract:
            raise ConnectionError("KU NFT contract not initialized.")
        try:
            # Ensure token_id is int if it comes as string
            nft_token_id = int(token_id)
            owner_address = self.ku_nft_contract.functions.ownerOf(nft_token_id).call()
            return owner_address
        except Exception as e: # Catch ContractLogicError for non-existent token, ValueError for bad token_id format
            print(f"Error fetching owner for NFT token ID {token_id}: {e}")
            return None

    async def get_ku_nft_token_uri(self, token_id: Union[str, int]) -> Optional[str]:
        if not self.ku_nft_contract:
            raise ConnectionError("KU NFT contract not initialized.")
        try:
            nft_token_id = int(token_id)
            uri = self.ku_nft_contract.functions.tokenURI(nft_token_id).call()
            return uri
        except Exception as e:
            print(f"Error fetching tokenURI for NFT token ID {token_id}: {e}")
            return None

    async def get_ku_system_id_for_nft(self, token_id: Union[str, int]) -> Optional[str]:
        """ Custom function if your NFT contract has getKUSystemId """
        if not self.ku_nft_contract:
            raise ConnectionError("KU NFT contract not initialized.")
        try:
            nft_token_id = int(token_id)
            # Check if the function exists in the ABI before calling
            if 'getKUSystemId' not in [f.fn_name for f in self.ku_nft_contract.all_functions()]:
                print("getKUSystemId function not found in KU NFT contract ABI.")
                return None
            ku_system_id = self.ku_nft_contract.functions.getKUSystemId(nft_token_id).call()
            return ku_system_id
        except Exception as e:
            print(f"Error fetching KU System ID for NFT token ID {token_id}: {e}")
            return None

    # --- Other utility functions ---
    def get_transaction_receipt(self, tx_hash: str, timeout_seconds: int = 120) -> Optional[Dict[str, Any]]:
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout_seconds)
            return dict(receipt)
        except Exception as e: # Catches web3.exceptions.TimeExhausted
            print(f"Timeout or error waiting for transaction receipt for {tx_hash}: {e}")
            return None


# Example Usage (Conceptual - requires setup and running blockchain node)
# async def main():
#     # Load ABIs (e.g., from erc20_templates.py, erc721_templates.py or JSON files)
#     from .erc20_templates import SC_TOKEN_ABI_EXAMPLE
#     from .erc721_templates import KU_NFT_ABI_EXAMPLE
#
#     # Configuration (replace with actual values from your environment/config)
#     # Ensure you have a .env or config mechanism for these secrets
#     rpc_url = "http://localhost:8545" # Or your Infura/Alchemy URL
#     operator_private_key = "YOUR_OPERATOR_PRIVATE_KEY" # Keep this secure!
#     sc_token_addr = "DEPLOYED_SC_TOKEN_CONTRACT_ADDRESS"
#     ku_nft_addr = "DEPLOYED_KU_NFT_CONTRACT_ADDRESS"
#
#     if operator_private_key == "YOUR_OPERATOR_PRIVATE_KEY" or \
#        sc_token_addr == "DEPLOYED_SC_TOKEN_CONTRACT_ADDRESS" or \
#        ku_nft_addr == "DEPLOYED_KU_NFT_CONTRACT_ADDRESS":
#         print("Please configure RPC URL, private key, and contract addresses to run the example.")
#         return
#
#     blockchain_service = BlockchainService(
#         rpc_url=rpc_url,
#         private_key=operator_private_key,
#         sc_token_address=sc_token_addr,
#         sc_token_abi=SC_TOKEN_ABI_EXAMPLE, # Replace with actual loaded ABI
#         ku_nft_address=ku_nft_addr,
#         ku_nft_abi=KU_NFT_ABI_EXAMPLE,     # Replace with actual loaded ABI
#     )
#
#     try:
#         print(f"Connected to chain ID: {blockchain_service.chain_id}")
#         print(f"Operator account: {blockchain_service.account.address}")
#
#         # Example: Get SC balance
#         balance = await blockchain_service.get_sc_balance(blockchain_service.account.address)
#         print(f"SC Balance for operator: {balance} SC")
#
#         # Example: Mint SC Tokens (replace with actual recipient and KU ID)
#         # recipient = "0xRecipientAddressHere"
#         # ku_id_for_mint = "test-ku-123"
#         # if Web3.is_address(recipient):
#         #     mint_tx_hash = await blockchain_service.mint_sc_tokens(recipient, 100.0, ku_id_for_mint, "Test mint")
#         #     print(f"SC Token mint transaction hash: {mint_tx_hash}")
#         #     # receipt = blockchain_service.get_transaction_receipt(mint_tx_hash)
#         #     # print(f"Mint transaction receipt: {receipt}")
#         # else:
#         #     print(f"Invalid recipient address: {recipient}")
#
#         # Example: Mint KU NFT
#         # ku_system_identifier = "system-ku-abc-789"
#         # metadata_ipfs_uri = "ipfs://bafyreihc4ryhor3sdyvb274wkbz3n7xc7s2mpul2m5s6xqverdqrk3oq7y/metadata.json"
#         # nft_tx_hash = await blockchain_service.mint_ku_nft(
#         #     owner_address=blockchain_service.account.address, # Mint to self for example
#         #     ku_system_id=ku_system_identifier,
#         #     token_uri=metadata_ipfs_uri
#         # )
#         # print(f"KU NFT mint transaction hash: {nft_tx_hash}")
#         # nft_receipt = blockchain_service.get_transaction_receipt(nft_tx_hash)
#         # print(f"NFT Mint transaction receipt: {nft_receipt}")
#         # if nft_receipt and nft_receipt.get('status') == 1:
#         #     # If your contract emits an event with the token ID, you'd parse it from logs here
#         #     # For now, assuming token ID 1 for a newly minted NFT if it's the first one
#         #     # This is a simplification; robust token ID retrieval is needed.
#         #     # One way is to listen for the Transfer event from address(0)
#         #     # or a custom Mint event that includes the tokenId.
#         #     # The KU_NFT_CONTRACT_TEMPLATE_SOLIDITY has a KUMinted event.
#         #     # You would use w3.eth.get_filter_logs or parse receipt.logs.
#
#         #     # Let's assume tokenId 1 for example (replace with actual logic)
#         #     example_token_id = 1
#         #     nft_owner = await blockchain_service.get_ku_nft_owner(example_token_id)
#         #     print(f"Owner of NFT {example_token_id}: {nft_owner}")
#         #     nft_uri = await blockchain_service.get_ku_nft_token_uri(example_token_id)
#         #     print(f"Token URI of NFT {example_token_id}: {nft_uri}")
#
#     except ConnectionError as e:
#         print(f"Connection error: {e}")
#     except ValueError as e:
#         print(f"Value error: {e}")
#     except Exception as e: # Catch any other web3 or contract related errors
#         print(f"An unexpected error occurred: {e}")

# if __name__ == "__main__":
#     import asyncio
#     # To run this example:
#     # 1. `pip install web3`
#     # 2. Have a local Ethereum node running (e.g., Ganache, Hardhat Network) or use Infura/Alchemy.
#     # 3. Deploy the ERC20 and ERC721 contracts from templates (or your own versions).
#     # 4. Update placeholders for RPC_URL, private key, and contract addresses.
#     # asyncio.run(main())
#     pass
