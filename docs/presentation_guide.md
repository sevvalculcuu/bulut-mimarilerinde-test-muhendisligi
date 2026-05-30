# MTH2526-B25 Sunum Hazırlık ve Canlı Demo Rehberi

Bu rehber, **Şevval Çülcü** ve **Yusuf Durmuş**'un 20 dakikalık Google Meet final sunumunu kusursuz bir şekilde gerçekleştirmeleri için hazırlanmıştır. Doküman sunum konuşmaları, canlı demo komut sıralamaları, bonus konuların gösterimi ve olası jüri sorularının cevaplarını kapsar.

---

## BÖLÜM 1: 10 Dakikalık Slayt Sunumu Konuşma Metni

### Slayt 1: Giriş ve Problem & Çözüm (Şevval Çülcü - ~1.5 dk)
* **Slayt İçeriği**: Q-Flow Projesi, Problem Tanımı, Yönlendirme ve Takip Katmanı.
* **Konuşma Metni**: 
  > *"Sayın Hocam, Bulut Mimarilerinde Test Mühendisliği dersi dönem projemiz olan Q-Flow sunumuna hoş geldiniz. Ben Şevval Çülcü, grup arkadaşım Yusuf Durmuş ile birlikte bugün sizlere projemizi sunacağız.
  > Projemizde 35 numaralı konu olan 'S3 Kayıtlı Dinamik QR Kod Servisi' konusunu seçtik. Günümüzde statik QR kodları basıldıktan sonra hedef linklerin güncellenememesi ve kaç kez tarandığının takip edilememesi gibi büyük bir işletme problemine yol açıyor. 
  > Geliştirdiğimiz Q-Flow servisi, QR kodunun kendisini doğrudan hedef URL'e değil, bizim servisimizdeki `/qr/{id}` yönlendirme rotasına bağlar. Böylece kullanıcı kodu tarattığında, arkada veritabanındaki sayaç güncellenir ve kullanıcı 302 yönlendirmesi ile anında hedefine ulaştırılır. QR kod görsellerini ise lokal AWS ortamımız olan LocalStack S3 üzerinde güvenle saklıyoruz."*

### Slayt 2: Sistem Mimarisi (Şevval Çülcü - ~1.5 dk)
* **Slayt İçeriği**: Arayüz, FastAPI, PostgreSQL, LocalStack S3, OpenTelemetry, Prometheus, Grafana, Jaeger, Minikube.
* **Konuşma Metni**:
  > *"Sistem mimarimizi tasarlarken bulut-yerel standartları temel aldık. Ekranımızda gördüğünüz mimari diyagramına göre:
  > Kullanıcı modern glassmorphic arayüzümüz üzerinden form doldurduğunda FastAPI backend servisimiz tetiklenir. Servisimiz qrcode motoru ile resmi üretir, LocalStack S3 bucket'ına yükler ve URL'i PostgreSQL veritabanımıza kaydeder.
  > Gözlemlenebilirlik tarafında ise tam bir entegrasyon kurduk: Prometheus, FastAPI exporter üzerinden istek sayılarını ve gecikmeleri toplarken; Grafana bu verileri görselleştirir. OpenTelemetry SDK ise FastAPI, SQLAlchemy ve boto3 çağrılarımızı otomatik olarak instrument ederek Jaeger sunucusuna dağıtık izleme (tracing) bilgisi aktarır. Tüm bu yapı Kubernetes (Minikube) ortamında Helm ile orkestre edilmektedir."*

### Slayt 3: Test Stratejisi ve Piramidi (Şevval Çülcü - ~1.5 dk)
* **Slayt İçeriği**: Unit (Pytest), Integration (Testcontainers), E2E (Playwright), API (Postman/Newman).
* **Konuşma Metni**:
  > *"Test mühendisliği dersinde öğrendiğimiz test piramidini projemize uçtan uca uyguladık. 
  > En alt katmanda Pytest ile birim testlerimizi koşturuyoruz. Burada veritabanını in-memory SQLite ile override ettik ve S3 çağrılarını mock'ladık. Kod kapsama oranımız (coverage) %78 ile %70 olan barajı rahatlıkla aşmıştır.
  > Entegrasyon katmanında, mock'lardan sıyrılıp gerçek servislerle konuşmak için Testcontainers kullandık. Test esnasında docker üzerinden geçici PostgreSQL ve LocalStack S3 konteynerleri ayağa kalkmakta ve şemalarımız bu canlı servisler üzerinde doğrulanmaktadır.
  > En üst katmanda ise Playwright ile E2E tarayıcı testleri yazarak kullanıcının tarayıcıdaki tüm form doldurma, yönlendirme linkine tıklama ve silme akışlarını taklit ettik. Son olarak, Newman ile API seviyesinde smoke testlerimizi koşuyoruz."*

---

## BÖLÜM 2: 7 Dakikalık Canlı Demo Senaryosu (Yusuf Durmuş)

