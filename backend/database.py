"""
SQLite Database Manager for Video Generation App
Replaces MongoDB with local SQLite database
"""
import aiosqlite
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Database path
DB_DIR = Path(__file__).parent / 'database'
DB_PATH = os.environ.get('DB_PATH', str(DB_DIR / 'video_gen.db'))


class Database:
    """Async SQLite database manager"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_dir()

    def _ensure_dir(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self):
        """Initialize database with all tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Image analyses table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS image_analyses (
                    id TEXT PRIMARY KEY,
                    image_url TEXT NOT NULL,
                    cloudinary_id TEXT,
                    analysis TEXT NOT NULL,
                    suggested_model TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')

            # Audio generations table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS audio_generations (
                    id TEXT PRIMARY KEY,
                    audio_url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    duration REAL,
                    text TEXT,
                    voice_id TEXT,
                    voice_settings TEXT,
                    cost REAL,
                    timestamp TEXT NOT NULL
                )
            ''')

            # Video generations table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS video_generations (
                    id TEXT PRIMARY KEY,
                    image_id TEXT NOT NULL,
                    audio_id TEXT,
                    model TEXT NOT NULL,
                    mode TEXT NOT NULL DEFAULT 'premium',
                    prompt TEXT NOT NULL,
                    duration REAL,
                    cost REAL DEFAULT 0.0,
                    estimated_cost REAL DEFAULT 0.0,
                    status TEXT NOT NULL DEFAULT 'pending',
                    result_url TEXT,
                    error TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')

            # Generated images table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS generated_images (
                    id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    cost REAL DEFAULT 0.039,
                    timestamp TEXT NOT NULL
                )
            ''')

            # Token usage table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS token_usage (
                    id TEXT PRIMARY KEY,
                    service TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    cost REAL NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')

            # API balances table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS api_balances (
                    id TEXT PRIMARY KEY,
                    service TEXT UNIQUE NOT NULL,
                    initial_balance REAL NOT NULL,
                    current_balance REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')

            # Create indexes for better performance
            await db.execute('CREATE INDEX IF NOT EXISTS idx_video_status ON video_generations(status)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_video_timestamp ON video_generations(timestamp)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_audio_timestamp ON audio_generations(timestamp)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_image_timestamp ON image_analyses(timestamp)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_token_service ON token_usage(service)')

            await db.commit()
            logger.info(f"Database initialized at {self.db_path}")

    # Image Analyses Operations
    async def insert_image_analysis(self, data: Dict[str, Any]) -> bool:
        """Insert image analysis record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO image_analyses (id, image_url, cloudinary_id, analysis, suggested_model, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['id'],
                    data['image_url'],
                    data.get('cloudinary_id'),
                    data['analysis'],
                    data['suggested_model'],
                    data['timestamp']
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting image analysis: {e}")
            return False

    async def get_image_analyses(self, limit: int = 100) -> List[Dict]:
        """Get all image analyses"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM image_analyses ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def delete_image_analysis(self, image_id: str) -> bool:
        """Delete image analysis by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM image_analyses WHERE id = ?', (image_id,))
            await db.commit()
            return cursor.rowcount > 0

    # Audio Generations Operations
    async def insert_audio_generation(self, data: Dict[str, Any]) -> bool:
        """Insert audio generation record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO audio_generations
                    (id, audio_url, source, duration, text, voice_id, voice_settings, cost, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['id'],
                    data['audio_url'],
                    data['source'],
                    data.get('duration'),
                    data.get('text'),
                    data.get('voice_id'),
                    json.dumps(data.get('voice_settings')) if data.get('voice_settings') else None,
                    data.get('cost'),
                    data['timestamp']
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting audio generation: {e}")
            return False

    async def get_audio_generations(self, limit: int = 100) -> List[Dict]:
        """Get all audio generations"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM audio_generations ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    if data.get('voice_settings'):
                        data['voice_settings'] = json.loads(data['voice_settings'])
                    result.append(data)
                return result

    async def delete_audio_generation(self, audio_id: str) -> bool:
        """Delete audio generation by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM audio_generations WHERE id = ?', (audio_id,))
            await db.commit()
            return cursor.rowcount > 0

    # Video Generations Operations
    async def insert_video_generation(self, data: Dict[str, Any]) -> bool:
        """Insert video generation record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO video_generations
                    (id, image_id, audio_id, model, mode, prompt, duration, cost, estimated_cost, status, result_url, error, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['id'],
                    data['image_id'],
                    data.get('audio_id'),
                    data['model'],
                    data.get('mode', 'premium'),
                    data['prompt'],
                    data.get('duration'),
                    data.get('cost', 0.0),
                    data.get('estimated_cost', 0.0),
                    data.get('status', 'pending'),
                    data.get('result_url'),
                    data.get('error'),
                    data['timestamp']
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting video generation: {e}")
            return False

    async def update_video_generation(self, video_id: str, updates: Dict[str, Any]) -> bool:
        """Update video generation record"""
        try:
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [video_id]

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    f'UPDATE video_generations SET {set_clause} WHERE id = ?',
                    values
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating video generation: {e}")
            return False

    async def get_video_generations(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get video generations, optionally filtered by status"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if status:
                query = 'SELECT * FROM video_generations WHERE status = ? ORDER BY timestamp DESC LIMIT ?'
                params = (status, limit)
            else:
                query = 'SELECT * FROM video_generations ORDER BY timestamp DESC LIMIT ?'
                params = (limit,)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def delete_video_generation(self, video_id: str) -> bool:
        """Delete video generation by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM video_generations WHERE id = ?', (video_id,))
            await db.commit()
            return cursor.rowcount > 0

    # Generated Images Operations
    async def insert_generated_image(self, data: Dict[str, Any]) -> bool:
        """Insert generated image record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO generated_images (id, prompt, image_url, cost, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['id'],
                    data['prompt'],
                    data['image_url'],
                    data.get('cost', 0.039),
                    data['timestamp']
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting generated image: {e}")
            return False

    async def get_generated_images(self, limit: int = 100) -> List[Dict]:
        """Get all generated images"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM generated_images ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def delete_generated_image(self, image_id: str) -> bool:
        """Delete generated image by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM generated_images WHERE id = ?', (image_id,))
            await db.commit()
            return cursor.rowcount > 0

    # Token Usage Operations
    async def insert_token_usage(self, data: Dict[str, Any]) -> bool:
        """Insert token usage record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO token_usage (id, service, operation, cost, details, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['id'],
                    data['service'],
                    data['operation'],
                    data['cost'],
                    json.dumps(data.get('details')) if data.get('details') else None,
                    data['timestamp']
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting token usage: {e}")
            return False

    async def get_token_usage(self, limit: int = 1000) -> List[Dict]:
        """Get all token usage records"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM token_usage ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    if data.get('details'):
                        data['details'] = json.loads(data['details'])
                    result.append(data)
                return result

    # API Balances Operations
    async def upsert_api_balance(self, service: str, initial_balance: float) -> bool:
        """Insert or update API balance"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if exists
                async with db.execute('SELECT id FROM api_balances WHERE service = ?', (service,)) as cursor:
                    existing = await cursor.fetchone()

                timestamp = datetime.now().isoformat()

                if existing:
                    await db.execute('''
                        UPDATE api_balances
                        SET initial_balance = ?, current_balance = ?, last_updated = ?
                        WHERE service = ?
                    ''', (initial_balance, initial_balance, timestamp, service))
                else:
                    import uuid
                    await db.execute('''
                        INSERT INTO api_balances (id, service, initial_balance, current_balance, last_updated)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (str(uuid.uuid4()), service, initial_balance, initial_balance, timestamp))

                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error upserting API balance: {e}")
            return False

    async def get_api_balance(self, service: str) -> Optional[Dict]:
        """Get API balance for a service"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM api_balances WHERE service = ?', (service,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_all_api_balances(self) -> List[Dict]:
        """Get all API balances"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM api_balances') as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


# Global database instance
db = Database()
