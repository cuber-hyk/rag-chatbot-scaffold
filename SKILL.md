---
name: rag-chatbot-scaffold
description: Generate a complete RAG chatbot project with three-layer architecture, multi-vector database support, multi-LLM provider support, file parsing, session management, and network search. Use when creating new RAG-based chatbot projects or scaffolding conversational AI applications.
---

# RAG Chatbot Scaffold

Fast generation of production-ready RAG chatbot projects with enterprise-grade architecture.

## Overview

This Skill generates a complete RAG chatbot project with:
- **Three-layer architecture**: API → Service → Repository
- **Multi-vector database**: Qdrant, Weaviate, Pinecone with plugin interface
- **Multi-LLM provider**: OpenAI, Anthropic, SiliconCloud, Azure with preset templates
- **Document parsing**: PDF, Markdown, Word, Plain Text
- **API Key authentication**
- **Redis session management**
- **Network search**: DuckDuckGo, Tavily
- **Configuration**: YAML + .env
- **Dynamic generation**: Placeholder substitution based on user config

## Quick Start

1. Copy project configuration template:
   ```bash
   cp project_config.yaml.example my_project_config.yaml
   ```

2. Edit `my_project_config.yaml` with your preferences:
   ```yaml
   project:
     name: my-chatbot
     description: "My RAG chatbot"
     version: "0.1.0"

   api:
     host: "0.0.0.0"
     port: 8000
     version_prefix: "v1"

   vector_db:
     provider: qdrant      # or weaviate, pinecone
     collection_name: documents

   llm:
     provider: openai      # or anthropic, siliconcloud, azure
     temperature: 0.7
     max_tokens: 2048

   search:
     provider: duckduckgo   # or tavily
     max_results: 5
   ```

3. Run the project generator:
   ```bash
   python scripts/generate_project.py my_project_config.yaml
   ```

The generator will:
- Create the project directory structure
- Generate `config/config.yaml` with your settings
- Copy appropriate LLM and Vector DB config files
- Substitute placeholders in templates with your values

## Instructions

### Step 1: Prepare Project Configuration

The project is generated from a configuration file (`project_config.yaml`). You define:
- Project metadata (name, description, version)
- Vector database choice and settings
- LLM provider and model settings
- Search tool configuration
- Session and authentication settings
- Document parsing settings

### Step 2: Configure Environment Variables

The generated project includes a `.env.example` file. Copy it and configure:
```bash
cd <project_name>
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables depend on your choices:
- **LLM**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SILICONCLOUD_API_KEY`, etc.
- **Vector DB**: `QDRANT_URL`, `WEAVIATE_URL`, `PINECONE_API_KEY`, etc.
- **Session**: `REDIS_URL`
- **Search**: `TAVILY_API_KEY` (if using Tavily)
- **Auth**: `API_KEY` (if using API Key authentication)

### Step 3: Install Dependencies

```bash
cd <project_name>
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Start Development Server

```bash
python main.py
```

The API will be available at `http://{host}:{port}` (from your config)

## Project Structure

The generated project follows three-layer architecture:

```
<project_name>/
├── config/                   # Configuration Files
│   ├── config.yaml           # Main config (generated from user input)
│   ├── llm.yaml             # LLM presets (copied based on provider)
│   └── vector_db.yaml        # Vector DB config (copied based on provider)
├── src/
│   ├── api/                    # API Layer
│   │   ├── v1/
│   │   │   └── endpoints/      # REST endpoints
│   │   └── dependencies.py      # Dependency injection
│   ├── services/               # Service Layer
│   │   ├── chat_service.py     # Chat logic
│   │   ├── document_service.py # Document processing with LangChain parsers
│   │   └── session_service.py  # Session management
│   ├── repositories/           # Repository Layer
│   │   ├── vector_repository.py # Vector DB abstraction
│   │   ├── qdrant_repository.py # Qdrant implementation
│   │   ├── weaviate_repository.py # Weaviate v4 implementation
│   │   ├── pinecone_repository.py # Pinecone implementation
│   │   └── session_repository.py # Session storage
│   ├── models/                 # Data Models
│   │   └── schemas/           # Pydantic schemas
│   ├── core/                  # Core Infrastructure
│   │   ├── config/            # Configuration management (reads config.yaml)
│   │   └── security/          # Security
│   ├── parsers/               # LangChain Document Loaders + Text Splitters
│   └── tools/                 # LangChain Tools
├── tests/                     # Tests
│   └── test_api.py
├── scripts/                 # Utility scripts
├── main.py                 # Application entry
├── requirements.txt         # Dependencies
├── .env.example           # Environment template
└── README.md
```

## Configuration Options

### Vector Database (Default: Weaviate)
- `weaviate`: Weaviate Cloud or self-hosted (default)
- `qdrant`: Local or remote Qdrant
- `pinecone`: Pinecone vector database

