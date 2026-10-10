import aiosqlite
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH

class Database:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)

    async def init_db(self):
        """Baza jadvallarini yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS music_cache (
                    video_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    artist TEXT,
                    duration INTEGER,
                    file_id TEXT NOT NULL,
                    file_unique_id TEXT,
                    downloads_count INTEGER DEFAULT 1,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    video_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    artist TEXT,
                    duration INTEGER,
                    file_id TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, video_id)
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    key TEXT PRIMARY KEY,
                    value INTEGER DEFAULT 0
                )
            """)

            # Boshlang'ich statistikani kiritish
            await db.execute("""
                INSERT OR IGNORE INTO stats (key, value) VALUES ('total_searches', 0), ('total_downloads', 0)
            """)

            await db.commit()

    # --- Foydalanuvchilar ---
    async def add_user(self, user_id: int, username: Optional[str], full_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, username, full_name)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name
            """, (user_id, username, full_name))
            await db.commit()

    async def get_users_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    # --- Musiqa keshi ---
    async def get_cached_music(self, video_id: str) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM music_cache WHERE video_id = ?", (video_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    # Yuklab olishlar sonini oshiramiz
                    await db.execute(
                        "UPDATE music_cache SET downloads_count = downloads_count + 1 WHERE video_id = ?",
                        (video_id,)
                    )
                    await db.execute(
                        "UPDATE stats SET value = value + 1 WHERE key = 'total_downloads'"
                    )
                    await db.commit()
                    return dict(row)
                return None

    async def save_music_cache(
        self,
        video_id: str,
        title: str,
        artist: str,
        duration: int,
        file_id: str,
        file_unique_id: Optional[str] = None
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO music_cache (video_id, title, artist, duration, file_id, file_unique_id, downloads_count)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(video_id) DO UPDATE SET
                    file_id = excluded.file_id,
                    downloads_count = downloads_count + 1
            """, (video_id, title, artist, duration, file_id, file_unique_id))
            await db.execute(
                "UPDATE stats SET value = value + 1 WHERE key = 'total_downloads'"
            )
            await db.commit()

    # --- Sevimlilar (Favorites) ---
    async def add_favorite(
        self,
        user_id: int,
        video_id: str,
        title: str,
        artist: str,
        duration: int,
        file_id: str
    ) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO favorites (user_id, video_id, title, artist, duration, file_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, video_id, title, artist, duration, file_id))
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                # Allaqachon bor
                return False

    async def remove_favorite(self, user_id: int, video_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("""
                DELETE FROM favorites WHERE user_id = ? AND video_id = ?
            """, (user_id, video_id))
            await db.commit()
            return cur.rowcount > 0

    async def is_favorite(self, user_id: int, video_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT 1 FROM favorites WHERE user_id = ? AND video_id = ?
            """, (user_id, video_id)) as cursor:
                return (await cursor.fetchone()) is not None

    async def get_user_favorites(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM favorites WHERE user_id = ? ORDER BY added_at DESC LIMIT ? OFFSET ?
            """, (user_id, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def count_user_favorites(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM favorites WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    # --- Trend va Statistika ---
    async def get_popular_music(self, limit: int = 10) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM music_cache ORDER BY downloads_count DESC LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def increment_searches(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE stats SET value = value + 1 WHERE key = 'total_searches'")
            await db.commit()

    async def get_stats(self) -> Dict[str, int]:
        async with aiosqlite.connect(self.db_path) as db:
            users = await self.get_users_count()
            async with db.execute("SELECT COUNT(*) FROM music_cache") as c:
                cached_count = (await c.fetchone())[0]
            async with db.execute("SELECT value FROM stats WHERE key = 'total_downloads'") as c:
                total_dl = (await c.fetchone())[0]
            async with db.execute("SELECT value FROM stats WHERE key = 'total_searches'") as c:
                total_searches = (await c.fetchone())[0]
            return {
                "users": users,
                "cached_songs": cached_count,
                "total_downloads": total_dl,
                "total_searches": total_searches
            }

db = Database()
