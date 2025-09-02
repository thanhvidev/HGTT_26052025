import os
import asyncio
import aiosqlite
from typing import Dict, Optional

DATA_ROOT = os.path.join(os.path.dirname(__file__), "data", "guilds")

# Ensure base directory exists
os.makedirs(DATA_ROOT, exist_ok=True)

class _DBManager:
    def __init__(self) -> None:
        self._conns: Dict[int, aiosqlite.Connection] = {}
        self._locks: Dict[int, asyncio.Lock] = {}
        self._initing: Dict[int, asyncio.Event] = {}
        self._conn_lock = asyncio.Lock()

    def _db_path(self, guild_id: int) -> str:
        return os.path.join(DATA_ROOT, f"{guild_id}.db")

    def get_lock(self, guild_id: int) -> asyncio.Lock:
        if guild_id not in self._locks:
            self._locks[guild_id] = asyncio.Lock()
        return self._locks[guild_id]

    async def get_conn(self, guild_id: int) -> aiosqlite.Connection:
        # Fast path
        conn = self._conns.get(guild_id)
        if conn is not None:
            return conn

        async with self._conn_lock:
            conn = self._conns.get(guild_id)
            if conn is not None:
                return conn
            # Create new connection
            db_path = self._db_path(guild_id)
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = await aiosqlite.connect(db_path)
            await conn.execute("PRAGMA journal_mode=WAL;")
            await conn.execute("PRAGMA synchronous=NORMAL;")
            await conn.execute("PRAGMA foreign_keys=ON;")
            await conn.execute("PRAGMA temp_store=MEMORY;")
            await conn.execute("PRAGMA cache_size=-20000;")  # ~20MB cache
            conn.row_factory = aiosqlite.Row
            self._conns[guild_id] = conn
        return conn

    async def close_all(self) -> None:
        for gid, c in list(self._conns.items()):
            try:
                await c.close()
            except Exception:
                pass
            finally:
                self._conns.pop(gid, None)

    async def ensure_users_schema(self, guild_id: int) -> None:
        conn = await self.get_conn(guild_id)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                balance INTEGER,
                captcha_attempts INTEGER DEFAULT 0,
                is_locked INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0,
                purchased_items TEXT DEFAULT '',
                marry TEXT DEFAULT '',
                num_gold_tickets INTEGER DEFAULT 0,
                num_diamond_tickets INTEGER DEFAULT 0,
                open_items TEXT DEFAULT '',
                daily_tickets INTEGER DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                total_tickets INTEGER DEFAULT 0,
                vietlottery_tickets INTEGER DEFAULT 0,
                vietlottery_numbers TEXT DEFAULT '',
                kimcuong INTEGER DEFAULT 0,
                pray INTEGER DEFAULT 0,
                love_marry INTEGER DEFAULT 0,
                response TEXT DEFAULT '',
                reaction TEXT DEFAULT '',
                love_items TEXT DEFAULT '',
                coin_kc INTEGER DEFAULT 0,
                last_voice TEXT DEFAULT NULL,
                kho_ca TEXT DEFAULT '',
                kho_moi TEXT DEFAULT '',
                kho_can TEXT DEFAULT '',
                exp_fish INTEGER DEFAULT 0,
                quest_time INTEGER DEFAULT 0,
                quest_mess INTEGER DEFAULT 0,
                quest_image INTEGER DEFAULT 0,
                quest TEXT DEFAULT '',
                quest_done INTEGER DEFAULT 0,
                quest_time_start INTEGER DEFAULT 0,
                streak_toan INTEGER DEFAULT 0,
                setup_marry1 TEXT DEFAULT '',
                setup_marry2 TEXT DEFAULT '',
                xu_hlw INTEGER DEFAULT 0,
                xu_love INTEGER DEFAULT 0,
                bxh_love INTEGER DEFAULT 0,
                pray_so INTEGER DEFAULT 0,
                pray_time INTEGER DEFAULT NULL,
                work_so INTEGER DEFAULT 0,
                work_time INTEGER DEFAULT NULL,
                love_so INTEGER DEFAULT 0,
                love_time INTEGER DEFAULT NULL
            )
            """
        )
        await conn.commit()

    async def ensure_giveaways_schema(self, guild_id: int) -> None:
        conn = await self.get_conn(guild_id)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS giveaways (
                id INTEGER PRIMARY KEY,
                time INTEGER,
                prize TEXT,
                message INTEGER,
                participants TEXT,
                winners TEXT,
                finished BOOL,
                host INTEGER,
                win INTEGER
            )
            """
        )
        await conn.commit()

DB = _DBManager()
