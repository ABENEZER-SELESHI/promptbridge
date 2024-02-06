from __future__ import annotations

import json
from datetime import UTC, datetime

import aiosqlite

from promptbridge.config import AppConfig
from promptbridge.schemas.chat import ChatCompletionRequest, ChatCompletionResponse


class ConversationStore:
    def __init__(self, config: AppConfig) -> None:
        self._path = config.database_path
        self._enabled = config.persist_conversations

    async def initialize(self) -> None:
        if not self._enabled:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
                """
            )
            await db.commit()

    async def save_exchange(
        self,
        conversation_id: str,
        provider: str,
        request: ChatCompletionRequest,
        response: ChatCompletionResponse,
    ) -> None:
        if not self._enabled:
            return
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                """
                INSERT INTO conversations (id, provider, model, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at
                """,
                (conversation_id, provider, request.model, now, now),
            )
            for message in request.messages:
                await db.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (conversation_id, message.role, message.content, now),
                )
            assistant = response.choices[0].message
            await db.execute(
                """
                INSERT INTO messages (conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, assistant.role, assistant.content, now),
            )
            await db.commit()

    async def get_conversation(self, conversation_id: str) -> dict | None:
        if not self._enabled:
            return None
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            msg_cursor = await db.execute(
                "SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id",
                (conversation_id,),
            )
            messages = [dict(item) for item in await msg_cursor.fetchall()]
            payload = dict(row)
            payload["messages"] = messages
            return payload

    async def stats(self) -> dict[str, int]:
        if not self._enabled:
            return {"conversations": 0, "messages": 0}
        async with aiosqlite.connect(self._path) as db:
            conv = await db.execute("SELECT COUNT(*) FROM conversations")
            msg = await db.execute("SELECT COUNT(*) FROM messages")
            conv_count = (await conv.fetchone())[0]
            msg_count = (await msg.fetchone())[0]
            return {"conversations": conv_count, "messages": msg_count}
