"""设置环境变量脚本 - 从 env.example 创建 .env 文件"""

import os
import shutil

def setup_env():
    """从 env.example 创建 .env 文件"""
    env_example = "env.example"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"✓ .env 文件已存在")
        response = input("是否要覆盖现有的 .env 文件？(y/N): ")
        if response.lower() != 'y':
            print("取消操作")
            return
    
    if not os.path.exists(env_example):
        print(f"✗ {env_example} 文件不存在")
        return
    
    try:
        shutil.copy(env_example, env_file)
        print(f"✓ 已从 {env_example} 创建 {env_file} 文件")
        print("\n请编辑 .env 文件，填入你的 API Keys:")
        print("  - LANGFUSE_PUBLIC_KEY")
        print("  - LANGFUSE_SECRET_KEY")
        print("  - DEEPSEEK_API_KEY (如果使用 DeepSeek)")
        print("  - OPENAI_API_KEY (如果使用 OpenAI)")
    except Exception as e:
        print(f"✗ 创建 .env 文件失败: {e}")

if __name__ == "__main__":
    setup_env()

