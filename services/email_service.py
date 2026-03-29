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
    total_price = sum(item.get("price") for item in bookings)
    total_deposit = sum(item.get("deposit", 0) for item in bookings)
    grand_total = total_price + total_deposit

    # ===== SZÖVEGES VERZIÓ =====
    text_lines = []
    text_lines.append(f"Kedves {recipient_name}!")
    text_lines.append("")
    text_lines.append("A kosárban jóváhagyott foglalásai sikeresen rögzítésre kerültek. Az alábbi táblázatban láthatja a foglalás részleteit.")
    text_lines.append("")
    text_lines.append("Foglalás részletei:")
    text_lines.append("")

    for index, item in enumerate(bookings, start=1):
        text_lines.append(f"{index}. utánfutó: {item['trailer_name']}")
        text_lines.append(f"   Dátum: {item['booking_date']}")
        text_lines.append(f"   Időszak: {PERIOD_TO_HU.get(item['period'], item['period'])}")
        text_lines.append(f"   Ár: {item.get('price')} Ft")
        text_lines.append(f"   Kaució: {item.get('deposit', 0)} Ft")
        text_lines.append("")

    text_lines.append(f"Bérlés összesen: {total_price} Ft")
    text_lines.append(f"Kaució összesen: {total_deposit} Ft")
    text_lines.append(f"Fizetendő összesen: {grand_total} Ft")
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
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;text-align:right;">{item.get('price')} Ft</td>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;text-align:right;">{item.get('deposit', 0)} Ft</td>
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
                </p>

                <h2 style="margin-top:20px;font-size:18px;">Foglalás részletei</h2>

                <table style="width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;">
                    <thead>
                        <tr style="background-color:#f9fafb;">
                            <th style="padding:12px;text-align:left;">Utánfutó</th>
                            <th style="padding:12px;text-align:left;">Dátum</th>
                            <th style="padding:12px;text-align:left;">Időszak</th>
                            <th style="padding:12px;text-align:right;">Ár</th>
                            <th style="padding:12px;text-align:right;">Kaució</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>

                <div style="margin-top:24px;padding:18px;background:#f0fdf4;border-radius:10px;">
                    <p><strong>Bérlés: {total_price} Ft</strong></p>
                    <p><strong>Kaució: {total_deposit} Ft</strong></p>
                    <p><strong>Fizetendő: {grand_total} Ft</strong></p>
                </div>

                <p style="margin-top:28px;">
                    Köszönjük a foglalást!<br>
                    <strong>PótkocsiPont</strong>
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

def send_booking_cancellation_email(
    recipient_email: str,
    recipient_name: str,
    trailer_name: str,
    booking_date,
    period: str
):
    from email.message import EmailMessage

    period_hu = PERIOD_TO_HU.get(period, period)

    # ===== TEXT =====
    text_body = f"""
Kedves {recipient_name}!

Az alábbi foglalása törlésre került:

Utánfutó: {trailer_name}
Dátum: {booking_date}
Időszak: {period_hu}

PótkocsiPont
"""

    # ===== HTML =====
    html_body = f"""
    <html>
    <body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial,Helvetica,sans-serif;color:#111827;">
        <div style="max-width:700px;margin:30px auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">

            <!-- 🔴 PIROS HEADER -->
            <div style="background:linear-gradient(90deg,#dc2626,#991b1b);padding:24px 30px;">
                <h1 style="margin:0;color:white;font-size:24px;">PótkocsiPont</h1>
                <p style="margin:8px 0 0 0;color:#fecaca;font-size:14px;">
                    Foglalás lemondva
                </p>
            </div>

            <div style="padding:30px;">
                <p style="margin-top:0;font-size:16px;">
                    Kedves <strong>{recipient_name}</strong>!
                </p>

                <p style="font-size:15px;line-height:1.6;color:#374151;">
                    Az alábbi foglalása sikeresen törlésre került:
                </p>

                <div style="margin:24px 0 10px 0;">
                    <h2 style="margin:0;font-size:18px;color:#111827;">Törölt foglalás</h2>
                </div>

                <table style="width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;">
                    <tbody>
                        <tr>
                            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">Utánfutó</td>
                            <td style="padding:12px;border-bottom:1px solid #e5e7eb;"><strong>{trailer_name}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">Dátum</td>
                            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">{booking_date}</td>
                        </tr>
                        <tr>
                            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">Időszak</td>
                            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">{period_hu}</td>
                        </tr>
                    </tbody>
                </table>

                <div style="margin-top:24px;padding:18px;background:#fef2f2;border:1px solid #fecaca;border-radius:10px;">
                    <p style="margin:0;font-size:15px;color:#991b1b;">
                        A foglalás törlésre került a rendszerben.
                    </p>
                </div>

                <p style="margin-top:28px;font-size:15px;color:#374151;">
                    Üdv,<br>
                    <strong>PótkocsiPont</strong>
                </p>
            </div>

            <div style="padding:16px 30px;background:#f9fafb;border-top:1px solid #e5e7eb;">
                <p style="margin:0;font-size:12px;color:#6b7280;">
                    Ez egy automatikusan generált email.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = "Foglalás lemondva - PótkocsiPont"
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
        print("EMAIL HIBA (törlés):", e)

def send_registration_email(email, name, password):
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = "Sikeres regisztráció - PótkocsiPont"
    msg["From"] = SENDER_EMAIL
    msg["To"] = email

    text = f"""
Kedves {name}!

Sikeresen regisztráltunk Önt a PótkocsiPont rendszerébe.

Bejelentkezési adatok:
Email: {email}
Jelszó: {password}

Kérjük, hogy első belépés után az "Adataim" menüpontban változtassa meg a jelszavát!

Üdv,
PótkocsiPont
"""

    html = f"""
    <html>
    <body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial;">
        <div style="max-width:600px;margin:30px auto;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">

            <div style="background:linear-gradient(90deg,#2563eb,#1d4ed8);padding:20px;">
                <h1 style="color:white;margin:0;">PótkocsiPont</h1>
                <p style="color:#dbeafe;margin:5px 0 0 0;">Sikeres regisztráció</p>
            </div>

            <div style="padding:25px;">
                <p>Kedves <strong>{name}</strong>!</p>

                <p>Sikeresen regisztráltuk Önt rendszerünkbe.</p>

                <div style="margin:20px 0;padding:15px;background:#eff6ff;border-radius:8px;">
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Jelszó:</strong> {password}</p>
                </div>

                <p style="color:#dc2626;">
                    Kérjük, hogy első belépés után változtassa meg jelszavát!
                </p>

                <p>Üdv,<br><strong>PótkocsiPont</strong></p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("EMAIL HIBA (reg):", e)