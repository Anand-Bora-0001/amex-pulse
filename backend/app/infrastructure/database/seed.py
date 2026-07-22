"""
AmEx Pulse — Database Seed Data
================================
Generates realistic synthetic data for 50 American Express card members
with diverse profiles, journeys, and interaction histories.
"""

import json
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    CHANNEL_METADATA,
    ChannelType,
    CardType,
    JourneyType,
    JourneyStatus,
    EventType,
    JOURNEY_STEPS,
    ActionType,
    CasePriority,
    CaseStatus,
)
from app.core.security import hash_password
from app.infrastructure.database.models import (
    User,
    Customer,
    CustomerIdentifier,
    Channel,
    Journey,
    JourneyStep,
    Session,
    Event,
    Prediction,
    Recommendation,
    SupportCase,
    ActivityLog,
)


# ── Synthetic Customer Data ──────────────────────────────────────
CUSTOMER_PROFILES = [
    {"first_name": "Sarah", "last_name": "Johnson", "card_type": "platinum", "member_since": "2018-03-15", "scenario": "frustrated_activation"},
    {"first_name": "Marcus", "last_name": "Johnson", "card_type": "gold", "member_since": "2020-06-22", "scenario": "happy_rewards"},
    {"first_name": "Priya", "last_name": "Sharma", "card_type": "platinum", "member_since": "2016-11-08", "scenario": "churn_risk"},
    {"first_name": "David", "last_name": "Miller", "card_type": "green", "member_since": "2022-01-30", "scenario": "dispute_journey"},
    {"first_name": "Emily", "last_name": "Rodriguez", "card_type": "gold", "member_since": "2019-09-14", "scenario": "credit_limit"},
    {"first_name": "James", "last_name": "O'Brien", "card_type": "platinum", "member_since": "2015-04-20", "scenario": "travel_support"},
    {"first_name": "Aisha", "last_name": "Patel", "card_type": "blue", "member_since": "2023-08-05", "scenario": "new_member"},
    {"first_name": "Robert", "last_name": "Kim", "card_type": "gold", "member_since": "2017-12-01", "scenario": "payment_issue"},
    {"first_name": "Maria", "last_name": "Garcia", "card_type": "platinum", "member_since": "2014-07-19", "scenario": "loyal_customer"},
    {"first_name": "Thomas", "last_name": "Anderson", "card_type": "green", "member_since": "2021-05-11", "scenario": "general_inquiry"},
    {"first_name": "Lisa", "last_name": "Wang", "card_type": "gold", "member_since": "2019-02-28", "scenario": "frustrated_activation"},
    {"first_name": "Daniel", "last_name": "Martinez", "card_type": "blue", "member_since": "2023-11-15", "scenario": "new_member"},
    {"first_name": "Jennifer", "last_name": "Taylor", "card_type": "platinum", "member_since": "2016-08-03", "scenario": "churn_risk"},
    {"first_name": "Michael", "last_name": "Brown", "card_type": "gold", "member_since": "2020-03-17", "scenario": "dispute_journey"},
    {"first_name": "Sophia", "last_name": "Lee", "card_type": "green", "member_since": "2022-07-22", "scenario": "happy_rewards"},
    {"first_name": "Christopher", "last_name": "Davis", "card_type": "platinum", "member_since": "2015-01-09", "scenario": "loyal_customer"},
    {"first_name": "Olivia", "last_name": "Wilson", "card_type": "gold", "member_since": "2018-10-25", "scenario": "credit_limit"},
    {"first_name": "Andrew", "last_name": "Moore", "card_type": "blue", "member_since": "2024-02-14", "scenario": "new_member"},
    {"first_name": "Emma", "last_name": "Jackson", "card_type": "platinum", "member_since": "2017-06-30", "scenario": "travel_support"},
    {"first_name": "William", "last_name": "White", "card_type": "green", "member_since": "2021-09-08", "scenario": "payment_issue"},
    {"first_name": "Ava", "last_name": "Harris", "card_type": "gold", "member_since": "2019-04-12", "scenario": "general_inquiry"},
    {"first_name": "Alexander", "last_name": "Thompson", "card_type": "platinum", "member_since": "2016-02-20", "scenario": "frustrated_activation"},
    {"first_name": "Isabella", "last_name": "Clark", "card_type": "blue", "member_since": "2023-05-07", "scenario": "happy_rewards"},
    {"first_name": "Ryan", "last_name": "Lewis", "card_type": "gold", "member_since": "2020-11-30", "scenario": "dispute_journey"},
    {"first_name": "Mia", "last_name": "Robinson", "card_type": "green", "member_since": "2022-04-18", "scenario": "credit_limit"},
    {"first_name": "Nathan", "last_name": "Walker", "card_type": "platinum", "member_since": "2015-08-25", "scenario": "churn_risk"},
    {"first_name": "Charlotte", "last_name": "Hall", "card_type": "gold", "member_since": "2018-01-14", "scenario": "travel_support"},
    {"first_name": "Benjamin", "last_name": "Allen", "card_type": "blue", "member_since": "2024-01-02", "scenario": "new_member"},
    {"first_name": "Amelia", "last_name": "Young", "card_type": "platinum", "member_since": "2017-03-21", "scenario": "loyal_customer"},
    {"first_name": "Ethan", "last_name": "King", "card_type": "green", "member_since": "2021-12-10", "scenario": "payment_issue"},
    {"first_name": "Harper", "last_name": "Wright", "card_type": "gold", "member_since": "2019-07-06", "scenario": "frustrated_activation"},
    {"first_name": "Jacob", "last_name": "Scott", "card_type": "platinum", "member_since": "2016-05-15", "scenario": "general_inquiry"},
    {"first_name": "Evelyn", "last_name": "Green", "card_type": "blue", "member_since": "2023-09-28", "scenario": "happy_rewards"},
    {"first_name": "Logan", "last_name": "Adams", "card_type": "gold", "member_since": "2020-08-13", "scenario": "dispute_journey"},
    {"first_name": "Abigail", "last_name": "Baker", "card_type": "green", "member_since": "2022-06-05", "scenario": "credit_limit"},
    {"first_name": "Lucas", "last_name": "Nelson", "card_type": "platinum", "member_since": "2015-11-22", "scenario": "churn_risk"},
    {"first_name": "Ella", "last_name": "Carter", "card_type": "gold", "member_since": "2018-04-09", "scenario": "travel_support"},
    {"first_name": "Mason", "last_name": "Mitchell", "card_type": "blue", "member_since": "2024-03-01", "scenario": "new_member"},
    {"first_name": "Scarlett", "last_name": "Perez", "card_type": "platinum", "member_since": "2017-09-17", "scenario": "loyal_customer"},
    {"first_name": "Jack", "last_name": "Roberts", "card_type": "green", "member_since": "2021-02-28", "scenario": "payment_issue"},
    {"first_name": "Grace", "last_name": "Turner", "card_type": "gold", "member_since": "2019-11-11", "scenario": "frustrated_activation"},
    {"first_name": "Owen", "last_name": "Phillips", "card_type": "platinum", "member_since": "2016-07-04", "scenario": "general_inquiry"},
    {"first_name": "Chloe", "last_name": "Campbell", "card_type": "blue", "member_since": "2023-12-20", "scenario": "happy_rewards"},
    {"first_name": "Henry", "last_name": "Parker", "card_type": "gold", "member_since": "2020-05-16", "scenario": "dispute_journey"},
    {"first_name": "Lily", "last_name": "Evans", "card_type": "green", "member_since": "2022-10-03", "scenario": "credit_limit"},
    {"first_name": "Sebastian", "last_name": "Edwards", "card_type": "platinum", "member_since": "2015-06-12", "scenario": "churn_risk"},
    {"first_name": "Zoe", "last_name": "Collins", "card_type": "gold", "member_since": "2018-07-28", "scenario": "travel_support"},
    {"first_name": "Caleb", "last_name": "Stewart", "card_type": "blue", "member_since": "2024-04-10", "scenario": "new_member"},
    {"first_name": "Hannah", "last_name": "Sanchez", "card_type": "platinum", "member_since": "2017-01-05", "scenario": "loyal_customer"},
    {"first_name": "Leo", "last_name": "Morris", "card_type": "green", "member_since": "2021-08-19", "scenario": "payment_issue"},
]


