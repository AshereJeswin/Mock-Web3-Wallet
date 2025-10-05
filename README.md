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
 ```


### Work Flow
<!-- HEADER -->
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&style=for-the-badge" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-1.28+-orange?logo=streamlit&style=for-the-badge" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Ethereum-Black?logo=ethereum&style=for-the-badge" alt="Ethereum" />
  <img src="https://img.shields.io/badge/SQLite-Black?logo=sqlite&style=for-the-badge" alt="SQLite" />
  <img src="https://img.shields.io/badge/Resend-FF5F5F?logo=resend&style=for-the-badge" alt="Resend" />
</div>

<br />

<div align="center">
  <h1>🔐 Mock Web3 Wallet</h1>
  <p><em>A sleek, interactive mock wallet for learning Web3 concepts — no real funds needed.</em></p>
</div>

<br />

<div align="center">
  <img width="70%" src="./images/homepage.png" alt="Homepage Screenshot" />
</div>

---

## 🌟 Features

✨ **Fully Interactive UI** | 💰 **Dual Currency (ETH/USD)** | 🔐 **Secure Signing** | 📧 **Email Notifications**

| Feature              | Description |
|----------------------|-------------|
| 🗝️ **Mnemonic Wallets** | Generate or import BIP39 12-word phrases |
| 🪙 **Mock ETH Balances** | Random starting balance (1–10 ETH) |
| 💸 **Send Transactions** | Send ETH or USD to any address |
| 🔄 **Real-time Pricing** | Powered by Skip API |
| 🛡️ **Transaction Approval** | Sign & verify with ECDSA |
| ⏳ **Auto-expiry** | 30-second approval window |
| 📨 **Email Alerts** | Instant confirmation via Resend |
| 📊 **History Logs** | View all past transactions |
| 📥 **Import Wallet** | Restore from existing mnemonic |

---

## 🎥 Quick Demo Flow

<div align="center">
  <img width="60%" src="./images/wallet.png" alt="Wallet Dashboard" />
  <br />
  <em>Dashboard with balance, send form, and transaction history</em>
</div>

---

## 🖼️ Step-by-Step Screenshots

| Step | Action | Image |
|------|--------|-------|
| **1. 🏠 Homepage** | Create or import a wallet | ![Homepage](./images/homepage.png) |
| **2. 💼 Wallet Dashboard** | View balance & prepare transaction | ![Wallet](./images/wallet.png) |
| **3. 📤 Prepare Transaction** | Enter recipient & amount | ![Prepare](./images/prepare.png) |
| **4. 🔐 Approve Transaction** | Review & sign within 30s | ![Approve](./images/approve.png) |
| **5. 📧 Email Confirmation** | Get notified via email | ![Email](./images/email.png) |
| **6. 📥 Import Existing Wallet** | Paste 12-word mnemonic to restore | ![Import](./images/import.png) |
| **7. 💸 Send with USD Value** | See real-time USD conversion on approval | ![Send USD](./images/send-usd.png) |
| **8. 📊 View Transaction History** | Track all sent/received transactions | ![History](./images/history.png) |

---
