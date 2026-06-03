"""Seed the database with sample call data."""

from __future__ import annotations

import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import select

from app.core.db import async_session
from app.modules.calls.schema import Call, CallLabel, CallStatus

NAMES = [
    "Sarah Mitchell",
    "James Harrington",
    "María García",
    "Derek Owens",
    "Klaus Bauer",
    "Priya Sharma",
    "Étienne Dupont",
    "Rachel Torres",
    "Bruno Almeida",
    "Amanda Chen",
    "Lorenzo Ricci",
    "Yuki Tanaka",
    "Carlos López",
    "Elena Ruiz",
    "Ana Martínez",
    "Juan Rodríguez",
    "Laura Sánchez",
    "Pedro Hernández",
    "Sofia Díaz",
    "Miguel Torres",
    "Isabella Moreno",
    "Andrés Romero",
    "Camille Bernard",
    "Klaus Weber",
    "Mei Lin",
    "Omar Hassan",
    "Fatima Al-Rashid",
    "Luca Ferrari",
    "Ingrid Larsson",
    "Raj Patel",
    "Amara Diallo",
    "Noah Williams",
    "Emma Johnson",
    "Oliver Smith",
    "Ava Brown",
    "Liam Davis",
    None,
    None,
    None,
]

PHONES = [
    "+1 (555) 201-4832",
    "+44 20 7946 0812",
    "+34 91 123 4567",
    "+1 (555) 873-0021",
    "+49 30 56789 123",
    "+1 (555) 334-9900",
    "+33 1 42 68 53 00",
    "+1 (555) 762-4410",
    "+55 11 9 8765 4321",
    "+1 (555) 489-2277",
    "+39 02 1234 5678",
    "+1 (555) 901-3344",
    "+52 55 2345 6789",
    "+34 623 456 789",
    "+1 555 234 5678",
    "+49 30 9876 5432",
    "+44 20 1234 5678",
    "+33 1 42 68 00 01",
    "+81 3 1234 5678",
    "+61 2 9876 5432",
    "+27 11 234 5678",
    "+91 98765 43210",
    "+86 10 1234 5678",
    "+7 495 123 4567",
    "+55 21 9 1234 5678",
    "+34 612 345 678",
    "+1 (555) 123-9999",
]

TRANSCRIPTS = [
    "Agent: Thank you for calling, how can I help you today?\nCaller: Hi, I'm interested in upgrading our account to the enterprise tier.\nAgent: Absolutely, I can walk you through our Enterprise options right now.",
    "Agent: Support line, how can I assist?\nCaller: My recordings from yesterday aren't showing up in the dashboard.\nAgent: Let me look into that for you. Can you tell me which date range you're checking?",
    "Agent: Good morning, how can I help?\nCaller: I want to schedule a demo for my team of 8 people.\nAgent: I'd be happy to set that up. What days work best for your group?",
    "Agent: Thank you for calling back. I see you had a billing concern previously.\nCaller: Yes, I wanted to confirm the credit showed up. It did — thanks for handling that so fast.\nAgent: Wonderful, glad we could resolve that for you.",
    "Agent: How can I help you today?\nCaller: I've been charged incorrectly for three months now. I'm very unhappy.\nAgent: I sincerely apologize. Let me pull up your account right now and make this right.",
    "Agent: How may I assist you?\nCaller: We run a marketing agency and I'm wondering if we can white-label your platform.\nAgent: Absolutely, we have a reseller program many agencies use. Let me share the details.",
    "Agent: Hello? Can you hear me?\nCaller: Hello? I can't hear anything.\nAgent: Hello? Is anyone there?\n[Disconnected]",
    "Agent: We have 4 new people starting Monday and I'd like to get them onboarded.\nCaller: Perfect, I can schedule an onboarding session for the whole team.\nAgent: Thursday at 2pm works great. I'll send the calendar invite now.",
    "Agent: Good afternoon, Voico support. How can I help?\nCaller: I'd like to cancel my subscription. The pricing has gotten too high for us.\nAgent: I understand. Before we proceed, let me share some alternative plan options that might work better.",
    "Agent: Thank you for calling. How may I assist?\nCaller: I need help setting up the API integration with our CRM system.\nAgent: Of course. Which CRM are you using? We have native integrations for most major platforms.",
    "Agent: How can I help you today?\nCaller: I'm calling to follow up on the refund I requested two weeks ago.\nAgent: Let me check the status. I can see it was approved and should appear in 3-5 business days.",
    "Agent: Support line, this is Alex.\nCaller: Hi, we're evaluating your platform for our call center of 50 agents. Can we get a custom quote?\nAgent: Absolutely, I'll connect you with our enterprise sales team right away.",
    "Agent: Good morning, how can I help?\nCaller: The mobile app keeps crashing when I try to view call recordings.\nAgent: I'm sorry about that. Can you tell me what device and OS version you're using?",
    "Agent: How may I assist you today?\nCaller: I want to add two more users to our account.\nAgent: Sure, I can do that right now. Can you confirm the email addresses for the new users?",
]

