"""工具函数"""

from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, AIMessage


def format_agent_response(response: Any) -> str:
    """
    格式化 Agent 响应
    
    Args:
        response: Agent 返回的响应对象
        
    Returns:
        格式化后的字符串
    """
    if isinstance(response, dict):
        # 如果是字典，尝试提取 messages
        messages = response.get("messages", [])
        if messages:
            return format_agent_response(messages[-1])
        return str(response)
    
    elif isinstance(response, list):
        # 如果是列表，取最后一个消息
        if response:
            return format_agent_response(response[-1])
        return ""
    
    elif isinstance(response, BaseMessage):
        # 如果是 LangChain 消息对象
        if isinstance(response, AIMessage):
            return response.content
        return str(response.content) if hasattr(response, "content") else str(response)
    
    else:
        return str(response)


def extract_final_answer(response: Any) -> str:
    """
    从 Agent 响应中提取最终答案
    
    Args:
        response: Agent 返回的响应对象
        
    Returns:
        最终答案字符串
    """
    formatted = format_agent_response(response)
    
    # 如果答案包含工具调用信息，尝试提取最终回答
    if "Final Answer:" in formatted:
        parts = formatted.split("Final Answer:")
        if len(parts) > 1:
            return parts[-1].strip()
    
    return formatted.strip()


def get_trace_id() -> str:
    """
    获取当前 trace ID
    
    Returns:
        Trace ID 字符串
    """
    from langfuse import get_client
    
    langfuse = get_client()
    return langfuse.get_current_trace_id() or ""


def get_observation_id() -> str:
    """
    获取当前 observation ID
    
    Returns:
        Observation ID 字符串
    """
    from langfuse import get_client
    
    langfuse = get_client()
    return langfuse.get_current_observation_id() or ""

