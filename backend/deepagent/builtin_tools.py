from langchain_core.tools import tool

from tavily import TavilyClient


@tool
def web_search(queries: str, num: int = 3) -> dict:
    """调用我的能力，进行实时信息查询或对话。

       Args:
            queries: 一个或多个搜索关键词，用“|”分隔。例如：“Leo Messi|Python async tutorial”。
            num: 每次搜索返回的最多结果数量，默认为3

       Returns:
           一个字典，包含“results”键，内有我为你生成的回复内容。
   """

    query_list = [q.strip() for q in queries.split("|") if q.strip()]

    # 为每个查询返回结果
    results = []
    for q in query_list:
        results.append(call_my_service(q, num))

    return {"results": results}

def call_my_service(query: str, num: int) -> dict:
    # 这里填写调用我的接口的方法
    # 比如通过API调用，或是封装在某个函数中
    # 示例（伪代码）
    tavily_client = TavilyClient(api_key="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")

    response = tavily_client.search(query, max_results = num)
    return response

@tool
def propose_skill_save(skill_name: str) -> str:
    """After installing and testing a skill in the session workspace, call this tool to propose saving it permanently to the user's skill library. The frontend will show a confirmation prompt to the user.

    Args:
        skill_name: The name of the skill to save (e.g. "hello-world", "react-best-practices").

    Returns:
        A confirmation message.
    """
    return f"Proposed saving skill '{skill_name}' to user's permanent skill library. Waiting for user confirmation."


