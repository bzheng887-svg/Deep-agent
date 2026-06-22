from deepagents.backends import BackendProtocol, LocalShellBackend
from deepagents.backends.protocol import WriteResult


class PolicyWrapper(BackendProtocol):
    def __init__(self, root_dir, virtual_mode, env, ):
        self.root_dir = root_dir
        self.virtual_mode = virtual_mode
        self.env = env
        self.inner = self._init_backend(self.root_dir, self.virtual_mode, self.env)  # 接收一个现有的后端实例

    def _init_backend(self, root_dir, virtual_mode, env) -> BackendProtocol:
        return LocalShellBackend(root_dir = root_dir, virtual_mode = virtual_mode, env = env)

    def write(self, file_path: str, content: str) -> WriteResult:
        # 在执行写操作前添加自定义验证逻辑
        if "forbidden_folder" in file_path:
             return WriteResult(error="该目录禁止写入")
        return self.inner.write(file_path, content)

