# Customer Support Multi-Agent API

A production-ready multi-agent conversational AI system for handling e-commerce customer service inquiries. 
Built with FastAPI, Redis, and OpenAI, this system manages complex multi-turn conversations for order tracking, 
order cancellation, and product information queries.

**Tech Stack**: Python 3.11, FastAPI, Redis, OpenAI Agents SDK, Docker, Ollama

---

## Architecture

### System Architecture Diagram

```
                                     User
                                      │
                                      │ POST /chat
                                      │ {session_id, message}
                                      ▼
                          ┌─────────────────────────┐
                          │   FastAPI Application   │
                          │   (app/api/main.py)     │
                          └─────────────────────────┘
                            │                    ▲
                            │                    │
                 ① Load    │                    │ ⑤ Return response
                  session   │                    │    {session_id,
                            │                    │     response,
                            ▼                    │     agent,
                  ┌──────────────┐              │     handover}
                  │    Redis     │              │
                  │  Session     │              │
                  │   Store      │◀─────────────┤ ⑤ Save updated
                  │              │              │    SessionState
                  │ • session_id │              │
                  │ • context    │              │
                  │ • pending_   │              │
                  │   intent     │              │
                  │ • last_agent │              │
                  │              │              │
                  │ TTL: 24 hrs  │              │
                  └──────────────┘              │
                            │                   │
                            │ Returns           │
                            │ SessionState      │
                            │                   │
                 ② Call     │                  │
                orchestrator│                   │
                (message +  │                   │
                 state)     │                   │
                            ▼                   │
                  ┌─────────────────────┐       │
                  │  Orchestrator Agent │───────┘
                  │  (orchestrator.py)  │  Returns
                  │                     │  {response, agent,
                  │ • Manages state     │   handover,
                  │ • Extracts order ID │   updated_context}
                  │ • Routes to agents  │
                  └─────────────────────┘
                            │              ▲
                            │              │
                ③ Classify │              │ Returns intent
                    intent  │              │ string
                  (message) │              │
                            ▼              │
                      ┌──────────────┐    │
                      │   Intent     │────┘
                      │  Classifier  │
                      │              │
                      │ Returns:     │
                      │ • track_order│
                      │ • cancel_    │
                      │   order      │
                      │ • product_   │
                      │   info       │
                      │ • unknown    │◀────┤
                      └──────────────┘     |
                 ④ Execute │              │ Returns
                specialist  │              │ response
                (message,   │              │ string
                 order_id,  │              │
                 intent)    │              │
                            ▼              │
                      ┌──────────────┐     │
                      │  Specialist  │─────┘
                      │   Agents     │
                      │              │
                      │ • Order      │
                      │   Tracking   │
                      │ • Order      │
                      │   Cancel     │
                      │ • Product    │
                      │   Info       │
                      └──────────────┘
                            │
                            │ Calls tools
                            ▼
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
          ┌──────────┐        ┌─────────────┐
          │  Data    │        │   OpenAI    │
          │ Sources  │        │     API     │
          │          │        │             │
          │ orders/  │        │ GPT-4.1-mini│
          │ products │        │ Vector Store│
          └──────────┘        └─────────────┘

                 ⑥ Evaluate │              │
                  response   │              │
                  quality    │              │
                            ▼              │
                      ┌──────────────┐     │
                      │   Ollama     │     │
                      │ LLM Judge    │     │
                      │              │     │
                      │ llama3:      │     │
                      │ instruct     │     │
                      │              │     │
                      │ Returns      │     │
                      │ score 1-5    │     │
                      └──────────────┘

Request Flow:
  ① FastAPI loads session state from Redis
     Output: SessionState object with context, history, last_agent

  ② FastAPI calls Orchestrator with message and state
     Input: user message + SessionState
     Output: {response, agent, handover, updated_context}

  ③ Orchestrator calls Intent Classifier to determine user's goal
     Input: user message
     Output: intent string (track_order, cancel_order, product_information, unknown)

  ④ Orchestrator routes to appropriate Specialist Agent
     Input: message, order_id, intent
     Output: agent response string

  ⑤ FastAPI updates session context, saves to Redis, returns response
     Input: orchestrator result + updated SessionState
     Output: API response {session_id, response, agent, handover}

  ⑥ LLM Judge evaluates response quality before returning to user
     Input: intent, user_message, ai_output
     Output: score 1-5 (stored in context["judge_scores"], returned in response)
     This score can later be used in accuracy calculations.
```


### Multi-Turn Conversation Flow

**Example Scenario**: User wants to cancel order but doesn't provide order ID upfront

**Turn 1**:
```
User: "I want to cancel my order"
│
├─> Orchestrator detects no order ID in message
├─> Calls Intent Classifier → returns "cancel_order"
├─> Sets context["pending_intent"] = "cancel_order"
└─> Response: "Please provide your order ID (format: ORD-XXXX)"
```

