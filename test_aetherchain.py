"""
AetherChain Test Suite

Comprehensive tests for all AetherChain components.
"""

import unittest

# Use absolute imports
from aetherchain.core.transaction import Transaction
from aetherchain.core.block import Block
from aetherchain.core.blockchain import Blockchain
from aetherchain.consensus.proof_of_compute import ProofOfCompute
from aetherchain.emulator.veil import EmulatorVeil
from aetherchain.network.p2p_network import P2PNetworkNode
from aetherchain.security.security_model import SecurityModel
from aetherchain.wallet.digital_wallet import DigitalWallet
from aetherchain.main import AetherChain

class TestTransaction(unittest.TestCase):
    """Test cases for Transaction class"""
    
    def setUp(self):
        self.inputs = [{"tx_id": "input1", "output_index": 0, "amount": 100}]
        self.outputs = [{"address": "addr1", "amount": 100}]
        self.transaction = Transaction(self.inputs, self.outputs)
    
    def test_transaction_creation(self):
        """Test transaction creation"""
        self.assertIsNotNone(self.transaction)
        self.assertEqual(self.transaction.inputs, self.inputs)
        self.assertEqual(self.transaction.outputs, self.outputs)
        self.assertIsNotNone(self.transaction.timestamp)
        self.assertIsNotNone(self.transaction.nonce)
    
    def test_transaction_hash(self):
        """Test transaction hashing"""
        hash1 = self.transaction.hash()
        hash2 = self.transaction.hash()
        self.assertEqual(hash1, hash2)  # Hash should be consistent
    
    def test_transaction_serialization(self):
        """Test transaction serialization"""
        serialized = self.transaction.serialize()
        self.assertIsInstance(serialized, str)
        self.assertIn('"inputs"', serialized)
        self.assertIn('"outputs"', serialized)

class TestBlock(unittest.TestCase):
    """Test cases for Block class"""
    
    def setUp(self):
        self.transactions = [
            Transaction(
                [{"tx_id": "input1", "output_index": 0, "amount": 100}],
                [{"address": "addr1", "amount": 100}]
            )
        ]
        self.block = Block(1, self.transactions, "0" * 64)
    
    def test_block_creation(self):
        """Test block creation"""
        self.assertEqual(self.block.index, 1)
        self.assertEqual(self.block.transactions, self.transactions)
        self.assertEqual(self.block.previous_hash, "0" * 64)
    
    def test_merkle_root_calculation(self):
        """Test Merkle root calculation"""
        merkle_root = self.block.merkle_root
        self.assertIsNotNone(merkle_root)
        self.assertIsInstance(merkle_root, str)
    
    def test_block_hash(self):
        """Test block hashing"""
        block_hash = self.block.hash()
        self.assertIsNotNone(block_hash)
        self.assertIsInstance(block_hash, str)
        self.assertEqual(len(block_hash), 64)  # SHA-256 hash length

class TestBlockchain(unittest.TestCase):
    """Test cases for Blockchain class"""
    
    def setUp(self):
        self.blockchain = Blockchain(difficulty=1)  # Low difficulty for testing
    
    def test_genesis_block(self):
        """Test genesis block creation"""
        self.assertEqual(len(self.blockchain.chain), 1)
        self.assertEqual(self.blockchain.chain[0].index, 0)
        self.assertEqual(self.blockchain.chain[0].previous_hash, "0" * 64)
    
    def test_transaction_addition(self):
        """Test adding transactions to mempool"""
        tx = Transaction(
            [{"tx_id": "input1", "output_index": 0, "amount": 100}],
            [{"address": "addr1", "amount": 100}]
        )
        
        result = self.blockchain.add_transaction(tx)
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)
    
    def test_block_mining(self):
        """Test block mining"""
        # Add a transaction
        tx = Transaction(
            [{"tx_id": "input1", "output_index": 0, "amount": 100}],
            [{"address": "addr1", "amount": 100}]
        )
        self.blockchain.add_transaction(tx)
        
        # Mine a block
        block = self.blockchain.mine_pending_transactions("miner_addr")
        self.assertIsNotNone(block)
        self.assertEqual(len(self.blockchain.chain), 2)  # Genesis + new block
        self.assertEqual(len(self.blockchain.pending_transactions), 0)

