"""
AmEx Pulse — Constants
======================
Business constants and enumerations used across the platform.
"""

from enum import Enum


# ── Channel Types ────────────────────────────────────────────────
class ChannelType(str, Enum):
    MOBILE = "mobile"
    WEB = "web"
    CALL_CENTER = "call_center"
    BRANCH = "branch"
    EMAIL = "email"
    CHATBOT = "chatbot"
    CRM = "crm"
    SUPPORT_TICKET = "support_ticket"


CHANNEL_METADATA = {
    ChannelType.MOBILE: {"display_name": "Mobile App", "icon": "📱", "color": "#6366F1"},
    ChannelType.WEB: {"display_name": "Website", "icon": "🌐", "color": "#3B82F6"},
    ChannelType.CALL_CENTER: {"display_name": "Call Center", "icon": "📞", "color": "#F59E0B"},
    ChannelType.BRANCH: {"display_name": "Branch", "icon": "🏦", "color": "#10B981"},
    ChannelType.EMAIL: {"display_name": "Email", "icon": "📧", "color": "#8B5CF6"},
    ChannelType.CHATBOT: {"display_name": "Chatbot", "icon": "🤖", "color": "#EC4899"},
    ChannelType.CRM: {"display_name": "CRM", "icon": "📊", "color": "#14B8A6"},
    ChannelType.SUPPORT_TICKET: {"display_name": "Support Ticket", "icon": "🎫", "color": "#F97316"},
}


# ── Event Types ──────────────────────────────────────────────────
class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    AUTH_FAILURE = "auth_failure"
    CALL_STARTED = "call_started"
    CALL_ENDED = "call_ended"
    TRANSACTION = "transaction"
    PAYMENT = "payment"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    CARD_ACTIVATION = "card_activation"
    CARD_ACTIVATION_FAILED = "card_activation_failed"
    DISPUTE_FILED = "dispute_filed"
    CREDIT_LIMIT_REQUEST = "credit_limit_request"
    REWARDS_QUERY = "rewards_query"
    SESSION_ABANDON = "session_abandon"
    CHAT_MESSAGE = "chat_message"
    FORM_SUBMIT = "form_submit"
    DOCUMENT_UPLOAD = "document_upload"


# ── Journey Types ────────────────────────────────────────────────
class JourneyType(str, Enum):
    CARD_ACTIVATION = "card_activation"
    DISPUTE = "dispute"
    CREDIT_LIMIT = "credit_limit"
    REWARDS = "rewards"
    PAYMENT = "payment"
    TRAVEL = "travel"
    ACCOUNT_CLOSURE = "account_closure"
    GENERAL_INQUIRY = "general_inquiry"


JOURNEY_STEPS = {
    JourneyType.CARD_ACTIVATION: [
        "Login", "Navigate to Card Section", "Initiate Activation",
        "Verify Identity", "Enter Card Details", "Confirm Activation", "Activation Complete"
    ],
    JourneyType.DISPUTE: [
        "Login", "View Transactions", "Select Transaction",
        "File Dispute", "Upload Evidence", "Submit", "Confirmation"
    ],
    JourneyType.CREDIT_LIMIT: [
        "Login", "Navigate to Account", "Request Increase",
        "Income Verification", "Review Terms", "Submit Request", "Decision"
    ],
    JourneyType.REWARDS: [
        "Login", "View Rewards Balance", "Browse Catalog",
        "Select Reward", "Confirm Redemption", "Confirmation"
    ],
    JourneyType.PAYMENT: [
        "Login", "View Statement", "Select Payment Method",
        "Enter Amount", "Confirm Payment", "Payment Processed"
    ],
    JourneyType.TRAVEL: [
        "Login", "Access Travel Portal", "Search Flights/Hotels",
        "Select Options", "Apply Points", "Book", "Confirmation"
    ],
    JourneyType.ACCOUNT_CLOSURE: [
        "Login", "Navigate to Settings", "Request Closure",
        "Retention Offer", "Confirm Closure", "Final Survey", "Account Closed"
    ],
    JourneyType.GENERAL_INQUIRY: [
        "Contact", "Describe Issue", "Resolution Provided", "Feedback"
    ],
}


# ── Journey Status ───────────────────────────────────────────────
class JourneyStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"


# ── Card Types ───────────────────────────────────────────────────
class CardType(str, Enum):
    PLATINUM = "platinum"
    GOLD = "gold"
    GREEN = "green"
    BLUE = "blue"


# ── Prediction Types ─────────────────────────────────────────────
class PredictionType(str, Enum):
    INTENT = "intent"
    CHURN = "churn"
    FRUSTRATION = "frustration"
    HEALTH = "health"
    NBA = "nba"  # Next Best Action


# ── Recommendation Actions ───────────────────────────────────────
class ActionType(str, Enum):
    PRIORITY_CALLBACK = "priority_callback"
    FEE_WAIVER = "fee_waiver"
    CREDIT_INCREASE = "credit_increase"
    TRAVEL_SUPPORT = "travel_support"
    FRAUD_REVIEW = "fraud_review"
    SPECIAL_REWARD = "special_reward"
    DEDICATED_AGENT = "dedicated_agent"


ACTION_METADATA = {
    ActionType.PRIORITY_CALLBACK: {
        "display_name": "Priority Callback",
        "icon": "📞",
        "description": "Schedule an immediate callback from a senior agent",
        "urgency": "high",
    },
    ActionType.FEE_WAIVER: {
        "display_name": "Fee Waiver",
        "icon": "💰",
        "description": "Waive applicable fees as a goodwill gesture",
        "urgency": "medium",
    },
    ActionType.CREDIT_INCREASE: {
        "display_name": "Credit Limit Increase",
        "icon": "📈",
        "description": "Pre-approve a credit limit increase offer",
        "urgency": "low",
    },
    ActionType.TRAVEL_SUPPORT: {
        "display_name": "Travel Support Package",
        "icon": "✈️",
        "description": "Activate premium travel support and insurance",
        "urgency": "medium",
    },
    ActionType.FRAUD_REVIEW: {
        "display_name": "Expedited Fraud Review",
        "icon": "🔒",
        "description": "Fast-track fraud investigation and card security",
        "urgency": "critical",
    },
    ActionType.SPECIAL_REWARD: {
        "display_name": "Special Reward Offer",
        "icon": "🎁",
        "description": "Exclusive loyalty reward for valued member",
        "urgency": "low",
    },
    ActionType.DEDICATED_AGENT: {
        "display_name": "Dedicated Agent Assignment",
        "icon": "👤",
        "description": "Assign a personal account manager",
        "urgency": "high",
    },
}


# ── Support Case ─────────────────────────────────────────────────
class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ── Sentiment ────────────────────────────────────────────────────
class Sentiment(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


# ── User Roles ───────────────────────────────────────────────────
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    AGENT = "agent"


# ── Frustration Score Weights ────────────────────────────────────
FRUSTRATION_WEIGHTS = {
    "repeated_login": 15,
    "channel_switch": 20,
    "session_abandon": 25,
    "auth_failure": 20,
    "negative_sentiment": 10,
    "long_call": 15,
    "complaint_keyword": 10,
    "repeated_contact": 12,
}


# ── Health Score Component Weights ───────────────────────────────
HEALTH_WEIGHTS = {
    "engagement": 0.25,
    "journey_completion": 0.20,
    "support_history": 0.15,
    "payment_behavior": 0.15,
    "frustration_inverse": 0.10,
    "risk_inverse": 0.10,
    "usage_patterns": 0.05,
}
