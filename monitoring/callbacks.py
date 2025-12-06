"""Langfuse Callback Handlers 模块"""

from langfuse.langchain import CallbackHandler
from typing import Optional, List


def get_callback_handler(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> CallbackHandler:
    """
    创建 Langfuse CallbackHandler
    
    Args:
        session_id: 会话 ID
        user_id: 用户 ID
        tags: 标签列表
        
    Returns:
        CallbackHandler 实例
    """
    handler = CallbackHandler()
    
    # 如果提供了 session_id 或 user_id，可以通过 metadata 传递
    # 注意：在 invoke 时通过 metadata 传递更灵活
    return handler

