import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import testcontainers
from testcontainers.postgres import PostgresContainer
from testcontainers.localstack import LocalStackContainer

from src.database import Base
from src.models import QRCodeModel
import src.s3_service
import src.database


@pytest.mark.integration
def test_database_and_s3_integration():
    """
    Integration test spinning up containerized Postgres and LocalStack via Testcontainers.
    Validates model mapping on real Postgres and S3 uploads/deletions on real LocalStack S3.
    """
    print("\nStarting Testcontainers Postgres and LocalStack...")

    # 1. Start PostgreSQL Container
    with PostgresContainer("postgres:16") as postgres:
        postgres_url = postgres.get_connection_url()
        print(f"PostgreSQL container running at: {postgres_url}")

        # 2. Start LocalStack Container
        with LocalStackContainer("localstack/localstack:latest") as localstack:
            # LocalStack starts all services, we retrieve the endpoint URL
            s3_url = localstack.get_url()
            print(f"LocalStack container running at: {s3_url}")

            # 3. Override application configuration environment variables
            os.environ["DATABASE_URL"] = postgres_url
            os.environ["AWS_ENDPOINT_URL"] = s3_url
            os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
            os.environ["AWS_ACCESS_KEY_ID"] = "test"
            os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
            os.environ["AWS_S3_BUCKET_NAME"] = "integration-qrcode-bucket"

            # Reload S3 configs in src.s3_service
            src.s3_service.AWS_ENDPOINT_URL = s3_url
            src.s3_service.BUCKET_NAME = "integration-qrcode-bucket"

            # 4. Set up Database schema on Postgres container
            engine = create_engine(postgres_url)
            TestingSession = sessionmaker(bind=engine)
            Base.metadata.create_all(bind=engine)
            db = TestingSession()

            # Ensure S3 Bucket exists in LocalStack S3 container
            src.s3_service.ensure_bucket_exists()

            # Check S3 bucket created successfully
            s3_client = src.s3_service.get_s3_client()
            buckets = s3_client.list_buckets()
            bucket_names = [b["Name"] for b in buckets.get("Buckets", [])]
            assert "integration-qrcode-bucket" in bucket_names
            print("S3 Bucket verification: OK")

            # 5. DB Test: Insert record using SQLAlchemy on Postgres
            qr_record = QRCodeModel(
                title="Integration Test QR",
                target_url="https://marmara.edu.tr",
                s3_key="qrcodes/integration-test.png",
                s3_url=f"{s3_url}/integration-qrcode-bucket/qrcodes/integration-test.png",
                scan_count=12,
            )
            db.add(qr_record)
            db.commit()
            db.refresh(qr_record)

            assert qr_record.id is not None
            assert qr_record.title == "Integration Test QR"
            print("Postgres insertion test: OK")

            # 6. S3 Test: Upload dummy content to LocalStack S3
            dummy_image_data = b"fake-png-binary-stream-content"
            uploaded_url = src.s3_service.upload_qr_image(
                dummy_image_data, qr_record.s3_key
            )
            assert qr_record.s3_key in uploaded_url

            # Verify file exists inside LocalStack S3 bucket
            response = s3_client.get_object(
                Bucket="integration-qrcode-bucket", Key=qr_record.s3_key
            )
            uploaded_content = response["Body"].read()
            assert uploaded_content == dummy_image_data
            print("LocalStack S3 image upload and read test: OK")

            # 7. S3 Deletion Test: Delete S3 object and verify
            src.s3_service.delete_qr_image(qr_record.s3_key)
            with pytest.raises(Exception):
                # Requesting deleted key should raise ClientError (404)
                s3_client.get_object(
                    Bucket="integration-qrcode-bucket", Key=qr_record.s3_key
                )
            print("LocalStack S3 image deletion test: OK")

            # Cleanup DB session
            db.close()
            Base.metadata.drop_all(bind=engine)
