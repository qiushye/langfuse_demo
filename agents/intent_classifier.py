"""意图识别模块"""

from typing import Literal, Optional
from langfuse import observe
from langfuse.langchain import CallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

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


class IntentClassifier:
    """意图分类器"""
    
    def __init__(
        self,
        model_type: Literal["openai", "deepseek"] = "deepseek",
        model_name: str = "deepseek-chat",
        temperature: float = 0.3,
    ):
        """
        初始化意图分类器
        
        Args:
            model_type: 模型类型（openai 或 deepseek）
            model_name: 模型名称
            temperature: 温度参数
        """
        self.model_type = model_type
        self.model_name = model_name
        self.temperature = temperature
        self._llm = None
    
    def _get_llm(self):
        """获取 LLM 实例"""
        if self._llm is None:
            if self.model_type == "openai":
                if not HAS_OPENAI:
                    raise ImportError("langchain-openai not installed")
                self._llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=self.temperature,
                )
            elif self.model_type == "deepseek":
                if not HAS_DEEPSEEK:
                    raise ImportError("langchain-deepseek-official not installed")
                self._llm = ChatDeepSeek(
                    model=self.model_name,
                    temperature=self.temperature,
                )
            else:
                raise ValueError(f"Unsupported model_type: {self.model_type}")
        return self._llm
    
    @observe(name="intent-classification", as_type="generation")
    def classify(
        self,
        user_input: str,
        langfuse_handler: Optional[CallbackHandler] = None,
    ) -> str:
        """
        分类用户意图
        
        Args:
            user_input: 用户输入
            langfuse_handler: Langfuse callback handler
            
        Returns:
            意图分类结果
        """
        llm = self._get_llm()
        
        prompt = ChatPromptTemplate.from_template(
            "你是一个意图分类助手。请分析用户的输入，判断用户的意图类型。\n\n"
            "可选意图类型：\n"
            "- 查询：用户想要获取信息或数据\n"
            "- 操作：用户想要执行某个操作或任务\n"
            "- 对话：用户在进行普通对话或闲聊\n\n"
            "用户输入：{input}\n\n"
            "请只返回意图类型（查询、操作、对话），不要返回其他内容。"
        )
        
        chain = prompt | llm
        
        config = {}
        if langfuse_handler:
            config["callbacks"] = [langfuse_handler]
        
        result = chain.invoke(
            {"input": user_input},
            config=config if config else None,
        )
        
        intent = result.content.strip()
        
        # 标准化意图类型
        if "查询" in intent or "query" in intent.lower():
            return "查询"
        elif "操作" in intent or "action" in intent.lower() or "操作" in intent:
            return "操作"
        elif "对话" in intent or "chat" in intent.lower() or "conversation" in intent.lower():
            return "对话"
        else:
            return "对话"  # 默认返回对话


# 便捷函数
def classify_intent(
    user_input: str,
    model_type: Literal["openai", "deepseek"] = "deepseek",
    langfuse_handler: Optional[CallbackHandler] = None,
) -> str:
    """
    分类用户意图（便捷函数）
    
    Args:
        user_input: 用户输入
        model_type: 模型类型
        langfuse_handler: Langfuse callback handler
        
    Returns:
        意图分类结果
    """
    classifier = IntentClassifier(model_type=model_type)
    return classifier.classify(user_input, langfuse_handler)

