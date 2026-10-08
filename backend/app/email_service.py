import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decimal import Decimal
from typing import List, Any
from app.config import settings

logger = logging.getLogger(__name__)


def format_inr(amount: Decimal) -> str:
    """Format decimal amount as Indian Rupee string (e.g. Rs. 1,200.00 or Rs. 1,200)."""
    # Standard format: Rs. 1,234.56
    return f"Rs. {amount:,.2f}"


def send_order_summary_email(
    recipient_email: str,
    recipient_name: str,
    order_id: int,
    order_items: List[Any],
    grand_total: Decimal
) -> bool:
    """
    Send an order summary email using smtplib with STARTTLS.
    Returns True if successful, False otherwise. Does NOT raise exceptions.
    """
    smtp_host = settings.SMTP_HOST.strip() if settings.SMTP_HOST else ""
    smtp_user = settings.SMTP_USER.strip() if settings.SMTP_USER else ""
    smtp_pass = settings.SMTP_PASSWORD.replace(" ", "").strip() if settings.SMTP_PASSWORD else ""
    smtp_from = settings.SMTP_FROM.strip() if settings.SMTP_FROM else smtp_user

    if not smtp_host or not smtp_user:
        print(f"[EMAIL WARNING] SMTP not configured. Host: '{smtp_host}', User: '{smtp_user}'. Skipping email for Order #{order_id}")
        logger.warning(
            f"SMTP not configured (SMTP_HOST='{smtp_host}', SMTP_USER='{smtp_user}'). "
            f"Skipping email delivery for Order #{order_id}."
        )
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Order #{order_id} Confirmation - Online Cart"
        msg["From"] = f"Online Cart <{smtp_from}>"
        msg["To"] = recipient_email

        formatted_total = format_inr(grand_total)

        # Build plain-text fallback
        lines = [
            f"Hi {recipient_name}, thanks for your order. Here is your bill:\n",
            f"Order ID: #{order_id}\n",
            f"{'Product':<30} | {'Qty':<5} | {'Price':<12} | {'Total':<12}",
            "-" * 65
        ]
        for item in order_items:
            lines.append(
                f"{item.product_name:<30} | {item.quantity:<5} | {format_inr(item.price):<12} | {format_inr(item.line_total):<12}"
            )
        lines.append("-" * 65)
        lines.append(f"Grand total {formatted_total}\n")
        lines.append("Thank you for shopping with Online Cart!")
        text_content = "\n".join(lines)

        # Build HTML content
        html_rows = ""
        for item in order_items:
            html_rows += f"""
            <tr>
                <td style="padding: 10px 12px; border-bottom: 1px solid #E5E7EB; color: #1F2933;">{item.product_name}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #E5E7EB; text-align: center; color: #1F2933;">{item.quantity}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #E5E7EB; text-align: right; color: #1F2933;">{format_inr(item.price)}</td>
                <td style="padding: 10px 12px; border-bottom: 1px solid #E5E7EB; text-align: right; font-weight: 600; color: #1F2933;">{format_inr(item.line_total)}</td>
            </tr>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your order summary</title>
        </head>
        <body style="font-family: 'Inter', system-ui, -apple-system, sans-serif; background-color: #F5F6F8; margin: 0; padding: 24px; color: #1F2933;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                <div style="border-bottom: 1px solid #E5E7EB; padding-bottom: 16px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 8px 0; color: #1D4ED8; font-size: 20px;">Online Cart</h2>
                    <p style="margin: 0; font-size: 14px; color: #6B7280;">Order Confirmation & Bill</p>
                </div>
                <p style="font-size: 15px; line-height: 1.5; margin: 0 0 16px 0;">
                    Hi <strong>{recipient_name}</strong>, thanks for your order. Here is your bill:
                </p>
                <div style="background-color: #F5F6F8; border-radius: 6px; padding: 8px 12px; margin-bottom: 16px; font-size: 13px; color: #6B7280;">
                    Order Reference: <strong>#{order_id}</strong>
                </div>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #F5F6F8;">
                            <th style="padding: 10px 12px; text-align: left; font-weight: 600; color: #1F2933; border-bottom: 1px solid #E5E7EB;">Product</th>
                            <th style="padding: 10px 12px; text-align: center; font-weight: 600; color: #1F2933; border-bottom: 1px solid #E5E7EB;">Qty</th>
                            <th style="padding: 10px 12px; text-align: right; font-weight: 600; color: #1F2933; border-bottom: 1px solid #E5E7EB;">Price</th>
                            <th style="padding: 10px 12px; text-align: right; font-weight: 600; color: #1F2933; border-bottom: 1px solid #E5E7EB;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {html_rows}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="3" style="padding: 14px 12px; text-align: right; font-weight: 600; font-size: 15px; color: #1F2933;">Grand total:</td>
                            <td style="padding: 14px 12px; text-align: right; font-weight: 700; font-size: 16px; color: #1D4ED8;">{formatted_total}</td>
                        </tr>
                    </tfoot>
                </table>
                <p style="font-size: 13px; color: #6B7280; margin: 0; text-align: center; border-top: 1px solid #E5E7EB; padding-top: 16px;">
                    Thank you for shopping with us!
                </p>
            </div>
        </body>
        </html>
        """

        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)

        import ssl

        ssl_context = ssl.create_default_context()
        sent = False
        last_error = None

        # Try designated port first, then fallback to 465 SSL if 587 is blocked by ISP/firewall
        ports_to_try = [settings.SMTP_PORT]
        if settings.SMTP_PORT != 465:
            ports_to_try.append(465)

        for port in ports_to_try:
            try:
                if port == 465:
                    with smtplib.SMTP_SSL(smtp_host, 465, timeout=10, context=ssl_context) as server:
                        if smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.sendmail(smtp_from, [recipient_email], msg.as_string())
                        sent = True
                        break
                else:
                    with smtplib.SMTP(smtp_host, port, timeout=10) as server:
                        server.starttls(context=ssl_context)
                        if smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.sendmail(smtp_from, [recipient_email], msg.as_string())
                        sent = True
                        break
            except Exception as e:
                last_error = e
                print(f"[EMAIL ATTEMPT FAILED on port {port}]: {e}")

        if sent:
            print(f"[EMAIL SUCCESS] Order confirmation email sent to {recipient_email} for Order #{order_id}")
            logger.info(f"Order summary email sent successfully to {recipient_email} for Order #{order_id}")
            return True
        else:
            raise last_error if last_error else Exception("Unknown SMTP error")

    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send email to {recipient_email} for Order #{order_id}: {exc}")
        logger.error(f"Failed to send email to {recipient_email} for Order #{order_id}: {exc}")
        return False
