# AI Customer Support Chatbot

AI-powered customer support application built with Angular, FastAPI, Ollama, RAG and SQLite.

The application combines a traditional customer-support interface with a locally hosted LLM, retrieval-augmented generation, conversation memory, authentication and user-specific order access.

## Features

- AI customer support chat
- Local LLM using Ollama
- Retrieval-Augmented Generation (RAG)
- Semantic search over store documentation
- Product, shipping, returns and warranty knowledge base
- Intent classification
- Order status support
- Follow-up questions using conversation history
- Guest conversations
- Guest conversation transfer after login/register
- User registration and login
- JWT authentication
- User-specific conversation history
- User-specific order access
- Protection against unauthorized conversation/order access
- Source display for RAG answers
- Angular HTTP interceptor for JWT authentication
- Dockerized frontend and backend

## Tech Stack

### Frontend

- Angular
- TypeScript
- Angular Signals
- Angular HttpClient
- HTML / CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- JWT authentication

### AI / RAG

- Ollama
- Qwen3 8B
- nomic-embed-text
- ChromaDB
- Retrieval-Augmented Generation

### Infrastructure

- Docker
- Docker Compose

## Architecture

```text
Angular Frontend
       |
       | HTTP / JWT
       v
FastAPI Backend
       |
       +------------------------+
       |                        |
       v                        v
Intent Classification      SQLite Database
       |                    - users
       |                    - conversations
       |                    - messages
       |                    - orders
       |
       +------------+
       |            |
       v            v
     RAG         Order Service
       |
       v
   ChromaDB
       |
       v
Knowledge Base
       |
       v
Ollama
Qwen3 8B
```

## Chat Flow

A user can use the chatbot without creating an account.

For general questions such as:

```text
How long does delivery take?
```

or:

```text
What warranty do the headphones have?
```

the backend retrieves relevant information from the knowledge base and provides it to the local LLM.

For questions involving private data, such as:

```text
Where is order #12345?
```

the user must be authenticated.

Order queries are filtered using both the order ID and the authenticated user's ID.

## Retrieval-Augmented Generation

The knowledge base currently contains information about:

- products
- shipping
- returns
- warranty

Documents are split into chunks and embedded using:

```text
nomic-embed-text
```

The embeddings are stored in ChromaDB.

When a customer asks a question:

```text
User question
      ↓
Query rewriting
      ↓
Embedding
      ↓
Semantic search
      ↓
Relevant knowledge chunks
      ↓
Qwen3
      ↓
Final answer
```

Conversation history is also used to resolve follow-up questions.

Example:

```text
User:
What headphones do you sell?

Assistant:
...

User:
How much are they?
```

The system can use the previous messages to determine what "they" refers to.

## Intent Classification

The application distinguishes between general knowledge questions and order-related requests.

Example:

```text
What is your return policy?
→ knowledge
```

```text
Where is my order?
→ order_status
```

Order information is handled by backend business logic instead of being retrieved from the RAG knowledge base.

## Authentication

The backend uses JWT authentication.

Supported operations include:

```text
POST /auth/register
POST /auth/login
```

After authentication, the frontend sends:

```text
Authorization: Bearer <JWT>
```

using an Angular HTTP interceptor.

Passwords are stored as hashes rather than plain text.

## Guest Sessions

Users can chat without logging in.

A guest receives a randomly generated session identifier:

```text
guest_session_id
```

This allows the backend to preserve conversation context between messages.

If the guest later logs in or creates an account, the existing guest conversation can be assigned to that user so the conversation can continue without losing its history.

## Authorization and Data Isolation

Authentication alone is not used as authorization.

User-owned resources are queried using both the resource identifier and the authenticated user's ID.

For example:

```python
Order.id == order_id
Order.user_id == current_user.id
```

and:

```python
Conversation.id == conversation_id
Conversation.user_id == current_user.id
```

This prevents a user from accessing another user's conversations or orders by manually changing an ID.

## Running the Project

### Requirements

Install:

- Docker Desktop
- Ollama

The application currently uses:

```text
qwen3:8b
nomic-embed-text
```

Pull the models:

```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

Make sure Ollama is running.

```bash
ollama serve
```

## Start with Docker

From the project root:

```bash
docker compose up --build
```

The services will be available at:

```text
Frontend:
http://localhost:4200

Backend:
http://localhost:8000

FastAPI Swagger:
http://localhost:8000/docs

Ollama:
http://localhost:11434
```

## Environment Configuration

Create a `.env` file in the backend directory.

Example:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
EMBEDDING_MODEL=nomic-embed-text
FRONTEND_URL=http://localhost:4200
CHROMA_PATH=data/chroma
JWT_SECRET_KEY=your-secret-key
```

The `.env` file should not be committed to Git.

Use `.env.example` to document the required configuration.

When the backend runs inside Docker, Docker Compose can override the Ollama address with:

```text
http://host.docker.internal:11434
```

## Knowledge Base

Knowledge documents are stored in:

```text
backend/knowledge/
```

Examples:

```text
products.md
shipping.md
returns.md
warranty.md
```

After modifying the knowledge base, rebuild the RAG index from the backend directory:

```bash
python -m app.rag.ingest
```

## Example Questions

General support:

```text
What products do you sell?
```

```text
How long does shipping take?
```

```text
Can I return a product after 20 days?
```

```text
What warranty do the wireless headphones have?
```

Follow-up conversation:

```text
What headphones do you sell?
How much are they?
Do they have a warranty?
```

Authenticated order support:

```text
Where is order #12345?
```

```text
Who is the carrier?
```

```text
When should it arrive?
```

```text
Can I cancel it?
```

## Security

The project includes several basic security measures:

- JWT authentication
- hashed passwords
- input validation with Pydantic
- restricted CORS configuration
- protected conversation history
- user-specific order access
- user-specific conversation access
- authorization checks performed in backend code
- environment variables for sensitive configuration
- no reliance on the LLM for access control

The LLM receives only data that the backend has already authorized.

## Purpose

The project was created as a portfolio application demonstrating how traditional web development can be combined with modern AI techniques.

It covers:

- frontend/backend integration
- REST APIs
- authentication and authorization
- relational data persistence
- local LLM integration
- embeddings
- vector search
- RAG
- conversation memory
- prompt design
- intent classification
- Docker-based development

The project is designed so that the AI component assists the customer while sensitive operations remain controlled by deterministic backend logic.
