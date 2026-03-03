# {project_name}

{project_description}

## Version
{version}

## Features

- **RAG Integration**: Upload and query documents using vector similarity search
- **Network Search**: Real-time information retrieval via web search
- **Multi-LLM Support**: Compatible with OpenAI, Anthropic, SiliconCloud, and Azure
- **Multi-Vector DB**: Supports Qdrant, Weaviate, and Pinecone
- **Document Deduplication**: Smart duplicate detection with conflict handling
- **Session Management**: Conversation history via Redis
- **Document Parsing**: Support for PDF, Markdown, Word, and Plain Text

## Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Start Services

Ensure required services are running:
- Redis: `docker run -d -p 6379:6379 redis:alpine`
- Vector DB: Depends on your choice (see configuration)

### 4. Run the Application

```bash
python main.py
```

The API will be available at `http://{host}:{port}`

## API Documentation

Once running, visit:
- Swagger UI: `http://{host}:{port}/docs`
- ReDoc: `http://{host}:{port}/redoc`

## Configuration

### Vector Database

Choose one of:
- **Qdrant**: Set `QDRANT_URL` in `.env`
- **Weaviate**: Set `WEAVIATE_URL` in `.env`
- **Pinecone**: Set `PINECONE_API_KEY` and `PINECLOUD_ENVIRONMENT` in `.env`

### LLM Provider

Choose one and set the corresponding API key:
- **OpenAI**: `OPENAI_API_KEY`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **SiliconCloud**: `SILICONCLOUD_API_KEY`
- **Azure**: `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_DEPLOYMENT`

### Search Tool

- **DuckDuckGo**: No API key required
- **Tavily**: Set `TAVILY_API_KEY`

## API Endpoints

### Health Check
```
GET /health
```

### Chat
```
POST /api/{version_prefix}/chat
Headers: X-API-Key: <your-api-key>
Body: {"query": "Your question"}
Response: { "response": "string", "thread_id": "string" }
```

### Document Upload
```
POST /api/{version_prefix}/documents
Headers: X-API-Key: <your-api-key>
Form: file=<document>
Query: on_conflict=error|replace|skip

# on_conflict options:
# - error (default): Return conflict info
# - replace: Delete existing and replace
# - skip: Skip upload if duplicate exists
```

**Response (Success):**
```json
{
  "success": true,
  "document_id": "uuid-123",
  "chunks_added": 10,
  "message": "Document processed successfully"
}
```

**Response (Filename Conflict):**
```json
{
  "success": false,
  "error": "filename_conflict",
  "message": "文件名已存在但内容不同。请选择：覆盖或修改文件名"
}
```

**Response (Duplicate Content):**
```json
{
  "success": false,
  "error": "duplicate_content",
  "message": "文档内容已存在（文件名: other_file.txt）"
}
```

### Session Management
```
GET /api/{version_prefix}/sessions/:thread_id
Response: { "thread_id": "string", "data": {...} }

DELETE /api/{version_prefix}/sessions/:thread_id
Response: { "success": true, "message": "..." }

GET /api/{version_prefix}/sessions
Response: { "sessions": ["thread_id1", "thread_id2"] }
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows:
- PEP 8 for Python code
- Three-layer architecture (API → Service → Repository)

## License

MIT
