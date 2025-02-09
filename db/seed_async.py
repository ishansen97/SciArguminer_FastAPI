from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import async_engine, AsyncSessionLocal
from db.models import Base, SampleHistory

async def seed_data(db: AsyncSession):
    """Seeds initial data asynchronously if the table is empty."""
    result = await db.execute(select(SampleHistory))
    history = result.scalars().all()

    if not history:
        histories = [
            SampleHistory(paper="Argument Mining as a Text-to-Text Generation Task", date=datetime.today(), authors="Masayuki Kawarada,Tsutomu Hirao,Wataru Uchida,Masaaki Nagata"),
            SampleHistory(paper="Full-Text Argumentation Mining on Scientific Publications", date=datetime.today(), authors="Arne Binder,Bhuvanesh Verma,Leonhard Hennig"),
            SampleHistory(paper="Argument Mining for Scholarly Document Processing: Taking Stock and Looking Ahead", date=datetime.today(), authors="Khalid Al-Khatib,Yufang Hou"),
            SampleHistory(paper="A Generative Marker Enhanced End-to-End Framework for Argument Mining", date=datetime.today(), authors="Nilmadhab Das,Vishal Choudhary,V. Vijaya Saradhi,Ashish Anand"),
            SampleHistory(paper="Incorporating Zoning Information into Argument Mining from Biomedical Literature", date=datetime.today(), authors="Boyang Liu,Viktor Schlegel,Riza Batista-Navarro,Sophia Ananiadou"),
        ]
        db.add_all(histories)
        await db.commit()
        print("Database seeded successfully!")

async def init_db():
    """Initialize database and seed data asynchronously."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await seed_data(db)