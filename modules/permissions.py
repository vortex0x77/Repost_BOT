from typing import List, Optional

from modules.config import ADMIN_IDS
from modules.database import is_contact_authorized, get_authorized_contacts

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_authorized(username: Optional[str]) -> bool:
    if not username:
        return False
    
    clean_username = username.lstrip('@')
    return is_contact_authorized(clean_username)

def get_all_authorized_contacts() -> List[str]:
    return get_authorized_contacts()

def add_contact(contact: str) -> bool:
    clean_contact = contact.lstrip('@')
    from modules.database import add_authorized_contact
    return add_authorized_contact(clean_contact)

def remove_contact(contact: str) -> bool:
    clean_contact = contact.lstrip('@')
    from modules.database import remove_authorized_contact
    return remove_authorized_contact(clean_contact)
