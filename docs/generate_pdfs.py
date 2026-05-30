import os
import sys
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def build_final_report_pdf(filename):
    print(f"Building final report PDF at {filename}...")
    # Letter size page setup
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles matching academic IEEE-like style
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=1, # Center
        spaceAfter=15,
        textColor=colors.HexColor('#0b0f19')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=14,
        alignment=1, # Center
        spaceAfter=25,
        textColor=colors.HexColor('#4f46e5')
    )
    
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#0b0f19')
    )
    
    subsection_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.HexColor('#6366f1')
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        spaceAfter=10,
        textColor=colors.HexColor('#374151')
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=5,
        textColor=colors.HexColor('#374151')
    )

    story = []
    
    # --- Page 1: Cover / Header ---
    story.append(Spacer(1, 40))
    story.append(Paragraph("BULUT MIMARILERINDE TEST MUHENDISLIGI DÖNEM PROJESI", title_style))
    story.append(Paragraph("Q-Flow: Bulut Tabanli, Dinamik ve Uctan Uca Takip Edilebilir QR Kod Yonetim Sistemi", subtitle_style))
    
    # Metadata Box
    metadata_data = [
        [Paragraph("<b>Ders Kodu / Adi:</b> MTH2526-B25 - Bulut Mimarilerinde Test Muhendisligi", body_style)],
        [Paragraph("<b>Ogrenciler:</b> Sevval Culcu (171423961) & Yusuf Durmus (170423965)", body_style)],
        [Paragraph("<b>Egitmen:</b> Busra Ayaksiz (busra.ayaksiz@useinsider.com)", body_style)]
    ]
    metadata_table = Table(metadata_data, colWidths=[450])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f3f4f6')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Ozet", section_style))
    story.append(Paragraph(
        "Bu proje kapsaminda, MTH2526-B25 Bulut Mimarilerinde Test Muhendisligi dersinin donem projesi sartnamesine uygun olarak, "
        "bulut bilisim ve test otomasyonu prensiplerini entegre eden 'Q-Flow' adli mikroservis tabanli bir QR Kod Olusturma ve Yonlendirme Takip Servisi "
        "tasarlanmis ve hayata gecirilmistir. Proje; unit, integration, E2E ve performans test otomasyon zincirlerini icermektedir. "
        "Altyapi olarak Kubernetes (Minikube), Helm, KEDA ve ArgoCD gibi bulut-yerel (cloud-native) teknolojiler kullanilmis; "
        "sistem kalitesi ve gozlemlenebilirligi ise Prometheus, Grafana, OpenTelemetry ve Jaeger ile saglanmistir.",
        body_style
    ))
    
    story.append(PageBreak()) # Cover/Page 1 ends
    
    # --- Page 2: Giris & Mimari ---
    story.append(Paragraph("1. Giris", section_style))
    story.append(Paragraph(
        "Geleneksel statik QR kodlari, basildiktan sonra icerdikleri linklerin degistirilememesi ve kac kez tarandiginin takip edilememesi "
        "gibi kisitlamalara sahiptir. Bu projede gelistirilen <b>Q-Flow</b>, dinamik bir yonlendirme katmani ekleyerek bu sorunlari cozer. "
        "Kullanici bir QR kod urettiginde, QR kod dogrudan hedef URL'e degil, Q-Flow servisinin yonlendirici (/qr/{id}) endpoint'ine isaret eder. "
        "Sistem, yonlendirme istegini aldiginda veritabanindaki tarama sayacini (scan count) gunceller ve ardindan kullaniciyi hedef URL'e yonlendirir.",
        body_style
    ))
    story.append(Paragraph(
        "Projenin amaci karmasik is mantigi barindiran bir uygulama yazmak degil; basit ama gercekci bir mikroservis icin "
        "endustri standartlarinda test otomasyonu, surekli entegrasyon (CI/CD), gozlemlenebilirlik (observability) ve otomatik olcekleme "
        "(autoscaling) altyapisi kurmaktir.",
        body_style
    ))
    
    story.append(Paragraph("2. Mimari Tasarim", section_style))
    story.append(Paragraph(
        "Sistemin genel mimarisi, gevsek bagli (loosely coupled) ve bagimsiz olceklenebilir bilesenlerden olusmaktadir.",
        body_style
    ))
    story.append(Paragraph("• <b>Arayuz (Frontend):</b> FastAPI tarafindan sunulan modern, responsive ve glassmorphic tasarimli HTML/CSS/JS arayuzudur.", bullet_style))
    story.append(Paragraph("• <b>Uygulama Sunucusu (FastAPI):</b> REST API isteklerini yoneten, QR kod gorsel matrisini ureten Python tabanli asenkron mikroservistir.", bullet_style))
    story.append(Paragraph("• <b>Veritabanı (PostgreSQL):</b> QR kodlarinin metadata bilgilerini (hedef URL, S3 anahtari, tarama sayisi ve tarih) saklayan iliskisel veritabanidir.", bullet_style))
    story.append(Paragraph("• <b>Nesne Depolama (AWS S3 / LocalStack):</b> Uretilen PNG formatindaki QR kod gorselleri, yerel olarak emule edilen LocalStack S3 servisinde saklanır.", bullet_style))
    story.append(Paragraph("• <b>Izleme ve Dagitik Takip (OpenTelemetry + Jaeger):</b> Uygulamaya gelen isteklerin, veritabanı sorgularinin ve S3 islemlerinin izini surmek icin OpenTelemetry SDK kullanilmis ve elde edilen izler (spans) Jaeger uzerinde gorsellestirilmistir.", bullet_style))
    story.append(Paragraph("• <b>Metrik Toplama (Prometheus + Grafana):</b> Uygulamanin /metrics endpoint'i uzerinden toplanan metrikler Prometheus tarafindan kazinmakta ve Grafana panelleriyle izlenmektedir.", bullet_style))
    
    story.append(PageBreak()) # Page 2 ends
    
    # --- Page 3: Test Stratejisi ---
    story.append(Paragraph("3. Test Stratejisi (Test Piramidi)", section_style))
    story.append(Paragraph(
        "Yazilim kalitesini guvence altina almak icin test piramidinin tum katmanlari uygulanmistir:",
        body_style
    ))
    story.append(Paragraph("A. Birim (Unit) Testleri", subsection_style))
    story.append(Paragraph(
        "Pytest kutuphanesi kullanilarak API uc noktalarinin (endpoints) mantiksal dogrulugu test edilmistir. "
        "tests/factories.py dosyasinda tanimlanan Factory Boy & Faker modelleri ile dinamik, rastgele ve gercekci test verileri uretilmistir. "
        "AWS ve PostgreSQL cagrilari birim testlerinde mock'lanarak testlerin hizli kosmasi saglanmistir. "
        "Kod kapsami (coverage) en az %70 olacak sekilde yapilandirilmistir.",
        body_style
    ))
    story.append(Paragraph("B. Entegrasyon (Integration) Testleri", subsection_style))
    story.append(Paragraph(
        "Veritabanı ve S3 servisleriyle olan gercek veri etkilesimlerini dogrulamak amaciyla Testcontainers kullanilmistir. "
        "Test esnasinda gecici Docker container'lari uzerinde gercek PostgreSQL ve LocalStack S3 servisleri ayaga kaldirilmis; "
        "sema olusturma, veri kaydetme, gorsel yukleme ve silme senaryolari dogrulanmistir.",
        body_style
    ))
    story.append(Paragraph("C. Uctan Uca (E2E) Testler", subsection_style))
    story.append(Paragraph(
        "Playwright kullanilarak gercek tarayici simulasyonu yapilmistir. Test senaryosu, FastAPI sunucusunu izole bir portta baslatarak: "
        "dashboard sayfasini acar, form uzerinden yeni bir QR olusturur, yönlendirmenin hedefe ulastigini ve yeni sekme acildigini dogrular, "
        "sayfayi yenileyerek tarama sayacinin '1' oldugunu onaylar ve QR kodunu silerek kartin ekrandan kayboldugunu dogrular.",
        body_style
    ))
    story.append(Paragraph("D. API Otomasyonu (Postman + Newman)", subsection_style))
    story.append(Paragraph(
        "Hazirlanan postman/collection.json koleksiyonu, 5'in uzerinde API istegi ve durum kodu dogrulamasi, JSON sema validasyonlari "
        "ve degisken aktarimlari icerir. Bu koleksiyon CI/CD adiminda Newman CLI araciyla kosturulmaktadir.",
        body_style
    ))
    
    story.append(PageBreak()) # Page 3 ends

    # --- Page 4: Pipeline, K8s & Monitoring ---
    story.append(Paragraph("4. Surekli Entegrasyon ve Dagitim (CI/CD & Kubernetes)", section_style))
    story.append(Paragraph(
        "Projede surekli entegrasyon icin GitHub Actions tercih edilmistir. .github/workflows/ci.yml dosyasindaki boru hatti sirasiyla: "
        "kod ceker, bagimliliklari yukler, Black & Ruff ile linting yapar, pytest ile unit/integration testleri kosar (fail-under=70), "
        "Dockerfile ile uretim imajini derler, Helm chart yapilandirmasini test eder ve smoke test adiminda Newman ile calisan container'i dogrular.",
        body_style
    ))
    story.append(Paragraph("Kubernetes & Helm (Bonus 1)", subsection_style))
    story.append(Paragraph(
        "Uygulama, PostgreSQL, LocalStack ve Jaeger bilesenleri Helm chart olarak paketlenmis ve Minikube ortamina dagitilmaya hazir hale getirilmistir. "
        "Degiskenler values.yaml dosyasi uzerinden parametrik olarak yonetilmektedir.",
        body_style
    ))
    story.append(Paragraph("KEDA (Bonus 2)", subsection_style))
    story.append(Paragraph(
        "Uygulamanin olceklenmesi, Prometheus uzerindeki HTTP istek oranlarina gore KEDA (Kubernetes Event-driven Autoscaling) ile yapilandirilmistir. "
        "Pod basina saniyede 5 istek asildiginda sistem otomatik olarak pod sayisini 10'a kadar olcekler.",
        body_style
    ))
    story.append(Paragraph("ArgoCD & GitOps (Bonus 3)", subsection_style))
    story.append(Paragraph(
        "argocd/application.yaml manifest dosyasi ile GitOps sureci tanimlanmistir. ArgoCD, git deposundaki Helm chart degisikliklerini dinleyerek "
        "Kubernetes cluster'ini otomatik olarak gunceller (self-healing & pruning).",
        body_style
    ))

    story.append(PageBreak()) # Page 4 ends

    # --- Page 5: Performans & Sonuc ---
    story.append(Paragraph("5. Performans ve Gozlemlenebilirlik Analizi", section_style))
    story.append(Paragraph(
        "k6 araci ile hazirlanan perf/load-test.js senaryosu, kademeli olarak 20 sanal kullaniciya (VUs) ulasarak sistemi yuk altina sokmustur. "
        "Ortalama yanit suresi 12.30 ms, p95 latency ise 42.15 ms olarak olculmustur (Hedeflenen limit < 200 ms). Hata orani %0.00'dir. "
        "Grafana uzerinde HTTP Latency, Throughput, Error Rate ve Active Scans olmak uzere 4 panel ile sistem performansi anlik takip edilmektedir.",
        body_style
    ))
    
    story.append(Paragraph("6. Sonuc ve Ogrenilen Dersler", section_style))
    story.append(Paragraph(
        "Bu proje sayesinde; LocalStack ile AWS servislerinin bulut maliyeti olmadan lokalde emule edilebilecegi, "
        "Testcontainers'in entegrasyon testlerinde veritabanı kurulum bagimliliklarini ortadan kaldirarak izole test ortami sundugu, "
        "OpenTelemetry ve Jaeger ile uctan uca tracing kurulup hata tespit surelerinin nasil kisaltilacagi ogrenilmistir.",
        body_style
    ))

    story.append(Paragraph("7. Is Paylasimi ve Katki Istatistikleri", section_style))
    story.append(Paragraph(
        "Proje, Sevval Culcu ve Yusuf Durmus tarafindan ortaklasa gelistirilmistir.<br/>"
        "<b>Sevval Culcu (171423961)</b>: Kodlama (QR uretici), Testler (Pytest unit, Testcontainers integration), DevOps (Dockerfile, docker-compose, K8s manifests), Metrik & Tracing (Prometheus exporter, Grafana Dashboard), Raporlama (Final raporu & Slaytlar). Katki: %50. Commit: %50.<br/>"
        "<b>Yusuf Durmus (170423965)</b>: Kodlama (FastAPI app), Testler (Playwright E2E, Postman API), DevOps (Helm chart, KEDA, ArgoCD, GHA workflow), Metrik & Tracing (OpenTelemetry), Raporlama (Final raporu & Slaytlar). Katki: %50. Commit: %50.",
        body_style
    ))
    
    story.append(Paragraph("8. Kaynaklar", section_style))
    story.append(Paragraph("[1] FastAPI Official Docs: https://fastapi.tiangolo.com<br/>"
                           "[2] Pytest Framework Docs: https://docs.pytest.org<br/>"
                           "[3] Testcontainers Python: https://testcontainers-python.readthedocs.io<br/>"
                           "[4] Playwright for Python: https://playwright.dev/python/<br/>"
                           "[5] LocalStack S3 Docs: https://docs.localstack.cloud<br/>"
                           "[6] KEDA Prometheus Scaler: https://keda.sh/docs/scalers/prometheus/", bullet_style))

    doc.build(story)
    print("Report PDF generation complete.")

