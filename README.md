# AgriTwin AI

AgriTwin AI, çiftçinin manuel olarak girdiği arazi, ürün ve toprak verilerini; IoT/bulut sistemlerinden alınan veya prototipte simüle edilen sensör verilerini ve ekip tarafından hazırlanmış test veri setlerini tek platformda birleştirerek sulama ihtiyacını ve toprak risklerini yapay zekâ ile analiz eden web tabanlı tarım karar destek sistemidir.

MVP, toprağın tüm fiziksel, kimyasal ve biyolojik özelliklerini modellemeyi değil; **toprak nemi ve sulama kararına odaklanan çalışan bir dijital ikiz prototipi** geliştirmeyi amaçlar. Gübre **reçetesi** üretilmez; arazi malzeme kaydı yalnızca kullanım/AI bağlamıdır.

**Canlı demo:** Frontend [aidea-three.vercel.app](https://aidea-three.vercel.app) · API [aidea-f8ji.onrender.com](https://aidea-f8ji.onrender.com) · Durum kaynağı: [`Progress.md`](Progress.md).

---

## Proje Amacı

Çiftçiler sulama kararlarını çoğunlukla:

- Gözleme
- Kişisel deneyime
- Sabit sulama saatlerine
- Genel hava tahminlerine
- Tek seferlik ölçümlere

dayanarak vermektedir.

Bu durum:

- Gereğinden fazla su kullanımına
- Yetersiz sulamaya
- Bitki su stresine
- Enerji maliyetinin artmasına
- Toprak sağlığının bozulmasına
- Verim kaybına

neden olabilir.

AgriTwin AI, bu sorunu verileri tek platformda birleştirerek, sulama ihtiyacını tahmin ederek ve farklı karar senaryolarını simüle ederek çözmeyi hedefler.

---

## Temel Değer Önerisi

> AgriTwin AI, çiftçiye yalnızca toprağın bugünkü durumunu göstermez; toprağın gelecekte nasıl değişeceğini tahmin eder, farklı sulama kararlarını uygulamadan önce simüle eder ve veriye dayalı sulama yönetimi sağlar.

---

## MVP Özellikleri (as-built)

### Çalışan (yerel + canlı)

- Auth: kayıt / doğrulama / giriş / demo-login (4 persona)
- Arazi CRUD, bölgeler (zones), ürün bilgisi
- Manuel veri + IoT simülasyonu + test dataset load
- Laboratuvar: dosya zorunlu `lab_report` + manuel; birim + kullanıcı onayı
- Gübre/ilaç **sınıf** kataloğu + farm association (reçete yok)
- Ürün sezon geçmişi + sonraki ürün önerileri (rotasyon; reçete yok)
- Cihaz yönetimi (liste / ekle / detay / kalibrasyon) + `/iot/ingest`
- Kural tabanlı sulama tahmini + isteğe bağlı OpenRouter Türkçe açıklama
- 24 / 48 / 72 saat nem (Recharts) · Open-Meteo hava
- Risk / anomali · senaryo karşılaştırma · onaylı sanal sulama
- Leaflet OSM haritalar (dashboard / twin / landing)
- Hub (rapor/KPI/tasarruf), abonelik plan seçimi (ödeme yok)
- Admin shell A01–A08

### Kalan / dürüst boşluklar

- ML modeli (Scikit-learn / XGBoost)
- Gerçek OCR / lab PDF hard parse
- Gerçek ödeme sağlayıcısı
- Üretim sertleştirme (Sentry, gerçek SMTP, MQTT, gerçek sensör)
- Sunum demosu / prova

---

## Veri Kaynakları

AgriTwin AI **dört** veri giriş yolunu hedefler. IoT, laboratuvarın yerine geçmez.

Ayrıntılı mimari: [`veri-mimarisi.md`](veri-mimarisi.md)

### 1. Manuel Veri Girişi

Çiftçi veya tarım danışmanı şu verileri sisteme girebilir:

- Toprak nemi, toprak/hava sıcaklığı, hava nemi, yağış ihtimali
- Son sulama zamanı, süresi, su miktarı
- (Opsiyonel) pH, EC — tercihen laboratuvar kaydı ile birimli

### 2. IoT ve Bulut Veri Akışı

Sürekli ölçülebilir: nem, sıcaklık, EC (gösterge), debi, vana durumu vb.

MVP’de akış kontrollü şekilde **simüle** edilir (`source_type: simulation`).

### 3. Test Veri Setleri

Ekip tarafından hazırlanmış senaryolar (`ai/datasets/`): normal, kuruma, aşırı sulama, anomali vb.

### 4. Laboratuvar Analizleri (P1)

Dönemsel ölçümler (OM, P, K, kireç, pH, EC…): rapor yükleme veya manuel lab girişi; **değer + birim + onay** zorunlu. Gübre reçetesi üretilmez.

---

## Yapay Zekânın Görevleri

AgriTwin AI içinde yapay zekâ şu görevlerde kullanılır:

### Sulama İhtiyacı Tahmini

Model aşağıdaki girdileri değerlendirir:

- Toprak nemi
- Toprak sıcaklığı
- Hava sıcaklığı
- Hava nemi
- Yağış ihtimali
- Toprak türü
- Ürün türü
- Gelişim dönemi
- Son sulama zamanı
- Nem değişim trendi

Model çıktıları:

- Sulama gerekli mi?
- Sulama ne kadar acil?
- Tahmini sulama süresi
- Risk seviyesi
- Güven skoru
- Kararın gerekçesi

### Nem Tahmini

Sistem şu zaman aralıkları için tahmin üretir:

- 24 saat
- 48 saat
- 72 saat

### Risk Sınıflandırması

- Düşük
- Orta
- Yüksek
- Kritik

Risk türleri:

- Kuruma riski
- Aşırı sulama riski
- Bitki su stresi
- Sensör arızası
- Veri yetersizliği

### Anomali Tespiti

Sistem şu durumları tespit eder:

- Ani nem düşüşü
- Gerçekçi olmayan sensör değeri
- Veri akış kesintisi
- Sulama sonrası beklenmeyen sonuç
- Çelişkili sensör verileri

### Açıklanabilir AI

Sistem yalnızca karar vermez, kararın nedenini de açıklar.

Örnek:

> Sulama öneriliyor çünkü mevcut toprak nemi %28, son 24 saatte %7 düşüş var, hava sıcaklığı yüksek ve önümüzdeki 48 saat içinde yağış beklenmiyor.

---

## Otomasyonun Görevleri

Otomasyon katmanı yapay zekâdan ayrıdır.

Otomasyon şu işlemleri gerçekleştirir:

- IoT sistemlerinden veri çekme
- Verileri belirli aralıklarla güncelleme
- Kritik durumda bildirim üretme
- Kullanıcı onayı sonrası sulamayı başlatma
- Sanal vanayı açma
- Sulama süresini takip etme
- Sulamayı durdurma
- Kullanılan su miktarını kaydetme
- Sulama sonrası veriyi güncelleme
- AI analizini yeniden çalıştırma

---

## Kullanıcı Akışı

1. Kullanıcı kayıt olur.
2. Arazi oluşturur.
3. Ürün bilgilerini girer.
4. Veri kaynağını seçer.
5. Manuel veri girer veya IoT simülasyonunu başlatır.
6. Sistem veriyi doğrular.
7. AI sulama ihtiyacını analiz eder.
8. Dashboard risk ve öneriyi gösterir.
9. Kullanıcı farklı sulama senaryolarını karşılaştırır.
10. Kullanıcı öneriyi onaylar.
11. Sanal vana açılır.
12. Sulama işlemi kaydedilir.
13. Nem değeri güncellenir.
14. Sistem yeniden analiz yapar.

---

## Demo Senaryosu

### Başlangıç Verileri

- Ürün: Domates
- Arazi türü: Sera
- Toprak nemi: %34
- Toprak sıcaklığı: 25°C
- Hava sıcaklığı: 33°C
- Hava nemi: %42
- Yağış ihtimali: %5
- Son sulama: 36 saat önce

### AI Çıktısı

> Kuruma riski yüksek. Önümüzdeki 18 saat içinde sulama öneriliyor.

### 24 Saat Bekleme Senaryosu

- Tahmini nem: %24
- Risk: Kritik
- Bitki stresi: Yüksek

### Şimdi Sulama Senaryosu

- Tahmini sulama süresi: 14 dakika
- Tahmini su kullanımı: 90 litre
- Sulama sonrası nem: %46
- Risk: Düşük

---

## Teknik Mimari (as-built)

### Frontend

- Next.js App Router + TypeScript + Tailwind CSS
- Recharts + Leaflet/OSM (Google Maps opsiyonel env)
- AppShell / AdminShell; ~39 `page.tsx` rotası (`ekran-haritasi.md` §7)

### Backend

- Python + FastAPI + SQLAlchemy 2.0 + JWT (API ≈ 0.5.x)
- Yerel SQLite; prod Supabase PostgreSQL (`psycopg2-binary`)

### Yapay Zekâ

- Kural motoru (güvenlik tabanı) + anomali kuralları
- İsteğe bağlı OpenRouter açıklama (`OPENROUTER_API_KEY`)
- ML (Scikit-learn / XGBoost): sonraki faz

### Veri / IoT / hava

- `POST /iot/simulate`, `/iot/ingest`, datasets; `source_type` etiketli
- Open-Meteo weather; CLI `iot/simulator/simulate.py`
- MQTT: sonraki faz

### Canlıya alma

- Frontend: Vercel · Backend: Render · DB: Supabase
- Plan / env: [`GO_LIVE_PLAN.md`](GO_LIVE_PLAN.md) · Demo: [`DEMO_USERS.md`](DEMO_USERS.md)

---

## Proje Yapısı

```text
AgriTwin/
├── frontend/                 # Next.js (src/app)
│   └── src/app/              # /, /login, /register, /dashboard, /farms/*
│   └── src/lib/api.ts
├── backend/
│   ├── app/                  # FastAPI (routers, models, ai_engine, anomaly)
│   ├── tests/
│   ├── supabase/001_initial_schema.sql
│   └── requirements.txt
├── ai/
│   ├── datasets/             # 6 sabit test senaryosu JSON
│   └── rule_engine.py
├── iot/simulator/simulate.py
├── .cursor/rules/            # Cursor agent kuralları
├── .env.example
├── AGENTS.md
├── README.md
├── veri-mimarisi.md          # Dört veri kaynağı + lab
├── iot-mimarisi.md           # Saha düğümü / ESP32 / LoRa
├── ekran-haritasi.md         # 38 ekran + MVP-20 UX/UI
├── prd.md, mvp.md, plan.md, Progress.md
├── techstack.md, designsystem.md
├── canvas.md, projeanalizi.md
```

Ürün dokümanları repo kökündedir (`docs/` klasörü yok).

---

## Veri Tabanı Tabloları

### Users

- id
- name
- email
- password_hash
- role
- created_at

### Farms

- id
- user_id
- name
- location
- area
- soil_type
- irrigation_type
- created_at

### Crops

- id
- farm_id
- crop_type
- planting_date
- growth_stage

### SensorReadings

- id
- farm_id
- source_type
- timestamp
- soil_moisture
- soil_temperature
- air_temperature
- air_humidity
- rainfall_probability
- ph
- ec
- salinity

### Predictions

- id
- farm_id
- irrigation_needed
- irrigation_duration
- risk_level
- confidence_score
- explanation
- created_at

### IrrigationEvents

- id
- farm_id
- start_time
- end_time
- duration
- water_amount
- status

### Devices

- id
- farm_id
- device_name
- device_type
- connection_status
- last_data_time

### LabReports / LabParameters (P1)

Şema taslağı: `veri-mimarisi.md` §12 (`LabReports`, `LabParameters`, opsiyonel `ManagementZones`).

---

## API (özet)

Yerel: `http://localhost:8000/docs` · Prod: `https://aidea-f8ji.onrender.com/docs` (API ≈ 0.5.x).

Öne çıkan uçlar: `/auth/*` (demo-login dahil), `/farms/*`, `/agro-materials`, `/billing/*`, `/sensor-readings/*`, `/datasets`, `/weather/{farm_id}`, `/predict/irrigation`, `/simulate/scenario`, `/irrigation/*`, `/devices/*`, `/iot/simulate|ingest`, `/zones`, `/lab-reports/*`, `/admin/*`, `/hub/{farm_id}`.

Tam liste: [`backend/README.md`](backend/README.md) · `prd.md` §14.

---

## Kurulum

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend: `http://localhost:8000`

### Frontend

```bash
cd frontend
# .env.example kökünden NEXT_PUBLIC_API_URL kopyalanabilir → frontend/.env.local
npm install
npm run dev
```

Frontend: `http://localhost:3000`

---

## Ortam Değişkenleri

Kökteki `.env.example` dosyasını temel alın.

```env
# backend/.env
DATABASE_URL=sqlite:///./agritwin.db
SECRET_KEY=change-me-to-a-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000
SEED_DEMO_USERS=1
# OPENROUTER_API_KEY=   # optional hybrid explanations

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Prod: Postgres `DATABASE_URL` + Vercel origin CORS. Gerçek anahtarlar depoya yüklenmemelidir.

---

## Test

### Backend

```bash
cd backend
pytest
```

### IoT simülasyonu (CLI)

```bash
python iot/simulator/simulate.py --token <JWT> --farm-id <id> --scenario drought_risk --once
```

Frontend birim testleri henüz eklenmedi (`npm run build` ile derleme doğrulanır).

---

## Başarı Kriterleri

MVP başarılı sayılır, eğer:

- Kullanıcı kayıt olup giriş yapabiliyorsa
- Arazi oluşturabiliyorsa
- Manuel veri girebiliyorsa
- IoT simülasyon verisi akıyorsa
- AI sulama önerisi üretiyorsa
- 72 saatlik nem tahmini gösteriliyorsa
- En az iki senaryo karşılaştırılabiliyorsa
- Sanal sulama başlatılıp durdurulabiliyorsa
- Sulama geçmişi kaydediliyorsa
- Uygulama canlı bir URL üzerinden erişilebiliyorsa

---

## Yol Haritası

### Faz 1 — MVP

- Manuel veri girişi
- IoT simülasyonu
- Sulama tahmini
- Senaryo simülasyonu
- Sanal otomasyon

### Faz 2 — Pilot

- Gerçek sensör entegrasyonu
- Gerçek hava durumu API’si
- Küçük sera testi
- Kullanıcı geri bildirimi

### Faz 3 — Gelişmiş Toprak Analizi

- pH
- EC
- Tuzluluk
- Toprak sağlık skoru

### Faz 4 — Gelişmiş Dijital İkiz

- Uydu görüntüleri
- Drone verileri
- Verim tahmini
- Gübreleme önerisi

### Faz 5 — Ölçekleme

- Kooperatif paneli
- Çoklu tarla yönetimi
- Kurumsal API
- Bölgesel tarım karar destek sistemi

---

## Sınırlılıklar

- MVP gerçek saha verisiyle doğrulanmamıştır.
- Test verileri gerçek tarımsal koşulları tam temsil etmeyebilir.
- IoT entegrasyonu prototipte simüle edilmektedir.
- Sistem karar destek amacı taşır.
- Kritik sulama kararlarında kullanıcı onayı gereklidir.
- Yapay zekâ çıktıları uzman görüşünün yerine geçmez.

---

## Proje Dokümanları

- `canvas.md` (strateji)
- `mvp.md`
- `prd.md`
- `plan.md`
- `Progress.md` (uygulama durumu — kaynak)
- `veri-mimarisi.md` (dört veri kaynağı + laboratuvar)
- `iot-mimarisi.md` (saha IoT / ESP32 mimarisi)
- `ekran-haritasi.md` (38 ekran + MVP-20 UX/UI; as-built App Router §7)
- `techstack.md`
- `designsystem.md`
- `projeanalizi.md` (erken vizyon; MVP kapsamı değil)
- `AGENTS.md`

---

## Ekip Görevleri

### Ürün Yönetimi

- Kapsam yönetimi
- PRD takibi
- Sprint planlama
- Demo akışı

### Frontend

- Kullanıcı arayüzleri
- Dashboard
- Senaryo ekranı
- IoT cihaz ekranı

### Backend

- API
- Veritabanı
- Kimlik doğrulama
- Veri akışı

### AI ve Veri

- Test veri seti
- Model geliştirme
- Risk analizi
- Açıklanabilir AI

### IoT ve Otomasyon

- IoT simülasyonu
- MQTT veya REST veri akışı
- Sanal vana
- Sulama olayları

### UX ve Sunum

- Arayüz tasarımı
- Kullanıcı testi
- Sunum
- Demo senaryosu

---

## Lisans

Lisans bilgisi proje ekibinin kararına göre eklenecektir.

Örnek:

```text
MIT License
```

---

## Sonuç

AgriTwin AI’ın ilk sürümündeki başarı ölçütü, çok sayıda özellik sunmak değildir.

Başarı ölçütü:

> Kullanıcının veri girebildiği, sistemin veriyi analiz ettiği, yapay zekânın sulama önerisi ürettiği, alternatif kararların simüle edildiği ve sanal otomasyonun çalıştığı uçtan uca deneyimin kesintisiz biçimde gösterilebilmesidir.