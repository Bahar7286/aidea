# AGRITWIN AI — TECH STACK

## 1. Doküman Amacı

Bu doküman, AgriTwin AI MVP’sinin geliştirilmesinde kullanılacak teknoloji yığınını, her teknolojinin projedeki rolünü, seçilme gerekçesini ve alternatiflerini tanımlar.

Temel hedef:

> Hızlı geliştirilebilen, canlıya alınabilen, yapay zekâ, veri, IoT simülasyonu ve kullanıcı arayüzünü tek sistemde birleştiren sade ve sürdürülebilir bir teknik yapı kurmak.

---

## 2. Teknik Yaklaşım

AgriTwin AI MVP’si aşağıdaki katmanlardan oluşacaktır:

1. Frontend
2. Backend API
3. Veritabanı
4. Yapay zekâ ve veri analizi
5. IoT/bulut veri simülasyonu
6. Kimlik doğrulama
7. Görselleştirme
8. Otomasyon
9. Test
10. Canlıya alma
11. İzleme ve hata yönetimi

---

## 3. Önerilen Ana Teknoloji Yığını

| Katman | Teknoloji | Kullanım Amacı |
|---|---|---|
| Frontend | Next.js + TypeScript | Kullanıcı arayüzü ve web uygulaması |
| UI | Tailwind CSS + shadcn/ui | Hızlı ve tutarlı arayüz geliştirme |
| Backend | FastAPI | REST API ve iş mantığı |
| Veritabanı | PostgreSQL + Supabase | Veri saklama ve kullanıcı yönetimi |
| ORM | SQLAlchemy | Veritabanı modelleri ve sorgular |
| AI/ML | Python + Scikit-learn + XGBoost | Tahmin ve risk analizi |
| Veri İşleme | Pandas + NumPy | Veri temizleme ve özellik üretme |
| Açıklanabilir AI | Kural tabanlı metin + güven skoru (SHAP P2) | Model kararlarını açıklama |
| IoT Simülasyonu | MQTT + Python Script | Sensör veri akışını simüle etme |
| Grafikler | Recharts | Nem, risk ve senaryo grafikleri |
| Harita | Leaflet / React Leaflet | Arazi konumu ve bölgesel görünüm |
| Kimlik Doğrulama | Supabase Auth veya JWT | Kayıt ve giriş |
| Frontend Deploy | Vercel | Web uygulamasını canlıya alma |
| Backend Deploy | Render veya Railway | FastAPI servislerini çalıştırma |
| Veritabanı Hosting | Supabase | PostgreSQL ve Auth |
| Test | Pytest + Vitest | Backend, AI ve frontend testleri |
| Kod Yönetimi | GitHub | Sürüm kontrolü ve ekip çalışması |

---

# 4. Frontend

## Önerilen Teknoloji

### Next.js

Next.js, React tabanlı bir web uygulama çatısıdır.

AgriTwin AI içinde:

- Kullanıcı kayıt ekranı
- Giriş ekranı
- Arazi oluşturma
- Manuel veri girişi
- Dashboard
- Dijital ikiz ekranı
- IoT cihaz yönetimi
- Senaryo simülasyonu
- Sulama otomasyonu
- Raporlama

sayfalarında kullanılacaktır.

### Neden Next.js?

- React ekosistemini kullanır.
- TypeScript desteği güçlüdür.
- Vercel üzerinde hızlı canlıya alınabilir.
- Sayfa yönlendirme yapısı hazırdır.
- API entegrasyonu kolaydır.
- Responsive arayüz geliştirmeye uygundur.

### Alternatif

- React + Vite
- Streamlit
- Flutter Web

### Karar

> Profesyonel ve ölçeklenebilir prototip için Next.js kullanılmalıdır.

Ekip frontend geliştirmede zorlanıyorsa:

> Hackathon süresinde Streamlit tercih edilebilir.

---

## 5. Frontend Dili

### TypeScript

TypeScript, JavaScript’e tip güvenliği ekler.

