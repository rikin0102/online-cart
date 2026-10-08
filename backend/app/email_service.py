import logging
import socket
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decimal import Decimal
from typing import List, Any
from app.config import settings

logger = logging.getLogger(__name__)


def create_ipv4_socket(host: str, port: int, timeout: float = 10.0) -> socket.socket:
    """
    Explicitly resolve and connect using IPv4 (AF_INET) to prevent '[Errno 101] Network is unreachable'
    errors on Linux/Docker cloud platforms (like Render) that lack outbound IPv6 routing.
    Falls back to standard resolution if IPv4-specific lookup returns empty.
    """
    try:
        addr_info = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    except Exception:
        addr_info = []

    last_err = None
    for res in addr_info:
        af, socktype, proto, _, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            sock.settimeout(timeout)
            sock.connect(sa)
            return sock
        except Exception as err:
            last_err = err
            if sock is not None:
                sock.close()

    # Fallback to standard socket connection if IPv4-specific attempt didn't connect
    try:
        return socket.create_connection((host, port), timeout=timeout)
    except Exception as fallback_err:
        raise last_err if last_err else fallback_err


class IPv4SMTP(smtplib.SMTP):
    """SMTP client that prioritizes IPv4 to avoid container IPv6 routing blackholes."""
    def _get_socket(self, host, port, timeout):
        return create_ipv4_socket(host, port, timeout)


