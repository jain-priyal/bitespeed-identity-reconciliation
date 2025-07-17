from sqlalchemy.orm import Session
from .models import Contact
from typing import List, Optional
from sqlalchemy import or_, and_
from collections import defaultdict


def identify_contact(
    db: Session, email: Optional[str] = None, phone_number: Optional[str] = None
):
    # Step 1: Fetch all contacts that match by email or phone
    matching_contacts = (
        db.query(Contact)
        .filter(or_(Contact.email == email, Contact.phoneNumber == phone_number))
        .all()
    )

    if not matching_contacts:
        # No match found: create new primary contact
        new_contact = Contact(
            email=email, phoneNumber=phone_number, linkPrecedence="primary"
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)

        return {
            "primaryContactId": new_contact.id,
            "emails": [email] if email else [],
            "phoneNumbers": [phone_number] if phone_number else [],
            "secondaryContactIds": [],
        }

    # Step 2: Traverse linked contacts to find the entire identity group
    all_contacts = []
    visited_ids = set()

    def dfs(contact: Contact):
        if contact.id in visited_ids:
            return
        visited_ids.add(contact.id)
        all_contacts.append(contact)
        if contact.linkedId:
            parent = db.query(Contact).filter(Contact.id == contact.linkedId).first()
            if parent:
                dfs(parent)
        linked = db.query(Contact).filter(Contact.linkedId == contact.id).all()
        for l in linked:
            dfs(l)

    for contact in matching_contacts:
        dfs(contact)

    # Step 3: Identify primary contact (earliest created)
    primary_contact = min(
        [c for c in all_contacts if c.linkPrecedence == "primary"],
        key=lambda c: c.createdAt,
    )

    # Step 4: Ensure all others are linked to the primary if not already
    for c in all_contacts:
        if c.id != primary_contact.id and (
            c.linkedId != primary_contact.id or c.linkPrecedence != "secondary"
        ):
            c.linkedId = primary_contact.id
            c.linkPrecedence = "secondary"
            db.add(c)
    db.commit()

    # Step 5: Prepare final merged response
    emails = set()
    phones = set()
    secondary_ids = []

    for c in all_contacts:
        if c.email:
            emails.add(c.email)
        if c.phoneNumber:
            phones.add(c.phoneNumber)
        if c.linkPrecedence == "secondary":
            secondary_ids.append(c.id)

    return {
        "primaryContactId": primary_contact.id,
        "emails": list(emails),
        "phoneNumbers": list(phones),
        "secondaryContactIds": secondary_ids,
    }
