"""Authorization / audit trail for the Web Console.

The architecture mockup introduces an explicit "Audit" layer: every privileged
action (starting a scan, granting/denying an approval, changing validation or
LLM configuration) is recorded here with who/what/when/decision so operators
have an accountable record of what the autonomous agent was allowed to do.
"""
from __future__ import annotations

import asyncio
import sqlite3
import time
from typing import Optional

from .settings import settings


class AuditStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self._db_path = path or str(settings.data_dir / "audit.db")
        self._lock = asyncio.Lock()
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT,
                decision TEXT,
                detail TEXT,
                request_id TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    async def add(self, actor: str, action: str, target: Optional[str] = None,
                  decision: Optional[str] = None, detail: Optional[str] = None,
                  request_id: Optional[str] = None) -> dict:
        item = {
            "ts": time.time(),
            "actor": actor,
            "action": action,
            "target": target,
            "decision": decision,
            "detail": detail,
            "request_id": request_id,
        }

        def _write() -> dict:
            conn = sqlite3.connect(self._db_path)
            cur = conn.execute(
                "INSERT INTO audit (ts, actor, action, target, decision, detail, request_id) "
                "VALUES (:ts, :actor, :action, :target, :decision, :detail, :request_id)",
                item,
            )
            conn.commit()
            item["id"] = cur.lastrowid
            conn.close()
            return item

        async with self._lock:
            return await asyncio.to_thread(_write)

    async def list(self, limit: int = 100, offset: int = 0,
                   action: Optional[str] = None) -> list[dict]:
        def _read() -> list[dict]:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            sql = "SELECT * FROM audit"
            args: list = []
            if action:
                sql += " WHERE action = ?"
                args.append(action)
            sql += " ORDER BY ts DESC LIMIT ? OFFSET ?"
            args.extend([limit, offset])
            rows = conn.execute(sql, args).fetchall()
            conn.close()
            return [dict(r) for r in rows]

        async with self._lock:
            return await asyncio.to_thread(_read)


audit_store = AuditStore()
