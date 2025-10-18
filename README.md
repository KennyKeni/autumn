# Autumn

Autumn is an intelligent document analysis and chat platform built with FastAPI and LlamaIndex. It enables users to organize documents into collections and partitions, automatically generate embeddings, and interact with document content through an AI-powered chat interface.

## Overview

Autumn provides a backend API for managing document collections, embedding documents into vector databases, and querying them through natural language conversations. The system leverages multiple AI models and vector databases to create a sophisticated document retrieval and query engine.

## Key Features

- **Document Management**: Upload and manage files with support for multiple MIME types
- **Collections & Partitions**: Organize documents into hierarchical collections and partitions with customizable embeddings and configurations
- **Vector Embeddings**: Automatic document embedding using configurable embedding models (FastEmbed)
- **Multi-Index Support**: Create different types of indices for each document (Summary and Vector indices)
- **AI-Powered Chat**: Query documents through a conversational interface powered by multiple LLM providers
- **Tool Generation**: Automatically generate specialized tools for each document within a partition
- **Cloud Storage Integration**: S3 bucket integration for file storage with presigned URLs
- **Health Monitoring**: Comprehensive health check endpoints for all services
- **Presigned URL Support**: Secure file uploads and downloads via presigned S3 URLs

## Technology Stack

### Backend & API
- **FastAPI** (>=0.116.0) - Modern async web framework
- **Pydantic** (>=2.11.7) - Data validation and settings management
- **Uvicorn** - ASGI application server

### AI/ML & Embeddings
- **LlamaIndex** (>=0.12.47) - Document indexing and retrieval framework
- **FastEmbed** (>=0.7.1) - Fast embedding model inference with caching
- **Transformers** (>=4.53.2) - Hugging Face transformers with PyTorch
- **LLaMA-Index Integrations**:
  - OpenAI-like LLMs (OpenRouter, DeepInfra, Novita)
  - OpenAI embeddings
  - Qdrant vector store support

### Databases
- **PostgreSQL** (asyncpg, psycopg2) - Primary relational database
- **Qdrant** - Vector database for similarity search
- **Redis/Dragonfly** - In-memory cache and session management

### Storage
- **S3/MinIO** - Cloud object storage (aioboto3)
- **SQLAlchemy** (>=2.0.41) - ORM with async support

### Development & DevOps
- **Alembic** - Database migrations
- **Black** - Code formatting
- **isort** - Import sorting
- **Pyright** - Static type checking (strict mode)
- **Docker & Docker Compose** - Containerization
- **Nix** - Reproducible builds

## Project Structure

```
autumn/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management (Pydantic)
│   ├── constants.py            # Environment constants
│   ├── model.py                # SQLAlchemy base models
│   ├── database.py             # Database connection managers
│   ├── lifespan.py             # FastAPI lifespan events
│   ├── manager.py              # FastEmbed model manager with caching
│   ├── factory.py              # Factory functions for dependencies
│   ├── dependencies.py         # Shared dependency injections
│   ├── repository.py           # Base repository pattern
│   ├── exceptions.py           # Custom exceptions
│   ├── utils.py                # Utility functions
│   ├── llamaindex_patch/       # Custom patches for LlamaIndex
│   │   ├── node_mapping/       # Tool ID mapping
│   │   └── stores/             # Custom vector store implementations
│   ├── files/                  # File management module
│   │   ├── models/             # File SQLAlchemy models
│   │   ├── router.py           # File API endpoints
│   │   ├── service.py          # File business logic
│   │   ├── repository.py       # File database access
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── config.py           # Module configuration
│   │   ├── constants.py        # File constants (MIME types, status)
│   │   ├── dependencies.py     # File-specific dependencies
│   │   ├── exceptions.py       # File-specific exceptions
│   │   └── utils.py            # File utilities
│   ├── collections/            # Collection management module
│   │   ├── models/             # Collection models
│   │   ├── router.py           # Collection API endpoints
│   │   ├── service.py          # Collection business logic
│   │   ├── repository.py       # Collection database access
│   │   ├── schemas/            # Request/response schemas
│   │   ├── config.py           # Qdrant collection settings
│   │   ├── constants.py        # Collection constants
│   │   ├── dependencies.py     # Collection dependencies
│   │   └── utils.py            # Collection utilities
│   ├── partitions/             # Partition management module
│   │   ├── models/             # Partition, PartitionFile, PartitionFileTool models
│   │   ├── router.py           # Partition API endpoints
│   │   ├── service.py          # Partition business logic
│   │   ├── repository.py       # Partition database access
│   │   ├── schemas/            # Request/response schemas
│   │   ├── constants.py        # Partition constants and tool types
│   │   ├── dependencies.py     # Partition dependencies
│   │   └── utils.py            # Partition utilities
│   ├── embedding/              # Embedding generation module
│   │   ├── router.py           # Embedding API endpoints (WIP)
│   │   ├── service.py          # Embedding business logic
│   │   ├── repository.py       # Embedding-related data access
│   │   ├── schemas/            # Request/response schemas
│   │   ├── config.py           # Embedding configuration
│   │   ├── constants.py        # Embedding model constants
│   │   ├── dependencies.py     # Embedding dependencies
│   │   └── utils.py            # Embedding utilities
│   ├── chat/                   # Chat/query module
│   │   ├── router.py           # Chat API endpoints
│   │   ├── service.py          # Chat business logic (agent-based queries)
│   │   ├── schemas/            # Request schemas
│   │   ├── constant.py         # System prompts
│   │   ├── dependencies.py     # Chat dependencies
│   │   └── __init__.py
│   └── tools/                  # Tool management module
│       ├── tool_handler.py     # Abstract tool handler classes
│       ├── service.py          # Tool creation and management
│       ├── dependencies.py     # Tool dependencies
│       ├── constants.py        # Tool type constants
│       └── utils.py            # Tool utilities
├── alembic/                    # Database migration configuration
│   ├── versions/               # Migration files
│   └── env.py, script.py.mako
├── docker-compose.yml          # Multi-service Docker setup
├── pyproject.toml              # Python project configuration
├── alembic.ini                 # Alembic configuration
├── Makefile                    # Common commands
├── .python-version             # Python version specification
└── .gitignore

```