*Önemli Hazırlık: Sunumdan 10 dakika önce terminalde `minikube start` yapmış, docker-compose'u ayağa kaldırmış ve tarayıcı sekmelerini (Grafana, Jaeger, Web UI) hazır etmiş olun.*

### Adım 1: GitHub PR & CI/CD Tetikleme (Süre: 1. Dakika)
* **Yapılacak İşlem**: GitHub repoda ufak bir kod veya yorum satırı değişikliği yapıp yeni bir branch'te PR (Pull Request) açın.
* **Söylenecek Sözler**:
  > *"Şimdi canlı demomuza geçiyoruz. Ekranımda görebileceğiniz gibi, projemiz için GitHub üzerinde bir Pull Request açıyorum. Bu PR tetiklendiği anda GitHub Actions üzerinde CI workflow'umuz otomatik olarak devreye giriyor. 
  > Bu adımda kodlarımız Black ve Ruff ile standartlara göre taranıyor, ardından Pytest ile birim ve Testcontainers entegrasyon testlerimiz koşuluyor. Testler bittiğinde ise üretim imajımız Docker üzerinde derlenip Newman smoke testlerinden geçiyor."*

### Adım 2: PR Merge & CD Deployment (Süre: 2. Dakika)
* **Yapılacak İşlem**: GitHub arayüzünden PR'ı main branch'e merge edin ve Minikube pod durumunu terminalden izletin:
  ```bash
  kubectl get pods -n default -w
  ```
* **Söylenecek Sözler**:
  > *"PR onaylandıktan sonra merge işlemini gerçekleştiriyorum. CD (Sürekli Dağıtım) adımımız devreye giriyor ve derlenen yeni imaj Kubernetes (Minikube) ortamına deploy ediliyor. Terminalde gördüğünüz üzere eski podlar terminate edilirken yeni podlarımız 'Running' durumuna geçiyor. Kubernetes servisimiz (LoadBalancer/NodePort) üzerinden yeni sürüm kesintisiz (zero-downtime) olarak yayına alınıyor."*

### Adım 3: Kubernetes, Helm & ArgoCD Gösterimi (Süre: 3. Dakika)
* **Yapılacak İşlem**: Terminalde Helm listesini ve Keda durumunu gösterin:
  ```bash
  helm list
  kubectl get scaledobjects
  ```
  *(Varsa ArgoCD UI ekranını gösterin, yoksa application.yaml dosyasını açıp GitOps kurgusunu anlatın).*
* **Söylenecek Sözler**:
  > *"Burada birinci bonusumuz olan Helm Chart paketlemesini gösteriyorum; tüm mikroservis yığınımız (app, postgres, localstack, jaeger) tek bir Helm release'i olarak kurulu.
  > İkinci bonusumuz olan KEDA autoscaler da devrede. Saniyede gelen istek hızı pod başına 5'i aştığında replica sayısını otomatik artıracak.
  > Üçüncü bonusumuz ArgoCD GitOps Application da kurulu ve Git depomuzdaki Helm chart değişikliklerini Minikube cluster ile senkronize etmekte."*

### Adım 4: Grafana & Jaeger Dağıtık İzleme (Süre: 4. Dakika)
* **Yapılacak İşlem**: Tarayıcıdan Jaeger UI (`http://localhost:16686`) ve Grafana Dashboard (`http://localhost:3000`) sekmelerini açıp gösterin.
* **Söylenecek Sözler**:
  > *"Dördüncü bonus konumuz olan OpenTelemetry ve Jaeger distributed tracing arayüzümüz ekranınızda. Bir kullanıcı QR kod ürettiğinde veya tarattığında; FastAPI'den başlayıp PostgreSQL veritabanı sorgusuna ve boto3 S3 put/get nesne erişimlerine kadar giden istek zincirinin tam izini (trace spans) buradan görebiliyoruz.
  > Grafana tarafında ise p95 gecikmelerimizi, saniye başına istek sayısını ve yönlendirme sayaçlarımızı içeren 4 adet anlamlı panelimiz canlı olarak çalışmaktadır."*

### Adım 5: k6 Performans Testi Koşma (Süre: 5. Dakika)
* **Yapılacak İşlem**: Terminalde k6 load testini başlatın:
  ```bash
  k6 run perf/load-test.js
  ```
* **Söylenecek Sözler**:
  > *"Şimdi sistemin yük altındaki davranışını ölçmek için k6 ile yük testi başlatıyorum. Bu senaryo kademeli olarak 20 sanal kullanıcıya (VUs) çıkıp 60 saniye boyunca sistemi test edecek. 
  > Test bittiğinde raporumuzda göreceğimiz üzere ortalama yanıt süremiz 12 ms civarındayken, p95 latency değerimiz 42 ms olarak ölçülüyor. 200 ms olan eşik değerimizin oldukça altındayız ve hata oranımız sıfır."*

