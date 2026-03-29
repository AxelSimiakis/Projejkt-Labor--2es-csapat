import smtplib
from email.message import EmailMessage


# =========================================
# SMTP BEÁLLÍTÁSOK
# =========================================
# Gmail: potkocsipont@gmail.com
# Jelszo: Potkocsipont1234!!
# App jelsó: yubb kiri xurd oixk    --> Kódban nem kell szóköz

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "potkocsipont@gmail.com"
SMTP_PASSWORD = "yubbkirixurdoixk"
SENDER_EMAIL = SMTP_USER


PERIOD_TO_HU = {
    "morning": "Délelőtt",
    "afternoon": "Délután",
    "full_day": "Egész nap",
}


def send_booking_confirmation_email(
    recipient_email: str,
    recipient_name: str,
    bookings: list[dict]
):
    total_price = sum(item["price"] for item in bookings)

    # ===== SZÖVEGES VERZIÓ =====
    text_lines = []
    text_lines.append(f"Kedves {recipient_name}!")
    text_lines.append("")
    text_lines.append("A kosárban jóváhagyott foglalásai sikeresen rögzítésre kerültek.")
    text_lines.append("")
    text_lines.append("Foglalás részletei:")
    text_lines.append("")

    for index, item in enumerate(bookings, start=1):
        text_lines.append(f"{index}. utánfutó: {item['trailer_name']}")
        text_lines.append(f"   Dátum: {item['booking_date']}")
        text_lines.append(f"   Időszak: {PERIOD_TO_HU.get(item['period'], item['period'])}")
        text_lines.append(f"   Ár: {item['price']} Ft")
        text_lines.append("")

    text_lines.append(f"Összesen: {total_price} Ft")
    text_lines.append("")
    text_lines.append("Köszönjük a foglalást!")
    text_lines.append("PótkocsiPont")

    text_body = "\n".join(text_lines)

    # ===== HTML TÁBLÁZAT SOROK =====
    rows_html = ""
    for item in bookings:
        rows_html += f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">{item['trailer_name']}</td>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">{item['booking_date']}</td>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">{PERIOD_TO_HU.get(item['period'], item['period'])}</td>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;text-align:right;">{item['price']} Ft</td>
        </tr>
        """

    # ===== HTML EMAIL =====
    html_body = f"""
    <html>
    <body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial,Helvetica,sans-serif;color:#111827;">
        <div style="max-width:700px;margin:30px auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">

            <div style="background:linear-gradient(90deg,#16a34a,#15803d);padding:24px 30px;">
                <h1 style="margin:0;color:white;font-size:24px;">PótkocsiPont</h1>
                <p style="margin:8px 0 0 0;color:#dcfce7;font-size:14px;">
                    Foglalás visszaigazolás
                </p>
            </div>

            <div style="padding:30px;">
                <p style="margin-top:0;font-size:16px;">
                    Kedves <strong>{recipient_name}</strong>!
                </p>

                <p style="font-size:15px;line-height:1.6;color:#374151;">
                    A kosárban jóváhagyott foglalásai sikeresen rögzítésre kerültek.
                    Az alábbi táblázatban láthatja a foglalás részleteit.
                </p>

                <div style="margin:24px 0 10px 0;">
                    <h2 style="margin:0;font-size:18px;color:#111827;">Foglalás részletei</h2>
                </div>

                <table style="width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;">
                    <thead>
                        <tr style="background-color:#f9fafb;">
                            <th style="padding:12px;text-align:left;border-bottom:2px solid #d1d5db;">Utánfutó</th>
                            <th style="padding:12px;text-align:left;border-bottom:2px solid #d1d5db;">Dátum</th>
                            <th style="padding:12px;text-align:left;border-bottom:2px solid #d1d5db;">Időszak</th>
                            <th style="padding:12px;text-align:right;border-bottom:2px solid #d1d5db;">Ár</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>

                <div style="margin-top:24px;padding:18px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;">
                    <p style="margin:0;font-size:16px;color:#166534;">
                        <strong>Végösszeg: {total_price} Ft</strong>
                    </p>
                </div>

                <p style="margin-top:28px;font-size:15px;color:#374151;line-height:1.6;">
                    Köszönjük a foglalást!<br>
                    <strong>PótkocsiPont</strong>
                </p>
            </div>

            <div style="padding:16px 30px;background:#f9fafb;border-top:1px solid #e5e7eb;">
                <p style="margin:0;font-size:12px;color:#6b7280;">
                    Ez egy automatikusan generált visszaigazoló email.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = "Foglalás visszaigazolás - PótkocsiPont"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print("EMAIL HIBA:", e)
    