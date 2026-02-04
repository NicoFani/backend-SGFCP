"""Utilidades para envío de email vía Brevo (Sendinblue)."""
import base64
import os
from typing import List, Dict, Tuple

import requests


def _encode_file_base64(file_path: str) -> str:
    with open(file_path, "rb") as file_handle:
        return base64.b64encode(file_handle.read()).decode("utf-8")


def send_brevo_email(
    api_key: str,
    sender_email: str,
    sender_name: str,
    recipients: List[str],
    subject: str,
    html_content: str,
    attachment_paths: List[str] | None = None,
) -> Tuple[bool, str]:
    """Enviar email con Brevo. Devuelve (success, message)."""
    if not api_key:
        return False, "BREVO_API_KEY no configurada"
    if not sender_email:
        return False, "BREVO_SENDER_EMAIL no configurado"
    if not recipients:
        return False, "No hay destinatarios configurados"

    attachments: List[Dict[str, str]] = []
    for path in attachment_paths or []:
        if not os.path.exists(path):
            return False, f"Adjunto no encontrado: {path}"
        attachments.append({
            "name": os.path.basename(path),
            "content": _encode_file_base64(path),
        })

    payload = {
        "sender": {"email": sender_email, "name": sender_name or sender_email},
        "to": [{"email": email.strip()} for email in recipients],
        "subject": subject,
        "htmlContent": html_content,
        "attachment": attachments,
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers=headers,
        timeout=30,
    )

    if response.status_code in (200, 201, 202):
        return True, "Email enviado"

    return False, f"Error Brevo {response.status_code}: {response.text}"