To switch vector databases, modify `vector_db.provider` in your project config.

### LLM Providers
- `openai`: GPT models via OpenAI API
- `anthropic`: Claude models via Anthropic API
- `siliconcloud`: SiliconCloud (GLM, Qwen, etc.)
- `azure`: Azure OpenAI

### Search Tools
- `duckduckgo`: Free web search, no API key required
- `tavily`: High-quality search, requires API key

### File Parsers
- `pdf`: PDF document parsing
- `markdown`: Markdown parsing
- `word`: Word document parsing
- `text`: Plain text parsing

## Repository Pattern

The scaffold uses an abstract `VectorRepository` interface:

```python
class VectorRepository(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[Document], collection_name: str) -> int:
        """Add documents to vector store"""

    @abstractmethod
    async def search(self, query: str, collection_name: str, top_k: int = 5) -> List[Document]:
        """Search for similar documents"""

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
```

Implementations:
- `QdrantRepository`: Qdrant backend
- `WeaviateRepository`: Weaviate backend
- `PineconeRepository`: Pinecone backend

## Configuration System

The project uses a two-tier configuration system with **flat field structure**:

### 1. config/config.yaml (Flat Structure)
- Contains all non-sensitive configuration
- Uses **flat field names** that directly map to `Settings` class fields
- Generated from user's `project_config.yaml`
- Settings class loads this file at startup

Example:
```yaml
# Flat structure - matches Settings class fields
project_name: my-chatbot
project_description: A RAG chatbot
version: 0.1.0
api_host: 0.0.0.0
api_port: 8000
vector_db_provider: qdrant
llm_provider: openai
```

### 2. .env
- Contains sensitive data (API keys)
- Loaded by pydantic-settings BaseSettings
- Values from .env override defaults from config.yaml

### Important: Flat vs Nested Structure

The `config/config.yaml` **must use flat field names**, not nested structure:

```yaml
# ✅ CORRECT - Flat structure
project_name: my-chatbot
api_port: 8000

# ❌ INCORRECT - Nested structure (won't work)
project:
  name: my-chatbot
api:
  port: 8000
```

This is because the `Settings` class uses `Settings(**config_dict)` to load the YAML, and nested structures won't map correctly to the class fields.

### Configuration Hierarchy

1. **Defaults**: From `Settings` class Field(default=...)
2. **config.yaml**: Overrides defaults (flat structure required)
3. **.env**: Overrides both above (for sensitive data)

This separation allows:
- Safe git commits (exclude .env with .gitignore)
- Environment-specific overrides (dev/staging/prod)
- No IDE warnings (config values are loaded at runtime)

## Weaviate v4 Client API

The scaffold uses **Weaviate Python Client v4**. Key API differences from v3:

```python
# Connection
client = weaviate.connect_to_local(host="localhost", port=8080)

# Delete collection
if client.collections.exists("collection_name"):
    client.collections.delete("collection_name")

# Health check
client.is_ready()  # v4 (was is_live() in v3)

# Close connection
client.close()
```

When adding Weaviate support, ensure `weaviate-client>=4.0.0` is in requirements.txt.

## Adding New Vector Database Support

1. Create a new repository class in `src/repositories/` inheriting from `VectorRepository`
2. Add configuration to `config/vector_db/<name>.yaml` in the skill
3. Register in `src/api/dependencies.py` (add new elif branch)
4. Add dependency in `requirements.txt`

See `config/qdrant.yaml` as a reference.

## Adding New LLM Provider

1. Create configuration in `llm/<provider>.yaml` in the skill
2. Add fields to `src/core/config/settings.py`
3. Add required packages to `requirements.txt`

See `llm/openai.yaml` as a reference.

## Adding New Document Format

1. Create parser in `src/parsers/{format}_parser.py`
2. Inherit from `BaseDocumentParser`
3. Implement `parse_from_file()` using LangChain document loaders
4. Register in `DocumentParserFactory._parsers` mapping
5. Add required packages to `requirements.txt`

Example using LangChain loader:

```python
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import YourLoader
from .base import BaseDocumentParser

class YourFormatParser(BaseDocumentParser):
    def parse_from_file(self, file_path: str) -> List[Document]:
        loader = YourLoader(file_path)
        documents = loader.load()
        return self._split_documents(documents)
```

## Document Service

The `DocumentService` uses LangChain parsers for document processing:

### Process Uploaded File (bytes)

```python
from src.services.document_service import DocumentService

result = await document_service.process_document(
    filename="document.pdf",
    content=file_bytes,
    content_type="application/pdf",
    chunk_size=1000,      # Optional: override default
    chunk_overlap=200,    # Optional: override default
)

# Returns:
# {
#     "document_id": "uuid-123",
#     "chunks_added": 15,
#     "filename": "document.pdf",
#     "content_type": "application/pdf"
# }
```

