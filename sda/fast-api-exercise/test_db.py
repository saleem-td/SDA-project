import asyncio
import asyncpg

# Database connection details
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "books"

async def test_connection():
    try:
        conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            #database=DB_NAME
        )
        print("✅ Successfully connected to PostgreSQL!")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        

# Run test
asyncio.run(test_connection())