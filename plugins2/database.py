import aiosqlite


class UserDatabase:
    def __init__(self):
        self.uri = "database/user2.db"

    async def initialize(self):
        await self._create_users_table()

    async def _create_users_table(self):
        await self._execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY
            )
        """)

    async def _execute(self, query, *args):
        async with aiosqlite.connect(self.uri) as db:
            await db.execute(query, args)
            await db.commit()

    async def _fetchone(self, query, *args):
        async with aiosqlite.connect(self.uri) as db:
            async with db.execute(query, args) as cursor:
                return await cursor.fetchone()

    async def _fetchall(self, query, *args):
        async with aiosqlite.connect(self.uri) as db:
            async with db.execute(query, args) as cursor:
                return await cursor.fetchall()

    async def add_user(self, id):
        if not await self.is_user_exist(id):
            await self._execute("INSERT INTO users (id) VALUES (?)", (id))

    async def get_user(self, id):
        user = self.cache.get(id)
        if user is not None:
            return user

        user = await self._fetchone("SELECT * FROM users WHERE id = ?", int(id))
        self.cache[id] = user
        return user

    async def is_user_exist(self, id):
        user = await self._fetchone("SELECT * FROM users WHERE id = ?", int(id))
        return True if user else False

    async def total_users_count(self):
        count = await self._fetchone("SELECT COUNT(*) FROM users")
        return count[0]

    async def get_all_users(self):
        all_users = await self._fetchall("SELECT * FROM users")
        return all_users

    async def delete_user(self, user_id):
        await self._execute("DELETE FROM users WHERE id = ?", int(user_id))

users_db2 = UserDatabase()