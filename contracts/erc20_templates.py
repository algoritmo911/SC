# contracts/erc20_templates.py

# This file will contain templates or Python representations for ERC-20 smart contracts.
# These are for the SC (Sense/Contribution) value tokens.

# --- Option 1: Basic Solidity Template as a Python String ---
# This is a simplified example. Real contracts would be more complex, include more features
# (like minting controls, pausing, burning from, etc.) and likely managed in .sol files.

SC_TOKEN_CONTRACT_TEMPLATE_SOLIDITY = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol"; // For minting control

/**
 * @title SCToken
 * @dev ERC20 token for representing value (SC) within the system.
 * Allows for minting by a central authority (e.g., contract owner or MINTER_ROLE)
 * and standard ERC20 operations.
 */
contract SCToken is ERC20, ERC20Burnable, Ownable {
    // Event for tracking minting operations, including the reason (e.g., KU ID)
    event TokensMinted(address indexed to, uint256 amount, string indexed kuId, string reason);

    /**
     * @dev Constructor initializes the token.
     * @param initialOwner The address that will initially own the contract and have minting rights.
     * @param name_ The name of the token.
     * @param symbol_ The symbol of the token.
     */
    constructor(address initialOwner, string memory name_, string memory symbol_)
        ERC20(name_, symbol_)
        Ownable(initialOwner) // Sets the deployer as the initial owner
    {
        // Optionally mint an initial supply to the deployer or a treasury address
        // _mint(msg.sender, INITIAL_SUPPLY * (10 ** decimals()));
    }

    /**
     * @dev Creates `amount` tokens and assigns them to `account`, increasing
     * the total supply.
     * Emits a {Transfer} event with `from` set to the zero address.
     * Emits a {TokensMinted} event with details about the minting operation.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     * - The caller must be the contract owner (or have a MINTER_ROLE if implemented).
     * @param account The address that will receive the minted tokens.
     * @param amount The amount of tokens to mint.
     * @param kuId The identifier of the Knowledge Unit for which tokens are minted (optional, for tracking).
     * @param reason A description for why the tokens were minted (optional, for tracking).
     */
    function mint(address account, uint256 amount, string memory kuId, string memory reason)
        public
        onlyOwner // Or a more granular MINTER_ROLE
    {
        require(account != address(0), "ERC20: mint to the zero address");
        _mint(account, amount);
        emit TokensMinted(account, amount, kuId, reason);
    }

    /**
     * @dev Allows the contract owner to set a new owner (e.g., a DAO or multi-sig wallet).
     * This is inherited from Ownable.
     */
    // function transferOwnership(address newOwner) public virtual override onlyOwner {
    //     super.transferOwnership(newOwner);
    // }

    // ERC20Burnable provides `burn` and `burnFrom` functions.
    // `decimals` is 18 by default in OpenZeppelin's ERC20. It can be overridden if needed.
    // function decimals() public view virtual override returns (uint8) {
    //     return 18; // Or your desired number of decimals
    // }

    // Consider adding:
    // - Role-based access control (e.g., MINTER_ROLE) for more flexible minting permissions.
    // - Pausable functionality (ERC20Pausable) for emergency stops.
    // - Snapshot functionality (ERC20Snapshot) for governance or historical balance checks.
}
"""

# --- Option 2: Python data structures for ABI and Bytecode ---
SC_TOKEN_ABI_EXAMPLE = [
    {"inputs": [
        {"internalType": "address", "name": "initialOwner", "type": "address"},
        {"internalType": "string", "name": "name_", "type": "string"},
        {"internalType": "string", "name": "symbol_", "type": "string"}
    ], "stateMutability": "nonpayable", "type": "constructor"},
    # ... (standard ERC20 events and functions like Transfer, Approval, balanceOf, transfer, etc.)
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"},
            {"indexed": True, "internalType": "string", "name": "kuId", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "reason", "type": "string"}
        ],
        "name": "TokensMinted",
        "type": "event"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "string", "name": "kuId", "type": "string"},
            {"internalType": "string", "name": "reason", "type": "string"}
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable", "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view", "type": "function"
    },
    # ... (and so on for all relevant functions from ERC20, ERC20Burnable, Ownable)
]

SC_TOKEN_BYTECODE_EXAMPLE = "0x6080604052348015..." # Actual bytecode

# Notes:
# - Similar to ERC-721, this uses OpenZeppelin contracts.
# - The `blockchain_interaction.py` file would use these (ABI, bytecode) to deploy and interact.
# - The `mint` function includes `kuId` and `reason` parameters for better traceability of
#   token generation, linking it back to specific contributions if desired.

if __name__ == "__main__":
    print("--- SC Token Contract Solidity Template ---")
    print(SC_TOKEN_CONTRACT_TEMPLATE_SOLIDITY)
    print("\n--- SC Token ABI Example (Partial) ---")
    import json
    print(json.dumps(SC_TOKEN_ABI_EXAMPLE[:3], indent=2)) # Print first few ABI entries
    print(f"\n--- SC Token Bytecode Example (Placeholder) ---")
    print(SC_TOKEN_BYTECODE_EXAMPLE[:30] + "...")
