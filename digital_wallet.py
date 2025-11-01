"""
AetherChain Digital Wallet Implementation

Based on the AetherChain white paper, the wallet system:
- Facilitates payments for contributing compute and storage
- Supports external cryptocurrencies
- Enables monetization of sacred human data
- Integrates with the blockchain for seamless transactions
"""

import hashlib
import json
from typing import List, Dict, Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.transaction import Transaction

class DigitalWallet:
    """
    AetherChain Digital Wallet class
    
    Implements the wallet system with:
    - Multi-currency support
    - Secure key management
    - Transaction creation and signing
    - Balance tracking
    - Payment facilitation for compute/storage
    """
    
    def __init__(self, wallet_id: str):
        """
        Initialize a digital wallet
        
        Args:
            wallet_id: Unique identifier for the wallet
        """
        self.wallet_id = wallet_id
        self.balances: Dict[str, float] = {}  # currency -> amount
        self.supported_currencies = ['AETH', 'BTC', 'ETH', 'USDC']  # AETH = AetherChain native
        self.private_key = None
        self.public_key = None
        self.address = None
        self.transaction_history: List[Dict[str, Any]] = []
        
        # Generate key pair
        self._generate_keypair()
    
    def _generate_keypair(self):
        """
        Generate a key pair for the wallet
        """
        # Generate private key using secp256k1 curve (as in Bitcoin)
        self.private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self.private_key.public_key()
        
        # Generate wallet address from public key
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.address = hashlib.sha256(public_key_bytes).hexdigest()[:40]
        
        # Initialize balances
        for currency in self.supported_currencies:
            self.balances[currency] = 0.0
    
    def get_address(self) -> str:
        """
        Get the wallet address
        
        Returns:
            str: Wallet address
        """
        return self.address
    
    def get_balance(self, currency: str = 'AETH') -> float:
        """
        Get the balance for a specific currency
        
        Args:
            currency: Currency to check balance for
            
        Returns:
            float: Balance amount
        """
        return self.balances.get(currency, 0.0)
    
    def get_balances(self) -> Dict[str, float]:
        """
        Get all balances
        
        Returns:
            dict: All currency balances
        """
        return self.balances.copy()
    
    def deposit(self, amount: float, currency: str = 'AETH'):
        """
        Deposit funds into the wallet
        
        Args:
            amount: Amount to deposit
            currency: Currency to deposit
        """
        if currency not in self.supported_currencies:
            raise ValueError(f"Unsupported currency: {currency}")
            
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balances[currency] += amount
        
        # Record transaction
        transaction_record = {
            'type': 'deposit',
            'amount': amount,
            'currency': currency,
            'timestamp': self._get_current_time(),
            'balance_after': self.balances[currency]
        }
        self.transaction_history.append(transaction_record)
        
        print(f"Deposited {amount} {currency} to wallet {self.wallet_id}")
    
    def withdraw(self, amount: float, currency: str = 'AETH') -> bool:
        """
        Withdraw funds from the wallet
        
        Args:
            amount: Amount to withdraw
            currency: Currency to withdraw
            
        Returns:
            bool: True if withdrawal successful, False otherwise
        """
        if currency not in self.supported_currencies:
            raise ValueError(f"Unsupported currency: {currency}")
            
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        if self.balances.get(currency, 0.0) < amount:
            print(f"Insufficient balance for withdrawal: {self.balances.get(currency, 0.0)} < {amount}")
            return False
            
        self.balances[currency] -= amount
        
        # Record transaction
        transaction_record = {
            'type': 'withdrawal',
            'amount': amount,
            'currency': currency,
            'timestamp': self._get_current_time(),
            'balance_after': self.balances[currency]
        }
        self.transaction_history.append(transaction_record)
        
        print(f"Withdrew {amount} {currency} from wallet {self.wallet_id}")
        return True
    
    def create_transaction(self, recipient_address: str, amount: float, 
                          currency: str = 'AETH', fee: float = 0.0001) -> Transaction:
        """
        Create a transaction for sending funds
        
        According to the white paper:
        "Incentives: Block proposers facilitate transaction fees (0.01% of data value) 
        via built-in digital currency wallets, promoting participation through external 
        cryptocurrency payments"
        
        Args:
            recipient_address: Recipient's wallet address
            amount: Amount to send
            currency: Currency to send
            fee: Transaction fee (0.01% of data value as mentioned in white paper)
            
        Returns:
            Transaction: Created transaction object
        """
        if currency not in self.supported_currencies:
            raise ValueError(f"Unsupported currency: {currency}")
            
        total_amount = amount + fee
        
        if self.balances.get(currency, 0.0) < total_amount:
            raise ValueError(f"Insufficient balance: {self.balances.get(currency, 0.0)} < {total_amount}")
            
        # Create transaction inputs and outputs
        inputs = [{
            'address': self.address,
            'amount': total_amount,
            'currency': currency
        }]
        
        outputs = [
            {
                'address': recipient_address,
                'amount': amount,
                'currency': currency
            },
            {
                'address': 'network_fee',  # Network fee collector
                'amount': fee,
                'currency': currency
            }
        ]
        
        # Create transaction
        transaction = Transaction(inputs, outputs, self._get_public_key_bytes())
        
        # Sign transaction
        transaction.sign(self._get_private_key_bytes())
        
        # Deduct from balance
        self.balances[currency] -= total_amount
        
        # Record transaction
        transaction_record = {
            'type': 'transfer',
            'amount': amount,
            'currency': currency,
            'fee': fee,
            'recipient': recipient_address,
            'transaction_id': transaction.hash(),
            'timestamp': self._get_current_time(),
            'balance_after': self.balances[currency]
        }
        self.transaction_history.append(transaction_record)
        
        print(f"Created transaction of {amount} {currency} to {recipient_address}")
        print(f"Transaction fee: {fee} {currency}")
        
        return transaction
    
    def receive_transaction(self, transaction: Transaction) -> bool:
        """
        Receive funds from a transaction
        
        Args:
            transaction: Transaction to receive funds from
            
        Returns:
            bool: True if funds received successfully, False otherwise
        """
        # Verify transaction signature
        if not transaction.verify_signature():
            print("Invalid transaction signature")
            return False
            
        # Check if this wallet is a recipient
        amount_received = 0.0
        currency_received = None
        
        for output in transaction.outputs:
            if output.get('address') == self.address:
                amount_received = output.get('amount', 0.0)
                currency_received = output.get('currency', 'AETH')
                break
                
        if amount_received <= 0:
            print("No funds for this wallet in transaction")
            return False
            
        # Add to balance
        self.balances[currency_received] += amount_received
        
        # Record transaction
        transaction_record = {
            'type': 'receive',
            'amount': amount_received,
            'currency': currency_received,
            'sender': transaction.public_key,  # Simplified
            'transaction_id': transaction.hash(),
            'timestamp': self._get_current_time(),
            'balance_after': self.balances[currency_received]
        }
        self.transaction_history.append(transaction_record)
        
        print(f"Received {amount_received} {currency_received} in wallet {self.wallet_id}")
        return True
    
    def facilitate_payment_for_compute(self, node_address: str, compute_units: int, 
                                     unit_price: float = 0.001) -> Transaction:
        """
        Facilitate payment for contributing compute resources
        
        According to the white paper:
        "Nodes host emulators and facilitate payments for successful relays using 
        supported cryptocurrencies"
        
        Args:
            node_address: Address of node providing compute
            compute_units: Number of compute units provided
            unit_price: Price per compute unit
            
        Returns:
            Transaction: Payment transaction
        """
        total_amount = compute_units * unit_price
        fee = total_amount * 0.0001  # 0.01% fee as mentioned in white paper
        
        print(f"Facilitating payment for {compute_units} compute units at {unit_price} AETH/unit")
        print(f"Total amount: {total_amount} AETH, Fee: {fee} AETH")
        
        return self.create_transaction(node_address, total_amount, 'AETH', fee)
    
    def facilitate_payment_for_storage(self, node_address: str, storage_gb: float, 
                                      price_per_gb: float = 0.01) -> Transaction:
        """
        Facilitate payment for contributing storage resources
        
        Args:
            node_address: Address of node providing storage
            storage_gb: Amount of storage provided in GB
            price_per_gb: Price per GB of storage
            
        Returns:
            Transaction: Payment transaction
        """
        total_amount = storage_gb * price_per_gb
        fee = total_amount * 0.0001  # 0.01% fee
        
        print(f"Facilitating payment for {storage_gb} GB storage at {price_per_gb} AETH/GB")
        print(f"Total amount: {total_amount} AETH, Fee: {fee} AETH")
        
        return self.create_transaction(node_address, total_amount, 'AETH', fee)
    
    def monetize_data_flow(self, data_value: float, recipient_address: str) -> Transaction:
        """
        Monetize sacred human data flows
        
        According to the white paper:
        "AetherChain treats data as sacred: Every transaction enables monetization of essence
        from user flows"
        
        Args:
            data_value: Value of the data being shared
            recipient_address: Address of data recipient
            
        Returns:
            Transaction: Data monetization transaction
        """
        fee = data_value * 0.0001  # 0.01% fee
        
        # According to the white paper:
        # "Relay Fees: 70% to originators, paid via integrated wallets"
        originator_share = data_value * 0.7
        network_share = data_value * 0.3
        
        print(f"Monetizing data flow valued at {data_value} AETH")
        print(f"Originator share: {originator_share} AETH")
        print(f"Network share: {network_share} AETH")
        print(f"Fee: {fee} AETH")
        
        # For this implementation, we'll send the originator share to the recipient
        # and the network share to a network address
        return self.create_transaction(recipient_address, originator_share, 'AETH', fee)
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """
        Get transaction history
        
        Returns:
            list: List of transaction records
        """
        return self.transaction_history.copy()
    
    def _get_private_key_bytes(self) -> bytes:
        """
        Get private key bytes
        
        Returns:
            bytes: Private key in DER format
        """
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    def _get_public_key_bytes(self) -> bytes:
        """
        Get public key bytes
        
        Returns:
            bytes: Public key in DER format
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def _get_current_time(self) -> float:
        """
        Get current timestamp
        
        Returns:
            float: Current time in seconds since epoch
        """
        import time
        return time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert wallet to dictionary representation
        
        Returns:
            dict: Wallet data
        """
        return {
            'wallet_id': self.wallet_id,
            'address': self.address,
            'balances': self.balances.copy(),
            'supported_currencies': self.supported_currencies.copy(),
            'transaction_count': len(self.transaction_history)
        }