# ── Scenario-based score profiles ────────────────────────────────
SCENARIO_PROFILES = {
    "frustrated_activation": {"health": (35, 55), "frustration": (65, 90), "churn": (0.3, 0.6)},
    "happy_rewards": {"health": (75, 95), "frustration": (0, 15), "churn": (0.01, 0.1)},
    "churn_risk": {"health": (20, 40), "frustration": (50, 75), "churn": (0.6, 0.9)},
    "dispute_journey": {"health": (40, 60), "frustration": (40, 65), "churn": (0.2, 0.45)},
    "credit_limit": {"health": (60, 80), "frustration": (10, 30), "churn": (0.05, 0.2)},
    "travel_support": {"health": (70, 90), "frustration": (5, 25), "churn": (0.02, 0.12)},
    "new_member": {"health": (50, 70), "frustration": (5, 20), "churn": (0.1, 0.25)},
    "payment_issue": {"health": (30, 55), "frustration": (35, 60), "churn": (0.25, 0.5)},
    "loyal_customer": {"health": (80, 98), "frustration": (0, 10), "churn": (0.01, 0.05)},
    "general_inquiry": {"health": (55, 75), "frustration": (10, 30), "churn": (0.08, 0.2)},
}

SCENARIO_JOURNEY_MAP = {
    "frustrated_activation": JourneyType.CARD_ACTIVATION,
    "happy_rewards": JourneyType.REWARDS,
    "churn_risk": JourneyType.ACCOUNT_CLOSURE,
    "dispute_journey": JourneyType.DISPUTE,
    "credit_limit": JourneyType.CREDIT_LIMIT,
    "travel_support": JourneyType.TRAVEL,
    "new_member": JourneyType.CARD_ACTIVATION,
    "payment_issue": JourneyType.PAYMENT,
    "loyal_customer": JourneyType.REWARDS,
    "general_inquiry": JourneyType.GENERAL_INQUIRY,
}


