import re
from src.services.core.exceptions import InvalidEmailFormat, InvalidEmailDomain


def validate_email_domain(email: str) -> bool:
    valid_domains = ['ru', 'su', 'рф', 'дети', 'москва', 'рус']
    domain = email.split('.')[-1]
    if domain in valid_domains:
        return True
    else:
        raise InvalidEmailDomain(email)