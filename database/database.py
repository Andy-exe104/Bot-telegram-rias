import os
import asyncio
import aiomysql
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
            self.pool = await aiomysql.create_pool(
                host=self.db_host,
                db=self.db_name,
                user=self.db_user,
                password=self.db_password,
                charset='utf8mb4',
                autocommit=True
            )
        return self.pool
    
    async def initialize_database(self):
        """Initialize database tables"""
        try:
            pool = await self.get_connection()
            
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    print("🔧 Creating users table...")
                    # Create users table
                    await cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            telegram_id BIGINT UNIQUE NOT NULL,
                            username VARCHAR(255),
                            first_name VARCHAR(255),
                            last_name VARCHAR(255),
                            rank VARCHAR(50) DEFAULT 'free_user',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP NULL,
                            is_active TINYINT(1) DEFAULT 1
                        )
                    """)
                    
                    print("🔧 Creating premium_keys table...")
                    # Create premium_keys table
                    await cursor.execute("""
                        CREATE TABLE IF NOT EXISTS premium_keys (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            key_code VARCHAR(255) UNIQUE NOT NULL,
                            rank VARCHAR(50) NOT NULL,
                            days_valid INT NOT NULL,
                            created_by BIGINT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            used_by BIGINT NULL,
                            used_at TIMESTAMP NULL,
                            is_used TINYINT(1) DEFAULT 0
                        )
                    """)
                    
                    print("🔧 Inserting default Issei user...")
                    # Insert default Issei user (Owner)
                    await cursor.execute("""
                        INSERT IGNORE INTO users (telegram_id, username, first_name, last_name, rank, expires_at)
                        VALUES (7560671542, 'kenny_kx', 'Issei', 'Owner', 'issei', NULL)
                    """)
            
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise e
    
    async def get_user(self, telegram_id: int):
        """Get user by telegram ID"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT * FROM users WHERE telegram_id = %s
                """, (telegram_id,))
                user = await cursor.fetchone()
        
        return user
    
    async def create_user(self, telegram_id: int, username: str, first_name: str, last_name: str):
        """Create new user"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT IGNORE INTO users (telegram_id, username, first_name, last_name, rank)
                    VALUES (%s, %s, %s, %s, 'free_user')
                """, (telegram_id, username, first_name, last_name))
                
                # Get the created user
                await cursor.execute("""
                    SELECT * FROM users WHERE telegram_id = %s
                """, (telegram_id,))
                user = await cursor.fetchone()
        
        return user
    
    async def update_user_rank(self, telegram_id: int, new_rank: str, days: int = None):
        """Update user rank and expiration"""
        pool = await self.get_connection()
        
        if days and new_rank != 'issei':
            expires_at = datetime.now() + timedelta(days=days)
        else:
            expires_at = None
            
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    UPDATE users 
                    SET rank = %s, expires_at = %s
                    WHERE telegram_id = %s
                """, (new_rank, expires_at, telegram_id))
                
                # Get the updated user
                await cursor.execute("""
                    SELECT * FROM users WHERE telegram_id = %s
                """, (telegram_id,))
                user = await cursor.fetchone()
        
        return user
    
    async def create_key(self, rank: str, days: int, created_by: int):
        """Create a new key"""
        pool = await self.get_connection()
        
        key_code = str(uuid.uuid4())[:12].upper()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO premium_keys (key_code, rank, days_valid, created_by)
                    VALUES (%s, %s, %s, %s)
                """, (key_code, rank, days, created_by))
                
                # Get the created key
                await cursor.execute("""
                    SELECT * FROM premium_keys WHERE key_code = %s
                """, (key_code,))
                key = await cursor.fetchone()
        
        return key
    
    async def get_unused_keys(self):
        """Get all unused keys"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT * FROM premium_keys WHERE is_used = 0
                """)
                keys = await cursor.fetchall()
        
        return keys
    
    async def use_key(self, key_code: str, used_by: int):
        """Use a key"""
        pool = await self.get_connection()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Get key info
                await cursor.execute("""
                    SELECT * FROM premium_keys WHERE key_code = %s AND is_used = 0
                """, (key_code,))
                key = await cursor.fetchone()
                
                if not key:
                    return None
                
                # Mark key as used
                await cursor.execute("""
                    UPDATE premium_keys 
                    SET is_used = 1, used_by = %s, used_at = CURRENT_TIMESTAMP
                    WHERE key_code = %s
                """, (used_by, key_code))
                
                # Update user rank
                await self.update_user_rank(used_by, key[3], key[4])  # rank and days_valid
        
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