import os
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import uuid

class DatabaseManager:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.connection = None
        
    async def get_connection(self):
        """Get database connection"""
        if not self.connection:
            self.connection = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                cursor_factory=RealDictCursor
            )
        return self.connection
    
    async def initialize_database(self):
        """Initialize database tables"""
        conn = await self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
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
        cursor.execute("""
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
        cursor.execute("""
            INSERT INTO users (telegram_id, username, first_name, last_name, rank, expires_at)
            VALUES (7560671542, 'kenny_kx', 'Issei', 'Owner', 'issei', NULL)
            ON CONFLICT (telegram_id) DO NOTHING
        """)
        
        conn.commit()
        cursor.close()
        print("✅ Database initialized successfully!")
    
    async def get_user(self, telegram_id: int):
        """Get user by telegram ID"""
        conn = await self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE telegram_id = %s
        """, (telegram_id,))
        
        user = cursor.fetchone()
        cursor.close()
        return user
    
    async def create_user(self, telegram_id: int, username: str, first_name: str, last_name: str):
        """Create new user"""
        conn = await self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (telegram_id, username, first_name, last_name, rank)
            VALUES (%s, %s, %s, %s, 'free_user')
            ON CONFLICT (telegram_id) DO NOTHING
            RETURNING *
        """, (telegram_id, username, first_name, last_name))
        
        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        return user
    
    async def update_user_rank(self, telegram_id: int, new_rank: str, days: int = None):
        """Update user rank and expiration"""
        conn = await self.get_connection()
        cursor = conn.cursor()
        
        if days and new_rank != 'issei':
            expires_at = datetime.now() + timedelta(days=days)
        else:
            expires_at = None
            
        cursor.execute("""
            UPDATE users 
            SET rank = %s, expires_at = %s
            WHERE telegram_id = %s
            RETURNING *
        """, (new_rank, expires_at, telegram_id))
        
        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        return user
    
    async def create_key(self, rank: str, days: int, created_by: int):
        """Create a new key"""
        conn = await self.get_connection()
        cursor = conn.cursor()
        
        key_code = str(uuid.uuid4())[:12].upper()
        
        cursor.execute("""
            INSERT INTO keys (key_code, rank, days_valid, created_by)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (key_code, rank, days, created_by))
        
        key = cursor.fetchone()
        conn.commit()
        cursor.close()
        return key
    
    async def get_unused_keys(self):
        """Get all unused keys"""
        conn = await self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM keys WHERE is_used = FALSE
        """)
        
        keys = cursor.fetchall()
        cursor.close()
        return keys
    
    async def use_key(self, key_code: str, used_by: int):
        """Use a key"""
        conn = await self.get_connection()
        cursor = conn.cursor()
        
        # Get key info
        cursor.execute("""
            SELECT * FROM keys WHERE key_code = %s AND is_used = FALSE
        """, (key_code,))
        
        key = cursor.fetchone()
        if not key:
            cursor.close()
            return None
        
        # Mark key as used
        cursor.execute("""
            UPDATE keys 
            SET is_used = TRUE, used_by = %s, used_at = CURRENT_TIMESTAMP
            WHERE key_code = %s
        """, (used_by, key_code))
        
        # Update user rank
        await self.update_user_rank(used_by, key['rank'], key['days_valid'])
        
        conn.commit()
        cursor.close()
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