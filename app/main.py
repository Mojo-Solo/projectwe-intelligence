from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from app.api import health, ai_tasks
from app.workers.kafka_consumer import KafkaWorker
import asyncio
import os

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)

app = FastAPI(
    title="ProjectWE Intelligence Service",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(ai_tasks.router, prefix="/api/tasks", tags=["tasks"])

# Start Kafka consumer on startup
@app.on_event("startup")
async def startup_event():
    worker = KafkaWorker()
    asyncio.create_task(worker.start())

@app.get("/")
async def root():
    return {"service": "ProjectWE Intelligence", "status": "operational"}
