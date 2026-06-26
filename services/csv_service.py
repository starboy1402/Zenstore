# pyrefly: ignore [missing-import]
import csv
# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
import models
# pyrefly: ignore [missing-import]
from cache import invalidate_cache

def process_csv_upload(filepath: str, job_id: int, user_id: int, db: Session):
    """Runs in the background, reading the CSV line by line"""
    
    # 1. Grab the "Job" tracker from the database
    job = db.query(models.BatchJob).filter(models.BatchJob.id == job_id).first()
    job.status = "processing"
    db.commit()
    
    processed = 0
    failed = 0
    failed_rows = []
    
    try:
        # 2. Open the CSV file from the hard drive
        with open(filepath, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file) # Automatically maps headers like "name", "price"
            
            for row in reader:
                try:
                    # 3. Queue up the product to be saved
                    new_product = models.Product(
                        owner_id=user_id,
                        name=row["name"],
                        price=float(row["price"]),
                        stock=int(row.get("stock", 0)),
                        raw_description=row.get("description", ""),
                        status="pending"
                    )
                    db.add(new_product)
                    processed += 1
                except Exception as e:
                    # If they type "twenty" instead of "20" for price, it fails gracefully!
                    failed += 1
                    failed_rows.append({"row": row, "error": str(e)})
                    
            # 4. Commit all 500 products at once (super fast database trick!)
            db.commit()
            
            job.processed = processed
            job.failed = failed
            job.failed_rows = failed_rows
            job.status = "completed"
            
            # Invalidate the cache because they just added tons of products!
            invalidate_cache(f"products_{user_id}")
            
    except Exception as e:
        job.status = "failed"
        job.failed_rows = [{"error": str(e)}]
        
    finally:
        db.commit()
        # 5. Delete the CSV file from our server so we don't run out of storage
        if os.path.exists(filepath):
            os.remove(filepath)
