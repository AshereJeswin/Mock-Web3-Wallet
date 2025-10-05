import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY', 're_2zf9B1g1_BeW763EyYQjH5v9e5pKmCzDH')
        self.from_email = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')  # ← Changed default
        self.base_url = "https://api.resend.com/emails"
    
        # Debug: Print to verify API key is loaded (remove in production)
        print(f"[NotificationService] API Key loaded: {self.api_key[:10]}..." if len(self.api_key) > 10 else "[NotificationService] ⚠️ Using default API key")
        print(f"[NotificationService] From Email: {self.from_email}")  # ← Add this to verify
    def send_transaction_notification(self, from_address: str, to_address: str,
                                      amount_eth: float, amount_usd: Optional[float] = None):
        """Send transaction notification email"""
        try:
            recipient_email = os.getenv('NOTIFICATION_EMAIL', 'asherejeswin@gmail.com')
            subject = "🔔 Transaction Completed - Mock Web3 Wallet"
            
            amount_text = f"{amount_eth:.6f} ETH"
            if amount_usd:
                amount_text += f" (${amount_usd:.2f} USD)"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #28a745;">✅ Transaction Successful</h2>
                        <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3>Transaction Details:</h3>
                            <p><strong>Amount:</strong> {amount_text}</p>
                            <p><strong>From:</strong> {from_address}</p>
                            <p><strong>To:</strong> {to_address}</p>
                            <p><strong>Status:</strong> <span style="color: #28a745;">Confirmed</span></p>
                        </div>
                        <p style="color: #6c757d; font-size: 14px;">
                            This is a notification from your Mock Web3 Wallet. 
                            If you did not initiate this transaction, please secure your wallet immediately.
                        </p>
                        <hr style="margin: 20px 0;">
                        <p style="text-align: center; color: #6c757d; font-size: 12px;">
                            Mock Web3 Wallet - Demo Application
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_content = (
                f"Transaction Successful!\n\n"
                f"Amount: {amount_text}\n"
                f"From: {from_address}\n"
                f"To: {to_address}\n"
                f"Status: Confirmed\n\n"
                f"This is a notification from your Mock Web3 Wallet."
            )
            
            return self._send_email(recipient_email, subject, html_content, text_content)
        
        except Exception as e:
            print(f"[NotificationService] ❌ Notification error: {str(e)}")
            return False

    def send_test_notification(self, email: str):
        """Send test notification"""
        subject = "🧪 Test Notification - Mock Web3 Wallet"
        
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #007bff;">🧪 Test Notification</h2>
                    <p>This is a test email from your Mock Web3 Wallet!</p>
                    <p>If you received this, email notifications are working correctly.</p>
                    <hr style="margin: 20px 0;">
                    <p style="text-align: center; color: #6c757d; font-size: 12px;">
                        Mock Web3 Wallet - Demo Application
                    </p>
                </div>
            </body>
        </html>
        """

        text_content = (
            "Test Notification\n\n"
            "This is a test email from your Mock Web3 Wallet!\n"
            "If you received this, email notifications are working correctly."
        )

        return self._send_email(email, subject, html_content, text_content)

    def _send_email(self, to_email: str, subject: str,
                    html_content: str, text_content: str) -> bool:
        """Send email using Resend API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'from': self.from_email,
                'to': [to_email],
                'subject': subject,
                'html': html_content,
                'text': text_content
            }

            response = requests.post(
                self.base_url,
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code in (200, 202):  # 202 = accepted, 200 = OK
                print(f"[NotificationService] ✅ Email sent to {to_email}")
                return True
            else:
                print(f"[NotificationService] ❌ Email failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"[NotificationService] ❗ Email send error: {str(e)}")
            return False