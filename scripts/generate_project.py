"""
RAG Chatbot Project Generator

Generate a complete RAG chatbot project from configuration file.
Supports automatic configuration file management to reduce manual work.
"""

import argparse
import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ProjectGenerator:
    """Generate RAG chatbot projects from configuration"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.skill_dir = Path(__file__).parent

    def _load_config(self) -> Dict[str, Any]:
        """Load project configuration"""
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

        print("=" * 60)
        print("🤖 RAG Chatbot 项目生成器")
        print("=" * 60)
        print()
        print(f"📦 项目名称: {self.config['project']['name']}")
        print(f"📦 项目描述: {self.config['project']['description']}")
        print(f"📦 输出目录: {output_path}")
        print()
        print(f"🔧 向量数据库: {self.config['vector_db']['provider']}")
        print(f"🤖 LLM 提供商: {self.config['llm']['provider']}")
        print(f"🔍 搜索工具: {self.config['search']['provider']}")
        print()
        print("=" * 60)

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

        print()
        print("=" * 60)
        print("✅ 项目生成成功!")
        print(f"📁 项目位置: {output_path}")
        print()
        print("🚀 快速开始 (3步):")
        print(f"   1️⃣ cd {self.config['project']['name']}")
        print(f"   2️⃣ cp .env.example .env")
        print(f"   3️⃣ 编辑 .env 填入 API Keys (如需要)")
        print(f"   4️⃣ python -m venv .venv")
        print(f"   5️⃣ pip install -r requirements.txt")
        print(f"   6️⃣ python main.py")
        print()
        print("💡 提示:")
        print("   - 查看生成的 README.md 了解详细配置")
        print("   - API 文档: http://{host}:{port}/docs")
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
            # Ask if user wants to generate project now
            print(f"   👉 生成项目:")
            print(f"       python scripts/generate_project.py {example_config}")
            print()
            # Exit after setup - user can re-run with their config
            print("📝 配置说明:")
            print("   project:")
            print("     name: my-chatbot")
            print("     vector_db:")
            print("       provider: qdrant  # qdrant, weaviate, pinecone")
            print("     llm:")
            print("       provider: openai  # openai, anthropic, siliconcloud, azure")
            print("     search:")
            print("       provider: duckduckgo  # duckduckgo, tavily")
            print()
            print("💡 可用配置选项:")
            print("   向量数据库: qdrant, weaviate, pinecone")
            print("   LLM提供商: openai, anthropic, siliconcloud, azure")
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
        # Copy main.py
        self._copy_template("main.py", output_path / "main.py")

        # Copy requirements.txt
        self._copy_template("requirements.txt", output_path / "requirements.txt")

        # Copy .env.example
        self._copy_template(".env.example", output_path / ".env.example")

        # Copy .gitignore
        self._copy_template(".gitignore", output_path / ".gitignore")

    def _generate_source_files(self, output_path: Path):
        """Generate source code files"""
        src_path = output_path / "src"
        src_path.mkdir(exist_ok=True)

        # Copy source structure
        template_src = self.template_dir / "src"
        for item in template_src.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(template_src)
                dest_path = src_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                self._copy_template(f"src/{rel_path}", dest_path)

    def _generate_config_files(self, output_path: Path):
        """Generate configuration files"""
        config_path = output_path / "config"
        config_path.mkdir(exist_ok=True)

        # Copy main config with variables substituted
        self._generate_config_yaml(output_path)

        # Copy LLM config based on provider
        provider = self.config['llm']['provider']
        llm_config_path = self.template_dir.parent / "llm" / f"{provider}.yaml"

        if llm_config_path.exists():
            shutil.copy2(llm_config_path, config_path / "llm.yaml")
        else:
            print(f"⚠️  警告: LLM配置文件未找到: {provider}.yaml")

        # Copy vector DB config
        vector_db = self.config['vector_db']['provider']
        vector_config_path = self.template_dir.parent / "config" / f"{vector_db}.yaml"

        if vector_config_path.exists():
            shutil.copy2(vector_config_path, config_path / "vector_db.yaml")
        else:
            print(f"⚠️  警告: 向量库配置文件未找到: {vector_db}.yaml")

    def _generate_config_yaml(self, output_path: Path):
        """Generate config/config.yaml with user's configuration"""
        config_content = self._build_config_yaml()
        config_path = output_path / "config" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)

    def _build_config_yaml(self) -> str:
        """Build the config.yaml content from user configuration

        Uses flat field structure to match Settings class in src/core/config/settings.py
        """
        # Build flat config structure that matches Settings field names
        config_lines = [
            "# RAG Chatbot Configuration",
            "# This file uses flat field structure to match Settings class",
            "",
            "# ============== Project Settings ==============",
            f"project_name: {self.config['project']['name']}",
            f"project_description: {self.config['project']['description']}",
            f"version: {self.config['project']['version']}",
            "",
            "# ============== API Settings ==============",
            f"api_host: {self.config['api']['host']}",
            f"api_port: {self.config['api']['port']}",
            f"api_version_prefix: {self.config['api']['version_prefix']}",
            f"cors_enabled: {str(self.config['api'].get('cors_enabled', True)).lower()}",
            "cors_origins:",
        ]

        for origin in self.config['api'].get('cors_origins', ['http://localhost:5173']):
            config_lines.append(f"  - {origin}")

        config_lines.extend([
            "",
            "# ============== Vector Database Settings ==============",
            f"# Choose provider: weaviate, qdrant, pinecone",
            f"# The corresponding API key should be set in .env",
            f"vector_db_provider: {self.config['vector_db']['provider']}",
            f"vector_db_collection: {self.config['vector_db'].get('collection_name', 'documents')}",
            f"embedding_model: {self.config['vector_db'].get('embedding_model', 'text-embedding-3-small')}",
            "",
            "# Qdrant Configuration",
            "qdrant_url: http://localhost:6333",
            "# Set QDRANT_API_KEY in .env if using Qdrant Cloud",
            "",
            "# Weaviate Configuration",
            "weaviate_url: http://localhost:8080",
            "# Set WEAVIATE_API_KEY in .env if using Weaviate Cloud",
            "",
            "# Pinecone Configuration",
            f"pinecone_cloud: {self.config['vector_db'].get('cloud', 'aws')}",
            f"pinecone_region: {self.config['vector_db'].get('region', 'us-east-1')}",
            "# Set PINECONE_API_KEY in .env",
            "",
            "# ============== LLM Settings ==============",
            f"# Choose provider: openai, anthropic, siliconcloud, azure",
            f"# The corresponding API key should be set in .env",
            f"llm_provider: {self.config['llm']['provider']}",
            f"llm_model: {self.config['llm'].get('model', 'gpt-4o')}",
            f"llm_temperature: {self.config['llm'].get('temperature', 0.7)}",
            f"llm_max_tokens: {self.config['llm'].get('max_tokens', 2048)}",
            "",
            "# OpenAI Configuration",
            "# Set OPENAI_API_KEY in .env",
            "openai_base_url: https://api.openai.com/v1",
            "",
            "# Anthropic Configuration",
            "# Set ANTHROPIC_API_KEY in .env",
            "anthropic_base_url: https://api.anthropic.com",
            "",
            "# SiliconCloud Configuration",
            "# Set SILICONCLOUD_API_KEY in .env",
            "siliconcloud_base_url: https://api.siliconflow.cn/v1",
            "",
            "# Azure OpenAI Configuration",
            "# Set AZURE_OPENAI_API_KEY in .env",
            "azure_openai_endpoint: \"\"",
            "azure_openai_deployment: \"\"",
            "",
            "# ============== Session Settings ==============",
            "redis_url: redis://localhost:6379",
            f"session_ttl: {self.config['session'].get('ttl', 300)}",
            "",
            "# ============== Search Settings ==============",
            f"# Choose provider: duckduckgo, tavily",
            f"search_provider: {self.config['search']['provider']}",
            f"search_max_results: {self.config['search'].get('max_results', 5)}",
            "# Set TAVILY_API_KEY in .env if using tavily",
            "",
            "# ============== Document Processing Settings ==============",
            "document_formats:",
        ])

        for fmt in self.config['documents'].get('formats', ['pdf', 'markdown', 'word', 'text']):
            config_lines.append(f"  - {fmt}")

        config_lines.extend([
            f"max_file_size_mb: {self.config['documents'].get('max_file_size', 10)}",
            f"chunk_size: {self.config['documents'].get('chunk_size', 1000)}",
            f"chunk_overlap: {self.config['documents'].get('chunk_overlap', 200)}",
            "",
            "# ============== Logging Settings ==============",
            f"log_level: {self.config['logging'].get('level', 'INFO')}",
            f"log_format: {self.config['logging'].get('format', 'text')}",
            "",
            "# ============== Feature Flags ==============",
            f"websocket_enabled: {str(self.config['features'].get('websocket_enabled', False)).lower()}",
            f"streaming_enabled: {str(self.config['features'].get('streaming_enabled', True)).lower()}",
        ])

        return "\n".join(config_lines)

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
            'cors_origins': str(self.config['api'].get('cors_origins', ['http://localhost:5173'])),
            'vector_db': self.config['vector_db']['provider'],
            'collection_name': self.config['vector_db'].get('collection_name', 'documents'),
            'embedding_model': self.config['vector_db'].get('embedding_model', 'text-embedding-3-small'),
            'llm_provider': self.config['llm']['provider'],
            'temperature': self.config['llm'].get('temperature', 0.7),
            'max_tokens': self.config['llm'].get('max_tokens', 2048),
            'search_provider': self.config['search']['provider'],
            'max_results': self.config['search'].get('max_results', 5),
            'ttl': self.config['session'].get('ttl', 300),
            'formats': str(self.config['documents'].get('formats', ['pdf', 'markdown', 'word', 'text'])),
            'max_file_size': self.config['documents'].get('max_file_size', 10),
            'chunk_size': self.config['documents'].get('chunk_size', 1000),
            'chunk_overlap': self.config['documents'].get('chunk_overlap', 200),
            'logging_level': self.config['logging'].get('level', 'INFO'),
            'logging_format': self.config['logging'].get('format', 'text'),
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
        print("   vector_db: qdrant, weaviate, pinecone")
        print("   llm: openai, anthropic, siliconcloud, azure")
        print("   search: duckduckgo, tavily")
        return 1

    # Create generator and run
    generator = ProjectGenerator(args.config)
    generator.generate(args.output, interactive=not args.no_interactive)

    return 0


if __name__ == "__main__":
    exit(main())
