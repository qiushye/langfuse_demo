"""基础 Agent 类"""

from typing import List, Optional, Literal, Dict, Any
from langchain_core.messages import HumanMessage
from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

# 尝试从不同位置导入 create_agent
# 根据 LangChain 版本，create_agent 可能在不同位置
CREATE_AGENT_AVAILABLE = False
try:
    from langchain.agents import create_agent
    CREATE_AGENT_AVAILABLE = True
except ImportError:
    try:
        from langchain_core.agents import create_agent
        CREATE_AGENT_AVAILABLE = True
    except ImportError:
        # create_agent 不可用，将在 _create_agent 中使用 AgentExecutor
        CREATE_AGENT_AVAILABLE = False

# 支持多种模型
try:
    from langchain_openai import ChatOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from langchain_deepseek import ChatDeepSeek
    HAS_DEEPSEEK = True
except ImportError:
    HAS_DEEPSEEK = False

from .intent_classifier import IntentClassifier
from .tools.custom_tools import get_all_tools


class BaseAgent:
    """基础 Agent 类，封装了 Agent 创建和调用逻辑"""
    
    def __init__(
        self,
        model_type: Literal["openai", "deepseek"] = "deepseek",
        model_name: Optional[str] = None,
        tools: Optional[List] = None,
        system_prompt: str = "你是一个有用的 AI 助手。",
        enable_intent_classification: bool = True,
        intent_model_type: Literal["openai", "deepseek"] = "deepseek",
    ):
        """
        初始化 Agent
        
        Args:
            model_type: 主模型类型（openai 或 deepseek）
            model_name: 模型名称
                - OpenAI: "gpt-4o", "gpt-4o-mini" 等
                - DeepSeek: "deepseek-chat", "deepseek-reasoner" 等
            tools: 工具列表，如果为 None 则使用默认工具
            system_prompt: 系统提示词
            enable_intent_classification: 是否启用意图识别
            intent_model_type: 意图识别使用的模型类型
        """
        self.model_type = model_type
        self.model_name = model_name or self._get_default_model_name(model_type)
        self.system_prompt = system_prompt
        self.enable_intent_classification = enable_intent_classification
        self.intent_model_type = intent_model_type
        
        # 初始化工具
        self.tools = tools or get_all_tools()
        
        # 初始化意图分类器
        if self.enable_intent_classification:
            self.intent_classifier = IntentClassifier(model_type=intent_model_type)
        else:
            self.intent_classifier = None
        
        # 创建 Agent
        self.agent = self._create_agent()
        
        # 初始化 Langfuse
        self.langfuse = get_client()
        self.langfuse_handler = CallbackHandler()
    
    def _get_default_model_name(self, model_type: str) -> str:
        """获取默认模型名称"""
        if model_type == "openai":
            return "gpt-4o"
        elif model_type == "deepseek":
            return "deepseek-chat"
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")
    
    def _create_agent(self):
        """创建 Agent 实例"""
        # 创建 LLM
        if self.model_type == "openai":
            if not HAS_OPENAI:
                raise ImportError("langchain-openai not installed")
            llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.7,
            )
        elif self.model_type == "deepseek":
            if not HAS_DEEPSEEK:
                raise ImportError("langchain-deepseek-official not installed")
            llm = ChatDeepSeek(
                model=self.model_name,
                temperature=0.7,
                max_tokens=2048,
            )
        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}")
        
        # 创建 Agent
        if CREATE_AGENT_AVAILABLE:
            # 使用 create_agent（如果可用）
            agent = create_agent(
                model=llm,
                tools=self.tools,
                system_prompt=self.system_prompt,
            )
        else:
            # 使用 AgentExecutor 作为替代方案
            try:
                from langchain.agents import AgentExecutor, create_react_agent
                from langchain import hub
                
                # 获取或创建 prompt
                try:
                    prompt = hub.pull("hwchase17/react")
                except Exception:
                    # 如果无法从 hub 获取，使用默认 prompt
                    from langchain_core.prompts import PromptTemplate
                    prompt = PromptTemplate.from_template(
                        """你是一个有用的 AI 助手。使用以下工具来回答问题。

工具：
{tools}

工具名称格式：{tool_names}

使用以下格式：

问题：输入的问题
思考：你应该思考要做什么
行动：要采取的行动，应该是 [{tool_names}] 中的一个
行动输入：行动的输入
观察：行动的结果
... (这个思考/行动/行动输入/观察可以重复 N 次)
思考：我现在知道最终答案了
最终答案：对原始输入问题的最终答案

开始！

问题：{input}
思考：{agent_scratchpad}"""
                    )
                
                # 创建 react agent
                agent_chain = create_react_agent(llm, self.tools, prompt)
                
                # 创建 AgentExecutor
                agent = AgentExecutor(
                    agent=agent_chain,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True,
                )
            except Exception as e:
                raise ImportError(
                    f"无法创建 Agent。错误: {e}\n"
                    "请确保安装了正确版本的 langchain: pip install 'langchain>=0.3.0 langchain-community'"
                )
        
        return agent
    
    def invoke(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        调用 Agent
        
        Args:
            query: 用户查询
            user_id: 用户 ID
            session_id: 会话 ID
            tags: 标签列表
            metadata: 自定义元数据
            
        Returns:
            Agent 响应结果
        """
        # 意图识别
        intent = None
        if self.enable_intent_classification and self.intent_classifier:
            intent = self.intent_classifier.classify(
                query,
                langfuse_handler=self.langfuse_handler,
            )
        
        # 准备 metadata
        trace_metadata = metadata or {}
        if intent:
            trace_metadata["intent"] = intent
        
        # 使用 Langfuse 追踪
        with self.langfuse.start_as_current_observation(
            as_type="span",
            name="agent-request",
            input={"query": query, "intent": intent},
        ) as root_span:
            with propagate_attributes(
                user_id=user_id,
                session_id=session_id,
                tags=tags or [],
                metadata=trace_metadata,
            ):
                # 调用 Agent
                # 兼容两种 Agent 输入：
                # - create_agent: 期望 {"messages": [HumanMessage(...)]}
                # - create_react_agent/AgentExecutor: 期望 {"input": str}
                payload = {
                    "input": query,
                    "messages": [HumanMessage(content=query)],
                }
                try:
                    result = self.agent.invoke(
                        payload,
                        config={"callbacks": [self.langfuse_handler]},
                    )
                except Exception as e:
                    # 在活动 span 上记录错误信息
                    root_span.update_trace(
                        output={
                            "error": str(e),
                            "error_type": type(e).__name__,
                        }
                    )
                    raise

            # 更新 trace 输出
            root_span.update_trace(output=result)

            return result
    
    def invoke_with_error_handling(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        调用 Agent（带错误处理）
        
        Args:
            query: 用户查询
            user_id: 用户 ID
            session_id: 会话 ID
            tags: 标签列表
            metadata: 自定义元数据
            
        Returns:
            Agent 响应结果
            
        Raises:
            Exception: Agent 调用失败时抛出异常
        """
        try:
            return self.invoke(query, user_id, session_id, tags, metadata)
        except Exception as e:
            # 记录错误信息，兼容 Langfuse v3 API（仅支持 metadata 等字段）
            error_metadata = {
                "error_type": type(e).__name__,
                "error_message": str(e),
            }
            try:
                self.langfuse.update_current_trace(metadata=error_metadata)
            except Exception:
                pass
            raise


def create_agent_with_monitoring(
    model_type: Literal["openai", "deepseek"] = "deepseek",
    model_name: Optional[str] = None,
    tools: Optional[List] = None,
    system_prompt: str = "你是一个有用的 AI 助手。",
    enable_intent_classification: bool = True,
) -> BaseAgent:
    """
    创建带监控的 Agent（便捷函数）
    
    Args:
        model_type: 模型类型
        model_name: 模型名称
        tools: 工具列表
        system_prompt: 系统提示词
        enable_intent_classification: 是否启用意图识别
        
    Returns:
        BaseAgent 实例
    """
    return BaseAgent(
        model_type=model_type,
        model_name=model_name,
        tools=tools,
        system_prompt=system_prompt,
        enable_intent_classification=enable_intent_classification,
    )
