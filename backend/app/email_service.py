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
    return f"Rs. {amount:,.2f}"


def send_order_summary_email(
    recipient_email: str,
    recipient_name: str,
    order_id: int,
    order_items: List[Any],
    grand_total: Decimal
) -> bool:
    """
    Send an order summary email using Brevo SMTP with STARTTLS on port 2525.
    Returns True if successful, False otherwise. Does NOT raise exceptions or affect order creation.
    """
    smtp_host = (settings.SMTP_HOST or "smtp-relay.brevo.com").strip()
    smtp_port = int(settings.SMTP_PORT) if settings.SMTP_PORT else 2525
    smtp_user = (settings.SMTP_USER or "").strip()
    smtp_pass = (settings.SMTP_PASSWORD or "").replace(" ", "").strip()
    smtp_from = (settings.SMTP_FROM or "").strip() or smtp_user

    if not smtp_host or not smtp_user or not smtp_pass:
        print(f"[EMAIL WARNING] SMTP not fully configured. Host: '{smtp_host}', User: '{smtp_user}'. Skipping email for Order #{order_id}")
        logger.warning(
            f"SMTP not fully configured (SMTP_HOST='{smtp_host}', SMTP_USER='{smtp_user}'). "
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

        # Standard SMTP connection with STARTTLS on port 2525
        smtp = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(smtp_user, smtp_pass)
            smtp.sendmail(smtp_from, [recipient_email], msg.as_string())
        finally:
            try:
                smtp.quit()
            except Exception:
                pass

        print(f"[EMAIL SUCCESS] Order confirmation email sent successfully to {recipient_email} for Order #{order_id}")
        logger.info(f"Order summary email sent successfully to {recipient_email} for Order #{order_id}")
        return True

    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send email to {recipient_email} for Order #{order_id}: {type(exc).__name__}: {exc}")
        logger.error(f"Failed to send email to {recipient_email} for Order #{order_id}: {type(exc).__name__}: {exc}")
        return False


# ============================================================================
# TEMPORARY DEVELOPMENT / TEST SMTP DIAGNOSTIC FUNCTION
# (Can be removed along with the /smtp-test endpoint after diagnosis)
# ============================================================================
def test_smtp_connectivity() -> dict:
    """
    Diagnose Brevo SMTP connectivity on port 2525 without sending any email.
    Tests raw TCP connection, STARTTLS handshake, and authentication.
    Never exposes SMTP_PASSWORD.
    """
    import socket

    host = (settings.SMTP_HOST or "smtp-relay.brevo.com").strip()
    port = int(settings.SMTP_PORT) if settings.SMTP_PORT else 2525
    user = (settings.SMTP_USER or "").strip()
    password = (settings.SMTP_PASSWORD or "").replace(" ", "").strip()
    from_addr = (settings.SMTP_FROM or "").strip() or user

    env_status = {
        "SMTP_HOST": host if host else "[NOT SET]",
        "SMTP_PORT": port,
        "SMTP_USER": user if user else "[NOT SET]",
        "SMTP_PASSWORD_SET": bool(password),
        "SMTP_PASSWORD_LENGTH": len(password) if password else 0,
        "SMTP_FROM": from_addr if from_addr else "[NOT SET]"
    }

    if not host:
        return {
            "status": "error",
            "message": "SMTP_HOST is not configured in environment variables.",
            "environment_variables": env_status
        }

    # 1. DNS Resolution Check
    dns_info = {"ips": [], "dns_error": None}
    try:
        addr_info = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        for _, _, _, _, sockaddr in addr_info:
            ip = sockaddr[0]
            if ip not in dns_info["ips"]:
                dns_info["ips"].append(ip)
    except Exception as e:
        dns_info["dns_error"] = f"{type(e).__name__}: {str(e)}"

    # 2. Raw TCP Probe on Port 2525
    tcp_probe = {"reachable": False, "exception_type": None, "error_message": None}
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        tcp_probe["reachable"] = True
    except Exception as e:
        tcp_probe["exception_type"] = type(e).__name__
        tcp_probe["error_message"] = str(e)

    # 3. SMTP + STARTTLS + Login Test
    smtp_test = {
        "port": port,
        "protocol": "SMTP + STARTTLS",
        "connection_successful": False,
        "starttls_successful": False,
        "auth_attempted": bool(user and password),
        "auth_successful": False,
        "exception_type": None,
        "error_message": None
    }

    smtp_obj = None
    try:
        smtp_obj = smtplib.SMTP(host, port, timeout=30)
        smtp_obj.ehlo()
        smtp_test["connection_successful"] = True

        smtp_obj.starttls()
        smtp_obj.ehlo()
        smtp_test["starttls_successful"] = True

        if user and password:
            smtp_obj.login(user, password)
            smtp_test["auth_successful"] = True
    except Exception as e:
        smtp_test["exception_type"] = type(e).__name__
        smtp_test["error_message"] = str(e)
    finally:
        if smtp_obj:
            try:
                smtp_obj.quit()
            except Exception:
                pass

    overall_success = (
        smtp_test["auth_successful"] or
        (smtp_test["starttls_successful"] and not password)
    )

    return {
        "status": "success" if overall_success else "failed",
        "environment_variables": env_status,
        "dns_resolution": dns_info,
        "tcp_probe": tcp_probe,
        "smtp_test": smtp_test,
        "summary": (
            f"Brevo SMTP connection and authentication succeeded on {host}:{port}!"
            if overall_success
            else f"Brevo SMTP test failed on {host}:{port}. Check error details above."
        )
    }



