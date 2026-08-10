"""Support & contact endpoints for Prompt Detective."""
from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, model_validator
from sqlalchemy.orm import Session

from ...core.config import settings
from ...database import get_db
from ...models.contact_message import ContactMessage
from ...services.email_service import (
    send_contact_acknowledgement_email,
    send_contact_notification_email,
)

router = APIRouter(prefix="/support", tags=["support"])


class ContactTopic(str, Enum):
    GETTING_STARTED = "getting_started"
    BILLING = "billing_and_payments"
    PRODUCT = "product_feedback"
    INTEGRATIONS = "integrations"
    ENTERPRISE = "enterprise_sales"
    SECURITY = "security_compliance"


CONTACT_TOPIC_DETAILS: dict[ContactTopic, dict[str, Any]] = {
    ContactTopic.GETTING_STARTED: {
        "title": "Getting started & onboarding",
        "description": "Account setup, verification, and first-analysis walkthroughs.",
        "faq_examples": [
            "I can't verify my email",
            "How do I upload my first analysis?",
            "Can you reset my onboarding tour?",
        ],
        "expected_response_hours": 12,
        "priority": "normal",
    },
    ContactTopic.BILLING: {
        "title": "Billing & payments",
        "description": "Invoices, GST details, refunds, and plan charges.",
        "faq_examples": [
            "I was charged twice",
            "Can you share a GST invoice?",
            "How do I update my payment method?",
        ],
        "expected_response_hours": 8,
        "priority": "high",
    },
    ContactTopic.PRODUCT: {
        "title": "Product ideas & feedback",
        "description": "Feature requests and quality improvements for Prompt Detective.",
        "faq_examples": [
            "I'd like to analyse longer videos",
            "Can you export prompts to Notion?",
            "Will you support Stable Diffusion XL?",
        ],
        "expected_response_hours": 24,
        "priority": "normal",
    },
    ContactTopic.INTEGRATIONS: {
        "title": "Developer integrations",
        "description": "API keys, webhooks, and third-party integrations.",
        "faq_examples": [
            "How can I increase my API quota?",
            "Do you have a webhook for completed analyses?",
            "Is there a Postman collection?",
        ],
        "expected_response_hours": 12,
        "priority": "high",
    },
    ContactTopic.ENTERPRISE: {
        "title": "Enterprise & partnerships",
        "description": "Dedicated plans for teams, agencies, and resellers.",
        "faq_examples": [
            "Do you support procurement via PO?",
            "Can you provide a security review?",
            "Do you have a white-label offering?",
        ],
        "expected_response_hours": 6,
        "priority": "urgent",
    },
    ContactTopic.SECURITY: {
        "title": "Security & compliance",
        "description": "Responsible disclosure, data retention, and legal enquiries.",
        "faq_examples": [
            "How long do you store uploaded files?",
            "I'd like to report a vulnerability",
            "Is Prompt Detective SOC 2 compliant?",
        ],
        "expected_response_hours": 4,
        "priority": "urgent",
    },
}


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    topic: ContactTopic
    selected_question: str | None = Field(
        default=None,
        description="Pre-fed question chosen by the user."
    )
    message: str | None = Field(
        default=None,
        max_length=2000,
        description="Additional context provided by the user."
    )
    account_stage: str | None = Field(
        default=None,
        max_length=120,
        description="Where the user is in their journey (e.g., evaluating, active, team admin)."
    )
    consent: bool = Field(
        True,
        description="User consent to be contacted via email."
    )

    @model_validator(mode="after")
    def ensure_payload_has_substance(self) -> "ContactRequest":
        if not (self.message and self.message.strip()) and not (self.selected_question and self.selected_question.strip()):
            raise ValueError("Please provide a short message or choose one of the suggested questions.")
        return self


class ContactResponse(BaseModel):
    success: bool
    message: str
    reference_id: int


@router.get("/contact/topics")
async def list_contact_topics() -> dict[str, Any]:
    """Expose the curated help topics so the frontend can render pre-fed options."""
    return {
        "topics": [
            {
                "key": topic.value,
                "title": meta["title"],
                "description": meta["description"],
                "faq_examples": meta["faq_examples"],
                "expected_response_hours": meta["expected_response_hours"],
            }
            for topic, meta in CONTACT_TOPIC_DETAILS.items()
        ]
    }


@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact_request(
    payload: ContactRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ContactResponse:
    """Persist a contact message and fan out internal + customer notifications."""

    topic_meta = CONTACT_TOPIC_DETAILS.get(payload.topic)
    if not topic_meta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported topic")

    subject = f"Support request · {topic_meta['title']}"

    additional_metadata = {
        "Journey stage": payload.account_stage or "Not provided",
        "Consent to contact": "Yes" if payload.consent else "No",
    }

    message_body = payload.message.strip() if payload.message else ""

    contact_record = ContactMessage(
        name=payload.name.strip(),
        email=payload.email.lower(),
        subject=subject,
        message=message_body or payload.selected_question or "",
        category=payload.topic.value,
        status="new",
        priority=topic_meta["priority"],
    )

    db.add(contact_record)
    db.commit()
    db.refresh(contact_record)

    admin_email = settings.SUPPORT_EMAIL or settings.ADMIN_EMAIL or settings.EMAIL_FROM_ADDRESS

    background_tasks.add_task(
        send_contact_notification_email,
        admin_email=admin_email,
        contact_name=payload.name.strip(),
        contact_email=payload.email.lower(),
        topic_label=topic_meta["title"],
        topic_key=payload.topic.value,
        message_body=message_body,
        selected_question=payload.selected_question,
        metadata=additional_metadata,
    )

    if payload.consent:
        background_tasks.add_task(
            send_contact_acknowledgement_email,
            contact_email=payload.email,
            contact_name=payload.name.strip(),
            topic_label=topic_meta["title"],
            expected_response_hours=topic_meta["expected_response_hours"],
        )

    return ContactResponse(
        success=True,
        message="Thanks for reaching out. Our team will respond shortly.",
        reference_id=contact_record.id,
    )