SUMMARIES = [
    "Caller inquired about upgrading to the enterprise tier. Agent offered to walk them through available options.",
    "Caller reported that call recordings from the previous day were missing from the dashboard. Agent began investigating the issue.",
    "Caller requested a product demo for a team of 8. Agent offered to schedule it based on the team's availability.",
    "Caller followed up on a previous billing concern and confirmed the credit was applied correctly. Issue resolved to the caller's satisfaction.",
    "Caller expressed frustration over three months of incorrect charges. Agent apologized and began reviewing the account to resolve the issue.",
    "Caller asked about white-labeling the platform for their marketing agency. Agent provided details on the reseller program.",
    "Call experienced an audio failure and disconnected before any issue could be addressed.",
    "Caller requested onboarding for four new team members starting Monday. Agent scheduled a session for Thursday at 2pm.",
    "Caller considered canceling their subscription due to pricing. Agent offered to present alternative plan options before proceeding.",
    "Caller needed assistance setting up a CRM API integration. Agent began guiding them through the available native integrations.",
    "Caller followed up on a refund request from two weeks prior. Agent confirmed the refund was approved and would arrive within 3–5 business days.",
    "Caller's company is evaluating the platform for a 50-agent call center and requested a custom quote. Agent escalated to the enterprise sales team.",
    "Caller reported the mobile app crashing when viewing call recordings. Agent began troubleshooting by asking about the device and OS version.",
    "Caller requested to add two new users to their account. Agent proceeded to collect the new users' email addresses.",
]

LABELS = list(CallLabel)
STATUSES_WEIGHTED = (
    [CallStatus.success] * 60 + [CallStatus.failed] * 25 + [CallStatus.in_progress] * 15
)


def make_call(minutes_ago: int) -> Call:
    status = random.choice(STATUSES_WEIGHTED)
    started_at = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)

    if status == CallStatus.in_progress:
        ended_at = None
        duration = None
        transcript = None
        summary = None
        label = None
    else:
        duration = random.randint(30, 720)
        ended_at = started_at + timedelta(seconds=duration)
        idx = random.randrange(len(TRANSCRIPTS))
        transcript = TRANSCRIPTS[idx]
        summary = SUMMARIES[idx]
        label = random.choice(LABELS)

    return Call(
        id=uuid.uuid4(),
        phone_number=random.choice(PHONES),
        caller_name=random.choice(NAMES),
        duration_seconds=duration,
        status=status,
        label=label,
        summary=summary,
        raw_transcript=transcript,
        started_at=started_at.replace(tzinfo=None),
        ended_at=ended_at.replace(tzinfo=None) if ended_at else None,
        created_at=started_at.replace(tzinfo=None),
        updated_at=started_at.replace(tzinfo=None),
    )


async def seed() -> None:
    async with async_session() as session:
        existing = (await session.exec(select(Call))).first()
        if existing:
            print("Database already has data — skipping seed.")
            print("To re-seed, delete db.sqlite3 and run alembic upgrade head first.")
            return

        random.seed(42)

        # Spread 100 calls over the last 7 days
        time_slots = sorted(
            [random.randint(1, 60 * 24 * 7) for _ in range(100)],
        )

        calls = [make_call(minutes_ago) for minutes_ago in time_slots]

        for call in calls:
            session.add(call)

        await session.commit()

        success = sum(1 for c in calls if c.status == CallStatus.success)
        failed = sum(1 for c in calls if c.status == CallStatus.failed)
        in_progress = sum(1 for c in calls if c.status == CallStatus.in_progress)
        print(
            f"Seeded {len(calls)} calls: {success} success, {failed} failed, {in_progress} in_progress."
        )


if __name__ == "__main__":
    asyncio.run(seed())
