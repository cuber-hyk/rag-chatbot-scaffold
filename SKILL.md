---
name: rag-chatbot-scaffold
description: Generate a complete RAG chatbot project with three-layer architecture, multi-vector database support, multi-LLM provider support, file parsing, session management, and network search. Use when creating new RAG-based chatbot projects or scaffolding conversational AI applications.
---

# RAG Chatbot Scaffold

Instant generation of production-ready RAG chatbot projects with enterprise-grade architecture.

## Overview

This Skill generates a complete RAG chatbot project with sensible defaults:
- **Three-layer architecture**: API → Service → Repository
- **Multi-vector database**: Weaviate (default), Qdrant, Pinecone
- **Multi-LLM provider**: OpenAI, Anthropic, Azure (with SiliconCloud support)
- **Document parsing**: PDF, Markdown, Word, Plain Text via LangChain
- **Document deduplication**: Smart duplicate detection with conflict handling
- **Redis session management**
- **Network search**: DuckDuckGo (free), Tavily (optional)
- **API Key authentication**: Simple and secure

## Quick Start

**Just use the skill!** The project will be generated with sensible defaults:

```bash
# Run this in Claude Code
/skill
```

The skill will create a complete project with:
- Project name: `my-rag-chatbot` (you can rename later)
- Vector DB: Weaviate (http://localhost:8080)
- LLM: OpenAI-compatible (configurable base URL)
- Embedding: BAAI/bge-large-zh-v1.5
- Search: DuckDuckGo (no API key needed)

## After Generation

1. **Navigate to the project**:
   ```bash
   cd my-rag-chatbot
   ```

2. **Configure API keys**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies**:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate  # Windows
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   python main.py
   ```

## Customization

After generation, you can modify settings in:

### `config/providers.yaml` - Provider Selection
```yaml
llm:
  provider: openai           # openai, anthropic, azure
  base_url: https://api.siliconflow.cn/v1  # For SiliconCloud
  model: gpt-4o

vector_db:
  provider: weaviate        # weaviate, qdrant, pinecone
```

### `.env` - API Keys
```env
OPENAI_API_KEY=sk-xxx
API_KEY=  # Leave empty to disable auth
```

## Configuration Options

### Vector Database
- **weaviate** (default): Local or cloud, Weaviate v4 client
- **qdrant**: Local or remote Qdrant
- **pinecone**: Cloud-based Pinecone

### LLM Providers
- **openai** (default): GPT models via OpenAI API
- **anthropic**: Claude models via Anthropic API
- **azure**: Azure OpenAI
- **siliconcloud/moonshot**: Use `openai` provider with custom `base_url`

### Search Tools
- **duckduckgo** (default): Free, no API key required
- **tavily**: High-quality search, requires `TAVILY_API_KEY`

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

## Configuration

The generated project uses a **three-file configuration structure**:

### config/application.yaml
Application settings (project info, API, documents, features)

### config/providers.yaml
Provider selection and connections (LLM, embedding, vector DB, search)

### config/prompts.yaml
System prompts for the chatbot

### .env
API keys (never committed to git)

### Configuration Priority
1. Defaults from Settings class
2. application.yaml / providers.yaml values
3. .env overrides (for API keys only)

## Weaviate v4 Client

The scaffold uses **Weaviate Python Client v4** with correct imports:
```python
from weaviate.classes.config import Configure, Property, DataType
```

## Adding New Features

For extending the scaffold with new features, refer to the generated project's inline documentation.

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