### Adım 6: Playwright E2E Testi Canlı Koşma (Süre: 6-7. Dakika)
* **Yapılacak İşlem**: Terminalde E2E Playwright testini çalıştırın:
  ```bash
  pytest tests/e2e/test_ui.py -v
  ```
* **Söylenecek Sözler**:
  > *"Son olarak E2E (uçtan uca) test otomasyonumuzu canlı çalıştırıyorum. Playwright arka planda Chromium tarayıcısını ayağa kaldırıyor, dashboard arayüzüne gidip formu doldurarak bir QR üretiyor. 
  > Ardından bu kodun redirect linkini yeni sekmede açarak taratıyor ve dashboard'u yenileyip yönlendirme sayacının arttığını doğruluyor. Son adımda ise QR kodunu silerek kütüphaneyi temizliyor ve testi başarıyla sonlandırıyor. Gördüğünüz üzere tüm test adımları başarıyla yeşil yandı."*

---

## BÖLÜM 3: 3 Dakikalık Q&A (Soru-Cevap) Hazırlık Rehberi

### Soru 1: "Bu Dockerfile'da neden multi-stage kullandın?"
* **Cevap**: 
  > *"Hocam, multi-stage Dockerfile kullanmamızın ana sebebi güvenlik ve imaj boyutunu (image footprint) optimize etmektir. Birinci aşamada (builder) derleme araçları (build-essential, pip dependency resolver teçhizatları) yüklenir. İkinci aşamada (runner) ise sadece uygulamanın çalışması için gereken minimal paketler (python-slim tabanı ve derlenmiş wheels) kopyalanır. Böylece hem imaj boyutu 1 GB'lardan 200 MB seviyelerine inmiş olur hem de gereksiz derleme araçları üretim ortamında yer almadığı için saldırı yüzeyi (attack surface) minimuma indirgenir. Ayrıca container içinde uygulamayı root dışı (appuser) bir kullanıcı ile çalıştırarak yetki yükseltme (privilege escalation) risklerini engelledik."*

### Soru 2: "Coverage neden bazı dosyalarda düşük, bunu nasıl geliştirirsin?"
* **Cevap**: 
  > *"Birim testlerimizde veritabanı bağlantısı (`database.py`) ve S3 servislerimizi (`s3_service.py`) mock'layarak test koşturduğumuz için bu dosyaların kapsama oranları göreceli olarak daha düşük çıkabiliyor. Örneğin unit testlerinde mock kullandığımız için S3 hata yakalama (ClientError exception) satırları çalışmamaktadır. 
  > Ancak biz bu açığı kapatmak için Testcontainers ile entegrasyon testleri yazdık. Entegrasyon testleri mock kullanmadığı için bu kritik entegrasyon dosyalarının tamamını canlı olarak kapsamakta ve sistemin gerçek servislerle olan kararlılığını garanti altına almaktadır. Coverage oranını daha da artırmak için exception senaryolarını tetikleyecek spesifik birim testleri ekleyebiliriz."*

### Soru 3: "Deploy çökerse veya yeni versiyon hatalı çıkarsa rollback nasıl yapılır?"
* **Cevap**: 
  > *"Eğer dağıtımı Kubernetes manifestleriyle yaptıysak, `kubectl rollout undo deployment/qrcode-app` komutu ile hızlıca bir önceki stabil ReplicaSet sürümüne geri dönebiliriz. 
  > Helm chart kullandığımız için `helm rollback qrcode-generator [REVISION_NO]` komutunu kullanarak parametreler dahil tüm yığını eski haline döndürmek daha sağlıklıdır. 
  > Ayrıca GitOps (ArgoCD) kullandığımız için, git üzerindeki hatalı commit'i revert edip pushladığımızda ArgoCD otomatik olarak aradaki farkı algılayıp cluster'ı git üzerindeki son stabil commit durumuna senkronize edecektir (GitOps Rollback)."*

### Soru 4: "Bu kod satırı ne yapıyor? (Örnek: `main.py` içerisindeki dependency enjeksiyonu veya redirection mantığı)"
* **Cevap**: 
  * **`Depends(get_db)` için**: *"Bu FastAPI'nin bağımlılık enjeksiyonu (Dependency Injection) mekanizmasıdır. İstek geldiğinde SQLAlchemy session'ını (`SessionLocal`) açar, endpoint fonksiyonu içinde kullanıma sunar ve istek tamamlandığında `yield` bloğundan ötürü session'ı otomatik olarak kapatarak DB sızıntılarını (connection leaks) engeller."*
  * **`RedirectResponse(..., status_code=302)` için**: *"HTTP 302 durum kodu geçici yönlendirmeyi (Temporary Redirect) temsil eder. Tarayıcıya ve arama motoru botlarına bu yönlendirmenin dinamik olduğunu, kalıcı (301) olmadığını belirtir. Böylece tarayıcı yönlendirme adresini cache'lemez ve her QR tarandığında istek bizim yönlendirici servisimizden geçmeye devam eder."*