Kullanım alanları:

- Form verileri
- API cevapları
- Kullanıcı modelleri
- Arazi verileri
- Sensör verileri
- Tahmin sonuçları
- Senaryo sonuçları

### Neden TypeScript?

- Veri yapılarındaki hataları azaltır.
- Büyük formlarda daha güvenlidir.
- Backend şemalarıyla uyumu kolaylaştırır.
- Ekip çalışmasını düzenler.

---

## 6. Arayüz Tasarımı

### Tailwind CSS

Tailwind CSS hızlı arayüz geliştirme için kullanılacaktır.

Kullanım alanları:

- Dashboard kartları
- Risk göstergeleri
- Formlar
- Menü
- Mobil görünüm
- Tablo ve grafik düzenleri

### shadcn/ui

Hazır ve özelleştirilebilir bileşenler için kullanılabilir.

Örnek bileşenler:

- Button
- Card
- Dialog
- Form
- Select
- Tabs
- Table
- Alert
- Progress
- Badge

### Alternatifler

- Material UI
- Chakra UI
- Bootstrap

### Karar

> Tailwind CSS + shadcn/ui kombinasyonu önerilir.

---

## 7. Backend

## Önerilen Teknoloji

### FastAPI

FastAPI, Python tabanlı modern bir API geliştirme çatısıdır.

AgriTwin AI içinde:

- Kullanıcı işlemleri
- Arazi yönetimi
- Sensör verisi kaydı
- IoT veri akışı
- AI tahmini
- Senaryo simülasyonu
- Sulama otomasyonu
- Raporlama

işlevlerini yönetecektir.

### Neden FastAPI?

- Python ile AI modellerine doğrudan bağlanır.
- REST API geliştirmesi hızlıdır.
- Otomatik API dokümantasyonu üretir.
- Pydantic ile veri doğrulama sağlar.
- Asenkron işlemleri destekler.
- Hackathon ve MVP geliştirme için uygundur.

### Alternatifler

- Django REST Framework
- Flask
- Node.js + Express
- NestJS

### Karar

> Yapay zekâ katmanıyla aynı dilde çalışmak için FastAPI kullanılmalıdır.

---

## 8. API Yapısı

MVP API öneki yoktur; uçlar kökte yayınlanır (`http://localhost:8000`).

```text
/auth/
/farms/
/sensor-readings/{farm_id}
/iot/simulate
/predict/irrigation
/predictions/{farm_id}
/anomalies/{farm_id}
/simulate/scenario
/irrigation/
/devices/
/health
```

### Temel API uçları

```http
POST /auth/register
POST /auth/login
GET  /auth/me

POST /farms
GET /farms
GET /farms/{id}
PUT /farms/{id}
DELETE /farms/{id}

POST /sensor-readings/{farm_id}
GET /sensor-readings/{farm_id}
POST /iot/simulate

POST /predict/irrigation?farm_id=
GET /predictions/{farm_id}
GET /anomalies/{farm_id}

POST /simulate/scenario

POST /irrigation/start
POST /irrigation/stop
GET /irrigation/history/{farm_id}

POST /devices
GET /devices/{farm_id}
POST /devices/test-connection
```

Not: `/api/v1` öneki gelecekte eklenebilir; şu an kullanılmamaktadır.

---

## 9. Veritabanı

## Önerilen Teknoloji

### PostgreSQL

Proje verileri ilişkisel yapıdadır.

Saklanacak temel veriler:

- Kullanıcılar
- Araziler
- Ürünler
- Sensör okumaları
- Cihazlar
- Tahminler
- Senaryolar
- Sulama olayları
- Raporlar

### Neden PostgreSQL?

- İlişkisel veri için uygundur.
- Güvenilir ve ölçeklenebilirdir.
- Zaman damgalı sensör verilerini destekler.
- PostGIS ile harita verisi desteklenebilir.
- Supabase ile kolay kullanılabilir.

---

## 10. Veritabanı Servisi

### Supabase

