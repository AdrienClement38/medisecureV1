import asyncio
import uuid
import sys
import os

# Add /app to python path
sys.path.append('/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from shared.infrastructure.database.models.patient_model import PatientModel

async def check():
    try:
        engine = create_async_engine('postgresql+asyncpg://medisecure_user:medisecure_password@medisecure-db:5432/medisecure')
        SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with SessionLocal() as session:
            # Check if patient exists using ORM
            print("Attempting ORM fetch...")
            stmt = select(PatientModel).where(PatientModel.id == 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
            result = await session.execute(stmt)
            patient = result.scalar_one_or_none()
            
            if patient:
                print(f"Patient found via ORM: {patient.first_name} {patient.last_name}")
                print(f"Content: {patient.__dict__}")
            else:
                print("Patient not found via ORM")
            
        await engine.dispose()
    except Exception as e:
        print(f"Error during ORM fetch: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check())
