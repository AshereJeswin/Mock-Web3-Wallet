# Mock Web3 Wallet

A fully functional mock Web3 wallet built with Python and Streamlit that demonstrates core wallet functionality including mnemonic generation, transaction signing, USD/ETH conversions, and email notifications.

## Features

### 🔐 Wallet Management
- **Create New Wallet**: Generate secure 12-word BIP39 mnemonic phrases
- **Import Existing Wallet**: Import wallets using mnemonic phrases
- **HD Wallet Support**: Ethereum address derivation from mnemonic
- **Persistent Storage**: SQLite database for wallet and transaction data

### 💰 Balance & Transactions
- **Mock ETH Balance**: Random initial balance (1-10 ETH) for new wallets
- **Send Transactions**: Transfer ETH to any Ethereum address
- **Dual Currency Support**: Send amounts in ETH or USD
- **Real-time Price Conversion**: USD to ETH using Skip API
- **Transaction History**: View complete transaction history

### 🔒 Security Features
- **Message Signing**: Cryptographic transaction approval
- **Signature Verification**: Backend verification of all transactions
- **Price Slippage Protection**: 1% tolerance for USD transactions
- **Transaction Expiry**: 30-second approval window

### 📧 Notifications
- **Email Notifications**: Transaction confirmations via Resend API
- **Test Notifications**: Verify email integration

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Blockchain**: eth-account, mnemonic libraries
- **Database**: SQLite (embedded database)
- **APIs**: Skip API (price quotes), Resend (email)
- **Security**: BIP39, ECDSA message signing

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Mock-Web3-Wallet

### Prerequisites
