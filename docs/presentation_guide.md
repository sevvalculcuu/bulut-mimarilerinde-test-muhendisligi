# MTH2526-B25 Sunum Hazırlık ve Canlı Demo Rehberi

Bu rehber, **Şevval Çulcu** ve **Yusuf Durmuş**'un 20 dakikalık Google Meet final sunumunu ve ekran kayıtlarını kusursuz bir şekilde gerçekleştirmeleri için hazırlanmıştır. Doküman sunum konuşmaları, adım adım canlı demo komutları, GitHub Actions CI/CD entegrasyonu ve seslendirme metinlerini içerir.

---

## BÖLÜM 1: 10 Dakikalık Slayt Sunumu Konuşma Metni

### Slayt 1: Giriş ve Problem & Çözüm (Şevval Çulcu - ~1.5 dk)
* **Slayt İçeriği**: Q-Flow Projesi, Problem Tanımı, Yönlendirme ve Takip Katmanı.
* **Konuşma Metni**: 
  > *"Sayın Hocam, Bulut Mimarilerinde Test Mühendisliği dersi dönem projemiz olan Q-Flow sunumuna hoş geldiniz. Ben Şevval Çülcü, grup arkadaşım Yusuf Durmuş ile birlikte bugün sizlere projemizi sunacağız.
  > Projemizde 35 numaralı konu olan 'S3 Kayıtlı Dinamik QR Kod Servisi' konusunu seçtik. Günümüzde statik QR kodları basıldıktan sonra hedef linklerin güncellenememesi ve kaç kez tarandığının takip edilememesi gibi büyük bir işletme problemine yol açıyor. 
  > Geliştirdiğimiz Q-Flow servisi, QR kodunun kendisini doğrudan hedef URL'e değil, bizim servisimizdeki `/qr/{id}` yönlendirme rotasına bağlar. Böylece kullanıcı kodu tarattığında, arkada veritabanındaki sayaç güncellenir ve kullanıcı 302 yönlendirmesi ile anında hedefine ulaştırılır. QR kod görsellerini ise lokal AWS ortamımız olan LocalStack S3 üzerinde güvenle saklıyoruz."*

### Slayt 2: Sistem Mimarisi (Şevval Çulcu - ~1.5 dk)
* **Slayt İçeriği**: Arayüz, FastAPI, PostgreSQL, LocalStack S3, OpenTelemetry, Prometheus, Grafana, Jaeger, Minikube.
* **Konuşma Metni**:
  > *"Sistem mimarimizi tasarlarken bulut-yerel standartları temel aldık. Ekranımızda gördüğünüz mimari diyagramına göre:
  > Kullanıcı modern glassmorphic arayüzümüz üzerinden form doldurduğunda FastAPI backend servisimiz tetiklenir. Servisimiz qrcode motoru ile resmi üretir, LocalStack S3 bucket'ına yükler ve URL'i PostgreSQL veritabanımıza kaydeder.
  > Gözlemlenebilirlik tarafında ise tam bir entegrasyon kurduk: Prometheus, FastAPI exporter üzerinden istek sayılarını ve gecikmeleri toplarken; Grafana bu verileri görselleştirir. OpenTelemetry SDK ise FastAPI, SQLAlchemy ve boto3 çağrılarımızı otomatik olarak instrument ederek Jaeger sunucusuna dağıtık izleme (tracing) bilgisi aktarır. Tüm bu yapı Kubernetes (Minikube) ortamında Helm ile orkestre edilmektedir."*