Supabase şu amaçlarla kullanılabilir:

- PostgreSQL veritabanı
- Kullanıcı kimlik doğrulama
- API anahtarları
- Dosya saklama
- Gerçek zamanlı veri güncellemeleri

### Neden Supabase?

- Hızlı kurulum sağlar.
- Ücretsiz başlangıç paketi vardır.
- Dashboard üzerinden veri yönetilebilir.
- Auth sistemi hazırdır.
- Hackathon prototipi için zaman kazandırır.

### Alternatifler

- Firebase
- Neon
- Railway PostgreSQL
- Render PostgreSQL
- SQLite

### Karar

> MVP için Supabase PostgreSQL önerilir.

---

## 11. ORM ve Veri Modelleri

### SQLAlchemy

FastAPI ile veritabanı modellerini yönetmek için kullanılacaktır.

### Kullanım alanları

- Users modeli
- Farms modeli
- Crops modeli
- SensorReadings modeli
- Predictions modeli
- IrrigationEvents modeli
- Devices modeli

### Alternatifler

- SQLModel
- Tortoise ORM
- Prisma

### Karar

> SQLAlchemy veya SQLModel kullanılabilir.

Daha hızlı MVP geliştirme için:

> SQLModel tercih edilebilir.

---

## 12. Yapay Zekâ ve Makine Öğrenmesi

## Kullanılacak Dil

### Python

AI ve veri analizi katmanının tamamı Python ile geliştirilecektir.

---

## 13. Veri İşleme

### Pandas

Kullanım alanları:

- Test veri setlerini okuma
- Veri temizleme
- Eksik değer analizi
- Özellik mühendisliği
- Model girdisi hazırlama
- Tahmin sonuçlarını işleme

### NumPy

Kullanım alanları:

- Sayısal hesaplamalar
- Nem değişim simülasyonları
- Senaryo motoru
- Matematiksel işlemler

---

## 14. Makine Öğrenmesi Modelleri

### Random Forest

Kullanım alanı:

- Sulama gerekli/gereksiz sınıflandırması
- Risk sınıflandırması

### Avantajları

- Küçük ve orta boy veri setlerinde başarılıdır.
- Karmaşık veri ilişkilerini yakalayabilir.
- Özellik önemini gösterebilir.
- Hızlı eğitilir.

---

### XGBoost

Kullanım alanı:

- Sulama ihtiyacı tahmini
- Risk tahmini
- Sulama süresi tahmini

### Avantajları

- Tablo verilerinde güçlüdür.
- Eksik verilerle çalışabilir.
- Yüksek doğruluk sağlayabilir.
- Açıklanabilir AI araçlarıyla uyumludur.

---

### Regresyon Modelleri

Kullanım alanı:

- 24 saatlik nem tahmini
- 48 saatlik nem tahmini
- 72 saatlik nem tahmini
- Sulama süresi tahmini

Öneriler:

- Linear Regression
- Random Forest Regressor
- XGBoost Regressor

---

### Isolation Forest

Kullanım alanı:

- Sensör anomalisi
- Ani nem değişimi
- Gerçekçi olmayan veri
- Veri akış bozukluğu

---

## 15. Hibrit Karar Sistemi

AgriTwin AI yalnızca makine öğrenmesine dayanmayacaktır.

Önerilen yapı:

```text
Kural Tabanı
     +
Makine Öğrenmesi
     +
Güvenlik Sınırları
     =
Hibrit Karar Motoru
```

### Neden hibrit sistem?

- Test verisi sınırlıdır.
- Gerçek saha doğrulaması yapılmamıştır.
- Kritik sulama kararlarında güvenlik gerekir.
- Model hata yaptığında temel kurallar sistemi korur.

---

## 16. Açıklanabilir Yapay Zekâ

### SHAP

SHAP, model kararlarını açıklamak için kullanılabilir.

Kullanım alanları:

