import streamlit as st
import os
from dotenv import load_dotenv
from wallet_service import WalletService
from database import DatabaseManager
from notification_service import NotificationService
import time
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Initialize services
@st.cache_resource
def init_services():
    db = DatabaseManager()
    wallet_service = WalletService(db)
    notification_service = NotificationService()
    return db, wallet_service, notification_service

db, wallet_service, notification_service = init_services()

# Initialize session state
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'mnemonic' not in st.session_state:
    st.session_state.mnemonic = None
if 'pending_transaction' not in st.session_state:
    st.session_state.pending_transaction = None

def main():
    st.title("🔐 Mock Web3 Wallet")
    st.markdown("---")
    
    # Sidebar for wallet management
    with st.sidebar:
        st.header("Wallet Management")
        
        if st.session_state.wallet_address is None:
            st.subheader("Create or Import Wallet")
            
            # Wallet creation/import options
            tab1, tab2 = st.tabs(["Create New", "Import Existing"])
            
            with tab1:
                if st.button("Generate New Wallet", type="primary"):
                    try:
                        mnemonic, address = wallet_service.create_wallet()
                        st.session_state.mnemonic = mnemonic
                        st.session_state.wallet_address = address
                        st.success("✅ New wallet created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating wallet: {str(e)}")
            
            with tab2:
                mnemonic_input = st.text_area(
                    "Enter 12-word mnemonic phrase:",
                    placeholder="word1 word2 word3 ... word12",
                    height=100
                )
                
                if st.button("Import Wallet"):
                    if mnemonic_input.strip():
                        try:
                            address = wallet_service.import_wallet(mnemonic_input.strip())
                            st.session_state.mnemonic = mnemonic_input.strip()
                            st.session_state.wallet_address = address
                            st.success("✅ Wallet imported successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error importing wallet: {str(e)}")
                    else:
                        st.error("Please enter a valid mnemonic phrase")
        
        else:
            # Wallet info
            st.subheader("Current Wallet")
            st.code(st.session_state.wallet_address, language="text")
            
            if st.button("Disconnect Wallet"):
                st.session_state.wallet_address = None
                st.session_state.mnemonic = None
                st.session_state.pending_transaction = None
                st.rerun()
            
            # Show mnemonic (expandable)
            with st.expander("Show Mnemonic Phrase"):
                st.warning("⚠️ Keep this phrase secure!")
                st.code(st.session_state.mnemonic)

    # Main content
    if st.session_state.wallet_address is None:
        st.info("👈 Please create or import a wallet to get started")
        st.markdown("### Welcome to Mock Web3 Wallet")
        st.markdown("""
        This is a demonstration Web3 wallet that allows you to:
        - Create or import wallets using BIP39 mnemonic phrases
        - Manage mock ETH balances
        - Send transactions with signature verification
        - Convert between ETH and USD using real-time prices
        - View transaction history
        - Receive email notifications
        """)
    else:
        # Wallet dashboard
        display_dashboard()

def display_dashboard():
    # Get wallet balance
    balance = wallet_service.get_balance(st.session_state.wallet_address)
    
    # Balance display
    st.subheader("💰 Wallet Balance")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ETH Balance", f"{balance:.6f} ETH")
    with col2:
        # Get ETH price in USD for display (optional)
        try:
            usd_value = wallet_service.get_eth_price_usd() * balance
            st.metric("USD Value", f"${usd_value:.2f}")
        except:
            st.metric("USD Value", "N/A")
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💸 Send Transaction", "📊 Transaction History", "⚙️ Settings"])
    
    with tab1:
        display_send_transaction()
    
    with tab2:
        display_transaction_history()
    
    with tab3:
        display_settings()

def display_send_transaction():
    st.subheader("Send ETH")
    
    # Check for pending transaction
    if st.session_state.pending_transaction:
        display_transaction_approval()
        return
    
    with st.form("send_transaction_form"):
        # Recipient address
        recipient = st.text_input(
            "Recipient Address:",
            placeholder="0x742d35Cc6634C0532925a3b8D4C9db96c728b0B4"
        )
        
        # Amount input with currency selection
        col1, col2 = st.columns([3, 1])
        with col1:
            amount = st.number_input("Amount:", min_value=0.0, step=0.001, format="%.6f")
        with col2:
            currency = st.selectbox("Currency:", ["ETH", "USD"])
        
        submitted = st.form_submit_button("Prepare Transaction", type="primary")
        
        if submitted:
            if not recipient or not amount:
                st.error("Please fill in all fields")
            elif not recipient.startswith('0x') or len(recipient) != 42:
                st.error("Invalid recipient address format")
            else:
                try:
                    # Prepare transaction
                    tx_data = wallet_service.prepare_transaction(
                        st.session_state.wallet_address,
                        recipient,
                        amount,
                        currency
                    )
                    st.session_state.pending_transaction = tx_data
                    st.rerun()
                except Exception as e:
                    st.error(f"Error preparing transaction: {str(e)}")