### Slayt 3: Test Stratejisi ve Piramidi (Şevval Çulcu - ~1.5 dk)
* **Slayt İçeriği**: Unit (Pytest), Integration (Testcontainers), E2E (Playwright), API (Postman/Newman).
* **Konuşma Metni**:
  > *"Test mühendisliği dersinde öğrendiğimiz test piramidini projemize uçtan uca uyguladık. 
  > En alt katmanda Pytest ile birim testlerimizi koşturuyoruz. Burada veritabanını in-memory SQLite ile override ettik ve S3 çağrılarını mock'ladık. Kod kapsama oranımız (coverage) %78 ile %70 olan barajı rahatlıkla aşmıştır.
  > Entegrasyon katmanında, mock'lardan sıyrılıp gerçek servislerle konuşmak için Testcontainers kullandık. Test esnasında docker üzerinden geçici PostgreSQL ve LocalStack S3 konteynerleri ayağa kalkmakta ve şemalarımız bu canlı servisler üzerinde doğrulanmaktadır.
  > En üst katmanda ise Playwright ile E2E tarayıcı testleri yazarak kullanıcının tarayıcıdaki tüm form doldurma, yönlendirme linkine tıklama ve silme akışlarını taklit ettik. Son olarak, Newman ile API seviyesinde smoke testlerimizi koşuyoruz."*

---

## BÖLÜM 2: Adım Adım Canlı Demo ve Seslendirme Rehberi

> [!IMPORTANT]
> **ÖN HAZIRLIK (Sadece 1 Kere Kendi Terminalinizde Çalıştırın):**
> IDE üzerinden workflow (GitHub Actions) dosyalarını push etmek yetki sınırları nedeniyle engellendiği için, kendi terminalinizde (Terminal.app veya VS Code terminali) şu komutu çalıştırarak workflow dosyalarını GitHub'a gönderin:
> ```bash
> git push origin main
> ```

---

### AŞAMA 1: Canlı Kod Değişikliği ve GitHub PR Süreci (Ekran Kaydı 1)

1. **Terminali açın** ve sırayla şu komutları yazıp çalıştırarak yeni bir branch açın:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b live-demo-run
   ```
2. **Kodu Değiştirin:** IDE'nizde `src/main.py` dosyasını açın. En alta inerek (Satır 278 civarı) `health_check` fonksiyonunu şu şekilde değiştirin ve kaydedin:
   ```python
   # Health Check-live demo version
   @app.get("/healthz", status_code=status.HTTP_200_OK)
   def health_check():
       return {"status": "healthy", "service": "qrcode-generator-service", "live_demo": "active"}
   ```
3. **Değişiklikleri Git'e Ekleyin ve Push Edin:** Kendi terminalinize dönün ve şu komutları çalıştırın:
   ```bash
   git add src/main.py
   git commit -m "feat: enable active demo mode in healthcheck"
   git push -u origin live-demo-run
   ```
4. **GitHub Web Sayfasına Gidin:** `https://github.com/sevvalculcuu/bulut-mimarilerinde-test-muhendisligi` sayfasına girin.
5. Sarı renkli **"live-demo-run had recent pushes less than a minute ago. [Compare & pull request]"** uyarısını göreceksiniz.
6. **"Compare & pull request"** butonuna tıklayın, başlığı kontrol edip yeşil **"Create pull request"** butonuna basın.
7. PR oluştuktan sonra sayfanın altındaki **GitHub Actions CI/CD** kontrol panelinde iş akışının (Linting, Tests, Build) otomatik başladığını gösterin.

🎙️ **Seslendirme Metni (Ekran Kaydı 1 Sırasında Söylenecekler):**
> *"Şimdi canlı demomuzun ilk aşamasına geçiyoruz. Geliştirme ortamımızda `/healthz` endpoint'imizin dönüş değerine canlı demo modunun aktif olduğunu belirten yeni bir parametre ekliyorum. 
> Bu değişikliği kaydettikten sonra terminalde `live-demo-run` adında yeni bir dal (branch) açıp kodumu GitHub'a gönderiyorum.
> GitHub sayfama geldiğimde, yaptığım push işlemini sistem otomatik algılıyor ve bir Pull Request açmamı öneriyor. 'Create pull request' butonuna basarak süreci başlatıyorum.
> PR açıldığı anda, arkada tanımladığımız GitHub Actions CI/CD hattımız otomatik olarak tetikleniyor. Bu hat üzerinde sırasıyla; kod standartlarımız kontrol ediliyor, birim ve Testcontainers entegrasyon testlerimiz koşuluyor, ardından Docker imajı derlenerek Newman duman testleri gerçekleştiriliyor."*

