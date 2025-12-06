"""自定义工具定义"""

from typing import Optional, List, Literal
from langchain.tools import tool
from langfuse import observe
import requests
import json


@tool
@observe(name="tool-search-doc")
def search_doc(
    keyword: str = "快速入门",
    page_no: int = 1,
    page_size: int = 10,
    product: str = "CCE",
) -> str:
    """
    搜索百度云文档。支持产品：CCE, CCR, CPROM, CFC, BCI, AIHC, BCC, VPC, BLB, EIP, BES, BOS, PFS, CFS
    
    CCE 是百度智能云容器引擎，是高度可扩展的高性能容器管理服务
    CCR 是百度云镜像仓库服务产品
    CPROM 是百度云 Prometheus 监控服务
    
    Args:
        keyword: 搜索关键词，默认为"快速入门"
        page_no: 页码，默认为 1
        page_size: 每页结果数，默认为 10
        product: 产品名称，支持 CCE/CCR/CPROM 等（不区分大小写）
        
    Returns:
        格式化的搜索结果或错误信息
    """
    BCE_DOC_SEARCH_URL = "https://cloud.baidu.com/api/doc/search"
    
    repo_name_map = {
        "CCE": "CCE",
        "CCR": "CCR",
        "CPROM": "CProm",
        "CFC": "CFC",
        "BCI": "BCI",
        "AIHC": "AIHC",
        "BCC": "BCC",
        "VPC": "VPC",
        "BLB": "BLB",
        "EIP": "EIP",
        "BLS": "BLS",
        "BES": "BES",
        "BOS": "BOS",
        "PFS": "PFS",
        "CFS": "CFS",
    }
    
    repo_key = product.upper()
    repo_name = repo_name_map.get(repo_key)
    if not repo_name:
        supported = ", ".join(repo_name_map.keys())
        return f"不支持的产品 '{product}'。支持的产品: {supported}。"
    
    payload = {
        "pageNo": page_no,
        "pageSize": page_size,
        "repoName": repo_name,
        "keyWord": keyword,
        "orgName": "bce-doc"
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(
            BCE_DOC_SEARCH_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            page_data = data.get("page", {})
            results = page_data.get("result", [])
            total_count = page_data.get("totalCount", 0)
            
            if not results:
                return f"未找到关键词 '{keyword}' 的搜索结果"
            
            formatted_results = []
            for i, item in enumerate(results, 1):
                document_name = item.get("documentName", "无标题")
                document_name = document_name.replace("<em>", "").replace("</em>", "")
                
                doc_url = item.get("docUrl", "")
                content_text = item.get("contentText", "无描述")
                content_text = content_text.replace("<em>", "").replace("</em>", "")
                
                resource_id = item.get("resourceId", "")
                
                formatted_results.append(
                    f"{i}. 【{document_name}】\n"
                    f"   资源ID: {resource_id}\n"
                    f"   文档链接: {doc_url}\n"
                    f"   内容摘要: {content_text[:100]}{'...' if len(content_text) > 100 else ''}\n"
                )
            
            result_count = len(results)
            summary = (
                f"📚 {repo_name} 文档搜索结果\n"
                f"🔍 搜索关键词: '{keyword}'\n"
                f"📊 共找到 {total_count} 条相关文档，本次显示 {result_count} 条\n\n"
                + "\n".join(formatted_results) +
                f"\n💡 提示: 使用 page_no 和 page_size 参数可以查看更多结果"
            )
            
            return summary
        else:
            error_msg = data.get("message", "未知错误")
            return f"API 返回错误: {error_msg}"
            
    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"
    except json.JSONDecodeError as e:
        return f"解析响应失败: {str(e)}"
    except Exception as e:
        return f"意外错误: {str(e)}"


@tool
@observe(name="tool-get-weather")
def get_weather(city: str) -> str:
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称，例如：北京、上海、深圳
        
    Returns:
        天气信息字符串
    """
    # 这里应该是实际的天气 API 调用
    # 示例实现
    weather_data = {
        "北京": "晴天，温度 25°C，湿度 60%",
        "上海": "多云，温度 22°C，湿度 70%",
        "深圳": "小雨，温度 28°C，湿度 80%",
    }
    
    return weather_data.get(city, f"{city}的天气：数据暂不可用")


@tool
@observe(name="tool-calculate")
def calculate(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 数学表达式，例如：2+2, 10*5, (100+200)/2
        
    Returns:
        计算结果或错误信息
    """
    try:
        # 实际应用中应使用更安全的计算方式，如使用 eval 的替代方案
        # 这里仅作为示例
        allowed_chars = set("0123456789+-*/()., ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


def get_all_tools() -> List:
    """
    获取所有可用工具
    
    Returns:
        工具列表
    """
    return [search_doc, get_weather, calculate]
