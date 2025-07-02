import aiosqlite

DB_NAME = "planner.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                text TEXT NOT NULL
            )
        """)
        await db.commit()

async def add_plan(date: str, text: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO plans (date, text) VALUES (?, ?)", (date, text))
        await db.commit()

async def get_plans_by_date(date: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT text FROM plans WHERE date = ?", (date,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def delete_plans_by_date(date: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM plans WHERE date = ?", (date,))
        await db.commit()