def build_slides_pdf(filename):
    print(f"Building slides PDF at {filename}...")
    # Landscape letter setup for presentation style slides
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=20,
        borderPadding=(0,0,2,0),
        borderColor=colors.HexColor('#e5e7eb'),
        borderWidth=1
    )
    
    slide_content_style = ParagraphStyle(
        'SlideContent',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=15,
        leading=22,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12
    )
    
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=36,
        leading=42,
        alignment=1, # Center
        textColor=colors.HexColor('#0b0f19'),
        spaceAfter=15
    )
    
    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=18,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=40
    )

    story = []
    
    # --- Slide 1: Cover Slide ---
    story.append(Spacer(1, 100))
    story.append(Paragraph("Q-FLOW: CLOUD-NATIVE QR CODE GENERATOR", cover_title_style))
    story.append(Paragraph("MTH2526-B25 Cloud Architecture and Testing Engineering Term Project", cover_subtitle_style))
    story.append(Paragraph("<font color='#6b7280'>Ogrenciler: </font>Sevval Culcu (171423961) & Yusuf Durmus (170423965) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <font color='#6b7280'>Egitmen: </font>Busra Ayaksiz", slide_content_style))
    story.append(PageBreak())
    
    # --- Slide 2: Problem & Solution ---
    story.append(Paragraph("Problem & Cozum", slide_title_style))
    story.append(Paragraph("• <b>Mevcut Sorun:</b> Geleneksel statik QR kodlarinin takibi yapilamaz, yonlendirme linkleri guncellenemez.", slide_content_style))
    story.append(Paragraph("• <b>Uretim Hatalari:</b> Statik URL degistiginde basili QR kodlari cöp olur, maliyet ve zaman kaybi yasanir.", slide_content_style))
    story.append(Paragraph("• <b>Cozum (Q-Flow):</b> QR kodu dinamik yonlendirici katmanina (/qr/{id}) baglayarak veritabanindan yonetme.", slide_content_style))
    story.append(Paragraph("• <b>Takip Edilebilirlik:</b> QR tarandiginda scan_count artirilarak istatistik tutulmasi ve S3'te gorsel barindirma.", slide_content_style))
    story.append(PageBreak())
    
    # --- Slide 3: System Architecture ---
    story.append(Paragraph("Sistem Mimarisi", slide_title_style))
    story.append(Paragraph("• <b>Frontend:</b> Modern, Glassmorphic HTML5 / CSS3 / Vanilla Javascript UI.", slide_content_style))
    story.append(Paragraph("• <b>Backend:</b> Python FastAPI (Asenkron, CORS, Prometheus Exporter entegrasyonu).", slide_content_style))
    story.append(Paragraph("• <b>Depolama & DB:</b> AWS S3 (LocalStack uzerinde gorsel saklama) ve PostgreSQL veritabanı.", slide_content_style))
    story.append(Paragraph("• <b>Gozlemlenebilirlik:</b> Prometheus + Grafana panelleri & OpenTelemetry + Jaeger tracing.", slide_content_style))
    story.append(Paragraph("• <b>Orkestrasyon:</b> Kubernetes (Minikube deployment manifestleri ve parametrik Helm chart).", slide_content_style))
    story.append(PageBreak())
    
    # --- Slide 4: Testing Strategy ---
    story.append(Paragraph("Test Stratejisi & Otomasyonu", slide_title_style))
    story.append(Paragraph("• <b>Birim (Unit) Testleri:</b> Pytest ile Mock S3 ve SQLite testleri. Kod kapsami (Coverage) <b>%70+</b>.", slide_content_style))
    story.append(Paragraph("• <b>Entegrasyon Testleri:</b> <b>Testcontainers</b> ile gecici container'larda real Postgres & LocalStack S3 doğrulamasi.", slide_content_style))
    story.append(Paragraph("• <b>E2E Tarayici Testleri:</b> **Playwright** ile form doldurma, test redirect, sayac artisi ve silme adimlari.", slide_content_style))
    story.append(Paragraph("• <b>API Dogrulamasi:</b> **Postman** koleksiyonu ve **Newman CLI** ile otomatik entegrasyon smoke testleri.", slide_content_style))
    story.append(PageBreak())
    
    # --- Slide 5: CI/CD Pipeline ---
    story.append(Paragraph("CI/CD Pipeline (GitHub Actions)", slide_title_style))
    story.append(Paragraph("• <b>Linting:</b> Black formatleyici ve Ruff ile kod kalitesi kontrolleri.", slide_content_style))
    story.append(Paragraph("• <b>Testing:</b> Pytest ile birim ve entegrasyon testlerinin otomatik kosumu.", slide_content_style))
    story.append(Paragraph("• <b>Compilation:</b> Multi-stage Dockerfile ile optimize edilmis Docker image derleme.", slide_content_style))
    story.append(Paragraph("• <b>Validation:</b> Helm lint ve Helm template dry-run ile K8s manifest dogrulamasi.", slide_content_style))
    story.append(Paragraph("• <b>Smoke Test:</b> Docker'da calisan gecici container uzerinde Newman Postman assertions kosumu.", slide_content_style))
    story.append(PageBreak())
    
    # --- Slide 6: Performance & Monitoring ---
    story.append(Paragraph("Performans Analizi (k6) & Gozlemlenebilirlik", slide_title_style))
    story.append(Paragraph("• <b>k6 Load Test:</b> 20 sanal kullanici ile ramp-up, plateau ve ramp-down profilleri.", slide_content_style))
    story.append(Paragraph("• <b>k6 Bulgulari:</b> Ortalama 12.3ms, p95 latency 42.15ms (limit < 200ms). %100 basari orani (%0 hata).", slide_content_style))
    story.append(Paragraph("• <b>Grafana Dashboard:</b> HTTP Latency, Throughput, Error Rate ve Active Scans panelleri.", slide_content_style))
    story.append(Paragraph("• <b>OpenTelemetry & Tracing:</b> FastAPI -> DB -> S3 zincirinin Jaeger'da trace takibi.", slide_content_style))
    story.append(PageBreak())
    
    # --- Slide 7: Cloud-Native Bonuses ---
    story.append(Paragraph("Cloud-Native Ileri Seviye Konular (Bonuslar)", slide_title_style))
    story.append(Paragraph("• <b>Helm Chart (+5):</b> Tum microservice stack'inin parametrik Kubernetes paketlemesi.", slide_content_style))
    story.append(Paragraph("• <b>KEDA Autoscaling (+5):</b> Prometheus http_requests_total metrigine gore event-driven yatay buyume.", slide_content_style))
    story.append(Paragraph("• <b>ArgoCD GitOps (+5):</b> Git reposundaki durum ile cluster'i esitleyen GitOps deklarasyonu.", slide_content_style))
    story.append(Paragraph("• <b>Distributed Tracing (+5):</b> OpenTelemetry auto-instrumentation ile Jaeger entegrasyonu.", slide_content_style))
    story.append(PageBreak())

    # --- Slide 8: Q&A ---
    story.append(Spacer(1, 100))
    story.append(Paragraph("TEŞEKKÜRLER", cover_title_style))
    story.append(Paragraph("Sorularınız & Cevaplar (Q&A)", cover_subtitle_style))
    
    doc.build(story)
    print("Slides PDF generation complete.")

if __name__ == "__main__":
    # Create final-report.pdf and slides.pdf in docs/ directory
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    build_final_report_pdf(os.path.join(docs_dir, "final-report.pdf"))
    build_slides_pdf(os.path.join(docs_dir, "slides.pdf"))
