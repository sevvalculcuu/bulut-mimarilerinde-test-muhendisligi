import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "qrcode-bucket")

# If AWS_ENDPOINT_URL is blank or "none" (case insensitive), we set it to None to use real AWS
if not AWS_ENDPOINT_URL or AWS_ENDPOINT_URL.lower() == "none":
    AWS_ENDPOINT_URL = None


def get_s3_client():
    """
    Creates and returns a boto3 S3 client with configured parameters.
    """
    params = {
        "region_name": AWS_REGION,
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    }
    if AWS_ENDPOINT_URL:
        params["endpoint_url"] = AWS_ENDPOINT_URL
        params["use_ssl"] = False
        params["verify"] = False

    return boto3.client("s3", **params)


def ensure_bucket_exists():
    """
    Ensures that the target S3 bucket exists. If not, it creates it.
    """
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        logger.info(f"S3 bucket '{BUCKET_NAME}' already exists.")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        # 404 means bucket does not exist
        if error_code in ["404", "NoSuchBucket"]:
            try:
                # For us-east-1, LocationConstraint causes errors, so handle regionally
                if AWS_REGION == "us-east-1":
                    s3.create_bucket(Bucket=BUCKET_NAME)
                else:
                    s3.create_bucket(
                        Bucket=BUCKET_NAME,
                        CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
                    )
                logger.info(f"Created S3 bucket '{BUCKET_NAME}'.")
            except Exception as ex:
                logger.error(f"Failed to create S3 bucket: {ex}")
                raise ex
        else:
            logger.error(f"Error checking bucket: {e}")
            raise e


def upload_qr_image(file_content: bytes, s3_key: str) -> str:
    """
    Uploads QR code bytes directly to S3 and returns the public/internal download URL.
    """
    s3 = get_s3_client()
    try:
        s3.put_object(
            Bucket=BUCKET_NAME, Key=s3_key, Body=file_content, ContentType="image/png"
        )

        # Build s3 url. If using LocalStack, we should use the configured endpoint
        # Otherwise, standard AWS S3 format
        if AWS_ENDPOINT_URL:
            # E.g. http://localhost:4566/qrcode-bucket/some-key.png
            url = f"{AWS_ENDPOINT_URL}/{BUCKET_NAME}/{s3_key}"
        else:
            url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        logger.info(f"Uploaded {s3_key} to S3. URL: {url}")
        return url
    except Exception as e:
        logger.error(f"Failed to upload {s3_key} to S3: {e}")
        raise e


def delete_qr_image(s3_key: str):
    """
    Deletes the QR code image from S3.
    """
    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        logger.info(f"Deleted {s3_key} from S3.")
    except Exception as e:
        logger.error(f"Failed to delete {s3_key} from S3: {e}")
        raise e
