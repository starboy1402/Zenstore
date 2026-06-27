# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
import models, schemas
# pyrefly: ignore [missing-import]
from routers.auth_router import get_current_user, get_db
# pyrefly: ignore [missing-import]
from cache import get_cache, set_cache, invalidate_cache
# pyrefly: ignore [missing-import]
from decorators import time_logger
# pyrefly: ignore [missing-import]
from services import ai_service
# pyrefly: ignore [missing-import]
from services import image_service
# pyrefly: ignore [missing-import]
from services import csv_service
import uuid
import os

router = APIRouter(prefix="/products", tags=["Products"])

# 1. CREATE A PRODUCT
@router.post("/", response_model=schemas.ProductResponse, status_code=201)
@time_logger  # <--- Our Custom Decorator constraint!
def create_product(product: schemas.ProductCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_product = models.Product(
        owner_id=current_user.id,
        name=product.name,
        price=product.price,
        stock=product.stock,
        raw_description=product.raw_description,
        status="pending"
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Invalidate the cache so the user sees this new product next time they look!
    invalidate_cache(f"products_{current_user.id}")
    
    # Send the AI generation to the background!
    background_tasks.add_task(ai_service.generate_product_details, new_product.id)
    
    return new_product

# 2. LIST ALL PRODUCTS
@router.get("/", response_model=list[schemas.ProductResponse])
@time_logger
def list_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cache_key = f"products_{current_user.id}"
    
    # Check the cache first! (Constraint 3)
    cached_data = get_cache(cache_key)
    if cached_data:
        print(" Cache HIT! Returning fast data.")
        return cached_data
        
    print(" Cache MISS! Fetching from Database...")
    products = db.query(models.Product).filter(models.Product.owner_id == current_user.id).all()
    
    # Save the data to the cache for next time
    set_cache(cache_key, products, ttl=60)
    return products

# 3. UPLOAD PRODUCT IMAGE
@router.post("/{product_id}/image", response_model=schemas.ProductResponse)
def upload_product_image(
    product_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # 1. Find the product and make sure this user actually owns it!
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product or product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized or product not found")
        
    # 2. Read the raw bytes and send them to our Image Service!
    contents = file.file.read()
    image_data = image_service.process_and_save_image(contents, file.filename)
    
    # 3. Save the new path to the database
    product.image_path = image_data["path"]
    product.image_metadata = image_data["metadata"]
    db.commit()
    db.refresh(product)
    
    # Invalidate cache since the product changed!
    invalidate_cache(f"products_{current_user.id}")
    
    return product

# 4. UPLOAD CSV FILE
@router.post("/bulk-upload", status_code=status.HTTP_202_ACCEPTED)
def upload_products_csv(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Must be a CSV file")
        
    # 1. Save the file to disk temporarily
    os.makedirs("uploads/csv", exist_ok=True)
    filepath = f"uploads/csv/{uuid.uuid4().hex}.csv"
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())
        
    # 2. Create the Job Tracker in the Database
    job = models.BatchJob(owner_id=current_user.id, filename=file.filename)
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # 3. Send the slow parsing task to the background!
    background_tasks.add_task(csv_service.process_csv_upload, filepath, job.id, current_user.id)
    
    return {"message": "Upload started", "job_id": job.id}

# 5. CHECK JOB STATUS
@router.get("/bulk-upload/{job_id}")
def get_batch_job_status(job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.BatchJob).filter(models.BatchJob.id == job_id).first()
    if not job or job.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job

# 6. TRIGGER AI FOR PENDING PRODUCT
@router.post("/{product_id}/generate-ai")
@time_logger
def trigger_ai_generation(
    product_id: int, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # 1. Grab the product
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    # 2. Security Check
    if not product or product.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # 3. Validation Check
    if product.status == "ready":
        raise HTTPException(status_code=400, detail="Product already has an AI description")
        
    # 4. Update status and trigger worker
    product.status = "processing"
    db.commit()
    
    # Invalidate cache so they see the "processing" status immediately
    invalidate_cache(f"products_{current_user.id}")
    
    # Trigger AI
    # No db passed in!
    background_tasks.add_task(ai_service.generate_product_details, product.id)
    
    return {"message": "AI generation started", "status": "processing"}
