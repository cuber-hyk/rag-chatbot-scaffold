# Examples

> **Important Note**: This file shows the **input configuration** (`project_config.yaml`) which uses **nested structure** for better readability. The generator automatically converts this to the **flat structure** required by `config/config.yaml`. See [Configuration Structure](#configuration-structure) below for details.

## Configuration Structure

### Input (project_config.yaml) - Nested Structure
The user input file uses nested structure for better organization:

```yaml
project:
  name: my-chatbot
  description: "My chatbot"
  version: "0.1.0"

api:
  host: "0.0.0.0"
  port: 8000
```

### Output (config/config.yaml) - Flat Structure
The generated config file uses flat structure that matches the `Settings` class:

```yaml
# Flat structure - matches Settings class fields
project_name: my-chatbot
project_description: My chatbot
version: 0.1.0
api_host: 0.0.0.0
api_port: 8000
```

This conversion happens automatically in `generate_project.py`. The flat structure ensures that `Settings(**config_dict)` can correctly map YAML values to class fields.

---

## Full Project Generation Example

```bash
# 1. Copy the configuration template
cp project_config.yaml.example my_chatbot_config.yaml

# 2. Edit configuration with your preferences
# my_chatbot_config.yaml
project:
  name: my-ai-assistant
  description: "An AI assistant with RAG capabilities"
  version: "0.1.0"

  api:
    host: "0.0.0.0"
    port: 8000
    version_prefix: "v1"

  vector_db:
    provider: qdrant
    collection_name: documents
    embedding_model: text-embedding-3-small

  llm:
    provider: openai
    temperature: 0.7
    max_tokens: 2048

  search:
    provider: duckduckgo
    max_results: 5

  session:
    ttl: 300

  auth:
    type: api_key

  documents:
    formats:
      - pdf
      - markdown
      - word
      - text
    max_file_size: 10
    chunk_size: 1000
    chunk_overlap: 200

  logging:
    level: INFO
    format: text

  features:
    websocket_enabled: false
    streaming_enabled: true

# 3. Generate the project
python scripts/generate_project.py my_chatbot_config.yaml

# 4. Navigate to the generated project
cd my-ai-assistant

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 6. Install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 7. Run the application
python main.py
```

## Different Vector Database Configurations

### Using Qdrant (Local)

Configuration:
```yaml
vector_db:
  provider: qdrant
  collection_name: documents
```

Start Qdrant with Docker:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

Environment:
```bash
# In .env
QDRANT_URL=http://localhost:6333
```

### Using Weaviate (Cloud)

Configuration:
```yaml
vector_db:
  provider: weaviate
  collection_name: documents
```

Environment:
```bash
# In .env
WEAVIATE_URL=https://your-cluster.weaviate.cloud
WEAVIATE_API_KEY=your-api-key
```

### Using Pinecone (Serverless)

Configuration:
```yaml
vector_db:
  provider: pinecone
  collection_name: documents
```

Environment:
```bash
# In .env
PINECONE_API_KEY=your-pinecone-api-key
PINECLOUD_ENVIRONMENT=us-east-1-aws
PINECONE_PROJECT_ID=your-project-id
```

## Multi-LLM Provider Configuration

### OpenAI

Configuration:
```yaml
llm:
  provider: openai
```

Environment:
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Anthropic (Claude)

Configuration:
```yaml
llm:
  provider: anthropic
```

Environment:
```bash
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_BASE_URL=https://api.anthropic.com
```

### SiliconCloud (Chinese Models)

Configuration:
```yaml
llm:
  provider: siliconcloud
```

Environment:
```bash
SILICONCLOUD_API_KEY=your-siliconcloud-key
SILICONCLOUD_BASE_URL=https://api.siliconflow.cn/v1
```

### Azure OpenAI

Configuration:
```yaml
llm:
  provider: azure
```

Environment:
```bash
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

## Testing the Generated API

```bash
# Health check
curl http://localhost:8000/health

# Chat with API key
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'

# Upload a document
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "X-API-Key: your-secret-key" \
  -F "file=@document.pdf"

# Get session info
curl -X GET "http://localhost:8000/api/v1/sessions/session-id" \
  -H "X-API-Key: your-secret-key"
```

## Document Parsing Examples

### PDF Parsing

```python
from src.parsers import PDFParser

parser = PDFParser()
text = parser.parse(file_content)
```

### Markdown Parsing

```python
from src.parsers import MarkdownParser

parser = MarkdownParser()
text = parser.parse(file_content)
```

### Word Document Parsing

```python
from src.parsers import WordParser

parser = WordParser()
text = parser.parse(file_content)
```

## Custom Tool Development

Add a custom tool to your project:

```python
# src/tools/custom_tool.py
from langchain_core.tools import tool

@tool
async def my_custom_tool(query: str) -> str:
    """
    Your tool description

    Args:
        query: The query parameter

    Returns:
        The result of your tool
    """
    # Your tool logic here
    return f"Processed: {query}"
```

Then register it in service:

```python
# src/services/chat_service.py
from src.tools import my_custom_tool

def _create_agent(self):
    tools = [vector_search, search, my_custom_tool]
    # ... rest of the code
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_api.py::test_health_check
```
