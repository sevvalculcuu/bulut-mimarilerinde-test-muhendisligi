import src.s3_service
from botocore.exceptions import ClientError


def test_get_s3_client():
    """
    Verifies that get_s3_client returns a valid boto3 client object.
    """
    client = src.s3_service.get_s3_client()
    assert client is not None


def test_ensure_bucket_exists_already_exists(monkeypatch):
    """
    Verifies ensure_bucket_exists succeeds directly if bucket already exists.
    """
    called = []

    class MockS3Client:
        def head_bucket(self, Bucket):
            called.append("head")
            return {}

    monkeypatch.setattr(src.s3_service, "get_s3_client", lambda: MockS3Client())
    src.s3_service.ensure_bucket_exists()
    assert "head" in called


def test_ensure_bucket_exists_creation(monkeypatch):
    """
    Verifies ensure_bucket_exists triggers S3 bucket creation if head_bucket returns 404.
    """
    called = []

    class MockS3Client:
        def head_bucket(self, Bucket):
            raise ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}}, "head_bucket"
            )

        def create_bucket(self, Bucket):
            called.append("create")
            return {}

    monkeypatch.setattr(src.s3_service, "get_s3_client", lambda: MockS3Client())
    src.s3_service.ensure_bucket_exists()
    assert "create" in called


def test_upload_qr_image(monkeypatch):
    """
    Verifies upload_qr_image makes put_object call and builds valid URL.
    """
    called = []

    class MockS3Client:
        def put_object(self, Bucket, Key, Body, ContentType):
            called.append("put")
            return {}

    monkeypatch.setattr(src.s3_service, "get_s3_client", lambda: MockS3Client())
    url = src.s3_service.upload_qr_image(b"mock-content", "qrcodes/test-qr.png")
    assert "put" in called
    assert "qrcodes/test-qr.png" in url


def test_delete_qr_image(monkeypatch):
    """
    Verifies delete_qr_image triggers S3 delete_object call.
    """
    called = []

    class MockS3Client:
        def delete_object(self, Bucket, Key):
            called.append("delete")
            return {}

    monkeypatch.setattr(src.s3_service, "get_s3_client", lambda: MockS3Client())
    src.s3_service.delete_qr_image("qrcodes/test-qr.png")
    assert "delete" in called
