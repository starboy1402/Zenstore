import os
import time
# pyrefly: ignore [missing-import]
from groq import Groq
import models
# pyrefly: ignore [missing-import]
from cache import invalidate_cache
# pyrefly: ignore [missing-import]
from decorators import time_logger
from database import SessionLocal

@time_logger
def generate_product_details(product_id: int):
    """This function will run in the background. It opens its own DB session!"""
    with SessionLocal() as db:
        # 1. First, tell the database we are working on it
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            return
            
        product.status = "processing"
        db.commit()

        api_key = os.environ.get("GROQ_API_KEY")
        
        try:
            if not api_key:
                print("No GROQ_API_KEY found, using MOCK MODE")
                time.sleep(2)
                product.ai_description = f"Introducing the incredible {product.name}! Perfect for your daily needs."
                product.category = "General"
            else:
                print("Calling Groq API...")
                client = Groq(api_key=api_key)
                prompt = f"Write a catchy 2-sentence description and give a 1-word category for this product: {product.name}. Description: {product.raw_description}"
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                product.ai_description = completion.choices[0].message.content
                product.category = "AI Generated"

            # 2. Tell the database we are done!
            product.status = "ready"
            db.commit()
            print(f"✅ [AI SERVICE] Product {product_id} completed.")

        except Exception as e:
            # 3. If Groq fails, we don't crash, we just update the status
            product.status = "ai_failed"
            db.commit()
            print(f"❌ [AI SERVICE] Failed: {str(e)}")
