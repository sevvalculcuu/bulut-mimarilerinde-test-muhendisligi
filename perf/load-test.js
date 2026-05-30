import http from 'k6/http';
import { check, sleep } from 'k6';

// k6 Load Test Configuration Options
export const options = {
  stages: [
    { duration: '30s', target: 20 }, // Ramp-up: 0 to 20 virtual users in 30s
    { duration: '1m', target: 20 },  // Plateau: hold 20 virtual users for 1m
    { duration: '30s', target: 0 },  // Ramp-down: 20 to 0 virtual users in 30s
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],             // Error rate must be less than 1%
    http_req_duration: ['p(95)<200'],           // 95% of requests must complete under 200ms
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  // Scenario Part 1: Health Check
  let healthRes = http.get(`${BASE_URL}/healthz`);
  check(healthRes, {
    'healthz status is 200': (r) => r.status === 200,
    'healthz is healthy': (r) => r.json().status === 'healthy',
  });
  sleep(0.5);

  // Scenario Part 2: Generate QR Code
  let payload = JSON.stringify({
    title: `LoadTest - ${Math.random().toString(36).substring(7)}`,
    target_url: 'https://useinsider.com',
  });
  let params = {
    headers: { 'Content-Type': 'application/json' },
  };

  let createRes = http.post(`${BASE_URL}/api/v1/qrcodes`, payload, params);
  let createOk = check(createRes, {
    'create status is 201': (r) => r.status === 201,
    'has s3_url': (r) => r.json().s3_url !== undefined,
  });

  if (createOk) {
    let qrId = createRes.json().id;

    // Scenario Part 3: Test scan redirection tracking
    // Turn off redirect following so we directly hit our endpoint and read the 302 redirect header
    let redirectRes = http.get(`${BASE_URL}/qr/${qrId}`, { redirects: 0 });
    check(redirectRes, {
      'redirect status is 302': (r) => r.status === 302,
      'redirects to correct target': (r) => r.headers['Location'] === 'https://useinsider.com/',
    });
    sleep(0.5);

    // Scenario Part 4: Retrieve QR metadata
    let getRes = http.get(`${BASE_URL}/api/v1/qrcodes/${qrId}`);
    check(getRes, {
      'retrieve status is 200': (r) => r.status === 200,
      'scan_count is positive': (r) => r.json().scan_count > 0,
    });
  }

  sleep(1);
}
