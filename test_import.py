"""测试导入是否正常"""

print("测试导入...")

try:
    from agents.base_agent import create_agent_with_monitoring
    print("✓ agents.base_agent 导入成功")
except Exception as e:
    print(f"✗ agents.base_agent 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from monitoring.langfuse_config import setup_langfuse
    print("✓ monitoring.langfuse_config 导入成功")
except Exception as e:
    print(f"✗ monitoring.langfuse_config 导入失败: {e}")

print("\n测试完成！")

