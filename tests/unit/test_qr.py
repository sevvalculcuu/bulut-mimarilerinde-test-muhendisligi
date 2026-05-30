from tests.factories import QRCodeFactory
from src.models import QRCodeModel


def test_health_check(client):
    """
    Verifies that the healthz endpoint is responsive and healthy.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "qrcode-generator-service",
    }


def test_generate_qrcode_success(client, test_db):
    """
    Verifies successful QR code generation, DB record inclusion, and S3 URL configuration.
    """
    payload = {"title": "Marmara University", "target_url": "https://marmara.edu.tr"}
    response = client.post("/api/v1/qrcodes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Marmara University"
    assert data["target_url"] == "https://marmara.edu.tr/"
    assert "s3_url" in data
    assert "id" in data

    # Assert DB has the item
    db_item = test_db.query(QRCodeModel).filter(QRCodeModel.id == data["id"]).first()
    assert db_item is not None
    assert db_item.title == "Marmara University"
    assert db_item.target_url == "https://marmara.edu.tr/"
    assert db_item.s3_key == f"qrcodes/{db_item.id}.png"


def test_generate_qrcode_invalid_url(client):
    """
    Verifies that creating a QR code with an invalid URL fails validation.
    """
    payload = {"title": "Bad Request", "target_url": "not-a-valid-url"}
    response = client.post("/api/v1/qrcodes", json=payload)
    assert response.status_code == 422


def test_list_qrcodes(client, test_db):
    """
    Verifies listing all generated QR codes.
    """
    # Create 3 QR codes using the factory
    for _ in range(3):
        qr = QRCodeFactory()
        test_db.add(qr)
    test_db.commit()

    response = client.get("/api/v1/qrcodes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_qrcode_details(client, test_db):
    """
    Verifies retrieving a specific QR code's details.
    """
    qr = QRCodeFactory(title="Special Title", target_url="https://google.com")
    test_db.add(qr)
    test_db.commit()
    test_db.refresh(qr)

    response = client.get(f"/api/v1/qrcodes/{qr.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Special Title"
    assert data["target_url"] == "https://google.com"


def test_get_qrcode_not_found(client):
    """
    Verifies 404 error when querying non-existing QR code.
    """
    response = client.get("/api/v1/qrcodes/999")
    assert response.status_code == 404


def test_redirect_qrcode_and_track_scan(client, test_db):
    """
    Verifies that visiting /qr/{id} increments scan count and redirects to target URL.
    """
    target = "https://github.com"
    qr = QRCodeFactory(target_url=target, scan_count=0)
    test_db.add(qr)
    test_db.commit()
    test_db.refresh(qr)

    # Visit redirect endpoint (do not allow follow redirects so we can inspect headers)
    response = client.get(f"/qr/{qr.id}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == target

    # Verify scan count in database is incremented to 1
    test_db.refresh(qr)
    assert qr.scan_count == 1


def test_delete_qrcode(client, test_db):
    """
    Verifies deletion of QR code from the database.
    """
    qr = QRCodeFactory()
    test_db.add(qr)
    test_db.commit()
    test_db.refresh(qr)

    # Delete
    response = client.delete(f"/api/v1/qrcodes/{qr.id}")
    assert response.status_code == 204

    # Verify it does not exist in DB
    db_item = test_db.query(QRCodeModel).filter(QRCodeModel.id == qr.id).first()
    assert db_item is None
