import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def list_patients():
    try:
        # Use exact connection string from container (simplified)
        engine = create_async_engine('postgresql+asyncpg://medisecure_user:medisecure_password@medisecure-db:5432/medisecure')
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT id, first_name, last_name FROM patients LIMIT 5"))
            rows = result.fetchall()
            print("Valid Patients:")
            for row in rows:
                print(f"ID: {row.id} - {row.first_name} {row.last_name}")
                
            print("\nValid Doctors (Users with role DOCTOR or ADMIN?):")
            # Usually users table. Let's assume the ADMIN ID used in token is valid for doctor_id as placeholder
            print("Using generic admin ID for doctor: 00000000-0000-0000-0000-000000000000")
            
        await engine.dispose()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(list_patients())
