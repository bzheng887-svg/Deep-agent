import os
from pathlib import Path

from dotenv import load_dotenv




class Filepath:
    FILE_ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    BACKEND_ROOT_DIR: Path = Path(__file__).resolve().parent
    BUILTIN_SKILLS_DIR: Path = BACKEND_ROOT_DIR / "builtin-skills"
    # BUILTIN_TOOLS_DIR: Path = BACKEND_ROOT_DIR / "builtin-tools"

    ROOT_DIR: Path = Path("D:\\.deepclaw\\")
    # EXT_SKILLS_DIR: Path = ROOT_DIR / "skills"
    # EXT_TOOLS_DIR: Path = ROOT_DIR / "tools"
    WORKSPACE_DIR: Path = ROOT_DIR / "workspace"

    USER_PATH = os.path.expanduser("~")
    MEMORY_PATH = os.path.join(USER_PATH, ".deepclaw", "projects")
    EXT_SKILLS_DIR = os.path.join(USER_PATH, ".deepclaw", "skills")
    EXT_TOOLS_DIR = os.path.join(USER_PATH, ".deepclaw", "tools")
    MEMORY_DIR = os.path.join(USER_PATH, ".deepclaw", "memory")
    PYTHON_DIR = os.path.join(USER_PATH, ".deepclaw", "python_env")
    ENV_DIR = os.path.join(USER_PATH, ".deepclaw", "env")

    SYSTEM_ROOT = os.environ.get('SystemRoot')
    powershell_path = os.path.join(SYSTEM_ROOT, "System32", "WindowsPowerShell", "v1.0")

file_path1 = Filepath()
print(file_path1.powershell_path)
load_dotenv()

model_ds_name: str = os.environ.get("DC_MODEL") or "deepseek-chat"
model_ds_api_key: str = os.environ.get("DC_API_KEY") or ""
model_ds_base_url: str = os.environ.get("DC_URL") or "https://api.deepseek.com/v1"
max_tokens: int = int(os.environ.get("MAX_TOKENS", "100000"))
context_window: int = int(os.environ.get("CONTEXT_WINDOW", "131072"))

# CLAW_ROOT_DIR: Path = Path(__file__).resolve().parent.parent
# INN_TOOLS_DIR: Path = CLAW_ROOT_DIR / "tools"
# INN_SKILLS_DIR: Path = CLAW_ROOT_DIR / "skills"
#
# EXT_TOOL_DIR = Path(__file__).resolve().parent.parent / "tools"
# ROOT_DIR = Path(__file__).resolve().parent.parent / "workspace"
# EXT_SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

_TOOL_RUNNER_PATH = Path(__file__).resolve().parent / "tools" / "tool_runner.py"
_EXECUTE_TIMEOUT = 120
print(model_ds_name)
print(model_ds_api_key)
print(model_ds_base_url)