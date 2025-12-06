"""主入口文件"""

import sys

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("警告: python-dotenv 未安装，将使用系统环境变量")
    print("建议运行: pip install python-dotenv")

from monitoring.langfuse_config import setup_langfuse
from agents.base_agent import create_agent_with_monitoring
from utils.helpers import extract_final_answer


def main():
    """主函数"""
    # 初始化 Langfuse
    try:
        langfuse = setup_langfuse()
        if not langfuse.auth_check():
            print("✗ Langfuse 连接失败，请检查配置")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Langfuse 初始化失败: {e}")
        sys.exit(1)
    
    # 创建 Agent
    print("正在创建 Agent...")
    try:
        agent = create_agent_with_monitoring(
            model_type="deepseek",  # 或 "openai"
            model_name="deepseek-chat",  # 或 "gpt-4o"
            system_prompt="你是一个有用的 AI 助手，可以帮助用户查询文档、获取天气信息和进行数学计算。",
            enable_intent_classification=True,
        )
        print("✓ Agent 创建成功")
    except Exception as e:
        print(f"✗ Agent 创建失败: {e}")
        sys.exit(1)
    
    # 交互式对话
    print("\n" + "="*50)
    print("Agent 已就绪，输入 'quit' 或 'exit' 退出")
    print("="*50 + "\n")
    
    session_id = "session_001"
    user_id = "user_001"
    
    while True:
        try:
            # 获取用户输入
            user_query = input("你: ").strip()
            
            if not user_query:
                continue
            
            if user_query.lower() in ["quit", "exit", "退出"]:
                print("再见！")
                break
            
            # 调用 Agent
            print("\nAgent 正在思考...")
            result = agent.invoke_with_error_handling(
                query=user_query,
                user_id=user_id,
                session_id=session_id,
                tags=["interactive", "demo"],
                metadata={"source": "cli"},
            )
            
            # 格式化并显示响应
            answer = extract_final_answer(result)
            print(f"\nAgent: {answer}\n")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n✗ 错误: {e}\n")
    
    # 确保数据发送完成
    langfuse.flush()
    print("✓ 数据已发送到 Langfuse")


if __name__ == "__main__":
    main()

