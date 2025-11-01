"""
AetherChain Demo Script

This script demonstrates the basic functionality of the AetherChain implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from main import AetherChain
from wallet.digital_wallet import DigitalWallet

def main():
    print("=== AetherChain Demo ===")
    
    # Create and start AetherChain node
    print("\n1. Initializing AetherChain node...")
    aetherchain = AetherChain("demo_node")
    aetherchain.start()
    
    # Check initial status
    print("\n2. Initial system status:")
    status = aetherchain.get_system_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Create a transaction
    print("\n3. Creating a sample transaction...")
    result = aetherchain.execute_command(
        "allocate 1GB memory for process P",
        {'memory': 1024}  # 1GB in MB
    )
    print(f"   Transaction status: {result['status']}")
    print(f"   Transaction ID: {result['transaction_id']}")
    
    # Mine a block
    print("\n4. Mining a block with pending transactions...")
    block = aetherchain.mine_block()
    if block:
        print(f"   Mined block: {block.hash()}")
        print(f"   Transactions in block: {len(block.transactions)}")
    else:
        print("   No transactions to mine")
    
    # Wallet operations
    print("\n5. Demonstrating wallet operations...")
    wallet = aetherchain.wallet
    print(f"   Wallet address: {wallet.get_address()}")
    print(f"   Initial balance: {wallet.get_balance('AETH')} AETH")
    
    # Deposit funds
    wallet.deposit(100.0, 'AETH')
    print(f"   Balance after deposit: {wallet.get_balance('AETH')} AETH")
    
    # Create another wallet for transfer
    recipient_wallet = DigitalWallet("recipient_wallet")
    recipient_wallet.deposit(50.0, 'AETH')
    
    # Transfer funds
    try:
        transaction = wallet.create_transaction(
            recipient_address=recipient_wallet.get_address(),
            amount=25.0,
            currency='AETH'
        )
        recipient_wallet.receive_transaction(transaction)
        print(f"   Transfer successful!")
        print(f"   Sender balance: {wallet.get_balance('AETH')} AETH")
        print(f"   Recipient balance: {recipient_wallet.get_balance('AETH')} AETH")
    except Exception as e:
        print(f"   Transfer failed: {e}")
    
    # Final status
    print("\n6. Final system status:")
    status = aetherchain.get_system_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Stop the node
    print("\n7. Stopping AetherChain node...")
    aetherchain.stop()
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()