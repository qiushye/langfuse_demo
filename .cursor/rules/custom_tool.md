# seach_doc tool

```
"""Search Baidu Cloud CCE/CCR/CPROM documentation through the open API."""

def search_doc(
    keyword: str = "快速入门",
    page_no: int = 1,
    page_size: int = 10,
    product: str = "CCR",
):
    """
    Search Baidu Cloud docs. Support products: CCE, CCR, CPROM, CFC, BCI, AIHC, BCC, VPC, BLB, VPC, BLS,  EIP, BES, BOS, PFS, CFS
    CCE 是百度智能云容器引擎，是高度可扩展的高性能容器管理服务
    CCR 是百度云镜像仓库服务产品
    CPROM 是百度云 Prometheus 监控服务
    CFC 是百度智能云函数计算服务
    BCI 是百度智能云容器实例提供无服务器化的容器资源,只需提供容器镜像及启动容器所需的配置参数，即可运行容器
    AIHC 百度百舸·AI计算平台（AI Heterogeneous Compute，简称AIHC）是面向大规模深度学习的高性能云原生AI计算平台
    BCC 云服务器BCC（Baidu Cloud Compute）是一种处理能力可弹性伸缩的计算服务
    VPC 私有网络 VPC(Virtual private Cloud) 是一个用户能够自定义的虚拟网络，灵活设置网络地址空间，实现私有网络隔离，多个虚拟网络之间（同城、跨城）稳定高速对等互通。
    BLB 百度负载均衡BLB（Baidu Load Balance）通过将同一区域的多台百度智能云服务器虚拟成一个组，设置一个内网或外网的服务地址，将前端并发访问转发给后台多台云服务器，实现应用程序的流量均衡，性能上实现业务水平扩展。负载均衡还通过故障自动切换及时地消除服务的单点故障，提升服务的可用性。
    BLS 日志服务BLS（Baidu Log Service）是一款集日志数据采集传输、查询分析、日志报警、数据投递、可视化于一体的完全托管式服务。低成本、高效率地实现日志的采集，轻松应对设备运维管理、商业趋势洞察、安全监控审计等业务场景。
    EIP 弹性公网IP EIP (Elastic IP) 提供公网带宽服务，可与任意BCC或BLB实例绑定或解绑，部署配置选项简单易懂，可灵活匹配业务变更。
    BES 百度智能云Elasticsearch是一项托管服务，让您可以在百度智能云中轻松地部署、操作和扩展 Elasticsearch
    BOS 百度对象存储 BOS (Baidu Object Storage) 提供稳定、安全、高效以及高扩展存储服务
    PFS 并行文件存储服务PFS (Parallel Filesystem Service)，是百度智能云提供的完全托管、简单可扩展的并行文件存储系统，针对高性能计算场景提供亚毫秒级的访问能力和高IOPS的数据读写请求能力。
    CFS 百度智能云文件存储（Cloud File System）是一种安全高效的文件存储服务，为云上的虚机、容器资源提供了跨操作系统的文件存储及共享能力。

    Args:
        keyword (str): Search keyword, default is "快速入门"
        page_no (int): Page number, default is 1
        page_size (int): Number of results per page, default is 10
        product (str): Product repo name, supports CCE/CCR/CPROM (case-insensitive)

    Returns:
        str: Formatted search results or error message
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
        return f"Unsupported product '{product}'. Supported: {supported}."
    
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
        import requests
        import json
        # Send POST request to the search API
        response = requests.post(
            BCE_DOC_SEARCH_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Check if the API returned success
        if data.get("success"):
            page_data = data.get("page", {})
            results = page_data.get("result", [])
            total_count = page_data.get("totalCount", 0)
            
            if not results:
                return f"No results found for keyword: '{keyword}'"
            
            # Format the results
            formatted_results = []
            for i, item in enumerate(results, 1):
                document_name = item.get("documentName", "No title")
                # 清理 HTML 标签
                document_name = document_name.replace("<em>", "").replace("</em>", "")
                
                doc_url = item.get("docUrl", "")
                content_text = item.get("contentText", "No description")
                # 清理 HTML 标签
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
            error_msg = data.get("message", "Unknown error occurred")
            return f"API returned error: {error_msg}"
            
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Failed to parse response: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

# fetch_webpage tool

```
async def fetch_webpage(self, agent_state: "AgentState", url: str) -> str:
    """
    Fetch a webpage and convert it to markdown/text format using trafilatura with readability fallback.

    Args:
        url: The URL of the webpage to fetch and convert

    Returns:
        String containing the webpage content in markdown/text format
    """
    import asyncio

    import html2text
    import requests
    from readability import Document
    from trafilatura import extract, fetch_url

    # Try exa first
    try:
        from exa_py import Exa

        agent_state_tool_env_vars = agent_state.get_agent_env_vars_as_dict()
        exa_api_key = agent_state_tool_env_vars.get("EXA_API_KEY") or tool_settings.exa_api_key
        if exa_api_key:
            logger.info(f"[DEBUG] Starting Exa fetch content for url: '{url}'")
            exa = Exa(api_key=exa_api_key)

            results = await asyncio.to_thread(
                lambda: exa.get_contents(
                    [url],
                    text=True,
                ).results
            )

            if len(results) > 0:
                result = results[0]
                return json.dumps(
                    {
                        "title": result.title,
                        "published_date": result.published_date,
                        "author": result.author,
                        "text": result.text,
                    }
                )
            else:
                logger.info(f"[DEBUG] Exa did not return content for '{url}', falling back to local fetch.")
        else:
            logger.info("[DEBUG] No Exa key available, falling back to local fetch.")
    except ImportError:
        logger.info("[DEBUG] Exa pip package unavailable, falling back to local fetch.")
        pass

    try:
        # single thread pool call for the entire trafilatura pipeline
        def trafilatura_pipeline():
            downloaded = fetch_url(url)  # fetch_url doesn't accept timeout parameter
            if downloaded:
                md = extract(downloaded, output_format="markdown")
                return md

        md = await asyncio.to_thread(trafilatura_pipeline)
        if md:
            return md

        # single thread pool call for the entire fallback pipeline
        def readability_pipeline():
            response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (compatible; LettaBot/1.0)"})
            response.raise_for_status()

            doc = Document(response.text)
            clean_html = doc.summary(html_partial=True)
            return html2text.html2text(clean_html)

        return await asyncio.to_thread(readability_pipeline)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching webpage: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