# Example usage
if __name__ == "__main__":
    # Create wallets
    wallet1 = DigitalWallet("wallet_001")
    wallet2 = DigitalWallet("wallet_002")
    
    print(f"Wallet 1 address: {wallet1.get_address()}")
    print(f"Wallet 2 address: {wallet2.get_address()}")
    
    # Deposit funds
    wallet1.deposit(100.0, 'AETH')
    wallet1.deposit(0.5, 'BTC')
    
    wallet2.deposit(50.0, 'AETH')
    
    # Check balances
    print(f"Wallet 1 AETH balance: {wallet1.get_balance('AETH')}")
    print(f"Wallet 1 BTC balance: {wallet1.get_balance('BTC')}")
    print(f"Wallet 2 AETH balance: {wallet2.get_balance('AETH')}")
    
    # Create a transaction
    print("\nCreating transaction from wallet 1 to wallet 2:")
    transaction = wallet1.create_transaction(
        recipient_address=wallet2.get_address(),
        amount=25.0,
        currency='AETH',
        fee=0.025  # 0.01% of 25.0 = 0.00025, but we'll use a simplified fee
    )
    
    # Receive transaction in wallet 2
    print("\nReceiving transaction in wallet 2:")
    wallet2.receive_transaction(transaction)
    
    # Check updated balances
    print(f"Wallet 1 AETH balance: {wallet1.get_balance('AETH')}")
    print(f"Wallet 2 AETH balance: {wallet2.get_balance('AETH')}")
    
    # Facilitate payment for compute
    print("\nFacilitating payment for compute:")
    compute_payment = wallet1.facilitate_payment_for_compute(
        node_address=wallet2.get_address(),
        compute_units=100,
        unit_price=0.001
    )
    wallet2.receive_transaction(compute_payment)
    
    # Facilitate payment for storage
    print("\nFacilitating payment for storage:")
    storage_payment = wallet1.facilitate_payment_for_storage(
        node_address=wallet2.get_address(),
        storage_gb=50,
        price_per_gb=0.01
    )
    wallet2.receive_transaction(storage_payment)
    
    # Monetize data flow
    print("\nMonetizing data flow:")
    data_payment = wallet1.monetize_data_flow(
        data_value=10.0,
        recipient_address=wallet2.get_address()
    )
    wallet2.receive_transaction(data_payment)
    
    # Final balances
    print("\nFinal balances:")
    print(f"Wallet 1: {wallet1.get_balances()}")
    print(f"Wallet 2: {wallet2.get_balances()}")
    
    # Transaction history
    print(f"\nWallet 1 transaction history: {len(wallet1.get_transaction_history())} transactions")
    print(f"Wallet 2 transaction history: {len(wallet2.get_transaction_history())} transactions")