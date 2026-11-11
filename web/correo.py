"""Envío de emails (recuperar contraseña). Usa cualquier servicio SMTP: Brevo (300 emails/día gratis), Mailgun,
Amazon SES, el de tu dominio… Ajustes en web/.env: SMTP_HOST, SMTP_PORT, SMTP_USUARIO, SMTP_CLAVE, SMTP_DE.
Sin SMTP configurado (desarrollo), el email se escribe en web/logs/emails.log en vez de enviarse."""
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

AQUI = os.path.dirname(os.path.abspath(__file__))


def configurado():
    return bool(os.environ.get("SMTP_HOST"))


def enviar(para, asunto, texto):
    remite = os.environ.get("SMTP_DE", "no-responder@localhost")
    m = EmailMessage()
    m["From"] = formataddr(("Caso Recortado Studio", remite))
    m["To"] = para
    m["Subject"] = asunto
    m.set_content(texto)
    if not configurado():
        from entorno import datos
        os.makedirs(datos("logs"), exist_ok=True)
        with open(datos("logs", "emails.log"), "a", encoding="utf-8") as f:
            f.write(f"\n--- Para: {para}\nAsunto: {asunto}\n{texto}\n")
        return False
    puerto = int(os.environ.get("SMTP_PORT", "587"))
    ctx = ssl.create_default_context()
    if puerto == 465:
        s = smtplib.SMTP_SSL(os.environ["SMTP_HOST"], puerto, context=ctx, timeout=20)
    else:
        s = smtplib.SMTP(os.environ["SMTP_HOST"], puerto, timeout=20)
        s.starttls(context=ctx)
    with s:
        if os.environ.get("SMTP_USUARIO"):
            s.login(os.environ["SMTP_USUARIO"], os.environ.get("SMTP_CLAVE", ""))
        s.send_message(m)
    return True
