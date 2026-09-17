from fastapi import FastAPI

from app.api.scans import router as scan_router


app = FastAPI(
    title="Security Scan API",
)

app.include_router(scan_router)