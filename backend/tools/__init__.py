import ast
import json
import subprocess
import threading
from pathlib import Path
from typing import List, Dict, Any

from langchain_core.tools import StructuredTool
from loguru import logger
from pydantic import Field, create_model

from backend.config import  _TOOL_RUNNER_PATH, _EXECUTE_TIMEOUT
from backend.deepagent.dir_watcher import watcher as _dir_watcher
_lock = threading.Lock()
# file_path = Path(__file__)
# print(file_path.read_text(encoding="utf-8"))
# tools_dir = file_path.parent

_tools_list:List[StructuredTool] = []

def _resolve_default(node: ast.expr) -> Any:
    """Return the default value, or Ellipsis (...) when there is none."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id == "None":
        return None
    if isinstance(node, ast.List):
        return []
    if isinstance(node, ast.Dict):
        return {}
    return ...

_SIMPLE_TYPES: Dict[str, type] = {
    "str": str, "int": int, "float": float, "bool": bool,
    "dict": dict, "list": list, "Dict": dict, "List": list, "Any": Any,
}
def _resolve_type(node: ast.expr | None) -> type:
    """Resolve the type of the tool."""
    if node is None:
        return str
    if isinstance(node, ast.Name):
        return _SIMPLE_TYPES.get(node.id, Any)

    return Any

def _execute_in_window(command: str, timeout: int = _EXECUTE_TIMEOUT) -> str:
    print("8881")
    result = subprocess.run(
        command,
        shell=True,  # Windows 需要 shell=True
        capture_output=True,  # 捕获输出
        text=True,  # 返回字符串
        timeout=timeout,
    )
    return result.stdout

def _create_proxy_tool(meta: Dict[str, Any]) -> StructuredTool:
    """
    mate = {
                "func_name": func_name,
                "func_docstring": func_docstring,
                "func_args": func_args,
                "file_path": file_path,
            }
    """
    func_name = meta["func_name"]
    func_docstring = meta["func_docstring"]
    func_args = meta["func_args"]
    file_path = meta["file_path"]
    fields: dict = {}
    for p in func_args:
        ptype = p["type"]
        pdefault = p["default"]
        if pdefault is not ...:
            if pdefault is None:
                fields[p["name"]] = (Optional[ptype], Field(default=pdefault))  # type: ignore[valid-type]
            else:
                fields[p["name"]] = (ptype, Field(default=pdefault))
        else:
            fields[p["name"]] = (ptype, ...)

    input_model = create_model(f"{func_name}_input", **fields)

    def make_proxy(fn: str, path: str):
        def _proxy_run(**kwargs: Any) -> Any:
            from backend.tools.tool_runner import call_tool


            raw_output: str = ""
            logger.info(f"[Tools] Proxy → window: {fn} , len kwargs : {len(kwargs)}")
            try:
                raw_output = call_tool(path, fn, **kwargs)

            except Exception as exc:
                logger.error(f"[Tools] tool call failed for {fn}: {exc}")
                return {
                    "window_exec": {"call_tool": fn},
                    "result": {"error": f"window execution failed: {exc}"},
                }

            if not raw_output:
                logger.error(f"[Tools] tool call failed for {fn}: No output")

                return {
                    "window_exec": {"call_tool": fn},
                    "result": {"error": f"window execution failed: No output"}
                }

            return {
                "window_exec": {"call_tool": fn},
                "result": raw_output,
            }

        return _proxy_run

    return StructuredTool(
        name=func_name,
        description=func_docstring,
        func=make_proxy(func_name, file_path),
        args_schema=input_model,
    )



def _scan_and_create_proxies(ext_tools_dir: Path) -> List[StructuredTool]:
    """
    遍历tools文件夹，ast文件解析
    """
    tools: List[StructuredTool] = []
    for py_file in ext_tools_dir.glob("*.py"):
        meta: dict[str, Any] = {}
        if py_file.name.startswith("_") or py_file.name == "__init__.py":
            continue
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            has_tool_decorator = any(
                (isinstance(decorator, ast.Name) and decorator.id == "tool") or
                (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == "tool")
                                     for decorator in node.decorator_list)
            if not has_tool_decorator:
                continue
            func_name = node.name
            func_docstring = ast.get_docstring(node) or f"Tool: {func_name}"
            func_args: list[dict] = []

            args_node = node.args
            num_defaults = len(args_node.defaults)
            num_args = len(args_node.args)
            for i, arg in enumerate(args_node.args):
                if arg.arg == "self":
                    continue
                ptype = _resolve_type(arg.annotation)
                default_idx = i - (num_args - num_defaults)
                pdefault = _resolve_default(args_node.defaults[default_idx]) if default_idx >= 0 else ...
                func_args.append({"name": arg.arg, "type": ptype, "default": pdefault})

            meta = {
                "func_name": func_name,
                "func_docstring": func_docstring,
                "func_args": func_args,
                "file_path": py_file,
            }
            break
        try:
            proxy = _create_proxy_tool(meta)
            tools.append(proxy)
            logger.info(f"[Tools] Proxy ready: {proxy.name} ← {py_file.name}")
        except Exception as exc:
            logger.warning(f"[Tools] Proxy creation failed for {py_file.name}: {exc}")
    return tools


def reload_external_tools(tool_dir:str):
    """
    加载外部技能，调用_scan_and_create_proxies
    """
    global _tools_list
    has_change = _dir_watcher.has_changed(tool_dir)
    if not has_change and _tools_list:
        return _tools_list

    with _lock:
        tools = _scan_and_create_proxies(Path(tool_dir))
        _tools_list = tools
        logger.info(f"[Tools] Loaded {len(tools)} proxy tools: {[t.name for t in tools]}")
        return tools

if __name__ == "__main__":
    # mate = {
    #     "func_name": "web_search",
    #     "func_docstring": "Search the internet for real-time information using one or more search queries.",
    #     "func_args": func_args,
    #     "file_path": file_path,
    # }
    DUR_pa = Path("D:.deepclaw/tools")
    res = _scan_and_create_proxies(DUR_pa)
    res[0].invoke({"queries": "name1111"})
