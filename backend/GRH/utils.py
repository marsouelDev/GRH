import urllib.request
import urllib.error
import json
import os
import logging

logger = logging.getLogger(__name__)

def envoyer_email_brevo(destinataire_email, destinataire_nom, sujet, message_html, message_texte=""):
    """
    Envoie un email via l'API HTTP de Brevo (contourne le blocage des ports SMTP de Render).
    """
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.getenv("BREVO_API_KEY")
    expediteur_email = os.getenv("DEFAULT_FROM_EMAIL")

    if not api_key:
        logger.error(" BREVO_API_KEY manquante dans les variables d'environnement Render.")
        return False

    payload = {
        "sender": {"name": "RH_Manager", "email": expediteur_email},
        "to": [{"email": destinataire_email, "name": destinataire_nom}],
        "subject": sujet,
        "htmlContent": message_html,
        "textContent": message_texte
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    try:
        # Timeout de 10 secondes pour éviter de bloquer le worker Gunicorn
        with urllib.request.urlopen(req, timeout=10) as response:
            logger.info(f" Email envoyé avec succès à {destinataire_email} via API Brevo.")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f" Erreur HTTP Brevo pour {destinataire_email} : {e.code} - {error_body}")
        return False
    except Exception as e:
        logger.error(f" Erreur réseau envoi email Brevo pour {destinataire_email} : {e}")
        return False