"""
AmEx Pulse — AI Pipeline Orchestrator
=======================================
Central orchestrator for all AI/ML modules.
Runs predictions through Identity Resolution → Intent → Frustration → Health → Churn → NBA → Summary.
"""

import random
from datetime import datetime, timezone

from app.core.constants import (
    FRUSTRATION_WEIGHTS,
    HEALTH_WEIGHTS,
    ActionType,
    ACTION_METADATA,
    EventType,
    JourneyType,
)


class AIPipeline:
    """
    Unified AI Pipeline that runs all prediction engines.
    For the hackathon, uses rule-based + statistical models
    that are fast, deterministic, and don't require GPU/external APIs.
    """

    def run_full_pipeline(
        self,
        customer,
        events: list,
        journeys: list,
        prediction_types: list[str] | None = None,
    ) -> dict:
        """
        Run the complete AI pipeline for a customer.

        Returns:
            Dict mapping prediction_type -> {result, confidence, explanation}
        """
        if prediction_types is None:
            prediction_types = ["intent", "frustration", "health", "churn", "nba", "summary"]

        results = {}

        # Build feature vector from events
        features = self._extract_features(customer, events, journeys)

        if "intent" in prediction_types:
            results["intent"] = self._detect_intent(features, events, journeys)

        if "frustration" in prediction_types:
            results["frustration"] = self._calculate_frustration(features, events)

        if "health" in prediction_types:
            frustration_score = results.get("frustration", {}).get("result", {}).get("score", customer.frustration_score)
            results["health"] = self._calculate_health(features, customer, frustration_score)

        if "churn" in prediction_types:
            results["churn"] = self._predict_churn(features, customer)

        if "nba" in prediction_types:
            results["nba"] = self._next_best_action(features, customer, results)

        if "summary" in prediction_types:
            results["summary"] = self._generate_summary(customer, events, journeys, results)

        return results

    def _extract_features(self, customer, events, journeys) -> dict:
        """Extract ML features from customer data."""
        now = datetime.now(timezone.utc)

        # Event-based features
        login_failures = sum(1 for e in events if e.event_type in (EventType.LOGIN_FAILED.value, EventType.AUTH_FAILURE.value))
        auth_failures = sum(1 for e in events if e.event_type == EventType.AUTH_FAILURE.value)
        complaints = sum(1 for e in events if e.event_type == EventType.COMPLAINT.value)
        session_abandons = sum(1 for e in events if e.event_type == EventType.SESSION_ABANDON.value)
        total_events = len(events)

        # Channel diversity
        unique_channels = len(set(e.channel_id for e in events))
        channel_switches = max(0, unique_channels - 1)

        # Sentiment
        sentiments = [e.sentiment_score for e in events if e.sentiment_score is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        negative_sentiments = sum(1 for s in sentiments if s < -0.3)

        # Journey features
        completed_journeys = sum(1 for j in journeys if j.status == "completed")
        failed_journeys = sum(1 for j in journeys if j.status == "failed")
        total_journeys = len(journeys)
        avg_progress = sum(j.progress for j in journeys) / total_journeys if total_journeys > 0 else 0

        # Temporal features
        if events:
            latest_event = max(events, key=lambda e: e.occurred_at if e.occurred_at else datetime.min.replace(tzinfo=timezone.utc))
            days_since_last_event = (now - latest_event.occurred_at).days if latest_event.occurred_at else 30
        else:
            days_since_last_event = 30

        return {
            "login_failures": login_failures,
            "auth_failures": auth_failures,
            "complaints": complaints,
            "session_abandons": session_abandons,
            "total_events": total_events,
            "unique_channels": unique_channels,
            "channel_switches": channel_switches,
            "avg_sentiment": avg_sentiment,
            "negative_sentiments": negative_sentiments,
            "completed_journeys": completed_journeys,
            "failed_journeys": failed_journeys,
            "total_journeys": total_journeys,
            "avg_progress": avg_progress,
            "days_since_last_event": days_since_last_event,
            "card_type": customer.card_type,
            "current_health": customer.health_score,
            "current_frustration": customer.frustration_score,
            "current_churn_risk": customer.churn_risk,
        }

    def _detect_intent(self, features: dict, events, journeys) -> dict:
        """
        Intent Detection Engine.
        Uses event patterns to classify customer intent.
        """
        intent_signals = {
            JourneyType.CARD_ACTIVATION.value: 0,
            JourneyType.DISPUTE.value: 0,
            JourneyType.CREDIT_LIMIT.value: 0,
            JourneyType.REWARDS.value: 0,
            JourneyType.PAYMENT.value: 0,
            JourneyType.TRAVEL.value: 0,
            JourneyType.ACCOUNT_CLOSURE.value: 0,
            JourneyType.GENERAL_INQUIRY.value: 0,
        }

        # Score intents based on event types
        for e in events:
            et = e.event_type
            if et in (EventType.CARD_ACTIVATION.value, EventType.CARD_ACTIVATION_FAILED.value):
                intent_signals[JourneyType.CARD_ACTIVATION.value] += 3
            elif et == EventType.DISPUTE_FILED.value:
                intent_signals[JourneyType.DISPUTE.value] += 3
            elif et == EventType.CREDIT_LIMIT_REQUEST.value:
                intent_signals[JourneyType.CREDIT_LIMIT.value] += 3
            elif et == EventType.REWARDS_QUERY.value:
                intent_signals[JourneyType.REWARDS.value] += 3
            elif et == EventType.PAYMENT.value:
                intent_signals[JourneyType.PAYMENT.value] += 3
            elif et == EventType.COMPLAINT.value:
                intent_signals[JourneyType.GENERAL_INQUIRY.value] += 2

        # Boost from active journeys
        for j in journeys:
            if j.status == "in_progress" and j.journey_type in intent_signals:
                intent_signals[j.journey_type] += 5

        # Find top intent
        if sum(intent_signals.values()) == 0:
            top_intent = JourneyType.GENERAL_INQUIRY.value
            confidence = 0.5
        else:
            top_intent = max(intent_signals, key=intent_signals.get)
            max_score = intent_signals[top_intent]
            total_score = sum(intent_signals.values())
            confidence = round(min(0.98, max_score / max(total_score, 1)), 2)

        return {
            "result": {
                "primary_intent": top_intent,
                "intent_label": top_intent.replace("_", " ").title(),
                "all_intents": {k: round(v / max(sum(intent_signals.values()), 1), 2) for k, v in intent_signals.items() if v > 0},
            },
            "confidence": confidence,
            "explanation": f"Primary intent detected as '{top_intent.replace('_', ' ').title()}' based on {len(events)} recent events and {len(journeys)} journey(s). Confidence: {confidence:.0%}",
        }

    def _calculate_frustration(self, features: dict, events) -> dict:
        """
        Frustration Detection Engine.
        Weighted scoring model based on behavioral signals.
        """
        raw_score = 0
        factors = []

        # Login failures
        if features["login_failures"] > 0:
            pts = features["login_failures"] * FRUSTRATION_WEIGHTS["repeated_login"]
            raw_score += pts
            factors.append(f"{features['login_failures']} login failure(s) (+{pts})")

        # Channel switching
        if features["channel_switches"] > 0:
            pts = features["channel_switches"] * FRUSTRATION_WEIGHTS["channel_switch"]
            raw_score += pts
            factors.append(f"{features['channel_switches']} channel switch(es) (+{pts})")

        # Session abandonment
        if features["session_abandons"] > 0:
            pts = features["session_abandons"] * FRUSTRATION_WEIGHTS["session_abandon"]
            raw_score += pts
            factors.append(f"{features['session_abandons']} abandoned session(s) (+{pts})")

        # Auth failures
        if features["auth_failures"] > 0:
            pts = features["auth_failures"] * FRUSTRATION_WEIGHTS["auth_failure"]
            raw_score += pts
            factors.append(f"{features['auth_failures']} auth failure(s) (+{pts})")

        # Negative sentiment
        if features["negative_sentiments"] > 0:
            pts = features["negative_sentiments"] * FRUSTRATION_WEIGHTS["negative_sentiment"]
            raw_score += pts
            factors.append(f"{features['negative_sentiments']} negative sentiment event(s) (+{pts})")

        # Complaints
        if features["complaints"] > 0:
            pts = features["complaints"] * FRUSTRATION_WEIGHTS["complaint_keyword"]
            raw_score += pts
            factors.append(f"{features['complaints']} complaint(s) (+{pts})")

        # Normalize to 0-100
        score = min(100, max(0, raw_score))

        # Determine level
        if score >= 70:
            level = "critical"
        elif score >= 50:
            level = "high"
        elif score >= 30:
            level = "medium"
        else:
            level = "low"

        return {
            "result": {
                "score": round(score, 1),
                "level": level,
                "factors": factors,
            },
            "confidence": round(min(0.95, 0.7 + (len(factors) * 0.05)), 2),
            "explanation": f"Frustration score: {score:.0f}/100 ({level}). Key factors: {'; '.join(factors[:3]) if factors else 'No frustration signals detected.'}",
        }

    def _calculate_health(self, features: dict, customer, frustration_score: float) -> dict:
        """
        Customer Health Score Engine.
        Composite weighted score across 7 dimensions.
        """
        components = {}

        # Engagement (25%): Based on event frequency and recency
        engagement_raw = max(0, min(100,
            100 - (features["days_since_last_event"] * 3) +
            min(30, features["total_events"] * 2)
        ))
        components["engagement"] = round(engagement_raw, 1)

        # Journey Completion (20%): % of journeys completed
        if features["total_journeys"] > 0:
            completion_rate = (features["completed_journeys"] / features["total_journeys"]) * 100
        else:
            completion_rate = 50  # neutral if no journeys
        components["journey_completion"] = round(completion_rate, 1)

        # Support History (15%): Inverse of complaint frequency
        support_score = max(0, 100 - (features["complaints"] * 20))
        components["support_history"] = round(support_score, 1)

        # Payment Behavior (15%): Based on card type as proxy
        payment_scores = {"platinum": 90, "gold": 75, "green": 60, "blue": 50}
        components["payment_behavior"] = payment_scores.get(features["card_type"], 50)

        # Frustration Inverse (10%)
        components["frustration_inverse"] = round(max(0, 100 - frustration_score), 1)

        # Risk Inverse (10%)
        components["risk_inverse"] = round(max(0, (1 - features["current_churn_risk"]) * 100), 1)

        # Usage Patterns (5%)
        usage_score = min(100, features["total_events"] * 5 + features["unique_channels"] * 10)
        components["usage_patterns"] = round(usage_score, 1)

        # Weighted composite
        health_score = sum(
            components[key] * HEALTH_WEIGHTS[key]
            for key in HEALTH_WEIGHTS
        )

        # Determine status
        if health_score >= 75:
            status = "healthy"
        elif health_score >= 50:
            status = "at_risk"
        elif health_score >= 25:
            status = "unhealthy"
        else:
            status = "critical"

        return {
            "result": {
                "score": round(health_score, 1),
                "status": status,
                "components": components,
            },
            "confidence": 0.88,
            "explanation": f"Health score: {health_score:.0f}/100 ({status}). Strongest factors: Engagement ({components['engagement']:.0f}), Journey Completion ({components['journey_completion']:.0f}%), Payment ({components['payment_behavior']})",
        }

    def _predict_churn(self, features: dict, customer) -> dict:
        """
        Churn Prediction Engine.
        XGBoost-style feature-weighted model (rule-based for hackathon determinism).
        """
        churn_score = 0.05  # Base probability

        # Feature contributions with SHAP-like explanations
        contributions = []

        # Days since last interaction
        if features["days_since_last_event"] > 14:
            contrib = 0.15
            churn_score += contrib
            contributions.append({"feature": "Inactivity", "value": f"{features['days_since_last_event']} days", "impact": contrib})
        elif features["days_since_last_event"] > 7:
            contrib = 0.08
            churn_score += contrib
            contributions.append({"feature": "Reduced Activity", "value": f"{features['days_since_last_event']} days", "impact": contrib})

        # Frustration level
        if features["current_frustration"] > 70:
            contrib = 0.2
            churn_score += contrib
            contributions.append({"feature": "High Frustration", "value": f"{features['current_frustration']:.0f}/100", "impact": contrib})
        elif features["current_frustration"] > 40:
            contrib = 0.1
            churn_score += contrib
            contributions.append({"feature": "Moderate Frustration", "value": f"{features['current_frustration']:.0f}/100", "impact": contrib})

        # Failed journeys
        if features["failed_journeys"] > 0:
            contrib = features["failed_journeys"] * 0.1
            churn_score += contrib
            contributions.append({"feature": "Failed Journeys", "value": str(features["failed_journeys"]), "impact": contrib})

        # Complaints
        if features["complaints"] > 0:
            contrib = features["complaints"] * 0.08
            churn_score += contrib
            contributions.append({"feature": "Complaints Filed", "value": str(features["complaints"]), "impact": contrib})

        # Low engagement (few channels)
        if features["unique_channels"] <= 1:
            contrib = 0.08
            churn_score += contrib
            contributions.append({"feature": "Low Channel Diversity", "value": f"{features['unique_channels']} channel(s)", "impact": contrib})

        # Negative sentiment
        if features["avg_sentiment"] < -0.3:
            contrib = 0.12
            churn_score += contrib
            contributions.append({"feature": "Negative Sentiment", "value": f"{features['avg_sentiment']:.2f}", "impact": contrib})

        # Card type (loyalty proxy — platinum members less likely to churn)
        loyalty_bonus = {"platinum": -0.1, "gold": -0.05, "green": 0, "blue": 0.05}
        bonus = loyalty_bonus.get(features["card_type"], 0)
        if bonus != 0:
            churn_score += bonus
            contributions.append({"feature": "Card Tier", "value": features["card_type"].title(), "impact": bonus})

        churn_score = round(max(0.01, min(0.99, churn_score)), 3)

        if churn_score >= 0.6:
            risk_label = "high"
        elif churn_score >= 0.3:
            risk_label = "medium"
        else:
            risk_label = "low"

        # Sort contributions by absolute impact
        contributions.sort(key=lambda x: abs(x["impact"]), reverse=True)

        return {
            "result": {
                "risk": churn_score,
                "label": risk_label,
                "contributions": contributions[:5],
            },
            "confidence": round(0.75 + min(0.2, len(contributions) * 0.03), 2),
            "explanation": f"Churn risk: {churn_score:.0%} ({risk_label}). Top factor: {contributions[0]['feature'] if contributions else 'None'} ({contributions[0]['value'] if contributions else 'N/A'})",
        }

    def _next_best_action(self, features: dict, customer, prediction_results: dict) -> dict:
        """
        Next Best Action Engine.
        Rule-based decision tree enhanced with prediction confidence scores.
        """
        actions = []

        frustration = prediction_results.get("frustration", {}).get("result", {}).get("score", customer.frustration_score)
        churn_risk = prediction_results.get("churn", {}).get("result", {}).get("risk", customer.churn_risk)
        intent = prediction_results.get("intent", {}).get("result", {}).get("primary_intent", "")

        # Rule 1: High frustration + auth issues → Priority callback
        if frustration > 60 and features["auth_failures"] > 0:
            actions.append({
                "type": ActionType.PRIORITY_CALLBACK.value,
                "description": ACTION_METADATA[ActionType.PRIORITY_CALLBACK]["description"],
                "confidence": round(min(0.95, 0.7 + frustration / 200), 2),
                "reasoning": f"Frustration score of {frustration:.0f} with {features['auth_failures']} authentication failure(s) indicates urgent need for human assistance.",
                "urgency": "high",
                "icon": ACTION_METADATA[ActionType.PRIORITY_CALLBACK]["icon"],
            })

        # Rule 2: High churn risk + long tenure → Fee waiver
        if churn_risk > 0.5 and customer.card_type in ("platinum", "gold"):
            actions.append({
                "type": ActionType.FEE_WAIVER.value,
                "description": ACTION_METADATA[ActionType.FEE_WAIVER]["description"],
                "confidence": round(min(0.9, 0.6 + churn_risk * 0.3), 2),
                "reasoning": f"High churn risk ({churn_risk:.0%}) for {customer.card_type.title()} member since {customer.member_since}. Fee waiver as retention strategy.",
                "urgency": "medium",
                "icon": ACTION_METADATA[ActionType.FEE_WAIVER]["icon"],
            })

        # Rule 3: Credit limit intent + good health → Credit increase
        if intent == JourneyType.CREDIT_LIMIT.value and customer.health_score > 50:
            actions.append({
                "type": ActionType.CREDIT_INCREASE.value,
                "description": ACTION_METADATA[ActionType.CREDIT_INCREASE]["description"],
                "confidence": 0.85,
                "reasoning": f"Customer is actively seeking credit limit increase with health score of {customer.health_score:.0f}. Pre-approving increases satisfaction and wallet share.",
                "urgency": "low",
                "icon": ACTION_METADATA[ActionType.CREDIT_INCREASE]["icon"],
            })

        # Rule 4: Travel-related activity → Travel support
        if intent == JourneyType.TRAVEL.value:
            actions.append({
                "type": ActionType.TRAVEL_SUPPORT.value,
                "description": ACTION_METADATA[ActionType.TRAVEL_SUPPORT]["description"],
                "confidence": 0.82,
                "reasoning": "Travel intent detected. Proactively offering travel support enhances the premium experience.",
                "urgency": "medium",
                "icon": ACTION_METADATA[ActionType.TRAVEL_SUPPORT]["icon"],
            })

        # Rule 5: Multiple complaints → Dedicated agent
        if features["complaints"] >= 2 or (features["channel_switches"] >= 2 and frustration > 50):
            actions.append({
                "type": ActionType.DEDICATED_AGENT.value,
                "description": ACTION_METADATA[ActionType.DEDICATED_AGENT]["description"],
                "confidence": round(min(0.92, 0.7 + features["complaints"] * 0.05), 2),
                "reasoning": f"Customer has {features['complaints']} complaint(s) across {features['unique_channels']} channels. Dedicated agent prevents further escalation.",
                "urgency": "high",
                "icon": ACTION_METADATA[ActionType.DEDICATED_AGENT]["icon"],
            })

        # Rule 6: High-value customer + good health → Special reward
        if customer.card_type == "platinum" and customer.health_score > 70 and churn_risk < 0.2:
            actions.append({
                "type": ActionType.SPECIAL_REWARD.value,
                "description": ACTION_METADATA[ActionType.SPECIAL_REWARD]["description"],
                "confidence": 0.78,
                "reasoning": f"Platinum member with strong health score ({customer.health_score:.0f}). Proactive reward strengthens loyalty.",
                "urgency": "low",
                "icon": ACTION_METADATA[ActionType.SPECIAL_REWARD]["icon"],
            })

        # Default: if no actions, suggest monitoring
        if not actions:
            actions.append({
                "type": "monitor",
                "description": "Continue monitoring — no immediate action required",
                "confidence": 0.6,
                "reasoning": "Customer metrics are within normal ranges. No intervention needed at this time.",
                "urgency": "low",
                "icon": "👀",
            })

        # Sort by confidence
        actions.sort(key=lambda a: a["confidence"], reverse=True)

        return {
            "result": {
                "actions": actions,
                "top_action": actions[0] if actions else None,
            },
            "confidence": actions[0]["confidence"] if actions else 0.5,
            "explanation": f"Top recommendation: {actions[0]['description']} (confidence: {actions[0]['confidence']:.0%})" if actions else "No action needed",
        }

    def _generate_summary(self, customer, events, journeys, prediction_results: dict) -> dict:
        """
        AI Journey Summary Generator.
        Template-based NLG engine that produces executive-quality narratives.
        """
        name = f"{customer.first_name} {customer.last_name}"
        card = customer.card_type.title()

        # Get scores
        frustration = prediction_results.get("frustration", {}).get("result", {}).get("score", customer.frustration_score)
        health = prediction_results.get("health", {}).get("result", {}).get("score", customer.health_score)
        churn = prediction_results.get("churn", {}).get("result", {}).get("risk", customer.churn_risk)
        intent = prediction_results.get("intent", {}).get("result", {}).get("intent_label", "General Inquiry")
        top_action = prediction_results.get("nba", {}).get("result", {}).get("top_action", {})

        # Count key events
        auth_fails = sum(1 for e in events if e.event_type in ("auth_failure", "login_failed"))
        channels_used = len(set(e.channel_id for e in events))

        # Build narrative
        lines = []
        lines.append(f"**{name}** is an AmEx {card} member since {customer.member_since}.")

        # Journey context
        active_journeys = [j for j in journeys if j.status == "in_progress"]
        if active_journeys:
            j = active_journeys[0]
            lines.append(f"Currently on a **{j.journey_type.replace('_', ' ').title()}** journey ({j.progress:.0f}% complete).")

        # Events summary
        lines.append(f"Recent activity: {len(events)} events across {channels_used} channel(s).")
        if auth_fails > 0:
            lines.append(f"⚠️ Experienced {auth_fails} authentication failure(s).")

        # Scores
        lines.append(f"Health: **{health:.0f}/100** | Frustration: **{frustration:.0f}/100** | Churn Risk: **{churn:.0%}**")

        # Intent
        lines.append(f"Detected intent: **{intent}**")

        # Recommendation
        if top_action:
            lines.append(f"📋 **Recommendation**: {top_action.get('description', 'N/A')} (confidence: {top_action.get('confidence', 0):.0%})")
            if top_action.get("reasoning"):
                lines.append(f"Reasoning: {top_action['reasoning']}")

        summary = "\n\n".join(lines)

        return {
            "result": {"summary": summary},
            "confidence": 0.90,
            "explanation": "AI-generated executive summary based on customer profile, events, and predictions.",
        }
