"""
DeepSeek 模型与 LangChain create_agent 集成示例

此示例展示如何使用 DeepSeek 模型创建 Agent，并与 Langfuse 集成进行监控。
"""

import os
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek
from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler
from langchain_core.messages import HumanMessage

# 配置环境变量
os.environ["DEEPSEEK_API_KEY"] = "sk-..."  # 替换为你的 DeepSeek API Key
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

# 初始化 Langfuse
langfuse = get_client()
langfuse_handler = CallbackHandler()


# 定义工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称，例如：北京、上海
        
    Returns:
        天气信息字符串
    """
    # 这里应该是实际的天气 API 调用
    return f"{city}的天气：晴天，温度 25°C"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 数学表达式，例如：2+2, 10*5
        
    Returns:
        计算结果
    """
    try:
        result = eval(expression)  # 实际应用中应使用更安全的计算方式
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


def create_deepseek_agent():
    """创建使用 DeepSeek 模型的 Agent"""
    
    # 方式 1：直接传入 ChatDeepSeek 实例（推荐）
    llm = ChatDeepSeek(
        model="deepseek-chat",  # 或 "deepseek-reasoner"（推理增强模型）
        temperature=0.7,
        max_tokens=2048
    )
    
    agent = create_agent(
        model=llm,  # 直接传入模型实例
        tools=[get_weather, calculate],
        system_prompt="你是一个有用的 AI 助手，可以帮助用户查询天气和进行数学计算。"
    )
    
    return agent


def run_agent_example():
    """运行 Agent 示例"""
    
    # 创建 Agent
    agent = create_deepseek_agent()
    
    # 用户查询
    user_query = "北京今天天气怎么样？然后帮我计算 123 * 456"
    
    # 使用 Langfuse 追踪
    with langfuse.start_as_current_observation(
        as_type="span",
        name="deepseek-agent-request",
        input={"query": user_query}
    ) as root_span:
        with propagate_attributes(
            user_id="user_123",
            session_id="session_abc",
            tags=["deepseek", "agent-v1"],
            metadata={"model": "deepseek-chat"}
        ):
            # 调用 Agent
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_query)]},
                config={"callbacks": [langfuse_handler]}
            )
        
        # 更新 trace 输出
        root_span.update_trace(output=result)
        
        print("Agent 响应：")
        print(result)
        
        return result


if __name__ == "__main__":
    # 验证 Langfuse 连接
    if langfuse.auth_check():
        print("✓ Langfuse 连接成功")
    else:
        print("✗ Langfuse 连接失败，请检查配置")
        exit(1)
    
    # 运行示例
    try:
        run_agent_example()
    except Exception as e:
        print(f"错误：{e}")
        langfuse.update_current_trace(
            metadata={
                "error_type": type(e).__name__,
                "error_message": str(e),
            }
        )
    finally:
        # 确保数据发送完成
        langfuse.flush()
