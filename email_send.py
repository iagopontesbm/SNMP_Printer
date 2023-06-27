import os
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

SUBJECT = f"Status impressoras - {datetime.today().strftime('%d/%m/%Y')}"  # Titulo do email
SENDER_EMAIL = os.getenv("EMAIL_SENDER")  # Remetente do email
RECEIVER_EMAIL = ", ".join([os.getenv("RECEIVER_EMAIL")])  # Lista de destinatários
SMTP_ADDRESS = os.getenv("SMTP_ADDRESS")  # Endereço SMTP
SMTP_PORT = os.getenv("SMTP_PORT")  # Porta SMTP
PASSWORD = os.getenv("EMAIL_PASSWORD")  # Senha email, caso seja do GMAIL é necessário cria a senha do app


def send_email(email_body: str):
    """Informe o texto que vai compor o corpo do email."""
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = SUBJECT
    # message["Bcc"] = RECEIVER_EMAIL  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(email_body, "plain"))

    # Add attachment to message and convert message to string
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_ADDRESS, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
