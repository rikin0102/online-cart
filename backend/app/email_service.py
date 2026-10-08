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

        # Build HTML content with mobile-responsive design
        html_rows = ""
        for item in order_items:
            html_rows += f"""
            <tr>
                <td style="padding: 10px 8px; border-bottom: 1px solid #E5E7EB; color: #1F2933; word-break: break-word; font-size: 13px; vertical-align: top;">
                    <strong>{item.product_name}</strong>
                </td>
                <td style="padding: 10px 6px; border-bottom: 1px solid #E5E7EB; text-align: center; color: #4B5563; font-size: 13px; vertical-align: top; white-space: nowrap;">
                    {item.quantity}
                </td>
                <td style="padding: 10px 6px; border-bottom: 1px solid #E5E7EB; text-align: right; color: #4B5563; font-size: 13px; vertical-align: top; white-space: nowrap;">
                    {format_inr(item.price)}
                </td>
                <td style="padding: 10px 8px; border-bottom: 1px solid #E5E7EB; text-align: right; font-weight: 600; color: #111827; font-size: 13px; vertical-align: top; white-space: nowrap;">
                    {format_inr(item.line_total)}
                </td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Order #{order_id} Confirmation - Online Cart</title>
    <style>
        body, table, td, p, a, li, blockquote {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        table, td {{
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        @media only screen and (max-width: 480px) {{
            .email-container {{
                padding: 16px 12px !important;
                width: 100% !important;
            }}
            .email-body-pad {{
                padding: 12px 6px !important;
            }}
            .table-head-th {{
                font-size: 12px !important;
                padding: 8px 4px !important;
            }}
            .table-cell-td {{
                font-size: 12px !important;
                padding: 8px 4px !important;
            }}
            .grand-total-label {{
                font-size: 14px !important;
            }}
            .grand-total-val {{
                font-size: 15px !important;
            }}
        }}
    </style>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F3F4F6; margin: 0; padding: 16px 8px; color: #1F2933; -webkit-font-smoothing: antialiased;">
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;">
        <tr>
            <td align="center" style="padding: 0;">
                <div class="email-container" style="max-width: 560px; width: 100%; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 24px; box-sizing: border-box; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); overflow: hidden;">
                    
                    <!-- Header -->
                    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-bottom: 2px solid #2563EB; padding-bottom: 14px; margin-bottom: 18px;">
                        <tr>
                            <td>
                                <h1 style="margin: 0 0 4px 0; color: #2563EB; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Online Cart</h1>
                                <p style="margin: 0; font-size: 13px; color: #6B7280; font-weight: 500;">Order Confirmation & Bill</p>
                            </td>
                        </tr>
                    </table>

                    <!-- Greeting & Order ID Badge -->
                    <p style="font-size: 14px; line-height: 1.5; margin: 0 0 14px 0; color: #374151;">
                        Hi <strong>{recipient_name}</strong>, thanks for your order! Here is your bill summary:
                    </p>
                    
                    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px 14px; margin-bottom: 16px; font-size: 13px; color: #475569;">
                        Order Reference: <strong style="color: #0F172A; font-size: 14px;">#{order_id}</strong>
                    </div>

                    <!-- Items Table -->
                    <div style="width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 18px;">
                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; min-width: 280px;">
                            <thead>
                                <tr style="background-color: #F8FAFC; border-bottom: 2px solid #E2E8F0;">
                                    <th class="table-head-th" style="padding: 10px 8px; text-align: left; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; width: 42%;">Product</th>
                                    <th class="table-head-th" style="padding: 10px 6px; text-align: center; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; width: 14%;">Qty</th>
                                    <th class="table-head-th" style="padding: 10px 6px; text-align: right; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; width: 22%;">Price</th>
                                    <th class="table-head-th" style="padding: 10px 8px; text-align: right; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; width: 22%;">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {html_rows}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3" class="grand-total-label" style="padding: 14px 8px 10px 8px; text-align: right; font-weight: 600; font-size: 14px; color: #1E293B;">
                                        Grand total:
                                    </td>
                                    <td class="grand-total-val" style="padding: 14px 8px 10px 8px; text-align: right; font-weight: 700; font-size: 16px; color: #2563EB; white-space: nowrap;">
                                        {formatted_total}
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>

                    <!-- Footer -->
                    <div style="border-top: 1px solid #E5E7EB; padding-top: 14px; text-align: center;">
                        <p style="font-size: 12px; color: #9CA3AF; margin: 0 0 4px 0;">
                            Thank you for shopping with Online Cart!
                        </p>
                        <p style="font-size: 11px; color: #CBD5E1; margin: 0;">
                            This is an automated bill receipt. Please keep it for your records.
                        </p>
                    </div>

                </div>
            </td>
        </tr>
    </table>
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



