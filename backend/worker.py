"""
Background worker for processing generation jobs.

This script polls the database for pending jobs, runs SDXL generation,
and updates job status. Designed to run on RunPod GPU instances.

Usage:
    python worker.py
"""
import time
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

from app.admin.models import GenerationJob
from app.models.generate import GenerationRequest
from app.services.generator import MockGenerator, SdxlTurboGenerator
from app.services.storage import LocalStorage, R2Storage, Storage
from app.core.config import settings

# Load environment variables
load_dotenv()

# Initialize database
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Initialize storage backend
storage: Storage
if settings.storage_backend == "r2":
    storage = R2Storage()
    print("✅ [Worker] Using Cloudflare R2 backend.")
else:
    storage = LocalStorage()
    print("✅ [Worker] Using LocalStorage backend.")

# Initialize generator
USE_MOCK = os.getenv("USE_MOCK_GENERATOR", "false").lower() == "true"
generator = MockGenerator(storage) if USE_MOCK else SdxlTurboGenerator(storage)
print(f"✅ [Worker] Using {'Mock' if USE_MOCK else 'SDXL'} generator.")


def process_job(db: Session, job: GenerationJob) -> None:
    """Process a single generation job."""

    print(f"🔄 [Job {job.job_id}] Starting processing...")

    # Update status to processing
    job.status = "processing"
    job.started_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    db.commit()

    try:
        # Create generation request
        request = GenerationRequest(
            family_id=job.family_id,
            color_id=job.color_id,
            cuts=job.cuts,
            seed=job.seed
        )

        # Run SDXL generation
        response = generator.generate(request)

        # Extract URLs from response
        result_urls = [img.url for img in response.images]

        # Update job with results
        job.status = "completed"
        job.result_urls = result_urls
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        db.commit()

        duration = (job.completed_at - job.started_at).total_seconds()
        print(f"✅ [Job {job.job_id}] Completed in {duration:.2f}s. Generated {len(result_urls)} images.")

    except Exception as e:
        # Mark job as failed
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        db.commit()

        print(f"❌ [Job {job.job_id}] Failed: {e}")


def worker_loop(poll_interval: int = 5) -> None:
    """Main worker loop that polls for pending jobs."""

    print(f"🚀 [Worker] Starting worker loop (polling every {poll_interval}s)...")

    while True:
        db = SessionLocal()
        try:
            # Query for pending jobs (oldest first)
            pending_jobs = db.query(GenerationJob)\
                .filter(GenerationJob.status == "pending")\
                .order_by(GenerationJob.created_at)\
                .limit(1)\
                .all()

            if pending_jobs:
                for job in pending_jobs:
                    process_job(db, job)
            else:
                # No jobs, wait before next poll
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n⚠️  [Worker] Received interrupt signal. Shutting down...")
            db.close()
            sys.exit(0)
        except Exception as e:
            print(f"❌ [Worker] Error in worker loop: {e}")
            time.sleep(poll_interval)
        finally:
            db.close()


if __name__ == "__main__":
    print("="*60)
    print("🎨 HF Virtual Stylist - Generation Worker")
    print("="*60)
    print(f"Database: {SQLALCHEMY_DATABASE_URL[:50]}...")
    print(f"Storage: {settings.storage_backend}")
    print(f"Generator: {'Mock' if USE_MOCK else 'SDXL Turbo'}")
    print("="*60)

    worker_loop()