- Sulama kararında hangi değişken etkili oldu?
- Nem seviyesi kararı ne kadar etkiledi?
- Yağış ihtimali sonucu değiştirdi mi?
- Sıcaklık risk skorunu artırdı mı?

### Alternatif

- Feature importance
- Kural tabanlı açıklama
- LIME

### Karar

> MVP’de kural tabanlı açıklama metni ve güven skoru yeterlidir.

SHAP P2’ye ertelenmiştir; zaman kalırsa eklenir.

---

## 17. IoT Simülasyonu

## Önerilen Teknoloji

### MQTT

MQTT, IoT cihazlarının hafif veri iletişimi için kullanılan mesajlaşma protokolüdür.

Prototipte:

- Sensör verisi gönderimi
- Cihaz durumu
- Vana durumu
- Veri akışı simülasyonu

için kullanılabilir.

### Önerilen MQTT Broker

- Mosquitto
- HiveMQ Cloud
- EMQX

### Alternatif

- REST API ile veri gönderimi
- Zamanlanmış Python scripti
- WebSocket

### Karar

> Hackathon/MVP için REST tabanlı kontrollü simülasyon kullanılmalıdır.

MQTT sonraki faza bırakılabilir.

---

## 18. IoT Simülasyon Scripti

Python scripti şu görevleri yapar:

- Hazır test senaryosunu okumak (`ai/datasets/*.json`)
- `POST /iot/simulate` ile sensör verisi göndermek (`source_type: simulation`)
- Cihaz `last_data_time` güncellemesini API üzerinden sağlamak

### Mevcut script

```text
iot/
└── simulator/
    └── simulate.py
```

Örnek:

```bash
python iot/simulator/simulate.py --token <JWT> --farm-id 1 --scenario drought_risk --once
```

---

## 19. Hava Durumu Verisi

MVP’de iki seçenek vardır:

### Seçenek 1 — Kullanıcı Girdisi

Kullanıcı:

- Hava sıcaklığı
- Hava nemi
- Yağış ihtimali

değerlerini manuel girer.

### Seçenek 2 — Hava Durumu API’si

İleri aşamada gerçek hava verisi alınabilir.

Olası servisler:

- OpenWeather
- WeatherAPI
- Meteoroloji Genel Müdürlüğü açık verileri

### Karar

> MVP’de kullanıcı girdisi ve kontrollü test verisi kullanılmalıdır.

Gerçek hava durumu API’si P1 veya Faz 2 özelliği olmalıdır.

---

## 20. Grafik ve Görselleştirme

### Recharts

Kullanım alanları:

- Nem değişim grafiği
- 72 saatlik tahmin
- Su kullanımı
- Senaryo karşılaştırması
- Risk grafikleri

### Neden Recharts?

- Next.js ve React ile doğrudan uyumludur.
- shadcn/ui ekosistemiyle iyi çalışır.
- Dashboard için hafif ve yeterlidir.

### Alternatifler

- Plotly.js
- Chart.js
- ECharts
- Matplotlib (yalnızca Python/Streamlit)

### Karar

> Next.js MVP için Recharts kullanılmalıdır.

Streamlit kullanılırsa Plotly tercih edilebilir.

---

## 21. Harita ve Dijital İkiz Görünümü

### React Leaflet

Kullanım alanları:

- Arazi konumu
- Tarla bölge görünümü
- Nem yoğunluk katmanı
- Risk bölgeleri

### Alternatifler

- Mapbox
- Google Maps
- Folium

### Karar

> MVP’de basit React Leaflet haritası yeterlidir.

Gerçek koordinat yoksa:

> Tarla bölgesi kart veya grid tabanlı gösterilebilir.

---

## 22. Kimlik Doğrulama

### Supabase Auth

Kullanım alanları:

- Kullanıcı kayıt
- Giriş
- Şifre sıfırlama
- Oturum yönetimi
- Kullanıcı kimliği

### Alternatif

- JWT
- Auth0
- Firebase Auth
- NextAuth

### Karar

> En hızlı MVP için Supabase Auth kullanılmalıdır.

