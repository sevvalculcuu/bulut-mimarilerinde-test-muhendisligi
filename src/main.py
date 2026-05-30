import io
import os
import logging
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
import qrcode
from prometheus_fastapi_instrumentator import Instrumentator

from src.database import engine, Base, get_db
from src.models import QRCodeModel
from src.s3_service import ensure_bucket_exists, upload_qr_image, delete_qr_image
from src.tracing import init_tracer

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title="QR Code Generator Service",
    description="MTH2526-B25 Cloud Architecture and Testing Engineering Term Project",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Templates (served from current file location)
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

# Initialize Tracing
init_tracer(app)

# Initialize Prometheus Instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


# Pydantic schemas
class QRCodeCreate(BaseModel):
    title: str
    target_url: HttpUrl


class QRCodeResponse(BaseModel):
    id: int
    title: str
    target_url: str
    s3_key: str
    s3_url: str
    scan_count: int
    created_at: str

    class Config:
        from_attributes = True


# Startup Event: Initialize DB and S3
@app.on_event("startup")
def startup_event():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

    logger.info("Verifying AWS S3 Bucket...")
    try:
        ensure_bucket_exists()
    except Exception as e:
        logger.error(f"S3 Bucket verification failed: {e}. Continuing for test setups.")


# HTML Frontend Route
@app.get("/", response_class=HTMLResponse)
def index_page(request: Request, db: Session = Depends(get_db)):
    qrcodes = db.query(QRCodeModel).order_by(QRCodeModel.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "qrcodes": qrcodes},
    )


# API: Generate QR Code
@app.post(
    "/api/v1/qrcodes",
    response_model=QRCodeResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_qrcode(
    request: Request, payload: QRCodeCreate, db: Session = Depends(get_db)
):
    target_url_str = str(payload.target_url)

    # 1. Create a database record to reserve the ID
    qr_record = QRCodeModel(
        title=payload.title,
        target_url=target_url_str,
        s3_key="temp",
        s3_url="temp",
        scan_count=0,
    )
    db.add(qr_record)
    db.commit()
    db.refresh(qr_record)

    # 2. Build the redirect URL
    # Use request base_url to route redirection via this FastAPI instance
    base_url = str(request.base_url).rstrip("/")
    redirect_url = f"{base_url}/qr/{qr_record.id}"

    # 3. Generate QR code image
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(redirect_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        file_content = img_bytes.getvalue()
    except Exception as e:
        db.delete(qr_record)
        db.commit()
        logger.error(f"Failed to generate QR image: {e}")
        raise HTTPException(
            status_code=500, detail=f"QR image generation failed: {str(e)}"
        )

    # 4. Upload to S3
    s3_key = f"qrcodes/{qr_record.id}.png"
    try:
        s3_url = upload_qr_image(file_content, s3_key)
    except Exception as e:
        db.delete(qr_record)
        db.commit()
        logger.error(f"S3 Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"S3 Upload failed: {str(e)}")

    # 5. Update and finalize DB record
    qr_record.s3_key = s3_key
    qr_record.s3_url = s3_url
    db.commit()
    db.refresh(qr_record)

    # Format datetime response
    response_data = {
        "id": qr_record.id,
        "title": qr_record.title,
        "target_url": qr_record.target_url,
        "s3_key": qr_record.s3_key,
        "s3_url": qr_record.s3_url,
        "scan_count": qr_record.scan_count,
        "created_at": qr_record.created_at.isoformat(),
    }
    return response_data


# Form Endpoint for UI Integration
@app.post("/generate", response_class=RedirectResponse)
def generate_qrcode_form(
    request: Request,
    title: str = Form(...),
    target_url: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        # Validate target_url using Pydantic HttpUrl
        from pydantic import TypeAdapter

        ta = TypeAdapter(HttpUrl)
        validated_url = ta.validate_python(target_url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid target URL format")

    payload = QRCodeCreate(title=title, target_url=validated_url)
    generate_qrcode(request, payload, db)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# API: List all QR Codes
@app.get("/api/v1/qrcodes", response_model=List[QRCodeResponse])
def list_qrcodes(db: Session = Depends(get_db)):
    qrcodes = db.query(QRCodeModel).order_by(QRCodeModel.id.desc()).all()

    response = []
    for qr in qrcodes:
        response.append(
            {
                "id": qr.id,
                "title": qr.title,
                "target_url": qr.target_url,
                "s3_key": qr.s3_key,
                "s3_url": qr.s3_url,
                "scan_count": qr.scan_count,
                "created_at": qr.created_at.isoformat(),
            }
        )
    return response


# API: Get QR Code details
@app.get("/api/v1/qrcodes/{id}", response_model=QRCodeResponse)
def get_qrcode(id: int, db: Session = Depends(get_db)):
    qr = db.query(QRCodeModel).filter(QRCodeModel.id == id).first()
    if not qr:
        raise HTTPException(status_code=404, detail="QR Code not found")

    return {
        "id": qr.id,
        "title": qr.title,
        "target_url": qr.target_url,
        "s3_key": qr.s3_key,
        "s3_url": qr.s3_url,
        "scan_count": qr.scan_count,
        "created_at": qr.created_at.isoformat(),
    }


# Redirect and scan-tracking endpoint
@app.get("/qr/{id}", response_class=RedirectResponse)
def redirect_qrcode(id: int, db: Session = Depends(get_db)):
    qr = db.query(QRCodeModel).filter(QRCodeModel.id == id).first()
    if not qr:
        raise HTTPException(status_code=404, detail="QR Code not found")

    # Increment scan count
    qr.scan_count += 1
    db.commit()

    logger.info(f"QR Code {id} scanned. Redirecting to {qr.target_url}")
    return RedirectResponse(url=qr.target_url, status_code=status.HTTP_302_FOUND)


# API: Delete QR Code
@app.delete("/api/v1/qrcodes/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_qrcode(id: int, db: Session = Depends(get_db)):
    qr = db.query(QRCodeModel).filter(QRCodeModel.id == id).first()
    if not qr:
        raise HTTPException(status_code=404, detail="QR Code not found")

    # Delete from S3 first
    if qr.s3_key and qr.s3_key != "temp":
        try:
            delete_qr_image(qr.s3_key)
        except Exception as e:
            logger.error(f"Failed to delete S3 image for QR {id}: {e}")

    # Delete from database
    db.delete(qr)
    db.commit()
    logger.info(f"QR Code {id} deleted successfully.")
    return None


# Delete via Form POST (UI capability)
@app.post("/delete/{id}", response_class=RedirectResponse)
def delete_qrcode_form(id: int, db: Session = Depends(get_db)):
    try:
        delete_qrcode(id, db)
    except HTTPException:
        pass
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# Health Check-live demo version
@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "service": "qrcode-generator-service"}
