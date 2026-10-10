from app.db.session import AsyncSession, get_session



async def get_user_by_email(db: AsyncSession, email: str):
    