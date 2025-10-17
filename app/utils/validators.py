import re

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email.strip()) is not None

def validate_name(name: str) -> bool:
    """Validar que el nombre solo contenga letras y espacios"""
    return re.match(r'^[a-zA-Z\s]+$', name.strip()) is not None