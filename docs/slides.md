# Q-Flow: Cloud-Native QR Code Generator Service
**MTH2526-B25 Cloud Architecture and Testing Engineering**
*Dönem Projesi Sunumu*

**Öğrenci:** Şevval Çülcü (20221001)
**Eğitmen:** Büşra Ayaksız

---

## Slide 1: Problem ve Çözüm
- **Mevcut Sorun**: Statik QR kodlarının takibi yapılamaz, yönlendirme linkleri güncellenemez ve bulut entegrasyonu olmadan ölçeklenemez.
- **Çözüm (Q-Flow)**:
  - Dinamik yönlendirme yapan QR Code API.
  - S3 (LocalStack) üzerinde görsel depolama.
  - Tıklamaların / taramaların veritabanında (PostgreSQL) izlenmesi.
  - Kapsamlı test piramidi otomasyonu.

---

## Slide 2: Sistem Mimarisi
- **Frontend**: Glassmorphic modern HTML/JS kullanıcı arayüzü.
- **Backend**: FastAPI (Python), CORS & Prometheus entegrasyonu.
- **Storage**: AWS S3 (LocalStack emülasyonu) QR kod görselleri için.
- **Veritabanı**: PostgreSQL (Görsel metadata ve tarama sayaçları için).
- **Observability**: Prometheus & Grafana (Metrikler) + OpenTelemetry & Jaeger (Distributed Tracing).
- **Orkestrasyon**: Kubernetes (Minikube) + Helm.

---

## Slide 3: Test Stratejisi (Test Piramidi)
- **Birim (Unit) Testleri**:
  - FastAPI endpoint doğrulamaları ve qrcode motoru testleri (pytest).
  - %70+ coverage barajı.
- **Entegrasyon Testleri**:
  - **Testcontainers** kullanılarak PostgreSQL ve LocalStack S3 docker konteynerleri üzerinde veri yazma/silme testleri.
- **Uçtan Uca (E2E) Testler**:
  - **Playwright** ile tarayıcı simülasyonu: QR ekleme, redirection testi, tarama sayacı artışı ve silme doğrulaması.
- **API Testleri**:
  - **Postman + Newman** ile CI'da koşan API doğrulama senaryoları.

---

## Slide 4: CI/CD Pipeline (GitHub Actions)
- **Tetikleyici**: Main/Master branch'e PR açıldığında veya push yapıldığında tetiklenir.
- **Aşamalar**:
  1. **Lint**: Black & Ruff ile kod standartları kontrolü.
  2. **Test**: Pytest ile birim ve entegrasyon (Testcontainers) testleri.
  3. **Build**: Multi-stage Docker image build.
  4. **Deploy**: Helm lint ve template dry-run.
  5. **Smoke**: Docker'da uygulamayı ayağa kaldırıp Newman ile uçtan uca API testi koşma.

---

## Slide 5: Gözlemlenebilirlik (Monitoring & Tracing)
- **Prometheus Exporter**: FastAPI istek sıklığı, hata oranları ve latency metrikleri.
- **Grafana Panelleri**:
  - HTTP Latency (p95)
  - Throughput (İstek sıklığı)
  - Hata Oranı (%)
  - QR Yönlendirme İstatistikleri
- **OpenTelemetry & Jaeger**:
  - FastAPI istekleri -> SQLAlchemy sorguları -> Boto3 S3 çağrıları arasında uçtan uca dağıtık izleme (tracing).

---

## Slide 6: Performans Analizi (k6 Load Test)
- **Senaryo**:
  - 30 sn: 0 -> 20 Sanal Kullanıcı (Ramp-up)
  - 60 sn: 20 Sanal Kullanıcı (Plateau)
  - 30 sn: 20 -> 0 Sanal Kullanıcı (Ramp-down)
- **Sonuçlar**:
  - **Başarı Oranı**: %100 (0.00% Hata oranı).
  - **p95 Latency**: 42.15 ms (Hedef < 200 ms).
  - **Peak Throughput**: 16.5 request/second.

---

## Slide 7: Öğrendiklerim ve Zorluklar
- **Öğrenilen Dersler**:
  - **LocalStack** ile bulut servislerinin maliyetsiz lokal testi.
  - **Testcontainers** sayesinde test veritabanlarının sıfır bağımlılıkla izole çalıştırılması.
  - **OpenTelemetry** ile dağıtık servis zincirlerinin debugging kolaylığı.
- **Karşılaşılan Zorluklar**:
  - Testcontainers container startup gecikmeleri ve Docker daemon izinleri.
  - Helm şablonları içerisinde configmap env enjeksiyonları.
