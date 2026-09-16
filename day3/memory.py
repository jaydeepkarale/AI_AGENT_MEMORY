import json
import sqlite3
from datetime import datetime
from typing import Optional


DB_NAME = "agent_memory.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            confidence REAL DEFAULT 1.0,
            embedding TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_memory(
    user_id: str,
    content: str,
    memory_type: str,
    importance: float = 0.5,
    confidence: float = 1.0,
    embedding: Optional[list[float]] = None,
):
    now = datetime.now().isoformat()

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO memories (
            user_id,
            content,
            memory_type,
            importance,
            confidence,
            embedding,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            content,
            memory_type,
            importance,
            confidence,
            json.dumps(embedding) if embedding else None,
            "active",
            now,
            now,
        ),
    )

    connection.commit()
    connection.close()


def get_memories(user_id: str):
    connection = get_connection()

    cursor = connection.execute(
        """
        SELECT
            id,
            content,
            memory_type,
            importance,
            confidence,
            embedding,
            status,
            created_at,
            updated_at
        FROM memories
        WHERE user_id = ?
          AND status = 'active'
        ORDER BY created_at
        """,
        (user_id,),
    )

    memories = cursor.fetchall()

    connection.close()

    return memories


def update_memory(
    memory_id: int,
    content: str,
    importance: float,
    confidence: float,
    embedding: list[float],
):
    connection = get_connection()

    connection.execute(
        """
        UPDATE memories
        SET
            content = ?,
            importance = ?,
            confidence = ?,
            embedding = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            content,
            importance,
            confidence,
            json.dumps(embedding),
            datetime.now().isoformat(),
            memory_id,
        ),
    )

    connection.commit()
    connection.close()


def delete_memory(memory_id: int):
    connection = get_connection()

    connection.execute(
        """
        UPDATE memories
        SET
            status = 'deleted',
            updated_at = ?
        WHERE id = ?
        """,
        (
            datetime.now().isoformat(),
            memory_id,
        ),
    )

    connection.commit()
    connection.close()