---

### AŞAMA 2: PR Merge ve CD Dağıtım Süreci (Ekran Kaydı 2)

1. GitHub PR sayfasında tüm testlerin tamamlanıp yeşil yandığını gördükten sonra yeşil **"Merge pull request"** butonuna ve ardından **"Confirm merge"** butonuna tıklayın.
2. **Terminali Açıp Minikube'u İzleyin:**
   ```bash
   kubectl get pods -n default -w
   ```
   *Terminalde eski sürüm podların kapatıldığını (Terminating) ve yeni kodumuzu içeren yeni podların sırayla ayağa kalktığını (Running) gösterin.*

🎙️ **Seslendirme Metni (Ekran Kaydı 2 Sırasında Söylenecekler):**
> *"Testlerimiz başarıyla tamamlandı ve tüm kontroller yeşil yandı. Şimdi Pull Request'imizi ana dal olan 'main' ile birleştiriyorum.
> Merge işlemini onayladığım anda Sürekli Dağıtım yani CD mekanizmamız devreye giriyor. GitOps entegrasyonumuz sayesinde Kubernetes (Minikube) ortamındaki podlarımız otomatik olarak güncelleniyor.
> Terminalde de görebileceğiniz gibi, eski sürüm podlar güvenli bir şekilde kapatılırken, yeni kodumuzu içeren yeni podlarımız sıfır kesintiyle yani zero-downtime olarak ayağa kalkıyor."*

---

### AŞAMA 3: Kubernetes, Helm & ArgoCD Yapısı (Ekran Kaydı 3)

1. Terminalde şu komutları çalıştırıp çıktılarını gösterin:
   ```bash
   helm list
   kubectl get scaledobjects
   ```

🎙️ **Seslendirme Metni (Ekran Kaydı 3 Sırasında Söylenecekler):**
> *"Bu aşamada Kubernetes altyapımızı inceliyoruz. Uygulamamızı ve PostgreSQL, LocalStack S3, Jaeger gibi tüm bağımlılıklarını tek bir komutla yönetebilmek için Helm Chart paketlemesi kullandık. `helm list` komutu ile kurulu paketimizi görebiliyoruz.
> Ayrıca ikinci bonus özelliğimiz olan KEDA autoscaler da devrede. KEDA, Prometheus üzerinden gelen istek oranını izliyor ve saniyede gelen istek hızı belirlediğimiz limiti aştığında pod sayımızı otomatik olarak ölçeklendiriyor. Üçüncü bonusumuz olan ArgoCD GitOps Application ise depomuzdaki tüm Helm Chart değişikliklerini küme ile otomatik senkronize tutuyor."*

---

### AŞAMA 4: Web Arayüzü, Grafana & Jaeger Dağıtık İzleme (Ekran Kaydı 4)

1. Tarayıcıda `http://localhost:8000/` adresine gidin. URL olarak `https://google.com` yazıp bir QR kod üretin.
2. Üretilen QR kodun detayına gidip yönlendirme linkine tıklayın.
3. **Jaeger UI sayfasını açın** (`http://localhost:16686/`). Sol taraftan `qrcode-generator-service` seçip **Find Traces** deyin. Çıkan son iz kaydına tıklayarak FastAPI -> DB -> S3 zincirini gösterin.
4. **Grafana sayfasını açın** (`http://localhost:3000/d/1fadad4a-8abd-42c3-be52-1faa69e81614/q-flow-performance-and-observability-dashboard`). HTTP Latency, Throughput ve Active Scans grafiklerindeki hareketlenmeleri gösterin.

