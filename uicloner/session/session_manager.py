"""
Session & State Management
Persists cookies, localStorage, sessionStorage for warm session reuse.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    session_id: str
    target_url: str
    cookies: list = field(default_factory=list)
    local_storage: dict = field(default_factory=dict)
    session_storage: dict = field(default_factory=dict)
    fingerprint_profile: dict = field(default_factory=dict)
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    use_count: int = 0


class SessionManager:
    """Manages browser session persistence for warm restarts."""

    def __init__(self, sessions_dir: Path = Path(".sessions")):
        self._dir = sessions_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self._dir / f"{session_id}.json"

    async def save(self, cdp, page, session: SessionState) -> None:
        """Persist complete browser state to disk."""
        # Capture cookies
        try:
            cookies_result = await cdp.send("Network.getAllCookies")
            session.cookies = cookies_result.get("cookies", [])
        except Exception as e:
            logger.debug(f"Cookie capture failed: {e}")

        # Capture storage
        try:
            storage_result = await cdp.send("Runtime.evaluate", {
                "expression": """
                    JSON.stringify({
                        local: Object.fromEntries(Object.entries(localStorage)),
                        session: Object.fromEntries(Object.entries(sessionStorage))
                    })
                """,
                "returnByValue": True,
            })
            storage = json.loads(storage_result.get("result", {}).get("value", "{}"))
            session.local_storage = storage.get("local", {})
            session.session_storage = storage.get("session", {})
        except Exception as e:
            logger.debug(f"Storage capture failed: {e}")

        session.last_used = time.time()
        session.use_count += 1

        async with aiofiles.open(self._path(session.session_id), "w") as f:
            await f.write(json.dumps(asdict(session), indent=2))
        logger.debug(f"Session {session.session_id} saved")

    async def restore(self, cdp, session: SessionState) -> None:
        """Restore a previously saved browser session."""
        # Restore cookies
        for cookie in session.cookies:
            try:
                await cdp.send("Network.setCookie", cookie)
            except Exception:
                pass

        # Restore localStorage
        if session.local_storage:
            entries = json.dumps(session.local_storage)
            await cdp.send("Runtime.evaluate", {
                "expression": f"""
                    (() => {{
                        const data = {entries};
                        Object.entries(data).forEach(([k, v]) => localStorage.setItem(k, v));
                    }})()
                """,
            })

        logger.debug(f"Session {session.session_id} restored")

    def load(self, session_id: str) -> Optional[SessionState]:
        """Load a saved session from disk."""
        path = self._path(session_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return SessionState(**data)
        except Exception as e:
            logger.warning(f"Failed to load session {session_id}: {e}")
            return None

    def list_sessions(self) -> list[SessionState]:
        """List all saved sessions."""
        sessions = []
        for path in self._dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                sessions.append(SessionState(**data))
            except Exception:
                pass
        return sorted(sessions, key=lambda s: s.last_used, reverse=True)

    def delete(self, session_id: str) -> bool:
        path = self._path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False
