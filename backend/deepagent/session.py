import time
from pathlib import Path
from typing import Optional, Dict, Any
import shortuuid

_BASE_WORKSPACE = Path.cwd()

def _session_workspace(session_id: str) -> Path:
    """Return the workspace directory for a session: /home/scienceclaw/{session_id}"""
    return Path(_BASE_WORKSPACE) / "workspace" / session_id

async def async_create_science_session(
    mode: str = "deep",
    user_id: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    source: Optional[str] = None,
) -> ScienceSession:
    session_id = shortuuid.uuid()
    thread_id = session_id

    vm_root = _session_workspace(session_id)
    vm_root.mkdir(parents=True, exist_ok=True)


    now = int(time.time())
    session = ScienceSession(
        session_id=session_id,
        thread_id=thread_id,
        vm_root_dir=vm_root,
        mode=mode,
        user_id=user_id,
        model_config=model_config,
        created_at=now,
        updated_at=now,
        source=source,
    )

    session_doc = {
        "_id": session_id,
        "thread_id": thread_id,
        "user_id": user_id,
        "mode": mode,
        "model_config": model_config,
        "vm_root_dir": str(vm_root),
        "created_at": now,
        "updated_at": now,
        "status": "pending",
        "events": [],
        "plan": [],
    }
    if source:
        session_doc["source"] = source
    await db.get_collection("sessions").insert_one(session_doc)

    async with _sessions_lock:
        _sessions[session_id] = session
        _sessions_atime[session_id] = time.time()
        _evict_stale_sessions()

    logger.info(f"Created session {session_id} (workspace={vm_root}, user={user_id})")
    return session