"""
RAG Chatbot Project Generator

Generate a complete RAG chatbot project from configuration file.
Uses the new configuration structure: application.yaml + providers.yaml + prompts.yaml
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, Any


class ProjectGenerator:
    """Generate RAG chatbot projects from configuration"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.template_dir = Path(__file__).parent.parent / "templates"

    def _load_config(self) -> Dict[str, Any]:
        """Load project configuration"""
        import yaml
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate(self, output_dir: str = ".", interactive: bool = True):
        """
        Generate a project

        Args:
            output_dir: Output directory (default: current directory)
            interactive: Enable interactive prompts (default: True)
        """
        output_path = Path(output_dir) / self.config['project']['name']

        self._print_header()

        # Auto-copy configuration files to current directory if interactive
        if interactive:
            self._auto_setup_config_files()

        # Create output directory
        if not output_path.exists():
            print(f"📁 创建项目目录: {output_path}")
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"⚠️  目录已存在，将覆盖现有文件: {output_path}")

        # Generate files
        self._generate_main_files(output_path)
        self._generate_source_files(output_path)
        self._generate_config_files(output_path)
        self._generate_readme(output_path)

        self._print_success(output_path)

    def _print_header(self):
        """Print generation header"""
        print("=" * 60)
        print("🤖 RAG Chatbot 项目生成器")
        print("=" * 60)
        print()
        print(f"📦 项目名称: {self.config['project']['name']}")
        print(f"📦 项目描述: {self.config['project']['description']}")
        print(f"📦 输出目录: {self.config['project']['name']}")
        print()
        print(f"🔧 向量数据库: {self.config['vector_db']['provider']}")
        print(f"🤖 LLM 提供商: {self.config['llm']['provider']}")
        print(f"🔍 搜索工具: {self.config['search']['provider']}")
        print()
        print("=" * 60)

    def _print_success(self, output_path: Path):
        """Print success message"""
        print()
        print("=" * 60)
        print("✅ 项目生成成功!")
        print(f"📁 项目位置: {output_path}")
        print()
        print("🚀 快速开始:")
        print(f"   1️⃣ cd {self.config['project']['name']}")
        print(f"   2️⃣ cp .env.example .env")
        print(f"   3️⃣ 编辑 .env 填入 API Keys")
        print(f"   4️⃣ python -m venv .venv")
        print(f"   5️⃣ .venv\\Scripts\\activate  (Windows) 或 source .venv/bin/activate (Linux/Mac)")
        print(f"   6️⃣ pip install -r requirements.txt")
        print(f"   7️⃣ python main.py")
        print()
        print("💡 提示:")
        print("   - API 文档: http://localhost:8000/docs")
        print("   - 配置文件: config/application.yaml, config/providers.yaml")
        print("=" * 60)

    def _auto_setup_config_files(self):
        """
        Automatically copy configuration files to current directory
        This reduces manual work for users
        """
        print()
        print("📋 自动配置文件设置")
        print("-" * 40)

        config_filename = f"{self.config['project']['name']}_config.yaml"

        # Check if user config file exists in current directory
        if os.path.exists(config_filename):
            print(f"✅ 检测到现有配置文件: {config_filename}")
            print(f"   将使用现有配置生成项目")
            print()
            return

        # Check if project_config.yaml.example exists in current directory
        example_config = "project_config.yaml.example"
        if os.path.exists(example_config):
            print(f"✅ 配置示例文件已存在: {example_config}")
            print(f"   您可以直接编辑此文件，然后使用以下命令:")
            print()
            print(f"   👉 编辑配置:")
            print(f"       notepad {example_config}")
            print()
            print(f"   👉 生成项目:")
            print(f"       python scripts/generate_project.py {example_config}")
            print()
            print("📝 配置说明:")
            print("   project:")
            print("     name: my-chatbot")
            print("     vector_db:")
            print("       provider: weaviate  # weaviate, qdrant, pinecone")
            print("     llm:")
            print("       provider: openai  # openai, anthropic, azure")
            print("       base_url: https://api.siliconflow.cn/v1  # 可选")
            print("       model: gpt-4o")
            print("     search:")
            print("       provider: duckduckgo  # duckduckgo, tavily")
            print()
            print("💡 可用配置选项:")
            print("   向量数据库: weaviate, qdrant, pinecone")
            print("   LLM提供商: openai, anthropic, azure")
            print("   搜索工具: duckduckgo, tavily")
            print()
            print("✨ 配置完成! 现在可以:")
            print("   1. 编辑配置文件")
            print("   2. 运行: python scripts/generate_project.py {example_config}")
            print()
            return

        # Auto-copy the example config file
        print("⚡ 正在复制配置文件到当前目录...")
        shutil.copy2(self.config_path, config_filename)
        print(f"✅ 已创建: {config_filename}")
        print(f"   请编辑此文件来配置您的项目")
        print()

    def _generate_main_files(self, output_path: Path):
        """Generate main project files"""
        print("📄 生成主文件...")

        # Copy main.py
        self._copy_template("main.py", output_path / "main.py")

        # Copy requirements.txt
        self._copy_template("requirements.txt", output_path / "requirements.txt")

        # Copy .env.example
        self._copy_template(".env.example", output_path / ".env.example")

        # Copy .gitignore
        self._copy_template(".gitignore", output_path / ".gitignore")

        print("   ✅ 主文件生成完成")

    def _generate_source_files(self, output_path: Path):
        """Generate source code files"""
        print("📝 生成源代码文件...")

        src_path = output_path / "src"
        src_path.mkdir(exist_ok=True)

        # Copy source structure
        template_src = self.template_dir / "src"
        file_count = 0

        for item in template_src.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(template_src)
                dest_path = src_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                self._copy_template(f"src/{rel_path}", dest_path)
                file_count += 1

        print(f"   ✅ 源代码文件生成完成 ({file_count} 个文件)")

    def _generate_config_files(self, output_path: Path):
        """Generate configuration files (new structure)"""
        print("⚙️  生成配置文件...")

        config_path = output_path / "config"
        config_path.mkdir(exist_ok=True)

        # Generate application.yaml
        self._generate_application_yaml(config_path)

        # Generate providers.yaml
        self._generate_providers_yaml(config_path)

        # Copy prompts.yaml template
        self._copy_template("config/prompts.yaml", config_path / "prompts.yaml")

        # Copy __init__.py
        self._copy_template("config/__init__.py", config_path / "__init__.py")

        print("   ✅ 配置文件生成完成")

    def _generate_application_yaml(self, config_path: Path):
        """Generate config/application.yaml"""
        import yaml

        content = f"""# RAG Chatbot - Application Configuration
# This file contains application-level settings only
# No sensitive data (API keys) should be stored here

# ============== Project Information ==============
project:
  name: {self.config['project']['name']}
  description: {self.config['project']['description']}
  version: {self.config['project']['version']}
  environment: development  # development, staging, production

# ============== API Server ==============
api:
  host: {self.config['api']['host']}
  port: {self.config['api']['port']}
  version_prefix: {self.config['api']['version_prefix']}

  # CORS settings
  cors:
    enabled: true
    origins: {self.config['api'].get('cors_origins', ['http://localhost:5173', 'http://localhost:5174'])}
    allow_credentials: true
    allow_methods: ["*"]
    allow_headers: ["*"]

# ============== Session Management ==============
session:
  # Session storage backend
  storage: redis  # redis, memory (memory is for development only)

  # Redis connection (from .env: REDIS_URL)
  # Default: redis://localhost:6379
  ttl: {self.config['session'].get('ttl', 300)}  # Session TTL in seconds

# ============== Document Processing ==============
documents:
  # Supported file formats
  formats: {self.config['documents'].get('formats', ['pdf', 'markdown', 'word', 'text'])}

  # File size limit
  max_file_size_mb: {self.config['documents'].get('max_file_size', 10)}

  # Text splitting (for chunking before vectorization)
  chunk_size: {self.config['documents'].get('chunk_size', 400)}
  chunk_overlap: {self.config['documents'].get('chunk_overlap', 50)}

# ============== Logging ==============
logging:
  level: {self.config['logging'].get('level', 'INFO')}  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: {self.config['logging'].get('format', 'text')}  # text, json

  # Output targets
  console: true
  file: false
  file_path: logs/app.log

# ============== Features ==============
features:
  # Enable WebSocket for real-time chat
  websocket: false

  # Enable streaming responses
  streaming: true

  # Enable document upload API
  document_upload: true

  # Enable session management API
  session_api: true

  # Enable health check endpoint
  health_check: true
"""

        with open(config_path / "application.yaml", 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_providers_yaml(self, config_path: Path):
        """Generate config/providers.yaml"""
        llm = self.config['llm']
        vector_db = self.config['vector_db']
        search = self.config['search']

        # Determine base URL for embedding (use same as LLM by default)
        embedding_base_url = llm.get('base_url', 'https://api.openai.com/v1')

        content = f"""# RAG Chatbot - Provider Configuration
# This file contains provider selection and connection settings
# API keys are loaded from .env file

# ============== LLM Provider ==============
llm:
  # Supported providers: openai, anthropic, azure
  # For SiliconCloud/Moonshot: use 'openai' provider with custom base_url
  provider: {llm['provider']}

  # Model configuration
  model: {llm.get('model', 'gpt-4o')}
  temperature: {llm.get('temperature', 0.7)}
  max_tokens: {llm.get('max_tokens', 2048)}

  # Base URL (use SiliconCloud URL if needed)
  # SiliconCloud: https://api.siliconflow.cn/v1
  # Moonshot: https://api.moonshot.cn/v1
  # OpenAI: https://api.openai.com/v1
  base_url: {llm.get('base_url', 'https://api.openai.com/v1')}

  # Azure-specific (only used when provider: azure)
  azure_deployment: ""
  azure_endpoint: ""

# ============== Embedding Model ==============
embedding:
  # Use same provider as LLM
  provider: openai
  model: {vector_db.get('embedding_model', 'text-embedding-3-small')}
  base_url: {embedding_base_url}

# ============== Vector Database ==============
vector_db:
  # Choose provider: weaviate, qdrant, pinecone
  provider: {vector_db['provider']}

  # Collection name
  collection: {vector_db.get('collection_name', 'documents')}

  # Provider-specific settings
  # Set API key in .env: {{PROVIDER}}_API_KEY
  connections:
    # Weaviate (default - local)
    weaviate:
      url: http://localhost:8080
      # Set in .env: WEAVIATE_API_KEY (for cloud only)

    # Qdrant
    qdrant:
      url: http://localhost:6333
      # Set in .env: QDRANT_API_KEY (for cloud only)

    # Pinecone
    pinecone:
      cloud: {vector_db.get('cloud', 'aws')}
      region: {vector_db.get('region', 'us-east-1')}
      # Set in .env: PINECONE_API_KEY

# ============== Search Tool ==============
search:
  # Choose provider: duckduckgo, tavily
  provider: {search['provider']}

  # Search settings
  max_results: {search.get('max_results', 5)}

  # Tavily-specific
  # Set in .env: TAVILY_API_KEY
  tavily:
    search_depth: basic
    include_answer: true
    include_raw_content: false
"""

        with open(config_path / "providers.yaml", 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_readme(self, output_path: Path):
        """Generate README.md"""
        self._copy_template("README.md", output_path / "README.md")

    def _copy_template(self, template_name: str, dest_path: Path):
        """Copy template file with variable substitution"""
        template_path = self.template_dir / template_name

        if not template_path.exists():
            print(f"⚠️  警告: 模板文件未找到: {template_name}")
            return

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Substitute variables
        content = self._substitute_variables(content)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _substitute_variables(self, content: str) -> str:
        """Substitute configuration variables in template"""
        variables = {
            'project_name': self.config['project']['name'],
            'project_description': self.config['project']['description'],
            'version': self.config['project']['version'],
            'host': self.config['api']['host'],
            'port': self.config['api']['port'],
            'version_prefix': self.config['api']['version_prefix'],
            'vector_db': self.config['vector_db']['provider'],
            'collection_name': self.config['vector_db'].get('collection_name', 'documents'),
            'llm_provider': self.config['llm']['provider'],
            'temperature': self.config['llm'].get('temperature', 0.7),
            'max_tokens': self.config['llm'].get('max_tokens', 2048),
            'search_provider': self.config['search']['provider'],
            'max_results': self.config['search'].get('max_results', 5),
            'ttl': self.config['session'].get('ttl', 300),
            'formats': str(self.config['documents'].get('formats', ['pdf', 'markdown', 'word', 'text'])),
            'max_file_size': self.config['documents'].get('max_file_size', 10),
            'chunk_size': self.config['documents'].get('chunk_size', 400),
            'chunk_overlap': self.config['documents'].get('chunk_overlap', 50),
        }

        for key, value in variables.items():
            content = content.replace(f'{{{key}}}', str(value))

        return content


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="生成 RAG 聊天机器人项目",
        epilog="示例: python scripts/generate_project.py my_config.yaml"
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="project_config.yaml.example",
        help="项目配置文件路径 (默认: project_config.yaml.example)"
    )
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="输出目录 (默认: 当前目录)"
    )
    parser.add_argument(
        "-n", "--no-interactive",
        action="store_true",
        help="禁用交互式提示 (用于自动化)"
    )

    args = parser.parse_args()

    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"❌ 错误: 配置文件未找到: {args.config}")
        print()
        print("💡 提示: 首次使用会自动创建配置文件")
        print("💡 可用配置文件: project_config.yaml.example (在项目根目录)")
        print("💡 可用选项:")
        print("   vector_db: weaviate, qdrant, pinecone")
        print("   llm: openai, anthropic, azure")
        print("   search: duckduckgo, tavily")
        return 1

    # Create generator and run
    generator = ProjectGenerator(args.config)
    generator.generate(args.output, interactive=not args.no_interactive)

    return 0


if __name__ == "__main__":
    exit(main())
