import os
import random
import time
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from mnemonic import Mnemonic
from database import DatabaseManager
from utils import validate_ethereum_address, wei_to_eth, eth_to_wei
import json
from typing import Dict, List, Optional, Tuple

class WalletService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.mnemo = Mnemonic("english")
        # Enable HD wallet features (required for mnemonic support)
        Account.enable_unaudited_hdwallet_features()
        
    def create_wallet(self) -> Tuple[str, str]:
        """Create a new wallet with mnemonic phrase"""
        # Generate 12-word mnemonic
        mnemonic = self.mnemo.generate(strength=128)
        
        # Derive Ethereum address
        account = Account.from_mnemonic(mnemonic)
        address = account.address
        
        # Initialize wallet in database with random balance (1-10 ETH)
        initial_balance = random.uniform(1.0, 10.0)
        self.db.create_wallet(address, initial_balance)
        
        return mnemonic, address
    
    def import_wallet(self, mnemonic: str) -> str:
        """Import wallet from mnemonic phrase"""
        if not self.mnemo.check(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        
        # Derive Ethereum address
        account = Account.from_mnemonic(mnemonic)
        address = account.address
        
        # Check if wallet exists in database, create if not
        if not self.db.get_wallet(address):
            initial_balance = random.uniform(1.0, 10.0)
            self.db.create_wallet(address, initial_balance)
        
        return address
    
    def get_balance(self, address: str) -> float:
        """Get wallet balance"""
        wallet = self.db.get_wallet(address)
        return wallet['balance'] if wallet else 0.0
    
    def get_eth_price_usd(self) -> float:
        """Get current ETH price in USD using a simple API"""
        try:
            # Using CoinGecko API as fallback for price display
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ethereum", "vs_currencies": "usd"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return float(data['ethereum']['usd'])
            else:
                return 3000.0  # Fallback price
        except Exception:
            return 3000.0  # Fallback price
    
    def get_usd_to_eth_quote(self, usd_amount: float) -> Dict:
        """Get ETH equivalent for USD amount using Skip API"""
        try:
            # Convert USD to USDC amount (6 decimals)
            usdc_amount = str(int(usd_amount * 1_000_000))
            
            url = "https://api.skip.build/v2/fungible/msgs_direct"
            payload = {
                "source_asset_denom": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "source_asset_chain_id": "1",
                "dest_asset_denom": "ethereum-native",
                "dest_asset_chain_id": "1",
                "amount_in": usdc_amount,
                "chain_ids_to_addresses": {
                    "1": "0x742d35Cc6634C0532925a3b8D4C9db96c728b0B4"
                },
                "slippage_tolerance_percent": "1",
                "smart_swap_options": {
                    "evm_swaps": True
                },
                "allow_unsafe": False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Extract ETH amount from response (18 decimals)
                eth_amount_wei = int(data['amount_out'])
                eth_amount = wei_to_eth(eth_amount_wei)
                
                return {
                    'success': True,
                    'eth_amount': eth_amount,
                    'usd_amount': usd_amount,
                    'rate': usd_amount / eth_amount if eth_amount > 0 else 0
                }
            else:
                # Fallback to simple calculation
                eth_price = self.get_eth_price_usd()
                eth_amount = usd_amount / eth_price
                return {
                    'success': True,
                    'eth_amount': eth_amount,
                    'usd_amount': usd_amount,
                    'rate': eth_price,
                    'fallback': True
                }
                
        except Exception as e:
            # Fallback to simple calculation
            try:
                eth_price = self.get_eth_price_usd()
                eth_amount = usd_amount / eth_price
                return {
                    'success': True,
                    'eth_amount': eth_amount,
                    'usd_amount': usd_amount,
                    'rate': eth_price,
                    'fallback': True,
                    'error': str(e)
                }
            except Exception as fallback_error:
                return {
                    'success': False,
                    'error': f"Quote failed: {str(e)}. Fallback failed: {str(fallback_error)}"
                }
    
    def prepare_transaction(self, from_address: str, to_address: str, 
                          amount: float, currency: str) -> Dict:
        """Prepare transaction for signing"""
        if not validate_ethereum_address(to_address):
            raise ValueError("Invalid recipient address")
        
        # Check sender balance
        sender_balance = self.get_balance(from_address)
        
        if currency == "ETH":
            if amount > sender_balance:
                raise ValueError(f"Insufficient balance. Available: {sender_balance:.6f} ETH")
            
            eth_amount = amount
            usd_amount = None
            eth_price = None
            
            message = f"Transfer {eth_amount:.6f} ETH to {to_address} from {from_address}"
            
        else:  # USD
            # Get ETH equivalent
            quote = self.get_usd_to_eth_quote(amount)
            if not quote['success']:
                raise ValueError(quote['error'])
            
            eth_amount = quote['eth_amount']
            
            if eth_amount > sender_balance:
                raise ValueError(f"Insufficient balance. Required: {eth_amount:.6f} ETH, Available: {sender_balance:.6f} ETH")
            
            usd_amount = amount
            eth_price = quote['rate']
            
            message = f"Transfer {eth_amount:.6f} ETH (${usd_amount:.2f} USD) to {to_address} from {from_address}"
        
        return {
            'from_address': from_address,
            'to_address': to_address,
            'amount_eth': eth_amount,
            'amount_usd': usd_amount,
            'original_usd_amount': amount if currency == "USD" else None,
            'original_eth_price': eth_price,
            'message': message,
            'created_at': time.time()
        }
    
    def sign_message(self, mnemonic: str, message: str) -> str:
        """Sign a message with the wallet's private key"""
        account = Account.from_mnemonic(mnemonic)
        signable_message = encode_defunct(text=message)
        signed_message = account.sign_message(signable_message)
        return signed_message.signature.hex()
    
    def verify_signature(self, address: str, message: str, signature: str) -> bool:
        """Verify a signature"""
        try:
            signable_message = encode_defunct(text=message)
            recovered_address = Account.recover_message(
                signable_message, 
                signature=signature
            )
            return recovered_address.lower() == address.lower()
        except Exception:
            return False
    
    def execute_transaction(self, from_address: str, to_address: str, 
                          amount_eth: float, signature: str, message: str,
                          original_usd_amount: Optional[float] = None,
                          original_eth_price: Optional[float] = None) -> Dict:
        """Execute a signed transaction"""
        try:
            # Verify signature
            if not self.verify_signature(from_address, message, signature):
                return {'success': False, 'error': 'Invalid signature'}
            
            # For USD transactions, check price slippage
            if original_usd_amount and original_eth_price:
                current_quote = self.get_usd_to_eth_quote(original_usd_amount)
                if current_quote['success']:
                    current_rate = current_quote['rate']
                    price_change = abs(current_rate - original_eth_price) / original_eth_price
                    
                    if price_change > 0.01:  # 1% tolerance
                        return {
                            'success': False, 
                            'error': f'Price changed by {price_change*100:.2f}%. Transaction rejected for your protection.'
                        }
            
            # Check balance again
            sender_balance = self.get_balance(from_address)
            if amount_eth > sender_balance:
                return {'success': False, 'error': 'Insufficient balance'}
            
            # Execute transfer
            self.db.transfer_balance(from_address, to_address, amount_eth)
            
            # Record transaction
            usd_amount = original_usd_amount if original_usd_amount else None
            self.db.add_transaction(from_address, to_address, amount_eth, usd_amount)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_transaction_history(self, address: str) -> List[Dict]:
        """Get transaction history for an address"""
        return self.db.get_transactions(address)
