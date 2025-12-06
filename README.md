# LangChain Agent + Langfuse 监控项目

本项目使用 LangChain 作为 Agent 底座，实现意图识别、工具调用、LLM 调用等功能，并使用 Langfuse 对 Agent 对话的完整链路进行监测。

## 项目结构

```
.
├── .cursorrules          # Cursor AI 开发规则
├── README.md            # 项目说明文档
├── agents/              # Agent 实现
│   ├── __init__.py
│   ├── base_agent.py    # 基础 Agent 类
│   ├── intent_classifier.py  # 意图识别
│   └── tools/           # 工具定义
│       ├── __init__.py
│       └── custom_tools.py
├── monitoring/          # Langfuse 监控配置
│   ├── __init__.py
│   ├── langfuse_config.py  # Langfuse 初始化
│   └── callbacks.py     # Callback handlers
├── utils/               # 工具函数
│   ├── __init__.py
│   └── helpers.py
└── main.py             # 入口文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install langchain langchain-openai langfuse langgraph
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# Langfuse 配置
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# OpenAI 配置
OPENAI_API_KEY=sk-...
```

### 3. 基本使用示例

```python
from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# 初始化 Langfuse
langfuse = get_client()
langfuse_handler = CallbackHandler()

# 创建 Agent
agent = create_agent(
    model="openai:gpt-4o",
    tools=[your_tools],
    system_prompt="你是一个有用的助手"
)

# 使用 Agent 并追踪
with langfuse.start_as_current_observation(
    as_type="span",
    name="agent-request",
    input={"query": user_query}
) as root_span:
    with propagate_attributes(
        user_id="user_123",
        session_id="session_abc",
        tags=["production"]
    ):
        result = agent.invoke(
            {"messages": [HumanMessage(content=user_query)]},
            config={"callbacks": [langfuse_handler]}
        )
    root_span.update_trace(output=result)
```

## Cursor Rules 说明

本项目包含 `.cursorrules` 文件，为 Cursor AI 提供开发指导。规则涵盖：

### 核心内容

1. **LangChain Agent 开发规范**
   - Agent 架构设计（意图识别、工具调用、LLM 调用）
   - Agent 实现模式（LangGraph、create_agent）
   - 代码组织规范

2. **Langfuse 集成规范**
   - 初始化配置
   - 追踪最佳实践
   - Trace 属性设置
   - 评估和评分

3. **高级功能**
   - Prompt 管理
   - 数据集评估
   - 分布式追踪
   - 性能优化

4. **最佳实践**
   - 错误处理
   - 安全注意事项
   - 测试和调试
   - 持续改进

### 关键优化点

1. **装饰器顺序**
   - 由于装饰器自下而上应用，需要让 `@tool` 包裹住 `@observe`（即 `@tool` 写在更上方），才能同时保留 LangChain Tool 元信息和 Langfuse 追踪

2. **上下文传播**
   - 使用 `propagate_attributes` 确保 user_id、session_id 等属性正确传播到所有子观察

3. **工具调用追踪**
   - 对于在独立线程/进程中执行的工具，需要手动传递 trace context

4. **Prompt 管理**
   - 使用 Langfuse Prompt Management 进行版本控制和 A/B 测试

5. **数据集评估**
   - 使用 Langfuse 数据集功能进行离线评估和性能对比

## 开发指南

### 意图识别实现

```python
from langfuse import observe
from langfuse.langchain import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

@observe(name="intent-classification", as_type="generation")
def classify_intent(user_input: str, langfuse_handler: CallbackHandler) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template(
        "分类用户意图：{input}\n"
        "可选意图：查询、操作、对话"
    )
    chain = prompt | llm
    result = chain.invoke(
        {"input": user_input},
        config={"callbacks": [langfuse_handler]}
    )
    return result.content
```

### 工具定义

```python
from langchain.tools import tool
from langfuse import observe

@tool  # 让 tool 包裹 observe，保持 BaseTool 特性
@observe(name="tool-weather")
def get_weather(city: str) -> str:
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字符串
    """
    # 工具逻辑
    return f"{city}的天气是晴天"
```

### LangGraph Agent

```python
from langgraph.graph import StateGraph
from langfuse import observe, propagate_attributes
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()

@observe(name="agent-node")
def agent_node(state: State):
    with propagate_attributes(
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
        tags=["agent-execution"]
    ):
        # Agent 逻辑
        return {"messages": [response]}

# 调用时传入 handler
graph.invoke(
    input={"messages": [HumanMessage(content=query)]},
    config={"callbacks": [langfuse_handler]}
)
```

## 监控和调试

### 查看 Traces

1. 登录 Langfuse 控制台
2. 在 Traces 页面查看所有追踪记录
3. 点击单个 trace 查看详细信息，包括：
   - 意图识别步骤
   - 工具调用记录
   - LLM 调用详情
   - 执行时间线
   - Token 使用和成本

### Trace 验证清单

- [ ] 意图识别步骤被记录
- [ ] 所有工具调用被追踪
- [ ] LLM 调用包含完整的输入/输出
- [ ] 错误被正确捕获和记录
- [ ] user_id 和 session_id 正确传播

## 评估和优化

### 用户反馈评分

```python
from langfuse import get_client

langfuse = get_client()

langfuse.score_current_trace(
    name="user-feedback",
    value=1,  # 1=正面, 0=负面
    data_type="NUMERIC",
    comment="用户反馈：回答准确"
)
```

### 数据集评估

```python
from langfuse import get_client

langfuse = get_client()
dataset = langfuse.get_dataset("agent-evaluation-dataset")

for item in dataset.items:
    with item.run(run_name="agent-v1-evaluation") as root_span:
        result = agent.invoke(...)
        root_span.score_trace(
            name="correctness",
            value=calculate_score(result, item.expected_output),
            data_type="NUMERIC"
        )
```

## 常见问题

### Trace 不完整

- 确保在所有 Agent 调用时传入 `langfuse_handler`
- 检查 OpenTelemetry 上下文是否正确传播

### 工具调用未追踪

- 确保工具函数使用 `@observe` 装饰器
- 检查装饰器顺序：`@tool` 应写在 `@observe` 之上，使其包裹观察逻辑
- 检查工具是否在正确的 trace 上下文中执行

### 意图识别未记录

- 确保意图识别函数被 `@observe` 装饰
- 检查是否在 Agent 调用前执行意图识别

## 参考资源

- [Langfuse 文档](https://langfuse.com/docs)
- [LangChain 文档](https://python.langchain.com/docs)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Langfuse + LangChain 集成指南](https://langfuse.com/integrations/frameworks/langchain)

## 贡献指南

1. 遵循 `.cursorrules` 中的开发规范
2. 确保所有新功能都有对应的 Langfuse 追踪
3. 添加适当的类型注解和文档字符串
4. 在提交前运行测试并验证 trace 完整性