async def seed_database(session: AsyncSession) -> None:
    """
    Populate the database with realistic synthetic data.
    Idempotent — checks if data already exists before seeding.
    """
    from sqlalchemy import select

    # Check if already seeded
    result = await session.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        return

    print("Seeding database with synthetic data...")

    # ── 1. Seed Users ────────────────────────────────────────────
    users = [
        User(
            id=str(uuid.uuid4()),
            email="admin@amexpulse.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            role="admin",
        ),
        User(
            id=str(uuid.uuid4()),
            email="agent@amexpulse.com",
            hashed_password=hash_password("agent123"),
            full_name="Alex Support",
            role="agent",
        ),
        User(
            id=str(uuid.uuid4()),
            email="analyst@amexpulse.com",
            hashed_password=hash_password("analyst123"),
            full_name="Dana Analyst",
            role="analyst",
        ),
        User(
            id=str(uuid.uuid4()),
            email="manager@amexpulse.com",
            hashed_password=hash_password("manager123"),
            full_name="Morgan Manager",
            role="manager",
        ),
    ]
    session.add_all(users)

    # ── 2. Seed Channels ─────────────────────────────────────────
    channels = {}
    for ch_type in ChannelType:
        meta = CHANNEL_METADATA[ch_type]
        ch = Channel(
            id=str(uuid.uuid4()),
            name=ch_type.value,
            display_name=meta["display_name"],
            icon=meta["icon"],
            color=meta["color"],
        )
        channels[ch_type.value] = ch
        session.add(ch)

    # ── 3. Seed Customers ────────────────────────────────────────
    now = datetime.now(timezone.utc)
    customer_objects = []

    for profile in CUSTOMER_PROFILES:
        scenario = profile["scenario"]
        sp = SCENARIO_PROFILES[scenario]

        health = round(random.uniform(*sp["health"]), 1)
        frustration = round(random.uniform(*sp["frustration"]), 1)
        churn = round(random.uniform(*sp["churn"]), 3)

        customer = Customer(
            id=str(uuid.uuid4()),
            universal_id=f"AMEX-{uuid.uuid4().hex[:8].upper()}",
            first_name=profile["first_name"],
            last_name=profile["last_name"],
            email=f"{profile['first_name'].lower()}.{profile['last_name'].lower()}@email.com",
            phone=f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            card_last_four=f"{random.randint(1000,9999)}",
            member_since=profile["member_since"],
            card_type=profile["card_type"],
            health_score=health,
            frustration_score=frustration,
            churn_risk=churn,
            metadata_json=json.dumps({"scenario": scenario}),
        )
        session.add(customer)
        customer_objects.append((customer, scenario))

        # Add identifiers
        for id_type, id_val in [
            ("email", customer.email),
            ("phone", customer.phone),
            ("account", customer.universal_id),
            ("device", f"device-{uuid.uuid4().hex[:12]}"),
        ]:
            session.add(CustomerIdentifier(
                customer_id=customer.id,
                identifier_type=id_type,
                identifier_value=id_val,
                confidence=1.0 if id_type in ("email", "account") else round(random.uniform(0.8, 1.0), 2),
            ))

    # ── 4. Seed Journeys, Events, Sessions ───────────────────────
    channel_list = list(channels.values())

    for customer, scenario in customer_objects:
        journey_type = SCENARIO_JOURNEY_MAP[scenario]
        steps = JOURNEY_STEPS[journey_type]

        # Determine journey status based on scenario
        if scenario in ("frustrated_activation", "churn_risk", "payment_issue"):
            j_status = random.choice([JourneyStatus.IN_PROGRESS.value, JourneyStatus.FAILED.value])
            progress = round(random.uniform(20, 60), 1)
        elif scenario in ("happy_rewards", "loyal_customer"):
            j_status = JourneyStatus.COMPLETED.value
            progress = 100.0
        else:
            j_status = random.choice([JourneyStatus.IN_PROGRESS.value, JourneyStatus.COMPLETED.value])
            progress = round(random.uniform(40, 100), 1)

        journey = Journey(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            journey_type=journey_type.value,
            status=j_status,
            progress=progress,
            detected_intent=journey_type.value,
            intent_confidence=round(random.uniform(0.7, 0.98), 2),
            started_at=now - timedelta(days=random.randint(1, 14)),
            completed_at=(now - timedelta(hours=random.randint(1, 48))) if j_status == "completed" else None,
        )
        session.add(journey)

        # Create sessions (1-3 per customer across different channels)
        num_sessions = random.randint(1, 3)
        selected_channels = random.sample(channel_list, min(num_sessions, len(channel_list)))

        for ch in selected_channels:
            sess = Session(
                id=str(uuid.uuid4()),
                customer_id=customer.id,
                channel_id=ch.id,
                session_token=f"sess-{uuid.uuid4().hex[:16]}",
                started_at=now - timedelta(hours=random.randint(1, 72)),
                event_count=random.randint(3, 15),
                is_abandoned=scenario in ("frustrated_activation", "churn_risk") and random.random() > 0.5,
            )
            session.add(sess)

            # Create events for the session
            event_types_pool = [
                (EventType.LOGIN.value, "User logged in"),
                (EventType.PAGE_VIEW.value, "Viewed account dashboard"),
                (EventType.CLICK.value, "Clicked card services"),
            ]

            # Add scenario-specific events
            if scenario == "frustrated_activation":
                event_types_pool.extend([
                    (EventType.CARD_ACTIVATION_FAILED.value, "Card activation failed - address mismatch"),
                    (EventType.AUTH_FAILURE.value, "Authentication failed"),
                    (EventType.LOGIN_FAILED.value, "Login attempt failed"),
                ])
            elif scenario == "dispute_journey":
                event_types_pool.extend([
                    (EventType.DISPUTE_FILED.value, "Dispute filed for transaction"),
                    (EventType.DOCUMENT_UPLOAD.value, "Supporting documents uploaded"),
                ])
            elif scenario == "happy_rewards":
                event_types_pool.extend([
                    (EventType.REWARDS_QUERY.value, "Checked rewards balance"),
                    (EventType.CLICK.value, "Browsed rewards catalog"),
                ])

            num_events = random.randint(3, 8)
            for i in range(num_events):
                et = random.choice(event_types_pool)
                sentiment = round(random.uniform(-0.8, -0.2), 2) if scenario in ("frustrated_activation", "churn_risk") else round(random.uniform(0.0, 0.8), 2)

                event = Event(
                    id=str(uuid.uuid4()),
                    customer_id=customer.id,
                    session_id=sess.id,
                    channel_id=ch.id,
                    event_type=et[0],
                    event_name=et[1],
                    event_data=json.dumps({"detail": f"Synthetic event for {scenario}"}),
                    sentiment_score=sentiment,
                    detected_emotion="frustrated" if sentiment < -0.3 else ("happy" if sentiment > 0.3 else "neutral"),
                    occurred_at=now - timedelta(hours=random.randint(0, 48), minutes=random.randint(0, 59)),
                )
                session.add(event)

        # Create journey steps
        completed_steps = int(len(steps) * (progress / 100))
        for idx, step_name in enumerate(steps):
            if idx < completed_steps:
                step_status = "completed"
            elif idx == completed_steps:
                step_status = "failed" if j_status == "failed" else "pending"
            else:
                step_status = "pending"

            session.add(JourneyStep(
                journey_id=journey.id,
                step_order=idx + 1,
                step_name=step_name,
                step_status=step_status,
            ))

        # Create predictions for some customers
        if scenario in ("frustrated_activation", "churn_risk", "payment_issue", "dispute_journey"):
            session.add(Prediction(
                customer_id=customer.id,
                prediction_type="churn",
                prediction_result=json.dumps({"risk": customer.churn_risk, "label": "high" if customer.churn_risk > 0.5 else "medium"}),
                confidence=round(random.uniform(0.75, 0.95), 2),
                explanation=f"Customer shows {'high' if customer.churn_risk > 0.5 else 'medium'} churn risk based on recent engagement decline and frustration indicators.",
                model_version="v1.0.0",
            ))

            # Create NBA recommendation
            if scenario == "frustrated_activation":
                action = ActionType.PRIORITY_CALLBACK
                desc = "Schedule immediate callback to assist with card activation"
            elif scenario == "churn_risk":
                action = ActionType.FEE_WAIVER
                desc = "Offer annual fee waiver as retention incentive"
            elif scenario == "payment_issue":
                action = ActionType.DEDICATED_AGENT
                desc = "Assign dedicated agent for payment resolution"
            else:
                action = ActionType.SPECIAL_REWARD
                desc = "Send exclusive reward offer"

            session.add(Recommendation(
                customer_id=customer.id,
                action_type=action.value,
                action_description=desc,
                confidence=round(random.uniform(0.7, 0.95), 2),
                reasoning=f"Based on {scenario.replace('_', ' ')} pattern analysis",
                status="pending",
            ))

        # Create support cases for frustrated/churn customers
        if scenario in ("frustrated_activation", "churn_risk", "dispute_journey", "payment_issue"):
            session.add(SupportCase(
                customer_id=customer.id,
                assigned_agent_id=users[1].id,  # agent user
                case_number=f"CASE-{random.randint(10000, 99999)}",
                subject=f"{'Card Activation Issue' if scenario == 'frustrated_activation' else 'Account Concern'}",
                description=f"Customer {customer.first_name} {customer.last_name} needs assistance with {scenario.replace('_', ' ')}",
                priority=CasePriority.HIGH.value if customer.frustration_score > 60 else CasePriority.MEDIUM.value,
                status=CaseStatus.OPEN.value,
            ))

    await session.commit()
    print(f"Created {len(users)} users, {len(CUSTOMER_PROFILES)} customers, {len(customer_objects)} journeys, {len(customer_objects)} events, {len(customer_objects)} cases, {len(customer_objects)} predictions")
