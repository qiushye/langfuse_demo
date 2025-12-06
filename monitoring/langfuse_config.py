"""Langfuse 初始化配置模块"""

import os
from typing import Optional
from langfuse import get_client, Langfuse

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 如果未安装 dotenv，跳过


def setup_langfuse(
    public_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    host: Optional[str] = None,
    sample_rate: Optional[float] = None,
) -> Langfuse:
    """
    初始化 Langfuse 客户端
    
    Args:
        public_key: Langfuse Public Key（可选，从环境变量读取）
        secret_key: Langfuse Secret Key（可选，从环境变量读取）
        host: Langfuse Host（可选，从环境变量读取）
        sample_rate: 采样率（0.0-1.0），用于生产环境减少数据量
        
    Returns:
        Langfuse 客户端实例
    """
    # 从参数或环境变量获取配置
    public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
    host = host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if not public_key or not secret_key:
        raise ValueError(
            "Langfuse credentials not found. "
            "Please set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables."
        )
    
    # 初始化 Langfuse 客户端
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
        sample_rate=sample_rate,
    )
    
    # 验证连接
    if langfuse.auth_check():
        print("✓ Langfuse 连接成功")
    else:
        print("✗ Langfuse 连接失败，请检查配置")
    
    return langfuse


def get_langfuse_client() -> Langfuse:
    """
    获取 Langfuse 客户端单例
    
    Returns:
        Langfuse 客户端实例
    """
    return get_client()