class IPv4SMTP_SSL(smtplib.SMTP_SSL):
    """SMTP_SSL client that prioritizes IPv4 to avoid container IPv6 routing blackholes."""
    def _get_socket(self, host, port, timeout):
        new_socket = create_ipv4_socket(host, port, timeout)
        return self.context.wrap_socket(new_socket, server_hostname=self._host)


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
    Send an order summary email using pure SMTP.
    Uses IPv4-resilient sockets and handles both Port 587 (STARTTLS) and Port 465 (SSL)
    with automatic fallbacks.
    Returns True if successful, False otherwise. Does NOT raise exceptions or block orders.
    """
    smtp_host = settings.SMTP_HOST.strip() if settings.SMTP_HOST else ""
    smtp_port = int(settings.SMTP_PORT) if settings.SMTP_PORT else 587
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

        ssl_context = ssl.create_default_context()
        sent = False
        last_error = None

        # Try configured port first, followed by alternate SMTP port (587 / 465)
        ports_to_try = [smtp_port]
        if smtp_port != 465:
            ports_to_try.append(465)
        if 587 not in ports_to_try:
            ports_to_try.append(587)

        for port in ports_to_try:
            # 1. Attempt IPv4-optimized connection
            try:
                if port == 465:
                    with IPv4SMTP_SSL(smtp_host, 465, timeout=12, context=ssl_context) as server:
                        server.ehlo()
                        if smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.sendmail(smtp_from, [recipient_email], msg.as_string())
                        sent = True
                        break
                else:
                    with IPv4SMTP(smtp_host, port, timeout=12) as server:
                        server.ehlo()
                        server.starttls(context=ssl_context)
                        server.ehlo()
                        if smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.sendmail(smtp_from, [recipient_email], msg.as_string())
                        sent = True
                        break
            except Exception as e_ipv4:
                last_error = e_ipv4
                print(f"[EMAIL ATTEMPT (IPv4) FAILED on {smtp_host}:{port}]: {type(e_ipv4).__name__}: {e_ipv4}")

            # 2. If IPv4 custom class failed, attempt standard smtplib connection
            if not sent:
                try:
                    if port == 465:
                        with smtplib.SMTP_SSL(smtp_host, 465, timeout=12, context=ssl_context) as server:
                            server.ehlo()
                            if smtp_pass:
                                server.login(smtp_user, smtp_pass)
                            server.sendmail(smtp_from, [recipient_email], msg.as_string())
                            sent = True
                            break
                    else:
                        with smtplib.SMTP(smtp_host, port, timeout=12) as server:
                            server.ehlo()
                            server.starttls(context=ssl_context)
                            server.ehlo()
                            if smtp_pass:
                                server.login(smtp_user, smtp_pass)
                            server.sendmail(smtp_from, [recipient_email], msg.as_string())
                            sent = True
                            break
                except Exception as e_std:
                    last_error = e_std
                    print(f"[EMAIL ATTEMPT (Standard) FAILED on {smtp_host}:{port}]: {type(e_std).__name__}: {e_std}")

        if sent:
            print(f"[EMAIL SUCCESS] Order confirmation email sent successfully to {recipient_email} for Order #{order_id}")
            logger.info(f"Order summary email sent successfully to {recipient_email} for Order #{order_id}")
            return True
        else:
            raise last_error if last_error else Exception("Unknown SMTP failure")

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
    Diagnose SMTP connection without sending any email.
    Tests DNS resolution, raw TCP sockets, IPv4 STARTTLS on port 587, and SSL on port 465.
    Never exposes SMTP_PASSWORD.
    """
    host = (settings.SMTP_HOST or "").strip()
    port = int(settings.SMTP_PORT) if settings.SMTP_PORT else 587
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

    # 2. Raw TCP Connection Probe (using IPv4 first)
    raw_tcp_results = {}
    for test_port in [587, 465, port]:
        if test_port in raw_tcp_results:
            continue
        try:
            sock = create_ipv4_socket(host, test_port, timeout=8)
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

    # 3. Port 587 Test (SMTP + STARTTLS via IPv4)
    port_587_result = {
        "port": 587,
        "protocol": "SMTP + STARTTLS (IPv4)",
        "connection_successful": False,
        "starttls_successful": False,
        "auth_attempted": bool(user and password),
        "auth_successful": False,
        "exception_type": None,
        "error_message": None
    }
    try:
        with IPv4SMTP(host, 587, timeout=10) as server:
            server.ehlo()
            port_587_result["connection_successful"] = True
            
            ssl_ctx = ssl.create_default_context()
            server.starttls(context=ssl_ctx)
            server.ehlo()
            port_587_result["starttls_successful"] = True
            
            if user and password:
                server.login(user, password)
                port_587_result["auth_successful"] = True
    except Exception as e:
        port_587_result["exception_type"] = type(e).__name__
        port_587_result["error_message"] = str(e)

    # 4. Port 465 Test (SMTP_SSL via IPv4)
    port_465_result = {
        "port": 465,
        "protocol": "SMTP_SSL (IPv4)",
        "connection_successful": False,
        "ssl_handshake_successful": False,
        "auth_attempted": bool(user and password),
        "auth_successful": False,
        "exception_type": None,
        "error_message": None
    }
    try:
        ssl_ctx = ssl.create_default_context()
        with IPv4SMTP_SSL(host, 465, timeout=10, context=ssl_ctx) as server:
            port_465_result["connection_successful"] = True
            server.ehlo()
            port_465_result["ssl_handshake_successful"] = True
            
            if user and password:
                server.login(user, password)
                port_465_result["auth_successful"] = True
    except Exception as e:
        port_465_result["exception_type"] = type(e).__name__
        port_465_result["error_message"] = str(e)

    overall_success = (
        port_587_result["auth_successful"] or 
        port_465_result["auth_successful"] or
        (port_587_result["starttls_successful"] and not password) or
        (port_465_result["ssl_handshake_successful"] and not password)
    )

    return {
        "status": "success" if overall_success else "failed",
        "environment_variables": env_status,
        "dns_resolution": dns_info,
        "tcp_socket_probe": raw_tcp_results,
        "port_587_starttls_test": port_587_result,
        "port_465_ssl_test": port_465_result,
        "summary": (
            "SMTP connection and authentication succeeded!"
            if overall_success
            else "SMTP test failed. Check the port test errors and DNS resolution details."
        )
    }