def display_transaction_approval():
    st.subheader("🔐 Transaction Approval Required")
    
    tx_data = st.session_state.pending_transaction
    
    # Display transaction details
    st.info("Please review and approve this transaction:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**From:**", tx_data['from_address'])
        st.write("**To:**", tx_data['to_address'])
    with col2:
        st.write("**Amount:**", f"{tx_data['amount_eth']:.6f} ETH")
        if tx_data.get('amount_usd'):
            st.write("**USD Value:**", f"${tx_data['amount_usd']:.2f}")
    
    # Show the message to be signed
    st.code(tx_data['message'], language="text")
    
    # Approval buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve & Sign", type="primary"):
            try:
                # Sign and execute transaction
                signature = wallet_service.sign_message(
                    st.session_state.mnemonic,
                    tx_data['message']
                )
                
                # Execute transaction
                result = wallet_service.execute_transaction(
                    tx_data['from_address'],
                    tx_data['to_address'],
                    tx_data['amount_eth'],
                    signature,
                    tx_data['message'],
                    tx_data.get('original_usd_amount'),
                    tx_data.get('original_eth_price')
                )
                
                if result['success']:
                    st.success("✅ Transaction completed successfully!")
                    
                    # Send notification
                    try:
                        notification_service.send_transaction_notification(
                            st.session_state.wallet_address,
                            tx_data['to_address'],
                            tx_data['amount_eth'],
                            tx_data.get('amount_usd')
                        )
                    except Exception as e:
                        st.warning(f"Transaction successful but notification failed: {str(e)}")
                    
                    # Clear pending transaction
                    st.session_state.pending_transaction = None
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Transaction failed: {result['error']}")
                    st.session_state.pending_transaction = None
                    
            except Exception as e:
                st.error(f"Error executing transaction: {str(e)}")
                st.session_state.pending_transaction = None
    
    with col2:
        if st.button("❌ Reject"):
            st.session_state.pending_transaction = None
            st.rerun()
    
    with col3:
        # Show transaction expiry
        created_time = tx_data.get('created_at', time.time())
        time_left = max(0, 30 - (time.time() - created_time))
        st.write(f"⏰ Expires in: {int(time_left)}s")
        
        if time_left <= 0:
            st.error("Transaction expired")
            st.session_state.pending_transaction = None
            st.rerun()
    
    # Auto-refresh every second to update the timer
    time.sleep(1)
    st.rerun()

def display_transaction_history():
    st.subheader("📊 Transaction History")
    
    transactions = wallet_service.get_transaction_history(st.session_state.wallet_address)
    
    if not transactions:
        st.info("No transactions found")
        return
    
    # Display transactions in a table
    for i, tx in enumerate(transactions):
        with st.expander(f"Transaction #{len(transactions) - i} - {tx['timestamp'][:19]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Type:**", "Sent" if tx['from_address'] == st.session_state.wallet_address else "Received")
                st.write("**From:**", tx['from_address'])
                st.write("**To:**", tx['to_address'])
            
            with col2:
                st.write("**Amount:**", f"{tx['amount']:.6f} ETH")
                if tx['usd_amount']:
                    st.write("**USD Value:**", f"${tx['usd_amount']:.2f}")
                st.write("**Status:**", "✅ Confirmed")

def display_settings():
    st.subheader("⚙️ Settings")
    
    # Email notification settings
    st.write("**Email Notifications**")
    email = st.text_input("Email address for notifications:", 
                         placeholder="your-email@example.com")
    
    if st.button("Test Email Notification"):
        if email:
            try:
                notification_service.send_test_notification(email)
                st.success("✅ Test email sent!")
            except Exception as e:
                st.error(f"Failed to send test email: {str(e)}")
        else:
            st.error("Please enter an email address")
    
    st.markdown("---")
    
    # Wallet info
    st.write("**Wallet Information**")
    st.write("Address:", st.session_state.wallet_address)
    
    balance = wallet_service.get_balance(st.session_state.wallet_address)
    st.write("Balance:", f"{balance:.6f} ETH")
    
    # Database stats
    total_transactions = len(wallet_service.get_transaction_history(st.session_state.wallet_address))
    st.write("Total Transactions:", total_transactions)

if __name__ == "__main__":
    main()
