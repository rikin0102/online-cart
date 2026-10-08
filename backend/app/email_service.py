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
    Send an order summary email using standard SMTP.
    Uses STARTTLS for port 2525 / 587 and SMTP_SSL for port 465.
    Returns True if successful, False otherwise. Does NOT raise exceptions.
    """
    import os
    import ssl

    # Read configuration from settings and environment variables
    smtp_host = (settings.SMTP_HOST or os.getenv("SMTP_HOST", "")).strip()
    
    # Parse SMTP_PORT safely to int
    raw_port = settings.SMTP_PORT or os.getenv("SMTP_PORT", 2525)
    try:
        smtp_port = int(raw_port)
    except (ValueError, TypeError):
        smtp_port = 2525

    smtp_user = (settings.SMTP_USER or os.getenv("SMTP_USER", "")).strip()
    smtp_pass = (settings.SMTP_PASSWORD or os.getenv("SMTP_PASSWORD", "")).replace(" ", "").strip()
    smtp_from = (settings.SMTP_FROM or os.getenv("SMTP_FROM", "")).strip() or smtp_user

    if not smtp_host:
        print(f"[EMAIL WARNING] SMTP_HOST not configured. Skipping email delivery for Order #{order_id}")
        logger.warning(f"SMTP_HOST not configured. Skipping email delivery for Order #{order_id}.")
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

        ssl_context = ssl.create_default_context()

        # Connect using the configured SMTP host and port
        if smtp_port == 465:
            logger.info(f"Connecting to SMTP server {smtp_host}:{smtp_port} with SSL...")
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15, context=ssl_context) as server:
                server.ehlo()
                if smtp_user and smtp_pass:
                    logger.info(f"Authenticating with SMTP user '{smtp_user}'...")
                    server.login(smtp_user, smtp_pass)
                logger.info(f"Sending email for Order #{order_id} to {recipient_email}...")
                server.sendmail(smtp_from, [recipient_email], msg.as_string())
        else:
            # Port 2525, 587, or custom relay port: smtplib.SMTP + STARTTLS
            logger.info(f"Connecting to SMTP server {smtp_host}:{smtp_port}...")
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.ehlo()
                logger.info("Initiating STARTTLS encryption...")
                server.starttls(context=ssl_context)
                server.ehlo()
                if smtp_user and smtp_pass:
                    logger.info(f"Authenticating with SMTP user '{smtp_user}'...")
                    server.login(smtp_user, smtp_pass)
                logger.info(f"Sending email for Order #{order_id} to {recipient_email}...")
                server.sendmail(smtp_from, [recipient_email], msg.as_string())

        print(f"[EMAIL SUCCESS] Order confirmation email sent to {recipient_email} for Order #{order_id} via {smtp_host}:{smtp_port}")
        logger.info(f"Order summary email sent successfully to {recipient_email} for Order #{order_id}")
        return True

    except smtplib.SMTPAuthenticationError as auth_err:
        print(f"[EMAIL AUTH ERROR] SMTP authentication failed for user '{smtp_user}' on {smtp_host}:{smtp_port}: {auth_err}")
        logger.error(f"SMTP authentication failed for user '{smtp_user}' on {smtp_host}:{smtp_port}: {auth_err}")
        return False
    except smtplib.SMTPConnectError as conn_err:
        print(f"[EMAIL CONNECT ERROR] Could not connect to SMTP server {smtp_host}:{smtp_port}: {conn_err}")
        logger.error(f"Could not connect to SMTP server {smtp_host}:{smtp_port}: {conn_err}")
        return False
    except smtplib.SMTPException as smtp_err:
        print(f"[EMAIL PROTOCOL ERROR] SMTP error ({type(smtp_err).__name__}) on {smtp_host}:{smtp_port}: {smtp_err}")
        logger.error(f"SMTP error ({type(smtp_err).__name__}) on {smtp_host}:{smtp_port}: {smtp_err}")
        return False
    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send email to {recipient_email} for Order #{order_id} ({type(exc).__name__}): {exc}")
        logger.error(f"Failed to send email to {recipient_email} for Order #{order_id} ({type(exc).__name__}): {exc}")
        return False


# ============================================================================
# TEMPORARY DEVELOPMENT / TEST SMTP DIAGNOSTIC FUNCTION
# (Can be removed along with the /smtp-test endpoint after diagnosis)
# ============================================================================
def test_smtp_connectivity() -> dict:
    """
    Diagnose SMTP connection without sending any email.
    Tests DNS, TCP connection, STARTTLS on configured port (e.g. 2525 / 587), and SSL on 465.
    Never exposes SMTP_PASSWORD or secret keys.
    """
    import os
    import socket
    import ssl

    host = (settings.SMTP_HOST or os.getenv("SMTP_HOST", "")).strip()
    
    raw_port = settings.SMTP_PORT or os.getenv("SMTP_PORT", 2525)
    try:
        port = int(raw_port)
    except (ValueError, TypeError):
        port = 2525

    user = (settings.SMTP_USER or os.getenv("SMTP_USER", "")).strip()
    password = (settings.SMTP_PASSWORD or os.getenv("SMTP_PASSWORD", "")).replace(" ", "").strip()
    from_addr = (settings.SMTP_FROM or os.getenv("SMTP_FROM", "")).strip() or user

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
    dns_info = {"ipv4": [], "ipv6": [], "dns_error": None}
    try:
        addr_info = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        for family, socktype, proto, canonname, sockaddr in addr_info:
            ip = sockaddr[0]
            if family == socket.AF_INET and ip not in dns_info["ipv4"]:
                dns_info["ipv4"].append(ip)
            elif family == socket.AF_INET6 and ip not in dns_info["ipv6"]:
                dns_info["ipv6"].append(ip)
    except Exception as e:
        dns_info["dns_error"] = f"{type(e).__name__}: {str(e)}"

    # 2. Raw TCP Connection Probe
    raw_tcp_results = {}
    test_ports = list(dict.fromkeys([port, 2525, 587, 465]))
    for test_port in test_ports:
        try:
            sock = socket.create_connection((host, test_port), timeout=8)
            sock.close()
            raw_tcp_results[f"port_{test_port}"] = {
                "reachable": True,
                "exception_type": None,
                "error_message": None
            }
        except Exception as e:
            raw_tcp_results[f"port_{test_port}"] = {
                "reachable": False,
                "exception_type": type(e).__name__,
                "error_message": str(e)
            }

    # 3. Test Configured Port (e.g. 2525 with STARTTLS)
    configured_port_result = {
        "port": port,
        "protocol": "SMTP_SSL" if port == 465 else "SMTP + STARTTLS",
        "connection_successful": False,
        "tls_or_ssl_handshake_successful": False,
        "auth_attempted": bool(user and password),
        "auth_successful": False,
        "exception_type": None,
        "error_message": None
    }
    try:
        ssl_ctx = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=10, context=ssl_ctx) as server:
                configured_port_result["connection_successful"] = True
                server.ehlo()
                configured_port_result["tls_or_ssl_handshake_successful"] = True
                if user and password:
                    server.login(user, password)
                    configured_port_result["auth_successful"] = True
        else:
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.ehlo()
                configured_port_result["connection_successful"] = True
                server.starttls(context=ssl_ctx)
                server.ehlo()
                configured_port_result["tls_or_ssl_handshake_successful"] = True
                if user and password:
                    server.login(user, password)
                    configured_port_result["auth_successful"] = True
    except Exception as e:
        configured_port_result["exception_type"] = type(e).__name__
        configured_port_result["error_message"] = str(e)

    overall_success = (
        configured_port_result["auth_successful"] or
        (configured_port_result["tls_or_ssl_handshake_successful"] and not password)
    )

    return {
        "status": "success" if overall_success else "failed",
        "environment_variables": env_status,
        "dns_resolution": dns_info,
        "tcp_socket_probe": raw_tcp_results,
        "configured_port_test": configured_port_result,
        "summary": (
            f"SMTP connection and authentication succeeded on {host}:{port}!"
            if overall_success
            else f"SMTP test failed on {host}:{port}. Review error_message and tcp_socket_probe details."
        )
    }


