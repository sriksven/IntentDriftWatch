import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formatdate

def _env_bool(name, default=False):
    v = os.getenv(name, str(int(default)))
    return str(v).lower() in {"1", "true", "yes", "y"}

def send_mail(subject: str, body: str):
    host = os.getenv("MAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("MAIL_PORT", "587"))
    use_tls = _env_bool("MAIL_USE_TLS", True)
    user = os.getenv("MAIL_USERNAME")
    pwd = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM", user)
    mail_to = [x.strip() for x in os.getenv("MAIL_TO", "").split(",") if x.strip()]
    if not mail_to:
        print("MAIL_TO not set. Skipping email.")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = ", ".join(mail_to)
    msg["Date"] = formatdate(localtime=True)

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(host, port) as s:
            if use_tls:
                s.starttls(context=ctx)
            s.login(user, pwd)
            s.sendmail(mail_from, mail_to, msg.as_string())
        print(f"✅ Email sent to {mail_to}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
