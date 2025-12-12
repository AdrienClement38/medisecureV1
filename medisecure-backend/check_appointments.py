import asyncio
import sys
import os
from datetime import datetime

# Add /app to python path
sys.path.append('/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from appointment_management.infrastructure.models.appointment_model import AppointmentModel

async def check():
    try:
        engine = create_async_engine('postgresql+asyncpg://medisecure_user:medisecure_password@medisecure-db:5432/medisecure')
        SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with SessionLocal() as session:
            print("Listing all appointments:")
            stmt = select(AppointmentModel)
            result = await session.execute(stmt)
            appointments = result.scalars().all()
            
            for appt in appointments:
                print(f"ID: {appt.id} | Doctor: {appt.doctor_id} | Start: {appt.start_time} | End: {appt.end_time} | Status: {appt.status}")
            
        await engine.dispose()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check())