class TestProofOfCompute(unittest.TestCase):
    """Test cases for ProofOfCompute class"""
    
    def setUp(self):
        self.poc = ProofOfCompute(initial_difficulty=1)
    
    def test_target_calculation(self):
        """Test target calculation"""
        target = self.poc.calculate_target()
        self.assertEqual(target, "0" * self.poc.difficulty)
    
    def test_puzzle_solving(self):
        """Test puzzle solving"""
        block_header = "test_header"
        nonce, hash_result = self.poc.solve_puzzle(block_header)
        self.assertIsInstance(nonce, int)
        self.assertIsInstance(hash_result, str)
        
        # Verify the hash meets the target
        target = self.poc.calculate_target()
        self.assertLessEqual(hash_result[:len(target)], target)
    
    def test_difficulty_adjustment(self):
        """Test difficulty adjustment"""
        initial_difficulty = self.poc.difficulty
        
        # Simulate block times (1 block per 30 seconds, faster than target of 60)
        block_times = [i * 30 for i in range(10)]
        new_difficulty = self.poc.adjust_difficulty(block_times)
        
        # Difficulty should increase since blocks are coming too fast
        self.assertGreaterEqual(new_difficulty, initial_difficulty)

class TestEmulatorVeil(unittest.TestCase):
    """Test cases for EmulatorVeil class"""
    
    def setUp(self):
        self.veil = EmulatorVeil()
    
    def test_emulator_initialization(self):
        """Test emulator initialization"""
        emulator = self.veil.initialize_emulator("test_emulator")
        self.assertEqual(emulator['id'], "test_emulator")
        self.assertEqual(emulator['type'], "wasm-sandbox")
        self.assertEqual(emulator['status'], "initialized")
    
    def test_commitment_creation(self):
        """Test commitment creation"""
        tx = Transaction(
            [{"tx_id": "input1", "output_index": 0, "amount": 100}],
            [{"address": "addr1", "amount": 100}]
        )
        
        commitment = self.veil.create_commitment(tx)
        self.assertIsNotNone(commitment)
        self.assertIsInstance(commitment, str)
        self.assertEqual(len(commitment), 64)  # SHA-256 hash length
    
    def test_commitment_verification(self):
        """Test commitment verification"""
        tx = Transaction(
            [{"tx_id": "input1", "output_index": 0, "amount": 100}],
            [{"address": "addr1", "amount": 100}]
        )
        
        commitment = self.veil.create_commitment(tx)
        is_valid = self.veil.verify_commitment(commitment, tx)
        self.assertTrue(is_valid)

class TestP2PNetwork(unittest.TestCase):
    """Test cases for P2PNetworkNode class"""
    
    def setUp(self):
        self.node = P2PNetworkNode("test_node")
    
    def test_node_creation(self):
        """Test node creation"""
        self.assertEqual(self.node.node_id, "test_node")
        self.assertEqual(self.node.host, "127.0.0.1")
        self.assertEqual(self.node.port, 8000)
    
    def test_peer_management(self):
        """Test peer management"""
        # Add a peer
        self.node.add_peer("peer1", "127.0.0.1", 8001)
        self.assertIn("peer1", self.node.peers)
        
        # Remove a peer
        self.node.remove_peer("peer1")
        self.assertNotIn("peer1", self.node.peers)
    
    def test_network_status(self):
        """Test network status"""
        status = self.node.get_network_status()
        self.assertIsInstance(status, dict)
        self.assertEqual(status['node_id'], "test_node")
        self.assertEqual(status['is_running'], False)

class TestSecurityModel(unittest.TestCase):
    """Test cases for SecurityModel class"""
    
    def setUp(self):
        self.blockchain = Blockchain()
        self.security = SecurityModel(self.blockchain)
    
    def test_double_execution_prevention(self):
        """Test double-execution prevention"""
        tx = Transaction(
            [{"tx_id": "input1", "output_index": 0, "amount": 100}],
            [{"address": "addr1", "amount": 100}]
        )
        
        # First execution should be allowed
        result1 = self.security.prevent_double_execution(tx)
        self.assertTrue(result1)
        
        # Second execution should be blocked
        result2 = self.security.prevent_double_execution(tx)
        self.assertFalse(result2)
    
    def test_attack_probability_calculation(self):
        """Test attack probability calculation"""
        # Test with 45% attacker hash power and 6 confirmations
        prob = self.security.calculate_attack_probability(0.45, 6)
        self.assertIsInstance(prob, float)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
    
    def test_fork_safety(self):
        """Test fork safety"""
        is_safe = self.security.is_fork_safe(10, 0.45)
        self.assertIsInstance(is_safe, bool)

