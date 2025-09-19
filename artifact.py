"""
Artifact Registry for CoreStack Agent System
- Tracks all data artifacts, API responses, and processing results
- Provides caching, versioning, and lineage tracking
"""

import json
import hashlib
import sqlite3
import time

class ArtifactRegistry:
    def __init__(self, db_path="artifacts.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id TEXT PRIMARY KEY,
            type TEXT,
            content TEXT,
            parent_id TEXT,
            timestamp REAL
        )
        """)
        self.conn.commit()

    def register(self, artifact_type, content, parent_id=None):
        artifact_json = json.dumps(content, sort_keys=True)
        artifact_id = hashlib.sha256(artifact_json.encode()).hexdigest()
        timestamp = time.time()
        c = self.conn.cursor()
        c.execute("""
        INSERT OR IGNORE INTO artifacts (id, type, content, parent_id, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (artifact_id, artifact_type, artifact_json, parent_id, timestamp))
        self.conn.commit()
        return artifact_id

    def get(self, artifact_id):
        c = self.conn.cursor()
        c.execute("SELECT type, content, parent_id, timestamp FROM artifacts WHERE id=?", (artifact_id,))
        row = c.fetchone()
        if row:
            return {
                "id": artifact_id,
                "type": row[0],
                "content": json.loads(row[1]),
                "parent_id": row[2],
                "timestamp": row[3]
            }
        return None

    def find_by_type(self, artifact_type):
        c = self.conn.cursor()
        c.execute("SELECT id, content FROM artifacts WHERE type=?", (artifact_type,))
        return [(row[0], json.loads(row[1])) for row in c.fetchall()]

    def get_stats(self):
        """
        Get registry statistics
        
        Returns:
            Dictionary with counts by artifact type and total count
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT type, COUNT(*) FROM artifacts GROUP BY type")
        type_counts = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM artifacts")
        total_count = cursor.fetchone()[0]
        
        return {
            "total_artifacts": total_count,
            "by_type": type_counts
        }