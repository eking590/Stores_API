import os 
from typing import List 
from requests import Response, post 
from libs.strings import gettext







class MailGunException(Exception):
    def __init__(self, message: str): 
        super().__init__(message)
        
        
class Mailgun:
    MAILGUN_DOMAIN="sandboxa04f22ea41164345a42337b1ab775692.mailgun.org"
    MAILGUN_API_KEY="aee281ca9a297cea890dc1a55f27dfb9"
    MAILGUN_DOMAIN_NAME = "sandbox6800dfbae7504d2eacf1ecd95c93c58e"
    #MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    #MAILGUN_API_KEY = os.environ.get(" MAILGUN_API_KEY")
    
    FROM_TITLE = "Stores REST API"
    FROM_EMAIL = "postmaster@sandbox6800dfbae7504d2eacf1ecd95c93c58e.mailgun.org"

    @classmethod
    def send_email(cls, email : List[str], subject: str, text: str, html: str) -> Response: 
            if cls.MAILGUN_API_KEY is None: 
                raise MailGunException(gettext("mailgun_failed_load_api_key"))
            
            if cls.MAILGUN_DOMAIN is None: 
                raise MailGunException(gettext("mailgun_failed_load_domain"))
            
            
            response = post(
                f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
                auth=("api", cls.MAILGUN_API_KEY), 
                data={
                    "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                    "to": email,
                    "subject": subject,
                    "text": text,
                    "html": html, 
                    
                }, 
            )
            if response.status_code != 200: 
                raise MailGunException(gettext("mailgun_error_send_email"))
            
            return response 