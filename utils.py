import re
from typing import Union

def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    if not address or not isinstance(address, str):
        return False
    
    # Check if it starts with 0x and has correct length
    if not address.startswith('0x') or len(address) != 42:
        return False
    
    # Check if it contains only valid hex characters
    hex_part = address[2:]
    return bool(re.match(r'^[0-9a-fA-F]+$', hex_part))

def wei_to_eth(wei: Union[int, str]) -> float:
    """Convert Wei to ETH (divide by 10^18)"""
    return float(int(wei)) / 10**18

def eth_to_wei(eth: float) -> int:
    """Convert ETH to Wei (multiply by 10^18)"""
    return int(eth * 10**18)

def format_address(address: str, chars: int = 6) -> str:
    """Format address for display (e.g., 0x1234...abcd)"""
    if len(address) <= chars * 2 + 2:
        return address
    return f"{address[:chars+2]}...{address[-chars:]}"

def format_eth_amount(amount: float, decimals: int = 6) -> str:
    """Format ETH amount for display"""
    return f"{amount:.{decimals}f} ETH"

def format_usd_amount(amount: float, decimals: int = 2) -> str:
    """Format USD amount for display"""
    return f"${amount:.{decimals}f}"
