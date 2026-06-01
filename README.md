# Q-Flow: Cloud-Native QR Code Generator Service

**Marmara University**  
**Engineering Faculty • Department of Computer Engineering**  
**MTH2526-B25 — Testing Engineering in Cloud Architectures (2025–2026)**  
**Term Project (Topic 35: QR Code Generator Service)**  

* Geliştirenler: 
  * **Şevval Çulcu** (Öğrenci No: 171423961)  
  * **Yusuf Durmuş** (Öğrenci No: 170423965)  
* Eğitmen: **Büşra Ayaksız** (busra.ayaksiz@useinsider.com)  
* Lisans: **MIT**  

---

## 🚀 Proje Hakkında (Topic 35)
**Q-Flow**, dinamik yönlendirme (routing) yeteneklerine sahip bulut-yerel bir QR Kod oluşturma ve tıklama takip servisidir. 
Üretilen QR kodları doğrudan hedef adrese değil, Q-Flow servisinin `/qr/{id}` yönlendirme adresine işaret eder. 
Böylece kullanıcı kodu tarattığında istek önce bizim servisimizden geçerek PostgreSQL veritabanındaki `scan_count` değerini artırır ve ardından hedef URL'e yönlendirilir (302 Redirect). QR kod görselleri **AWS S3 (LocalStack)** üzerinde saklanır.

---

## 🛠️ Mimari ve Teknolojik Altyapı
Uygulama bileşenleri gevşek bağlı (loosely coupled) mikroservis desenine uygundur:
* **Backend**: FastAPI (Python 3.13) + SQLAlchemy ORM.
* **Database**: PostgreSQL (Ana depolama) & SQLite (Birim testleri).
* **Object Storage**: AWS S3 (Lokal testler için **LocalStack** emülatörü).
* **Observability**: **Prometheus** (Metrikler), **Grafana** (Paneller) ve **OpenTelemetry + Jaeger** (Dağıtık tracing).
* **Containerization & Orchestration**: Multi-stage **Dockerfile**, **Docker Compose** & **Kubernetes (Minikube)**.
* **GitOps & Scaling**: **Helm Chart**, **KEDA** (Prometheus metrik tabanlı autoscaler) ve **ArgoCD**.
* **CI/CD**: **GitHub Actions** (Linting -> Pytest -> Docker Build -> Helm lint -> Newman smoke test).

---

## 📂 Klasör Yapısı
```text
bulutproje/
├── README.md                 # Kurulum ve çalıştır kılavuzu
├── LICENSE                   # MIT Lisans dosyası
├── pyproject.toml            # Poetry paket yapılandırması
├── requirements.txt          # Python bağımlılıkları fallback
├── Dockerfile                # Multi-stage Docker imaj tanımı
├── docker-compose.yml        # Yerel orkestrasyon dosyası
├── src/                      # Uygulama kaynak kodları
│   ├── main.py               # FastAPI uygulaması ve REST API
│   ├── models.py             # SQLAlchemy DB Modelleri
│   ├── database.py           # PostgreSQL / SQLite bağlantı katmanı
│   ├── s3_service.py         # AWS S3 / LocalStack dosya işlemleri
│   ├── tracing.py            # OpenTelemetry & Jaeger ayarları
│   └── templates/
│       └── index.html        # Premium Glassmorphic Frontend UI
├── tests/                    # Test Otomasyon Süiti
│   ├── factories.py          # Factory Boy & Faker modelleri
│   ├── conftest.py           # Pytest test fikstürleri
│   ├── unit/                 # Birim testleri (FastAPI & S3)
│   ├── integration/          # Testcontainers PostgreSQL & S3 testleri
│   └── e2e/                  # Playwright Uçtan Uca tarayıcı testleri
├── postman/
│   └── collection.json       # Postman Newman entegrasyon testleri
├── k8s/                      # Kubernetes Ham Manifest Dosyaları
├── helm/                     # Helm Chart Paketlemesi
├── keda/                     # KEDA ScaledObject tanımı
├── argocd/                   # ArgoCD GitOps uygulaması
├── perf/                     # k6 Performans Test Senaryoları & Raporu
├── monitoring/               # Prometheus & Grafana ayarları
└── docs/                     # Şartname Raporları & Sunum Slaytları
    ├── architecture.png      # Mimari diyagram
    ├── work-distribution.md  # İş paylaşımı dosyası
    ├── slides.md             # Sunum slaytları (Markdown)
    ├── slides.pdf            # Sunum slaytları (Hazır PDF)
    ├── final-report.md       # Final raporu (Markdown)
    └── final-report.pdf      # Final raporu (Akademik IEEE PDF)
```