**Turn 2**:
```
User: "ORD-1234"
│
├─> Orchestrator sees pending_intent = "cancel_order" in context
├─> Extracts order_id = "ORD-1234" from message
├─> Routes to OrderCancellationAgent with order ID
├─> Agent processes cancellation
├─> Clears pending_intent from context
└─> Response: "Your order ORD-1234 has been cancelled. Refund processed."
```

**State Management**:
- `context["order_id"]`: Persists across conversation for reuse
- `context["pending_intent"]`: Tracks incomplete requests
- `state.last_agent`: Records which agent last handled request
- Redis automatically saves state after each turn

---

## How to Build and Run the System

### Prerequisites

- **Docker & Docker Compose** (required for running the application)
- **OpenAI API Key** (with access to Vector Store API)
- **Git** (for cloning repository)

### Quick Start with Docker

**1. Clone the Repository**
```bash
git clone https://github.com/NamrataChakka/Basic-MultiAgent-CustomerSupport.git
cd Basic-MultiAgent-CustomerSupport
```

**2. Create Environment File**

Create a `.env` file in the project root:
```bash
# Required
OPENAI_API_KEY=sk-proj-<your-actual-key-here>
OPENAI_MODEL=<your chosen model here>

# Will be auto-generated during vector store setup
PRODUCT_VECTOR_STORE_ID=vs_...

```

**3. Start the Application**
```bash
docker-compose up
```

**4. Pull the LLM Judge Model** (One-Time Setup)

In a new terminal, pull the llama3:instruct model for the LLM judge:

```bash
docker exec -it ollama ollama pull llama3:instruct
```

This downloads the ~4GB model to the Ollama container (stored in persistent volume).

**5. Initialize OpenAI Vector Store** (One-Time Setup)

The ProductInfoAgent requires a vector store with embedded product information:

```bash
# Initialize vector store using Docker
docker-compose run --rm app python -c "from app.utils.read_write_ops import create_vector_store; create_vector_store('app/dataset/products.json')"
```

This uploads `products.json` to OpenAI's Files API, creates a vector store, and automatically appends the `PRODUCT_VECTOR_STORE_ID` to your `.env` file.

**6. Access the API**
- Base URL: `http://0.0.0.0:8000`
- Endpoint: `POST /chat`

**7. Test the Endpoint**
```bash
curl --location 'http://0.0.0.0:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "session_id": "user_123",
    "message": "track my order. ORD-1234"
}'
```

Expected response will include a `judge_score` field (1-5) rating the AI's response quality.

**8. Stop the Application**
```bash
# Press Ctrl+C in the terminal where docker-compose is running
# Or:
docker-compose down
```

**9. View Logs**
```bash
docker-compose logs -f app
```

### Running Tests

**Run Integration Tests**:
```bash
docker compose exec app python -m pytest app/api/api_tests/integration_tests.py
```

**Run Specific Test**:
```bash
docker compose exec app python -m pytest app/api/api_tests/integration_tests.py::test_single_turn_order_tracking_flow
```

## Structured Output Schemas

### API Endpoint Schema
```

**Response Field Descriptions**:
- `session_id`: Unique identifier for the conversation session
- `response`: Natural language response generated by the AI assistant
- `agent`: Name of the agent that handled the request (e.g., "track_order", "cancel_order")
- `handover`: Indicates agent handoff (currently always false)
- `judge_score`: Quality rating from LLM-as-a-judge (1=poor, 5=excellent). Returns null if evaluation fails.

**Example Request**:
```bash
curl --location 'http://0.0.0.0:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "session_id": "user_123",
    "message": "track my order. ORD-1234"
}'
```

**Example Response**:
```json
{
    "session_id": "user_123",
    "response": "The current status of your order ORD-1234 is pending. The estimated delivery date is December 25, 2025. If you need any more details, feel free to ask!",
    "agent": "Orchestrator -> OrderTrackingAgent",
    "tools": [
        "order_tracking_process"
    ],
    "handover": true,
    "judge_score": 5
}
```
### Internal State Schemas

#### SessionState Model
**Location**: `app/services/redis_state.py`

**Structure** (Pydantic model):
```python
class SessionState(BaseModel):
    session_id: str
    context: Dict[str, Any] = {}
    last_tool_calls: List[str] = []
    last_agent: str | None = None
    updated_at: str | None = None
```

**Container Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Redis       │  │  Ollama      │  │  App         │      │
│  │  Container   │  │  Container   │  │  Container   │      │
│  │              │  │              │  │              │      │
│  │  Port: 6379  │  │  Port: 11434 │  │  Port: 8000  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ▲                ▲                    │             │
│         │                │                    │             │
│         └────────────────┴────────────────────┘             │
│                     App connects to both                    │
│                                                              │
│                          │                                   │
└──────────────────────────│───────────────────────────────────┘
                           │
                           │ Volume Mounts
                           ├─ .:/app (source code)
                           └─ ollama_data (models)
                           ▼
                     Host Filesystem
```