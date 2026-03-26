# Customer Support Multi-Agent API

FastAPI service for a multi-agent customer support workflow. The project routes incoming requests to specialized agents for order tracking, order cancellation, and product information.

## Features

- FastAPI chat endpoint for session-based support conversations
- Intent routing through an orchestrator agent
- Redis-backed session state
- OpenAI-powered intent detection and agent execution
- Product lookup support backed by a vector store

## Project Structure

- `app/api`: API entrypoint and tests
- `app/agents`: orchestrator and specialist agents
- `app/services`: Redis and API support services
- `app/utils`: helpers and vector store lookup utilities
- `app/dataset`: sample order and product data

## Requirements

- Python 3.11+
- Redis
- OpenAI API key

## Environment Variables

Create a `.env` file from `.env.example` and set the required values.

- `OPENAI_API_KEY`: OpenAI API key
- `PRODUCT_VECTOR_STORE_ID`: vector store identifier for product lookup
- `REDIS_URL`: optional, defaults to `redis://localhost:6379/0`

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Run With Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## API

### `POST /chat`

Request body:

```json
{
  "session_id": "session-123",
  "message": "Where is my order ORD-1001?"
}
```

Example response:

```json
{
  "session_id": "session-123",
  "response": "Your order is in transit.",
  "agent": "Orchestrator -> OrderTrackingAgent",
  "handover": true
}
```
