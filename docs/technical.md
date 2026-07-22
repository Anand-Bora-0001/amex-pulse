# Technical Architecture & Schema

## 🛣️ API Endpoints Reference

The backend exposes a highly documented OpenAPI interface (Swagger UI at `/docs`). Below is a detailed breakdown of the request and response schemas.

### Auth Endpoints

#### `POST /api/v1/auth/login`
Authenticates a user and returns a JWT Bearer token.
**Request Body:**
```json
{
  "username": "admin@amexpulse.com",
  "password": "admin123"
}
```
**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@amexpulse.com",
    "role": "admin",
    "full_name": "Admin User"
  }
}
```

#### `GET /api/v1/auth/me`
Retrieves the current user's profile and RBAC permissions.
**Response (200 OK):**
```json
{
  "id": 1,
  "email": "admin@amexpulse.com",
  "role": "admin",
  "full_name": "Admin User",
  "is_active": true
}
```

### Customer Endpoints

#### `GET /api/v1/customers`
Retrieves a paginated list of customers, sortable by churn risk, frustration score, or health.
**Query Parameters:**
- `page`: integer (default: 1)
- `size`: integer (default: 50)
- `sort_by`: string ("frustration_score", "churn_risk", "health_score")
- `order`: string ("desc", "asc")

**Response (200 OK):**
```json
{
  "total": 50,
  "page": 1,
  "size": 50,
  "customers": [
    {
      "id": 1,
      "universal_id": "AMX-7B39F",
      "first_name": "Maria",
      "last_name": "Garcia",
      "email": "maria.g@example.com",
      "phone": "+1-555-0192",
      "frustration_score": 85.5,
      "health_score": 42.0,
      "churn_risk": 0.88,
      "card_type": "platinum"
    }
  ]
}
```

#### `GET /api/v1/customers/{id}`
Retrieves the complete 360-degree profile for a specific customer, including recent predictions.

#### `GET /api/v1/customers/{id}/events`
Retrieves the stitched timeline of cross-channel events.
**Response (200 OK):**
```json
[
  {
    "id": 105,
    "event_type": "auth_failure",
    "channel_id": 2,
    "timestamp": "2026-07-22T08:15:00Z",
    "metadata": {
      "error_code": "INVALID_CVV",
      "device": "iOS"
    }
  },
  {
    "id": 106,
    "event_type": "call_initiated",
    "channel_id": 4,
    "timestamp": "2026-07-22T08:17:00Z",
    "metadata": {
      "wait_time": 120
    }
  }
]
```

### Journey & Intelligence Endpoints

#### `GET /api/v1/journeys`
Lists active customer journeys across the platform.

#### `GET /api/v1/journeys/{id}/graph`
Returns React Flow compatible Nodes & Edges to visualize a journey.
**Response (200 OK):**
```json
{
  "nodes": [
    {
      "id": "node-105",
      "type": "eventNode",
      "position": { "x": 0, "y": 0 },
      "data": { "label": "Login Failed", "channel": "Mobile App", "isFriction": true }
    }
  ],
  "edges": [
    {
      "id": "edge-105-106",
      "source": "node-105",
      "target": "node-106",
      "animated": true,
      "style": { "stroke": "#EF4444" }
    }
  ]
}
```

#### `POST /api/v1/predictions/simulate`
Manually trigger the 6-engine AI pipeline for a specific user to generate a new intelligence snapshot.

### WebSockets

#### `ws://localhost:8000/ws`
Connect to the live event stream. Emits real-time JSON payloads whenever a customer interaction occurs.
**Message Payload:**
```json
{
  "type": "NEW_EVENT",
  "data": {
    "customer_id": 1,
    "event_type": "page_view",
    "channel_name": "Web",
    "frustration_delta": +5
  }
}
```

---

## 🗄️ Database Schema (Domain Models)

The system uses SQLAlchemy 2.0 with asynchronous session management. Below are the detailed schema definitions.

### `users` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing ID |
| `email` | String | Unique, Not Null | User's email address |
| `hashed_password` | String | Not Null | Bcrypt hashed password |
| `full_name` | String | Not Null | User's full name |
| `role` | String | Not Null | Enum: admin, agent, analyst |
| `is_active` | Boolean | Default: True | Account status |

### `customers` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing ID |
| `universal_id` | String | Unique, Index | Cross-channel unique identifier |
| `first_name` | String | Not Null | Customer's first name |
| `last_name` | String | Not Null | Customer's last name |
| `email` | String | Unique | Contact email |
| `phone` | String | | Contact phone |
| `card_type` | String | Not Null | e.g., platinum, gold, green |
| `health_score` | Float | Default: 100.0| AI-calculated health score (0-100) |
| `frustration_score` | Float | Default: 0.0| AI-calculated frustration (0-100) |
| `churn_risk` | Float | Default: 0.0 | AI-calculated churn prob (0-1) |

### `channels` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing ID |
| `name` | String | Unique | e.g., Web, Mobile, IVR, Chatbot |
| `type` | String | | e.g., digital, voice, physical |

### `journeys` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing ID |
| `customer_id` | Integer | Foreign Key | References `customers.id` |
| `status` | String | Not Null | Enum: active, completed, abandoned |
| `intent` | String | | e.g., "Card Activation" |
| `start_time` | DateTime| Not Null | Journey start timestamp |
| `end_time` | DateTime| | Journey end timestamp |

### `events` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing ID |
| `journey_id` | Integer | Foreign Key | References `journeys.id` |
| `channel_id` | Integer | Foreign Key | References `channels.id` |
| `event_type` | String | Not Null | e.g., "login_failed", "page_view" |
| `timestamp` | DateTime| Not Null | Event occurrence time |
| `metadata` | JSONB | | Contextual event data |

### `ai_predictions` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing ID |
| `customer_id` | Integer | Foreign Key | References `customers.id` |
| `prediction_type`| String | Not Null | e.g., "churn", "nba", "intent" |
| `score` | Float | | Confidence or probability score |
| `reasoning` | String | | Explainable AI justification |
| `timestamp` | DateTime| Not Null | When the prediction was made |

### `support_cases` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing ID |
| `customer_id` | Integer | Foreign Key | References `customers.id` |
| `assigned_agent` | Integer | Foreign Key | References `users.id` |
| `case_number` | String | Unique | e.g., "CASE-12345" |
| `status` | String | Not Null | Enum: open, pending, resolved |
| `priority` | String | Not Null | Enum: low, medium, high, critical|

---