---

## ⚡ Yerel Çalıştırma (Docker Compose)
Tüm servisleri (FastAPI, PostgreSQL, LocalStack S3, Prometheus, Grafana, Jaeger) tek bir komutla ayağa kaldırın:
```bash
docker-compose up -d --build
```
Servisler başladıktan sonra tarayıcınızdan şu adreslere erişebilirsiniz:
* **Q-Flow Frontend UI**: [http://localhost:8000/](http://localhost:8000/)
* **Prometheus Dashboard**: [http://localhost:9090/](http://localhost:9090/)
* **Grafana Dashboard**: [http://localhost:3000/](http://localhost:3000/) *(Kullanıcı: `admin` / Şifre: `admin`)*
* **Jaeger Tracing UI**: [http://localhost:16686/](http://localhost:16686/)

---

## 🧪 Test Otomasyon Süitini Çalıştırma
Öncelikle lokal bir sanal ortam (`venv`) kurun ve bağımlılıkları yükleyin:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 1. Birim (Unit) Testleri & Coverage Ölçümü (>=%70)
Mock bağımlılıkları kullanarak izole birim testlerini çalıştırın:
```bash
pytest tests/unit/ -v --cov=src
```

### 2. Entegrasyon (Integration) Testleri (Testcontainers)
Arka planda Docker daemon üzerinden Postgres ve LocalStack konteynerleri açarak çalışan entegrasyon testleri:
```bash
pytest tests/integration/ -v
```

### 3. E2E Tarayıcı Testleri (Playwright)
Playwright tarayıcı kütüphanelerini kurup E2E senaryolarını test edin:
```bash
playwright install chromium
pytest tests/e2e/ -v
```

### 4. Postman API Testleri (Newman)
FastAPI servisi çalışırken API senaryolarını koşturun:
```bash
npm install -g newman
newman run postman/collection.json --env-var "baseUrl=http://localhost:8000"
```

### 5. Performans Testi (k6)
k6 aracı ile load test senaryosunu başlatın:
```bash
k6 run perf/load-test.js
```

---

## ☸️ Kubernetes (Minikube) & Helm Dağıtımı

### 1. Minikube Başlatma ve Image Aktarımı
```bash
minikube start
# Docker CLI'ı minikube ortamına bağlayın
eval $(minikube docker-env)
# Imajı minikube içinde derleyin
docker build -t qrcode-app:latest .
```

### 2. Helm ile Dağıtım (Deploy)
```bash
helm install qrcode-generator ./helm/qrcode-generator
```

### 3. KEDA Autoscaler & ArgoCD GitOps
```bash
# KEDA ScaledObject uygulaması
kubectl apply -f keda/scaled-object.yaml

# ArgoCD uygulamasını tanımlama
kubectl apply -f argocd/application.yaml
```

---

## 🎥 Canlı Sunum Can Simidi (Demo Videosu)
Sunum esnasında canlı demoda çıkabilecek teknik aksaklıklara karşı hazırlanan yedek demo videosu linki:
* **Demo Videosu**: [Google Drive / YouTube Linki]([https://drive.google.com/drive/folders/your-folder-id-here](https://drive.google.com/file/d/1DgMoOCOM7MNNNxCdYwgvzoprd1IPVQKO/view?usp=sharing))
* **Sunum Slaytları**: [docs/slides.pdf](file:///Users/sevvalculcu/bulutproje/docs/slides.pdf) konumunda hazırdır.
* **Akademik Rapor**: [docs/final-report.pdf](file:///Users/sevvalculcu/bulutproje/docs/final-report.pdf) konumundadır.
