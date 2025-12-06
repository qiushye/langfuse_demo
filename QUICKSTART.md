# 快速开始指南

## 项目结构

```
langfuse_demo/
├── agents/                    # Agent 实现
│   ├── __init__.py
│   ├── base_agent.py         # 基础 Agent 类
│   ├── intent_classifier.py  # 意图识别模块
│   └── tools/                # 工具定义
│       ├── __init__.py
│       └── custom_tools.py    # 自定义工具（search_doc, get_weather, calculate）
├── monitoring/                # Langfuse 监控配置
│   ├── __init__.py
│   ├── langfuse_config.py    # Langfuse 初始化
│   └── callbacks.py          # Callback handlers
├── utils/                     # 工具函数
│   ├── __init__.py
│   └── helpers.py            # 辅助函数
├── examples/                  # 示例代码
│   └── deepseek_agent_example.py
├── main.py                    # 入口文件
├── requirements.txt           # 依赖列表
└── env.example                # 环境变量示例
```

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并填入你的 API Keys：

```bash
cp env.example .env
```

编辑 `.env` 文件，填入：
- `LANGFUSE_PUBLIC_KEY`: 从 https://cloud.langfuse.com 获取
- `LANGFUSE_SECRET_KEY`: 从 https://cloud.langfuse.com 获取
- `DEEPSEEK_API_KEY`: 从 https://platform.deepseek.com/ 获取（如果使用 DeepSeek）
- `OPENAI_API_KEY`: 从 https://platform.openai.com/ 获取（如果使用 OpenAI）

### 3. 运行示例

```bash
python main.py
```

## 使用方式

### 方式 1：使用 BaseAgent 类

```python
from monitoring.langfuse_config import setup_langfuse
from agents.base_agent import create_agent_with_monitoring

# 初始化 Langfuse
setup_langfuse()

# 创建 Agent
agent = create_agent_with_monitoring(
    model_type="deepseek",  # 或 "openai"
    model_name="deepseek-chat",  # 或 "gpt-4o"
    system_prompt="你是一个有用的 AI 助手。",
    enable_intent_classification=True,
)

# 调用 Agent
result = agent.invoke(
    query="帮我搜索 CCE 的快速入门文档",
    user_id="user_123",
    session_id="session_abc",
    tags=["demo"],
)
```

### 方式 2：直接使用 create_agent

```python
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langfuse.langchain import CallbackHandler
from langfuse import get_client, propagate_attributes
from agents.tools.custom_tools import get_all_tools

# 初始化
langfuse = get_client()
langfuse_handler = CallbackHandler()

# 创建模型
llm = ChatDeepSeek(model="deepseek-chat", temperature=0.7)

# 创建 Agent
agent = create_agent(
    model=llm,
    tools=get_all_tools(),
    system_prompt="你是一个有用的 AI 助手。",
)

# 调用
with langfuse.start_as_current_observation(
    as_type="span",
    name="agent-request",
    input={"query": "查询北京天气"}
) as root_span:
    with propagate_attributes(
        user_id="user_123",
        session_id="session_abc",
        tags=["demo"]
    ):
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "查询北京天气"}]},
            config={"callbacks": [langfuse_handler]}
        )
    root_span.update_trace(output=result)
```

## 功能特性

### ✅ 已实现功能

1. **意图识别**
   - 自动识别用户意图（查询、操作、对话）
   - 支持 OpenAI 和 DeepSeek 模型
   - 使用 `@observe` 装饰器追踪

2. **工具调用**
   - `search_doc`: 搜索百度云文档
   - `get_weather`: 获取天气信息
   - `calculate`: 数学计算
   - 所有工具都使用 `@observe` 装饰器追踪

3. **Langfuse 监控**
   - 完整的 trace 追踪
   - 意图识别、工具调用、LLM 调用全链路监控
   - 支持 user_id、session_id、tags 等属性

4. **多模型支持**
   - OpenAI (gpt-4o, gpt-4o-mini 等)
   - DeepSeek (deepseek-chat, deepseek-reasoner)

## 查看监控数据

1. 登录 Langfuse 控制台：https://cloud.langfuse.com
2. 在 Traces 页面查看所有追踪记录
3. 点击单个 trace 查看详细信息：
   - 意图识别步骤
   - 工具调用记录
   - LLM 调用详情
   - 执行时间线
   - Token 使用和成本

## 自定义工具

在 `agents/tools/custom_tools.py` 中添加新工具：

```python
from langchain.tools import tool
from langfuse import observe

@observe(name="tool-your-tool")  # observe 在前
@tool  # tool 在后
def your_tool(param: str) -> str:
    """工具描述，LLM 会根据此描述决定是否调用
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
    """
    # 工具逻辑
    return result
```

## 故障排查

### Langfuse 连接失败
- 检查 `LANGFUSE_PUBLIC_KEY` 和 `LANGFUSE_SECRET_KEY` 是否正确
- 检查 `LANGFUSE_HOST` 是否正确（默认：https://cloud.langfuse.com）

### Agent 创建失败
- 检查模型 API Key 是否正确设置
- 检查是否安装了对应的模型包（`langchain-openai` 或 `langchain-deepseek-official`）

### 工具调用失败
- 检查工具函数的文档字符串是否清晰
- 检查工具是否在正确的 trace 上下文中执行

## 下一步

- 查看 `.cursor/rules/langfuse_demo.mdc` 了解详细开发规范
- 查看 `examples/deepseek_agent_example.py` 了解更多示例
- 在 Langfuse UI 中查看和分析 trace 数据