```

# web_search tool
```
async def web_search(
    self,
    agent_state: "AgentState",
    query: str,
    num_results: int = 10,
    category: Optional[
        Literal["company", "research paper", "news", "pdf", "github", "tweet", "personal site", "linkedin profile", "financial report"]
    ] = None,
    include_text: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    start_published_date: Optional[str] = None,
    end_published_date: Optional[str] = None,
    user_location: Optional[str] = None,
) -> str:
    """
    Search the web using Exa's AI-powered search engine and retrieve relevant content.

    Args:
        query: The search query to find relevant web content
        num_results: Number of results to return (1-100)
        category: Focus search on specific content types
        include_text: Whether to retrieve full page content (default: False, only returns summary and highlights)
        include_domains: List of domains to include in search results
        exclude_domains: List of domains to exclude from search results
        start_published_date: Only return content published after this date (ISO format)
        end_published_date: Only return content published before this date (ISO format)
        user_location: Two-letter country code for localized results

    Returns:
        JSON-encoded string containing search results
    """
    try:
        from exa_py import Exa
    except ImportError:
        raise ImportError("exa-py is not installed in the tool execution environment")

    if not query.strip():
        return json.dumps({"error": "Query cannot be empty", "query": query})

    # Get EXA API key from agent environment or tool settings
    agent_state_tool_env_vars = agent_state.get_agent_env_vars_as_dict()
    exa_api_key = agent_state_tool_env_vars.get("EXA_API_KEY") or tool_settings.exa_api_key
    if not exa_api_key:
        raise ValueError("EXA_API_KEY is not set in environment or on agent_state tool execution environment variables.")

    logger.info(f"[DEBUG] Starting Exa web search for query: '{query}' with {num_results} results")

    # Build search parameters
    search_params = {
        "query": query,
        "num_results": min(max(num_results, 1), 100),  # Clamp between 1-100
        "type": "auto",  # Always use auto search type
    }

    # Add optional parameters if provided
    if category:
        search_params["category"] = category
    if include_domains:
        search_params["include_domains"] = include_domains
    if exclude_domains:
        search_params["exclude_domains"] = exclude_domains
    if start_published_date:
        search_params["start_published_date"] = start_published_date
    if end_published_date:
        search_params["end_published_date"] = end_published_date
    if user_location:
        search_params["user_location"] = user_location

    # Configure contents retrieval
    contents_params = {
        "text": include_text,
        "highlights": {"num_sentences": 2, "highlights_per_url": 3, "query": query},
        "summary": {"query": f"Summarize the key information from this content related to: {query}"},
    }

    def _sync_exa_search():
        """Synchronous Exa API call to run in thread pool."""
        exa = Exa(api_key=exa_api_key)
        return exa.search_and_contents(**search_params, **contents_params)

    try:
        # Perform search with content retrieval in thread pool to avoid blocking event loop
        logger.info(f"[DEBUG] Making async Exa API call with params: {search_params}")
        result = await asyncio.to_thread(_sync_exa_search)

        # Format results
        formatted_results = []
        for res in result.results:
            formatted_result = {
                "title": res.title,
                "url": res.url,
                "published_date": res.published_date,
                "author": res.author,
            }

            # Add content if requested
            if include_text and hasattr(res, "text") and res.text:
                formatted_result["text"] = res.text

            # Add highlights if available
            if hasattr(res, "highlights") and res.highlights:
                formatted_result["highlights"] = res.highlights

            # Add summary if available
            if hasattr(res, "summary") and res.summary:
                formatted_result["summary"] = res.summary

            formatted_results.append(formatted_result)

        response = {"query": query, "results": formatted_results}

        logger.info(f"[DEBUG] Exa search completed successfully with {len(formatted_results)} results")
        return json.dumps(response, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Exa search failed for query '{query}': {str(e)}")
        return json.dumps({"query": query, "error": f"Search failed: {str(e)}"})
```