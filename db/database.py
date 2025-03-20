from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "mssql+aioodbc://@ISHAN-S-WL/sciarguminer?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
# encoding the password due to the presence of '@' character
DATABASE_URL = "mssql+aioodbc://sciarguminer_db:sciarguminer%40123@44.196.130.217/sciarguminer?driver=ODBC+Driver+17+for+SQL+Server"

# Create Async Engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Async Session Factory
AsyncSessionLocal = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