class TestDigitalWallet(unittest.TestCase):
    """Test cases for DigitalWallet class"""
    
    def setUp(self):
        self.wallet = DigitalWallet("test_wallet")
    
    def test_wallet_creation(self):
        """Test wallet creation"""
        self.assertEqual(self.wallet.wallet_id, "test_wallet")
        self.assertIsNotNone(self.wallet.address)
        self.assertIsNotNone(self.wallet.private_key)
        self.assertIsNotNone(self.wallet.public_key)
    
    def test_balance_operations(self):
        """Test balance operations"""
        # Initial balance should be 0
        self.assertEqual(self.wallet.get_balance('AETH'), 0.0)
        
        # Deposit funds
        self.wallet.deposit(100.0, 'AETH')
        self.assertEqual(self.wallet.get_balance('AETH'), 100.0)
        
        # Withdraw funds
        result = self.wallet.withdraw(50.0, 'AETH')
        self.assertTrue(result)
        self.assertEqual(self.wallet.get_balance('AETH'), 50.0)
        
        # Attempt to withdraw more than balance
        result = self.wallet.withdraw(100.0, 'AETH')
        self.assertFalse(result)  # Should fail
        self.assertEqual(self.wallet.get_balance('AETH'), 50.0)  # Balance unchanged
    
    def test_transaction_creation(self):
        """Test transaction creation"""
        # Deposit some funds first
        self.wallet.deposit(100.0, 'AETH')
        
        # Create a transaction
        recipient_address = "recipient_addr"
        transaction = self.wallet.create_transaction(recipient_address, 25.0, 'AETH')
        
        self.assertIsNotNone(transaction)
        self.assertEqual(len(transaction.inputs), 1)
        self.assertEqual(len(transaction.outputs), 2)  # Recipient + fee

class TestAetherChain(unittest.TestCase):
    """Test cases for AetherChain main class"""
    
    def setUp(self):
        self.aetherchain = AetherChain("test_node")
    
    def test_aetherchain_creation(self):
        """Test AetherChain creation"""
        self.assertEqual(self.aetherchain.node_id, "test_node")
        self.assertFalse(self.aetherchain.is_running)
        
        # Check that all components are initialized
        self.assertIsNotNone(self.aetherchain.blockchain)
        self.assertIsNotNone(self.aetherchain.proof_of_compute)
        self.assertIsNotNone(self.aetherchain.emulator_veil)
        self.assertIsNotNone(self.aetherchain.network)
        self.assertIsNotNone(self.aetherchain.security)
        self.assertIsNotNone(self.aetherchain.wallet)
    
    def test_system_lifecycle(self):
        """Test system start/stop lifecycle"""
        # Start the system
        self.aetherchain.start()
        self.assertTrue(self.aetherchain.is_running)
        
        # Get system status
        status = self.aetherchain.get_system_status()
        self.assertIsInstance(status, dict)
        self.assertTrue(status['is_running'])
        
        # Stop the system
        self.aetherchain.stop()
        self.assertFalse(self.aetherchain.is_running)
    
    def test_command_execution(self):
        """Test command execution"""
        # Start the system first
        self.aetherchain.start()
        
        # Execute a command
        result = self.aetherchain.execute_command(
            "allocate 1GB memory for process P",
            {'memory': 1024}
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'success')
        self.assertIn('transaction_id', result)
        self.assertIn('commitment', result)
        
        # Stop the system
        self.aetherchain.stop()

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTransaction))
    suite.addTests(loader.loadTestsFromTestCase(TestBlock))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockchain))
    suite.addTests(loader.loadTestsFromTestCase(TestProofOfCompute))
    suite.addTests(loader.loadTestsFromTestCase(TestEmulatorVeil))
    suite.addTests(loader.loadTestsFromTestCase(TestP2PNetwork))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityModel))
    suite.addTests(loader.loadTestsFromTestCase(TestDigitalWallet))
    suite.addTests(loader.loadTestsFromTestCase(TestAetherChain))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running AetherChain Test Suite...")
    success = run_tests()
    
    if success:
        print("\nAll tests passed! AetherChain implementation is working correctly.")
    else:
        print("\nSome tests failed. Please check the implementation.")
    
    sys.exit(0 if success else 1)