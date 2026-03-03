"""
Chat Service

Handles chat operations including RAG and network search.
"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from src.repositories.vector_repository import VectorRepository
from src.repositories.session_repository import SessionRepository
from src.tools import vector_search, search
from src.core.config.settings import get_settings, get_prompts
from src.core.config.llm import LLMConfig


class ChatService:
    """Service for chat operations"""

    def __init__(self, vector_repo: VectorRepository, session_repo: SessionRepository):
        self.vector_repo = vector_repo
        self.session_repo = session_repo
        self.settings = get_settings()
        self.llm_config = LLMConfig()
        self.agent = self._create_agent()

    def _create_agent(self):
        """Create the LangChain agent using LLMConfig"""
        model = init_chat_model(
            model=self.settings.llm_model,
            model_provider=self.settings.llm_provider,
            api_key=self.llm_config._get_api_key(),
            base_url=self.llm_config._get_base_url(),
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
        )

        tools = [vector_search, search]
        prompts = get_prompts()
        system_prompt = prompts.get("system", """You are a helpful AI assistant with access to:
1. vector_search: For searching through uploaded documents
2. search: For finding current information online

Use these tools to provide accurate, up-to-date responses.""")

        return create_agent(model=model, system_prompt=system_prompt, tools=tools, debug=False)

    async def chat(self, query: str, thread_id: str) -> str:
        """Process a chat query"""
        messages = [HumanMessage(content=query)]

        session = await self.session_repo.get_session(thread_id)
        if session and "messages" in session:
            for msg in session["messages"][-10:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        result = self.agent.invoke({"messages": messages})
        response = result["messages"][-1].content if result["messages"] else ""

        await self._update_session(thread_id, query, response)
        return response

    async def _update_session(self, thread_id: str, query: str, response: str):
        """Update session with new messages"""
        session = await self.session_repo.get_session(thread_id) or {"messages": []}
        session["messages"].append({"role": "user", "content": query})
        session["messages"].append({"role": "assistant", "content": response})
        await self.session_repo.update_session(thread_id, session)
