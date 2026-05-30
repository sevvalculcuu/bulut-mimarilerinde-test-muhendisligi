import os
import time
import socket
import subprocess
import pytest
from playwright.sync_api import sync_playwright


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="module")
def live_server():
    """
    Spins up the FastAPI server on port 8001 in a background process.
    Forces clean database tables and local SQLite usage for E2E isolation.
    """
    # Clean previous test database to ensure fresh run
    test_db_path = "./qrcode.db"
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

    # Start FastAPI app on port 8001 using uvicorn in a separate process
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///./qrcode.db"
    env["AWS_ENDPOINT_URL"] = "none"  # Disable S3 upload errors during E2E UI testing

    proc = subprocess.Popen(
        [
            "python3",
            "-m",
            "uvicorn",
            "src.main:app",
            "--port",
            "8001",
            "--host",
            "127.0.0.1",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for the server to bind and be available
    server_started = False
    for _ in range(50):
        if is_port_open("127.0.0.1", 8001):
            server_started = True
            break
        time.sleep(0.1)

    if not server_started:
        proc.terminate()
        raise RuntimeError("FastAPI server failed to start on port 8001 for E2E tests.")

    yield "http://localhost:8001"

    proc.terminate()
    proc.wait()


@pytest.mark.e2e
def test_frontend_qr_flow(live_server):
    """
    End-to-End browser test covering:
    1. Navigation to the main dashboard.
    2. Form submission to create a QR code.
    3. Verifying the card has been rendered on the active page.
    4. Navigating to the redirection endpoint to trigger click counts.
    5. Triggering code deletion.
    """
    with sync_playwright() as p:
        # Launch headless Chromium browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Navigate to the App
        page.goto(live_server)

        # Verify page header is rendered
        assert page.locator("h1").inner_text() == "Q-Flow"
        print("E2E Step 1: Web dashboard loaded successfully.")

        # 2. Form submission
        page.fill("#title", "E2E Test QR Code")
        page.fill("#target_url", "https://marmara.edu.tr")
        page.click("#submit-btn")

        # Wait for page reload/redirect
        page.wait_for_load_state("networkidle")

        # 3. Verify item listed in Library
        qr_title = page.locator(".qr-title").first
        assert "E2E Test QR Code" in qr_title.inner_text()

        qr_target = page.locator(".qr-target").first
        assert "https://marmara.edu.tr" in qr_target.inner_text()
        print("E2E Step 2: Form submitted and card created.")

        # Verify scan count is 0
        scan_value = page.locator(".scan-value").first
        assert scan_value.inner_text() == "0"

        # 4. Click 'Test Scan' (redirection check)
        # We capture the new tab that opens up
        with page.context.expect_page() as new_page_info:
            page.locator(".btn-redirect").first.click()
        new_page = new_page_info.value

        # Wait for new page load
        new_page.wait_for_load_state()
        assert "marmara.edu.tr" in new_page.url
        new_page.close()
        print("E2E Step 3: Redirection target matches destination.")

        # Refresh dashboard and verify scan count is incremented to 1
        page.reload()
        page.wait_for_load_state("networkidle")
        new_scan_value = page.locator(".scan-value").first
        assert new_scan_value.inner_text() == "1"
        print("E2E Step 4: Scan count incremented successfully.")

        # 5. Trigger deletion
        # Handle the browser confirm() alert dialog automatically
        page.once("dialog", lambda dialog: dialog.accept())
        page.locator(".btn-delete").first.click()

        # Wait for page reload
        page.wait_for_load_state("networkidle")

        # Verify empty state or card disappears
        assert page.locator("article.qr-card").count() == 0
        print("E2E Step 5: QR Code deletion succeeded.")

        browser.close()
