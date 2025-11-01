"""
AetherChain Main Implementation

Main class that integrates all AetherChain components into a cohesive decentralized operating system.
"""

import time
from typing import List, Dict, Any
from core.transaction import Transaction
from core.block import Block
from core.blockchain import Blockchain
from consensus.proof_of_compute import ProofOfCompute
from emulator.veil import EmulatorVeil
from network.p2p_network import P2PNetworkNode
from security.security_model import SecurityModel
from wallet.digital_wallet import DigitalWallet

class AetherChain:
    """
    AetherChain Main class
    
    Integrates all components of the decentralized operating system:
    - Transaction processing
    - Blockchain management
    - Proof-of-Compute consensus
    - Emulator Veil for privacy
    - P2P Network for communication
    - Security mechanisms
    - Digital wallet system
    """
    
    def __init__(self, node_id: str = "aetherchain_node"):
        """
        Initialize the AetherChain system
        
        Args:
            node_id: Unique identifier for this node
        """
        print("Initializing AetherChain: A Peer-to-Decentralized Operating System")
        
        # Initialize core components
        self.blockchain = Blockchain()
        self.proof_of_compute = ProofOfCompute()
        self.emulator_veil = EmulatorVeil()
        self.network = P2PNetworkNode(node_id)
        self.security = SecurityModel(self.blockchain)
        self.wallet = DigitalWallet(f"wallet_{node_id}")
        
        # Initialize emulator
        self.emulator_veil.initialize_emulator("main_emulator")
        
        # System state
        self.is_running = False
        self.node_id = node_id
        
        print("AetherChain initialization complete")
    
    def start(self):
        """
        Start the AetherChain system
        """
        if self.is_running:
            print("AetherChain is already running")
            return
            
        self.is_running = True
        self.network.start()
        
        print(f"AetherChain node {self.node_id} started")
        print(f"Wallet address: {self.wallet.get_address()}")
        print(f"Current blockchain height: {len(self.blockchain.chain)}")
    
    def stop(self):
        """
        Stop the AetherChain system
        """
        if not self.is_running:
            print("AetherChain is not running")
            return
            
        self.is_running = False
        self.network.stop()
        
        print(f"AetherChain node {self.node_id} stopped")
    
    def create_transaction(self, command: str, resources: Dict[str, Any]) -> Transaction:
        """
        Create a transaction from a user command
        
        According to the white paper:
        "In AetherChain, the OS interface captures user commands—e.g., "allocate 1GB memory
        for process P" or "exchange data shard D with node N"—as structured transactions"
        
        Args:
            command: User command (e.g., "allocate 1GB memory for process P")
            resources: Resource requirements for the command
            
        Returns:
            Transaction: Created transaction
        """
        # Parse command to determine inputs and outputs
        inputs = []
        outputs = []
        
        # Example command parsing (simplified)
        if "allocate" in command:
            # Memory allocation command
            amount = resources.get('memory', 0)
            inputs.append({
                'type': 'memory_request',
                'amount': amount,
                'command': command
            })
            outputs.append({
                'type': 'memory_allocation',
                'amount': amount,
                'status': 'pending'
            })
        elif "exchange" in command:
            # Data exchange command
            data_shard = resources.get('data_shard', '')
            node = resources.get('node', '')
            inputs.append({
                'type': 'data_request',
                'shard': data_shard,
                'target_node': node
            })
            outputs.append({
                'type': 'data_exchange',
                'shard': data_shard,
                'status': 'pending'
            })
        
        # Create transaction with public key for signing
        transaction = Transaction(inputs, outputs, self._get_public_key())
        
        # Sign transaction with wallet
        transaction.sign(self._get_private_key())
        
        print(f"Created transaction for command: {command}")
        return transaction
    
    def execute_command(self, command: str, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a user command through the AetherChain system
        
        Args:
            command: User command to execute
            resources: Resources required for execution
            
        Returns:
            dict: Execution result
        """
        if not self.is_running:
            raise RuntimeError("AetherChain is not running")
        
        print(f"Executing command: {command}")
        
        # Step 1: Create transaction from command
        transaction = self.create_transaction(command, resources)
        
        # Step 2: Apply security checks
        if not self.security.prevent_double_execution(transaction):
            return {
                'status': 'failed',
                'error': 'Double-execution prevented',
                'transaction_id': transaction.hash()
            }
        
        # Step 3: Create commitment for privacy (Emulator Veil)
        commitment = self.emulator_veil.create_commitment(transaction)
        print(f"Created privacy commitment: {commitment}")
        
        # Step 4: Execute in Emulator Veil
        try:
            execution_result = self.emulator_veil.execute_in_veil("main_emulator", transaction)
            print(f"Execution result: {execution_result['status']}")
        except Exception as e:
            return {
                'status': 'failed',
                'error': f'Execution failed: {str(e)}',
                'transaction_id': transaction.hash()
            }
        
        # Step 5: Add to mempool and broadcast
        self.network.handle_incoming_transaction(transaction)
        self.network.broadcast_transaction(transaction)
        
        # Step 6: Return result
        return {
            'status': 'success',
            'transaction_id': transaction.hash(),
            'commitment': commitment,
            'execution_result': execution_result
        }
    
    def mine_block(self) -> Block:
        """
        Mine a new block with pending transactions
        
        Returns:
            Block: Mined block
        """
        if not self.is_running:
            raise RuntimeError("AetherChain is not running")
        
        print("Mining new block...")
        
        # Mine pending transactions
        new_block = self.blockchain.mine_pending_transactions(
            reward_address=self.wallet.get_address()
        )
        
        if new_block:
            # Apply Proof-of-Compute
            print("Applying Proof-of-Compute...")
            
            # Generate computational proof
            proof = self.proof_of_compute.generate_computational_proof(new_block.transactions)
            new_block.proof_of_compute = {
                'nonce': new_block.nonce,
                'proof': proof,
                'energy_sample': self.proof_of_compute.sample_thermodynamic_entropy()
            }
            
            # Broadcast block to network
            self.network.broadcast_block(new_block)
            
            print(f"Mined block {new_block.hash()}")
            return new_block
        else:
            print("No transactions to mine")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current system status
        
        Returns:
            dict: System status information
        """
        return {
            'node_id': self.node_id,
            'is_running': self.is_running,
            'blockchain_height': len(self.blockchain.chain),
            'pending_transactions': len(self.blockchain.pending_transactions),
            'wallet_balances': self.wallet.get_balances(),
            'network_peers': len(self.network.peers),
            'emulator_status': 'active' if self.emulator_veil.active_emulators else 'inactive',
            'security_model': 'active',
            'timestamp': time.time()
        }
    
    def facilitate_resource_payment(self, resource_type: str, amount: float, 
                                  provider_address: str) -> Transaction:
        """
        Facilitate payment for computational resources
        
        Args:
            resource_type: Type of resource (compute, storage, data)
            amount: Amount of resources
            provider_address: Address of resource provider
            
        Returns:
            Transaction: Payment transaction
        """
        if resource_type == 'compute':
            return self.wallet.facilitate_payment_for_compute(provider_address, amount)
        elif resource_type == 'storage':
            return self.wallet.facilitate_payment_for_storage(provider_address, amount)
        elif resource_type == 'data':
            return self.wallet.monetize_data_flow(amount, provider_address)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def _get_public_key(self) -> bytes:
        """
        Get the node's public key
        
        Returns:
            bytes: Public key
        """
        return self.wallet._get_public_key_bytes()
    
    def _get_private_key(self) -> bytes:
        """
        Get the node's private key
        
        Returns:
            bytes: Private key
        """
        return self.wallet._get_private_key_bytes()

# Example usage and demonstration
if __name__ == "__main__":
    # Create AetherChain instance
    aetherchain = AetherChain("demo_node")
    
    # Start the system
    aetherchain.start()
    
    # Check system status
    status = aetherchain.get_system_status()
    print(f"System status: {status}")
    
    # Execute sample commands
    print("\n--- Executing Sample Commands ---")
    
    # Memory allocation command
    result1 = aetherchain.execute_command(
        "allocate 1GB memory for process P",
        {'memory': 1024}  # 1GB in MB
    )
    print(f"Memory allocation result: {result1['status']}")
    
    # Data exchange command
    result2 = aetherchain.execute_command(
        "exchange data shard D with node N",
        {'data_shard': 'shard_D', 'node': 'node_N'}
    )
    print(f"Data exchange result: {result2['status']}")
    
    # Check system status after commands
    status = aetherchain.get_system_status()
    print(f"System status after commands: {status}")
    
    # Mine a block with the pending transactions
    print("\n--- Mining Block ---")
    block = aetherchain.mine_block()
    
    if block:
        print(f"Mined block with {len(block.transactions)} transactions")
        
        # Check wallet balance after mining reward
        print(f"Wallet balance after mining: {aetherchain.wallet.get_balance('AETH')} AETH")
    
    # Demonstrate resource payment
    print("\n--- Facilitating Resource Payments ---")
    
    # Create another wallet for the provider
    provider_wallet = DigitalWallet("provider_wallet")
    provider_wallet.deposit(50.0, 'AETH')
    
    # Facilitate compute payment
    compute_payment = aetherchain.facilitate_resource_payment(
        'compute', 100, provider_wallet.get_address()
    )
    print(f"Compute payment transaction: {compute_payment.hash()}")
    
    # Facilitate storage payment
    storage_payment = aetherchain.facilitate_resource_payment(
        'storage', 50, provider_wallet.get_address()
    )
    print(f"Storage payment transaction: {storage_payment.hash()}")
    
    # Facilitate data monetization
    data_payment = aetherchain.facilitate_resource_payment(
        'data', 10.0, provider_wallet.get_address()
    )
    print(f"Data monetization transaction: {data_payment.hash()}")
    
    # Final system status
    print("\n--- Final System Status ---")
    final_status = aetherchain.get_system_status()
    print(f"Final system status: {final_status}")
    
    # Stop the system
    aetherchain.stop()