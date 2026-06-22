import importlib.util
import sys


# def _emit(payload: dict) -> None:
#     print(_START_MARKER)
#     print(json.dumps(payload, ensure_ascii=False, default=str))
#     print(_END_MARKER)


def call_tool(tool_file: str, func_name: str, **kwargs)-> str:
    """直接调用工具函数，替代 _make_proxy"""

    # 1. 动态加载模块
    spec = importlib.util.spec_from_file_location("_tool_mod", tool_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # 2. 获取函数
    tool_obj = getattr(mod, func_name)

    # 3. 调用 invoke
    return str(tool_obj.invoke(kwargs))

if __name__ == '__main__':
    call_tool("builtintools.py", "web_search", queries="name1111")
