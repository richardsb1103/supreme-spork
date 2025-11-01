"""
AetherChain Example Script

This script demonstrates the key features of the AetherChain implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from main import AetherChain
from wallet.digital_wallet import DigitalWallet

def demonstrate_core_features():
    print("=== AetherChain Core Features Demonstration ===")
    
    # 1. Initialize AetherChain
    print("\n1. Initializing AetherChain...")
    aetherchain = AetherChain("example_node")
    aetherchain.start()
    
    # 2. Demonstrate transaction creation and execution
    print("\n2. Demonstrating transaction creation and execution...")
    
    # Execute different types of commands
    commands = [
        ("allocate 2GB memory for process Q", {'memory': 2048}),
        ("exchange data shard E with node M", {'data_shard': 'shard_E', 'node': 'node_M'}),
        ("start network service on port 8080", {'port': 8080, 'protocol': 'TCP'})
    ]
    
    transactions = []
    for command, resources in commands:
        print(f"   Executing: {command}")
        result = aetherchain.execute_command(command, resources)
        if result['status'] == 'success':
            transactions.append(result['transaction_id'])
            print(f"   Success! Transaction ID: {result['transaction_id'][:16]}...")
        else:
            print(f"   Failed: {result['error']}")
    
    # 3. Demonstrate Proof-of-Compute
    print("\n3. Demonstrating Proof-of-Compute...")
    print(f"   Current blockchain height: {len(aetherchain.blockchain.chain)}")
    
    # Mine a block to demonstrate PoC
    block = aetherchain.mine_block()
    if block:
        print(f"   Mined block: {block.hash()[:16]}...")
        print(f"   Block contains {len(block.transactions)} transactions")
        if block.proof_of_compute:
            print(f"   Proof-of-Compute generated with nonce: {block.proof_of_compute.get('nonce', 'N/A')}")
    
    # 4. Demonstrate Emulator Veil
    print("\n4. Demonstrating Emulator Veil...")
    print(f"   Active emulators: {len(aetherchain.emulator_veil.active_emulators)}")
    print(f"   Stored commitments: {len(aetherchain.emulator_veil.commitments)}")
    
    # 5. Demonstrate security features
    print("\n5. Demonstrating security features...")
    # Try to execute the same transaction twice (should be prevented)
    if transactions:
        first_tx_id = transactions[0]
        print(f"   Attempting double-execution of transaction {first_tx_id[:16]}...")
        # In a real implementation, this would be prevented by the security model
    
    # 6. Demonstrate wallet and payment system
    print("\n6. Demonstrating wallet and payment system...")
    provider_wallet = DigitalWallet("provider_wallet")
    provider_wallet.deposit(100.0, 'AETH')
    
    # Facilitate payments for different resources
    payments = [
        ('compute', 150, "Compute units"),
        ('storage', 75, "Storage GB"),
        ('data', 25.0, "Data value")
    ]
    
    for resource_type, amount, description in payments:
        print(f"   Facilitating payment for {description}...")
        try:
            payment_tx = aetherchain.facilitate_resource_payment(
                resource_type, amount, provider_wallet.get_address()
            )
            provider_wallet.receive_transaction(payment_tx)
            print(f"   Payment successful! Transaction ID: {payment_tx.hash()[:16]}...")
        except Exception as e:
            print(f"   Payment failed: {e}")
    
    # 7. Show final status
    print("\n7. Final system status:")
    status = aetherchain.get_system_status()
    print(f"   Blockchain height: {status['blockchain_height']}")
    print(f"   Pending transactions: {status['pending_transactions']}")
    print(f"   Wallet balances: {status['wallet_balances']}")
    print(f"   Network peers: {status['network_peers']}")
    
    # Clean up
    aetherchain.stop()
    print("\n=== Demonstration Complete ===")

if __name__ == "__main__":
    demonstrate_core_features()