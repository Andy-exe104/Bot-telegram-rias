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
        
        # Check if all database environment variables are set
        if not all([self.db_host, self.db_name, self.db_user, self.db_password]):
            print("❌ Error: Database environment variables are not set properly")
            print(f"DB_HOST: {'✅' if self.db_host else '❌'}")
            print(f"DB_NAME: {'✅' if self.db_name else '❌'}")
            print(f"DB_USER: {'✅' if self.db_user else '❌'}")
            print(f"DB_PASSWORD: {'✅' if self.db_password else '❌'}")
            raise ValueError("Missing database environment variables")
        
    async def get_connection(self):
        """Get database connection"""
        if not self.pool:
            try:
                print(f"🔧 Connecting to database: {self.db_host}/{self.db_name}")
                self.pool = await aiomysql.create_pool(
                    host=self.db_host,
                    db=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    charset='utf8mb4',
                    autocommit=True
                )
                print("✅ Database connection pool created successfully!")
            except Exception as e:
                print(f"❌ Error creating database connection: {e}")
                raise e
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