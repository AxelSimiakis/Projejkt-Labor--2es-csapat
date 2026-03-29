import smtplib

try:
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    server.ehlo()
    server.starttls()
    server.ehlo()
    print("CSATLAKOZVA OK")
    server.quit()
except Exception as e:
    print("HIBA:", e)