### Process File from Disk

```python
result = await document_service.process_document_file(
    file_path="/path/to/document.pdf",
    content_type="application/pdf",  # Optional
    chunk_size=1000,
    chunk_overlap=200,
)
```

### Document Processing Flow

```
File Upload → DocumentService
              ↓
         1. File Size Validation
              ↓
         2. Get Parser (PDF/Markdown/Word/Text)
              ↓
         3. Save to Temp File (for bytes input)
              ↓
         4. Parser.parse_from_file()
              ├─ LangChain Document Loader
              └─ RecursiveCharacterTextSplitter
              ↓
         5. Enhance Metadata (document_id, filename, etc.)
              ↓
         6. VectorRepository.add_documents()
```

## API Endpoints

### Health
```
GET /health
```

### Chat
```
POST /api/v1/chat
Headers: X-API-Key
Body: { "query": "string" }
Response: { "response": "string", "thread_id": "string" }
```

### Session Management
```
GET /api/v1/sessions/:thread_id
DELETE /api/v1/sessions/:thread_id
GET /api/v1/sessions
```

### Documents

Upload a document:
```
POST /api/v1/documents/upload
Headers: X-API-Key
Form: file=<document>
Response: { "document_id": "uuid", "chunks_added": 15 }
```

List all documents:
```
GET /api/v1/documents
Headers: X-API-Key
Response: { "documents": [{ "document_id": "...", "filename": "...", "chunk_count": 5 }] }
```

Get document chunks:
```
GET /api/v1/documents/:document_id/chunks
Headers: X-API-Key
Response: { "chunks": [...] }
```

Delete a document:
```
DELETE /api/v1/documents/:document_id
Headers: X-API-Key
Response: { "success": true }
```

Get document statistics:
```
GET /api/v1/documents/stats
Headers: X-API-Key
Response: { "total_documents": 10, "total_chunks": 150 }
```

## Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=src tests/
```

## Best Practices

- **API Key Management**: Store API keys in `.env`, never commit to git
- **Session TTL**: Configure Redis TTL for session cleanup
- **Vector Collection**: Use separate collections for different document types
- **Error Handling**: The scaffold includes proper error handling and logging
- **Model Selection**: Use `config/llm.yaml` to easily switch between models
- **Config Separation**: Keep sensitive data in .env, other config in config.yaml

## Requirements

The generated project requires:
- Python 3.10+
- Redis (for session management)
- Vector database (Qdrant/Weaviate/Pinecone)
- LLM provider API access

### Base Dependencies
- fastapi>=0.115.0
- uvicorn>=0.41.0
- langchain>=1.2.0
- langchain-core>=1.2.0
- langchain-openai>=1.1.0
- langchain-community>=0.4.0
- langchain-text-splitters>=1.1.0
- redis>=7.1.0
- langgraph-checkpoint-redis>=0.3.5
- qdrant-client>=1.17.0 (if using Qdrant)
- weaviate-client>=4.0.0 (if using Weaviate) - **Uses v4 client API**
- pinecone-client>=5.0.0 (if using Pinecone)
- pypdf>=6.7.0
- docx2txt>=0.8 (for Word documents)
- beautifulsoup4>=4.14.0
- python-dotenv>=1.2.0
- duckduckgo-search>=8.1.0
- tavily-python>=0.5.0 (optional)

### Document Loaders

The scaffold uses official LangChain document loaders:

| Format | Loader | Package |
|--------|--------|---------|
| PDF | `PyPDFLoader` | langchain_community |
| Markdown | `TextLoader` + `MarkdownHeaderTextSplitter` | langchain_community |
| Word | `Docx2txtLoader` | langchain_community |
| Plain Text | `TextLoader` | langchain_community |

### Text Splitting

All parsers support optional text splitting using `RecursiveCharacterTextSplitter`:

```python
parser = DocumentParserFactory.get_parser(
    "document.pdf",
    chunk_size=1000,
    chunk_overlap=200,
    enable_splitting=True
)
docs = parser.parse_from_file("document.pdf")
```

## Advanced Usage

### Custom Prompt Templates

Edit `config/prompts.yaml` to customize system prompt:

```yaml
prompts:
  system: |
    You are a helpful AI assistant.
    Use the following tools:
    - vector_search: For finding information in uploaded documents
    - search: For finding current information online
```

### Adding Custom Tools

1. Create tool in `src/tools/`
2. Import and add to `chat_service.py`
3. Update requirements.txt if needed

### Adding New API Endpoints

1. Create endpoint file in `src/api/v1/endpoints/`
2. Register in `src/api/v1/__init__.py`
3. Add dependencies if needed

## Examples

See `examples.md` file for:
- Full project generation example
- Custom vector database setup
- Multi-LLM provider configuration
- Custom tool development
