import logging
import aiosqlite

class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.logger = logging.getLogger("bot.database")

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_name)
        self.conn.row_factory = aiosqlite.Row  # Allows accessing columns by name
        self.logger.info(f"Connected to SQLite database: {self.db_name}")

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.logger.info("Database connection closed.")

    async def execute(self, sql: str, *args):
        """Executes a query and commits."""
        if not self.conn:
            return
        async with self.conn.execute(sql, args) as cursor:
            await self.conn.commit()
            return cursor.lastrowid

    async def fetchone(self, sql: str, *args):
        """Fetches a single row."""
        if not self.conn:
            return None
        async with self.conn.execute(sql, args) as cursor:
            return await cursor.fetchone()

    async def fetchall(self, sql: str, *args):
        """Fetches all rows."""
        if not self.conn:
            return []
        async with self.conn.execute(sql, args) as cursor:
            return await cursor.fetchall()