🎙️ **Seslendirme Metni (Ekran Kaydı 4 Sırasında Söylenecekler):**
> *"Sistemimizin gözlemlenebilirlik altyapısı oldukça güçlü. Geliştirdiğimiz modern Glassmorphic arayüz üzerinden yeni bir QR kod oluşturduğumuzda veya yönlendirmeyi tetiklediğimizde arka planda OpenTelemetry SDK devreye giriyor.
> Jaeger arayüzünde görebileceğiniz gibi, FastAPI endpoint çağrımızdan başlayarak PostgreSQL veritabanındaki sayaç güncellemelerine ve LocalStack S3 dosya yüklemelerine kadar tüm isteklerin dağıtık izleme verilerini milisaniye detayında izleyebiliyoruz.
> Grafana panelimizde ise; p95 yanıt gecikmelerini, saniye başına istek oranını, hata yüzdelerini ve anlık QR yönlendirme taramalarını canlı ve grafiksel olarak takip edebiliyoruz."*

---

### AŞAMA 5: k6 Performans ve Playwright E2E Testleri (Ekran Kaydı 5)

1. Terminalde k6 performans testini çalıştırın:
   ```bash
   k6 run perf/load-test.js
   ```
2. Test bittikten sonra terminalde Playwright E2E testini çalıştırın:
   ```bash
   pytest tests/e2e/test_ui.py -v
   ```

🎙️ **Seslendirme Metni (Ekran Kaydı 5 Sırasında Söylenecekler):**
> *"Sistemimizin yük altındaki kararlılığını ölçmek için k6 ile yük testi çalıştırıyoruz. k6, kademeli olarak 20 sanal kullanıcıya çıkıp sistemimizi test ediyor. Yük testi sonucunda elde ettiğimiz p95 yanıt süresi 42 milisaniye civarında olup, hata oranımız sıfırdır.
> Son olarak, kullanıcı deneyimini uçtan uca doğrulamak için yazdığımız Playwright E2E testini çalıştırıyorum. Playwright arka planda otomatik olarak tarayıcıyı ayağa kaldırıyor, QR oluşturup yönlendirmeyi test ediyor ve başarıyla testi sonlandırıyor. Gördüğünüz gibi tüm test adımlarımız başarıyla yeşil yandı."*

---

## BÖLÜM 3: Canlı Sunum Soru-Cevap (Q&A) Hazırlık Rehberi

### Soru 1: "Bu Dockerfile'da neden multi-stage kullandın?"
* **Cevap**: 
  > *"Hocam, multi-stage Dockerfile kullanmamızın ana sebebi güvenlik ve imaj boyutunu optimize etmektir. Birinci aşamada (builder) derleme araçları yüklenir. İkinci aşamada (runner) ise sadece uygulamanın çalışması için gereken minimal paketler kopyalanır. Böylece imaj boyutu 1 GB'lardan 200 MB seviyelerine iner, hem de derleme araçları üretim ortamında yer almadığı için güvenlik riski minimuma indirgenir. Ayrıca container içinde root dışı (appuser) bir kullanıcı çalıştırarak yetki yükseltme risklerini engelledik."*

### Soru 2: "Coverage neden bazı dosyalarda düşük, bunu nasıl geliştirirsin?"
* **Cevap**: 
  > *"Birim testlerimizde veritabanı bağlantısı ve S3 servislerimizi mock'layarak test koşturduğumuz için bu dosyaların kapsama oranları göreceli olarak daha düşük çıkabiliyor. Ancak biz bu açığı kapatmak için Testcontainers ile entegrasyon testleri yazdık. Entegrasyon testleri mock kullanmadığı için bu kritik entegrasyon dosyalarının tamamını canlı olarak kapsamakta ve sistemin gerçek servislerle olan kararlılığını garanti altına almaktadır."*

### Soru 3: "Deploy çökerse veya yeni versiyon hatalı çıkarsa rollback nasıl yapılır?"
* **Cevap**: 
  > *"Eğer dağıtımı Kubernetes manifestleriyle yaptıysak, `kubectl rollout undo deployment/qrcode-app` komutu ile hızlıca geri dönebiliriz. Helm chart kullandığımız için `helm rollback qrcode-generator [REVISION_NO]` komutunu kullanmak daha sağlıklıdır. Ayrıca GitOps (ArgoCD) kullandığımız için, git üzerindeki hatalı commit'i revert edip pushladığımızda ArgoCD otomatik olarak aradaki farkı algılayıp cluster'ı git üzerindeki son stabil commit durumuna senkronize edecektir."*
