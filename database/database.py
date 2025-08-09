import os
import asyncio
import asyncpg
from datetime import datetime, timedelta
import uuid

class DatabaseManager:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.pool = None
        
    async def get_connection(self):
        """Get database connection"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
        return self.pool
    
    async def initialize_database(self):
        """Initialize database tables"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            # Create users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    rank VARCHAR(50) DEFAULT 'free_user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create keys table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS keys (
                    id SERIAL PRIMARY KEY,
                    key_code VARCHAR(255) UNIQUE NOT NULL,
                    rank VARCHAR(50) NOT NULL,
                    days_valid INTEGER NOT NULL,
                    created_by BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_by BIGINT NULL,
                    used_at TIMESTAMP NULL,
                    is_used BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Insert default Issei user (Owner)
            await conn.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name, rank, expires_at)
                VALUES (7560671542, 'kenny_kx', 'Issei', 'Owner', 'issei', NULL)
                ON CONFLICT (telegram_id) DO NOTHING
            """)
        
        print("✅ Database initialized successfully!")
    
    async def get_user(self, telegram_id: int):
        """Get user by telegram ID"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT * FROM users WHERE telegram_id = $1
            """, telegram_id)
        
        return user
    
    async def create_user(self, telegram_id: int, username: str, first_name: str, last_name: str):
        """Create new user"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            user = await conn.fetchrow("""
                INSERT INTO users (telegram_id, username, first_name, last_name, rank)
                VALUES ($1, $2, $3, $4, 'free_user')
                ON CONFLICT (telegram_id) DO NOTHING
                RETURNING *
            """, telegram_id, username, first_name, last_name)
        
        return user
    
    async def update_user_rank(self, telegram_id: int, new_rank: str, days: int = None):
        """Update user rank and expiration"""
        pool = await self.get_connection()
        
        if days and new_rank != 'issei':
            expires_at = datetime.now() + timedelta(days=days)
        else:
            expires_at = None
            
        async with pool.acquire() as conn:
            user = await conn.fetchrow("""
                UPDATE users 
                SET rank = $1, expires_at = $2
                WHERE telegram_id = $3
                RETURNING *
            """, new_rank, expires_at, telegram_id)
        
        return user
    
    async def create_key(self, rank: str, days: int, created_by: int):
        """Create a new key"""
        pool = await self.get_connection()
        
        key_code = str(uuid.uuid4())[:12].upper()
        
        async with pool.acquire() as conn:
            key = await conn.fetchrow("""
                INSERT INTO keys (key_code, rank, days_valid, created_by)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """, key_code, rank, days, created_by)
        
        return key
    
    async def get_unused_keys(self):
        """Get all unused keys"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            keys = await conn.fetch("""
                SELECT * FROM keys WHERE is_used = FALSE
            """)
        
        return keys
    
    async def use_key(self, key_code: str, used_by: int):
        """Use a key"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            # Get key info
            key = await conn.fetchrow("""
                SELECT * FROM keys WHERE key_code = $1 AND is_used = FALSE
            """, key_code)
            
            if not key:
                return None
            
            # Mark key as used
            await conn.execute("""
                UPDATE keys 
                SET is_used = TRUE, used_by = $1, used_at = CURRENT_TIMESTAMP
                WHERE key_code = $2
            """, used_by, key_code)
            
            # Update user rank
            await self.update_user_rank(used_by, key['rank'], key['days_valid'])
        
        return key
    
    async def get_rank_info(self, rank: str):
        """Get rank information"""
        ranks = {
            'issei': {'name': 'Issei (Owner)', 'emoji': '👑', 'description': 'Dueño del bot'},
            'admin': {'name': 'Admin', 'emoji': '⚡', 'description': 'Administrador'},
            'seller': {'name': 'Seller', 'emoji': '💎', 'description': 'Vendedor'},
            'premium': {'name': 'Premium', 'emoji': '🌟', 'description': 'Usuario Premium'},
            'free_user': {'name': 'Free User', 'emoji': '👤', 'description': 'Usuario Gratuito'}
        }
        return ranks.get(rank, ranks['free_user'])