Backend kontrolü için JWT doğrulaması eklenebilir.

---

## 23. Dosya Saklama

MVP’de büyük dosya ihtiyacı sınırlıdır.

Gelecekte:

- Toprak analiz raporları
- CSV dosyaları
- Sensör veri dosyaları
- Görseller

saklanabilir.

### Önerilen Servis

- Supabase Storage

---

## 24. Test Teknolojileri

## Backend Testleri

### Pytest

Kullanım alanları:

- API testleri
- Veri doğrulama testleri
- AI servis testleri
- Otomasyon testleri

---

## Frontend Testleri

### Vitest

Kullanım alanları:

- Bileşen testleri
- Form testleri
- Kullanıcı etkileşimleri

### Alternatif

- Jest
- React Testing Library

---

## Uçtan Uca Test

### Playwright

Kullanım alanları:

- Kayıt
- Arazi oluşturma
- Veri girişi
- Tahmin
- Sulama başlatma

akışlarını test etmek.

---

## 25. Canlıya Alma

### Frontend

#### Vercel

Avantajları:

- Next.js ile uyumlu
- Hızlı deploy
- GitHub entegrasyonu
- Otomatik build

---

### Backend

#### Render

Avantajları:

- FastAPI destekler
- Kolay deploy
- Ücretsiz başlangıç seçeneği

#### Railway

Alternatif backend servisi olarak kullanılabilir.

---

### Veritabanı

#### Supabase

- PostgreSQL
- Auth
- Storage
- API

tek platformda sağlanabilir.

---

## 26. İzleme ve Hata Yönetimi

### Backend Logging

- Python logging
- Loguru

### Hata Takibi

- Sentry

### Kullanım Alanları

- API hataları
- Frontend hataları
- Tahmin servis hataları
- Kullanıcı akış sorunları

### Karar

> Hackathon için temel loglama yeterlidir.

Sentry zaman kalırsa eklenmelidir.

---

## 27. Kod Kalitesi

### Python

- Black
- Ruff
- MyPy

### TypeScript

- ESLint
- Prettier

### Git

- Branch yapısı
- Pull request
- Commit standardı

---

## 28. Git Branch Yapısı

```text
main
develop
feature/auth
feature/farm-management
feature/manual-data
feature/iot-simulator
feature/ai-model
feature/scenario-simulation
feature/irrigation-automation
```

---

## 29. Önerilen Proje Klasör Yapısı

```text
AgriTwin/
├── frontend/
│   └── src/app/          # App Router sayfaları
│   └── src/lib/api.ts
├── backend/
│   ├── app/              # FastAPI (routers, models, ai_engine, anomaly)
│   ├── tests/
│   ├── supabase/
│   └── requirements.txt
├── ai/
│   ├── datasets/
│   └── rule_engine.py
├── iot/simulator/simulate.py
├── .cursor/rules/
├── .env.example
├── AGENTS.md
├── README.md
├── prd.md / mvp.md / plan.md / Progress.md / techstack.md / …
└── (ürün dokümanları kökte; docs/ klasörü yok)
```

Docker / LICENSE isteğe bağlıdır; şu an zorunlu değildir.

---

## 30. Docker Kullanımı

### Öneri

Docker zorunlu değildir.

Ancak ekip teknik olarak uygunsa:

- Backend
- PostgreSQL
- MQTT broker

servisleri Docker Compose ile çalıştırılabilir.

### MVP kararı

> Hackathon süresinde Docker yalnızca ekip hâkimse kullanılmalıdır.

Aksi hâlde zaman kaybettirir.

---

## 31. Minimum Teknik Stack

Ekip küçük ve süre kısıtlıysa şu sade yapı kullanılmalıdır:

| Katman | Minimum Tercih |
|---|---|
| Uygulama | Streamlit |
| Backend | Streamlit içinde Python |
| Veritabanı | SQLite |
| AI | Scikit-learn |
| Veri İşleme | Pandas |
| Grafik | Recharts (veya Streamlit için Plotly) |
| IoT Simülasyonu | Python scripti |
| Deploy | Streamlit Cloud |

