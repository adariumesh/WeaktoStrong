"""
Simple script to create tables without migrations
"""

import asyncio
from sqlalchemy import text
from app.core.database import get_db

async def create_tables():
    """Create necessary tables for challenges"""
    
    async for db in get_db():
        try:
            # Create tracks table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    order_index INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            
            # Create challenges table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS challenges (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL,
                    track_id UUID REFERENCES tracks(id),
                    difficulty VARCHAR(20) NOT NULL,
                    order_index INTEGER NOT NULL,
                    requirements JSON,
                    constraints JSON,
                    test_config JSON,
                    validation_rules JSON,
                    points INTEGER DEFAULT 100 NOT NULL,
                    estimated_time_minutes INTEGER,
                    model_tier VARCHAR(20) DEFAULT 'local' NOT NULL,
                    is_red_team BOOLEAN DEFAULT FALSE,
                    hints JSON,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            
            # Insert default data track
            await db.execute(text("""
                INSERT INTO tracks (name, description, order_index) 
                VALUES ('Data Analysis', 'Data science and analysis challenges', 2)
                ON CONFLICT DO NOTHING;
            """))
            
            await db.commit()
            print("✅ Tables created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            await db.rollback()
        finally:
            await db.close()
        break

if __name__ == "__main__":
    asyncio.run(create_tables())