## Core Concepts

### Collections
Collections are top-level containers for organizing documents. Each collection:
- Has configurable embedding models (e.g., BAAI/bge-small-en-v1.5)
- Specifies vector database parameters (dimension, distance metric, shards, replicas)
- Stores metadata about vector database configuration
- Contains multiple partitions

### Partitions
Partitions are sub-divisions within a collection for organizing related documents. Each partition:
- Belongs to a single collection
- Contains metadata about indexed files
- Has an optional system prompt for customizing LLM behavior
- Serves as a query context for the chat interface

### Partition Files
PartitionFiles represent documents associated with a partition. Each partition file:
- Links a file to a partition
- Manages multiple tool instances for different query strategies
- Supports both vector and summary-based queries

### Tools
Autumn supports multiple tool types for querying documents:
- **Vector Tools**: Semantic similarity-based search across document content
- **Summary Tools**: Hierarchical summarization-based search for technical content

### Embeddings
The system uses:
- **FastEmbed**: For local embedding generation with automatic model caching
- **Qdrant**: For vector storage and similarity search
- **Custom Sparse Encoders**: For hybrid search capabilities

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - System health check (PostgreSQL, Redis, Qdrant, S3)

### Files Management (`/files`)
- `GET /files` - List all files (paginated)
- `GET /files/{file_id}` - Get file details
- `POST /files/presigned` - Generate presigned URL for file upload
- `PUT /files/presigned/confirm/{file_id}` - Confirm file upload
- `DELETE /files/{file_id}` - Mark file as deleted

### Collections (`/collections`)
- `POST /collections` - Create a new collection
- `DELETE /collections/{collection_id}` - Delete a collection

### Partitions (`/partitions`)
- `POST /partitions` - Create a new partition
- `POST /partitions/{partition_id}/files/{file_id}` - Add file to partition
- `DELETE /partitions/{partition_id}` - Delete a partition

### Chat (`/chat`)
- `POST /chat/{partition_id}` - Query a partition with natural language

### Embeddings (`/embed`)
Currently under development - endpoints for explicit embedding operations

## Configuration

The application is configured via environment variables through Pydantic Settings:

### Database Configuration
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `POSTGRES_POOL_SIZE`, `POSTGRES_MAX_OVERFLOW`

### Vector Database (Qdrant)
- `QDRANT_HOST`, `QDRANT_HTTP_PORT`, `QDRANT_GRPC_PORT`
- `QDRANT_HTTPS`, `QDRANT_API_KEY`, `QDRANT_TIMEOUT`

### Cache (Redis/Dragonfly)
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_MAX_CONNECTIONS`

### Cloud Storage (S3)
- `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET`

### LLM Providers
- `OPENROUTER_API_KEY` - OpenRouter API key
- `NOVITA_API_KEY` - Novita API key
- `DEEPINFRA_API_KEY` - DeepInfra API key

### Application
- `CORS_ORIGINS` - Allowed CORS origins (default: "*")
- `CORS_HEADERS` - Allowed CORS headers (default: "*")
- `ENVIRONMENT` - Environment (development/staging/production)
- `APP_VERSION` - Application version

## Getting Started

### Prerequisites
- Python 3.13+
- Docker and Docker Compose
- PostgreSQL 14+
- Qdrant
- Redis/Dragonfly

### Local Development

1. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start development server**:
   ```bash
   python -m src.main
   # or
   uvicorn src.main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
docker-compose up
```

This starts:
- PostgreSQL database
- Qdrant vector database
- Dragonfly (Redis-compatible) cache
- Autumn application (when configured)

## Database Schema

Key tables:
- **files** - File metadata and S3 references
- **collections** - Document collections with embedding configurations
- **partitions** - Subdivisions of collections
- **partition_files** - Links between files and partitions
- **partition_file_tools** - Tool instances for each partition file

See `alembic/versions/` for detailed schema migrations.

## Development

### Code Quality
- Format: `black src/`
- Sort imports: `isort src/`
- Remove unused imports: `autoflake --in-place --remove-all-unused-imports -r src/`
- Type check: `pyright`

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

## Performance Considerations

- **Model Caching**: FastEmbed models are cached with TTL (default 30 minutes)
- **Vector Database**: Uses HNSW algorithm with configurable parameters
- **Async/Await**: Full async/await support for concurrent operations
- **Connection Pooling**: SQLAlchemy connection pool for database efficiency
- **Presigned URLs**: Secure direct S3 uploads without proxying

## Future Enhancements

- Additional tool types (QA, Named Entity Extraction)
- Streaming chat responses
- Document metadata extraction
- Fine-tuning support for embedding models
- Advanced analytics and usage tracking
- Multi-language support

## License

This project is private and proprietary.