### Avantaj

- Çok hızlı geliştirme
- Tek dil
- Kolay deploy
- Az entegrasyon

### Dezavantaj

- Profesyonel kullanıcı deneyimi sınırlı
- Ölçeklenebilirlik düşük
- Frontend kontrolü az

---

## 32. Önerilen Profesyonel Stack

| Katman | Profesyonel Tercih |
|---|---|
| Frontend | Next.js + TypeScript |
| UI | Tailwind CSS + shadcn/ui |
| Backend | FastAPI |
| Veritabanı | Supabase PostgreSQL |
| Auth | Supabase Auth |
| AI | Scikit-learn + XGBoost |
| Veri | Pandas + NumPy |
| IoT | MQTT veya REST simülasyonu |
| Grafik | Recharts |
| Harita | React Leaflet |
| Frontend Deploy | Vercel |
| Backend Deploy | Render |
| Test | Pytest + Vitest |
| Kod Yönetimi | GitHub |

---

## 33. Nihai Teknik Karar

Hackathon için önerilen ana yapı:

> **Next.js + TypeScript + Tailwind CSS + FastAPI + Supabase PostgreSQL + Scikit-learn + XGBoost + Python IoT Simülasyonu + Vercel + Render**

### Gerekçe

- Arayüz profesyonel görünür.
- AI katmanı Python ile doğrudan entegre olur.
- Supabase geliştirme süresini azaltır.
- IoT veri akışı simüle edilebilir.
- Uygulama canlıya alınabilir.
- Proje daha sonra gerçek sensörlerle genişletilebilir.

---

## 34. Teknik Öncelik Sırası

### P0 — Zorunlu (MVP çalışır dilim)

- Next.js + FastAPI
- SQLite veya PostgreSQL
- Kural tabanlı AI motoru
- IoT REST simülasyonu
- Senaryo + sanal sulama API/UI
- Yerel çalışır demo

### P1 — Önemli

- Recharts
- shadcn/ui
- Veri güven skoru (UI genişletme)
- Anomali UI iyileştirmeleri
- Su tasarrufu raporu
- Canlıya alma (Vercel/Render)

### P2 — Sonraki Faz

- Scikit-learn / XGBoost
- SHAP
- MQTT
- Supabase Auth
- React Leaflet
- Gerçek hava durumu API’si
- Gerçek sensör entegrasyonu
- Docker
- Sentry

---

## 35. Kritik Teknik Uyarılar

### 1. Karmaşık stack kullanmayın

Çalışmayan mikroservis mimarisi, basit ama çalışan uygulamadan daha kötü sonuç verir.

### 2. IoT simülasyonunu gerçek entegrasyon gibi sunmayın

Arayüzde açıkça:

> IoT Simülasyonu

etiketi bulunmalıdır.

### 3. Yapay veriye dayalı modeli gerçek saha modeli gibi göstermeyin

Model, MVP karar destek prototipi olarak sunulmalıdır.

### 4. LLM kullanımı zorunlu değildir

Sulama tahmini için üretken yapay zekâ kullanmak gereksizdir.

Temel makine öğrenmesi modelleri daha uygundur.

### 5. Dijital ikiz sadece dashboard değildir

Dijital ikiz katmanı:

- Mevcut durumu göstermeli
- Geleceği tahmin etmeli
- Senaryo simülasyonu yapmalı
- Sonuçlarla güncellenmelidir

---

## 36. Sonuç

AgriTwin AI’ın teknik başarısı kullanılan teknoloji sayısıyla ölçülmemelidir.

Başarı ölçütü:

> Kullanıcının veri girebildiği, IoT veri akışının simüle edildiği, yapay zekânın sulama kararı ürettiği, senaryoların karşılaştırıldığı ve sanal otomasyonun çalıştığı uçtan uca sistemin canlı olarak gösterilebilmesidir.