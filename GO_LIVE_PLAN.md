# AgriTwin AI — Canlıya Alma (Go-Live) Planı

Bu doküman, **yerelde çalışan** AgriTwin web MVP’sini uç kullanıcıların erişebileceği bir canlı ortama almak için **dışarıdan eklenmesi gereken** servisleri, ortam değişkenlerini, adımları ve AI durumunu özetler. Ürün özelliklerinin yeniden tasarlanması değildir; as-built stack’e (`techstack.md`, `.env.example`, `Progress.md`) dayanır.

**Hedef stack (mevcut kararlar):** Frontend → **Vercel** · Backend → **Render veya Railway** · DB → **Supabase PostgreSQL** · Auth → mevcut **JWT** (Supabase Auth P2).

---

## 1. Mevcut durum (yerel vs canlı)

| Katman | Yerel (şimdi) | Canlı (hedef) |
|--------|---------------|---------------|
| Frontend | `npm run dev` → `localhost:3000` | Vercel HTTPS URL |
| Backend | `uvicorn` → `localhost:8000` | Render/Railway HTTPS URL |
| DB | SQLite (`sqlite:///./agritwin.db`) | Supabase Postgres (`DATABASE_URL`) |
| CORS | `http://localhost:3000` | Vercel origin(s) |
| Auth | JWT + sabit demo kod `123456` | Aynı JWT API; e-posta kodu gerçek SMTP ile (önerilir) |
| IoT | `POST /iot/simulate`, `source_type: simulation` | Aynı (simülasyon etiketi korunur) |
| Lab OCR | Simüle extract | Aynı uçlar; gerçek OCR P2 |
| AI | Kural motoru (`ai/rule_engine.py`) | Aynı; ML sonra backend sürecinde |
| Seed | `scripts.seed_demo` + `Secret12` | Demo için kontrollü seed; prod kullanıcı verisi ayrı politika |

**Zaten canlıya hazır (uygulama tarafı):** kayıt → arazi → veri → sulama önerisi → senaryo → onaylı sanal sulama; pytest yeşil; `/health` var.

**Eksik (dış dünya):** cloud hesapları, secret’lar, Postgres URL, CORS/domain, deploy pipeline, (önerilen) gerçek e-posta gönderimi.

---

## 2. Zorunlu dış servisler (P0)

### 2.1 Supabase — PostgreSQL

| Ne | Nasıl / Nerede | Amaç |
|----|----------------|------|
| Supabase projesi | [supabase.com](https://supabase.com) → New project | Kalıcı kullanıcı, arazi, sensör, tahmin verisi |
| Connection string | Project Settings → Database → URI | Backend `DATABASE_URL` |
| Şema | İki yol (aşağı) | Tabloların Postgres’te oluşması |

**.env (backend host):**

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
```

> Alternatif: pooler URI (Supabase “Connection pooling”, genelde port `6543`) — Render/Railway uyuyan süreçlerde bağlantı limiti sorununu azaltır.

**Şema nasıl uygulanır?**

1. **Önerilen (SQL ile kontrol):** Supabase SQL Editor’da sırayla çalıştır:
   - `backend/supabase/001_initial_schema.sql`
   - `backend/supabase/002_lab_zones_iot.sql`
2. **Alternatif (hızlı):** Backend ayağa kalkınca `Base.metadata.create_all` modellerden tablo oluşturur (`backend/app/main.py`). SQL dosyaları şema kaydıdır; prod’da tercihen SQL’i önce çalıştırıp drift’i gözden geçirin.

**Paket zorunluluğu (hard blocker):** `backend/requirements.txt` şu an yalnızca SQLite sürücüsü içerir. Postgres için deploy öncesi ekleyin:

```text
psycopg2-binary>=2.9.9
```

(veya SQLAlchemy 2 ile `psycopg[binary]`). Yoksa `DATABASE_URL=postgresql://...` ile süreç ayağa kalkmaz.

**Çalışma yöntemi:** Yerelde SQLite ile geliştirmeye devam; prod’da yalnızca `DATABASE_URL` Postgres’e işaret eder. Kod değişikliği gerekmez (`database.py` zaten URL’e göre `connect_args` ayarlar).

---

### 2.2 Backend hosting — Render (birincil) veya Railway

| Ne | Nasıl / Nerede | Amaç |
|----|----------------|------|
| Web Service | Render → New → Web Service → GitHub repo | FastAPI’yi 7/24 yayınlamak |
| Root / build | Root Directory: `backend` · Build: `pip install -r requirements.txt` · Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | API |
| Env vars | Dashboard → Environment | Secret + DB + CORS |

**Railway alternatifi:** Aynı repo/`backend` klasörü, start komutu aynı; `$PORT` Railway’de otomatik.

**Fly.io:** `techstack` / Progress’te alternatif; Dockerfile sonra. MVP için Render/Railway yeterli.

**Backend env (isimler as-built — `backend/app/config.py`):**

| Değişken | Örnek / not |
|----------|-------------|
| `DATABASE_URL` | Supabase Postgres URI |
| `SECRET_KEY` | Uzun rastgele string (**`JWT_SECRET` değil** — Progress eski notunda karışıklık vardı) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (veya daha kısa prod politikası) |
| `CORS_ORIGINS` | `https://YOUR-APP.vercel.app` (virgülle birden fazla) |

Smoke: `GET https://YOUR-BACKEND.onrender.com/health` → `{"status":"ok","service":"agritwin-api"}`.

---

### 2.3 Frontend hosting — Vercel

| Ne | Nasıl / Nerede | Amaç |
|----|----------------|------|
| Proje | Vercel → Import GitHub → Root Directory: `frontend` | Next.js App Router yayını |
| Env | Project → Settings → Environment Variables | API adresi |
| Framework | Next.js (otomatik) | HTTPS + CDN |

```env
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND.onrender.com
```

Build sonrası tarayıcı bu URL’e istek atar (`frontend/src/lib/api.ts`). Protocol `https`, trailing slash yok.

**CORS kilidi:** Vercel URL’i kesinleşince backend `CORS_ORIGINS`’i güncelleyin; aksi halde tarayıcı preflight başarısız olur.

---

### 2.4 Domain + HTTPS

| Ne | Nasıl | Amaç |
|----|-------|------|
| Vercel domain | Varsayılan `*.vercel.app` veya Custom Domain | Kullanıcı erişimi |
| Backend URL | Render/Railway `*.onrender.com` / `*.up.railway.app` | API |
| HTTPS | Her iki platformda varsayılan | JWT cookie dışı Bearer token bile TLS şart |

Özel alan adı (opsiyonel P0+): örn. `app.agritwin.example` → Vercel; `api.agritwin.example` → Render CNAME. Fake URL uydurulmaz — gerçek URL deploy sonrası `Progress.md`’ye yazılır.

---

### 2.5 Sırlar ve demolar

| Ne | Nasıl | Amaç |
|----|-------|------|
| `SECRET_KEY` | Platform secret store; asla git’e commit etme | JWT imza |
| Demo kullanıcılar | `SEED_DEMO_USERS=1` (veya Postgres’te otomatik) + `POST /auth/demo-login` | Jüri / iç demo |
| Şifre | `DEMO_USERS.md` — `Secret12` | Yalnızca demo; gerçek kullanıcıya zorla dağıtma |

---

## 3. Kimlik doğrulama ve e-posta

### As-built

- Backend kendi JWT’sini üretir (`SECRET_KEY`, HS256).
- Kayıt → `POST /auth/verify` ile e-posta doğrulama.
- Kod üretimi: `backend/app/routers/auth.py` içinde **`DEMO_CODE = "123456"`** sabit; API yanıtında sıkça `demo_code` döner (SMTP yok).
- Şifre unutma: `POST /auth/forgot-password` + `POST /auth/reset-password` — yine aynı demo kod yolu.

Supabase Auth / `NEXT_PUBLIC_SUPABASE_*` `.env.example`’da **opsiyonel** tanımlı; uygulama şu an JWT akışını kullanır. Canlı P0 için Supabase Auth zorunlu değildir.

### Canlıda ne eklenmeli? (P0 önerisi / P1 zorunlu sayılabilir)

| Ne | Nerede | Nasıl | Amaç |
|----|--------|-------|------|
| Transactional e-posta | Resend, SendGrid, Amazon SES veya SMTP (Brevo vb.) | Backend’e `SMTP_*` / `RESEND_API_KEY` env; `_create_code` rastgele 6 hane üretsin; e-posta gövdesinde kod gönderilsin; API’den `demo_code` kaldır veya yalnızca `ENV=development`’ta döndür | Gerçek doğrulama / reset |
| Rate limit | Auth router veya reverse proxy | Brute-force kod denemesini sınırla | Güvenlik |

**Çalışma yöntemi (değiştirme sırası):**

1. E-posta sağlayıcı hesabı aç → API key / SMTP al.
2. Env’e ekle (henüz kod yoksa bile secret hazır olsun).
3. Küçük auth değişikliği: rastgele kod + send mail (bu adım **kod** gerektirir; deploy’un “demo-only” fazında atlanabilir, kullanıcıya UI’da `123456` gösterilmeye devam eder — **açıkça “prototip” olarak etiketlenmeli**).
4. Prod’da `demo_code` alanını kapat.

**Supabase Auth (P2):** Frontend’i Supabase Auth’a taşımak ayrı iş; şu anki FastAPI `/auth/*` sözleşmesi korunarak canlıya çıkmak daha hızlıdır.

---

## 4. Opsiyonel dış servisler (P1 / P2)

| Öncelik | Servis | Ne eklenir | Nerede / nasıl | Amaç / sonuç |
|---------|--------|------------|----------------|--------------|
| P1 | Gerçek hava durumu | **Open-Meteo** (ücretsiz, key yok) — `GET /weather/{farm_id}` as-built | Dashboard + canlı sensör | Tahmin girdisi |
| P1 | Supabase Storage | Bucket + service role | Lab PDF/görsel saklama | Lab yükleme dosyalarının kalıcılığı |
| P2 | Gerçek IoT ingest | Device token + `POST` sensor veya webhook | Mevcut `source_type` genişletme (`simulation` değil); LoRa/Wi-Fi gateway → HTTPS | Gerçek nem akışı; UI’da simülasyon etiketi kalkar |
| P2 | MQTT broker | HiveMQ Cloud / EMQX / Mosquitto | `iot-mimarisi.md`; backend subscriber → DB | Alan cihazlarından sürekli yayın |
| P2 | OCR | Google Cloud Vision / Document AI / Azure Form Recognizer | Lab upload pipeline; **kullanıcı onayı sonrası kaydet** (mevcut kural) | Rapor metninden P/K/pH vb. çıktı |
| P1 | Harita | **Leaflet + OSM** (as-built dashboard/twin/login) — Google Maps yalnızca `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` varsa | Arazi konumu görselleştirme |
| P2 | ML hosting | Aynı FastAPI süreci veya model artifact (joblib) | `ai/` + Scikit-learn/XGBoost; ayrı “AI microservice” şart değil | Sınıflandırma/regresyon skorları |
| P2 | Sentry | DSN env | Frontend + FastAPI SDK | Hata izleme |
| P2 | Custom domain | DNS | Vercel + Render | Marka URL |

Bu maddeler **P0 go-live’ı engellemez**; önce Vercel + API + Postgres + CORS yeterlidir.

---

## 5. Yapay zekâ — şimdi vs sonra

### 5.1 Şimdi: kural tabanlı motor

| Ne | Detay |
|----|--------|
| Nerede | `ai/rule_engine.py` (+ backend `app` içinde aynı mantık / predict uçları) |
| Girdi | Nem, sıcaklık, yağış ihtimali, son sulama saati, toprak/ürün, veri yaşı, `data_confidence` |
| Çıktı tipi | `irrigation_needed`, `irrigation_duration` (dk), `risk_level` (`low\|medium\|high\|critical`), `confidence_score` (0–100), Türkçe `explanation`, `moisture_24h/48h/72h` |
| Çalışma yöntemi | Eşik kuralları (örn. nem &lt; 25 → kritik sulama; nem &gt; 70 → aşırı sulama riski); günlük nem düşüşü ile 72s projeksiyon |
| Dış model API | **Yok** — LLM veya bulut AI çağrısı yok |

**Güvenlik sınırları (korunmalı):**

- Güven &lt; **60** → otomasyon önerilmez / `POST /irrigation/start` reddedilir (`MIN_CONFIDENCE_FOR_AUTOMATION`).
- Sanal sulama yalnızca `user_approved=true` ile.
- Simülasyon / test verisi UI ve API’de `source_type` ile etiketlenir.

**Örnek sonuç (şekil):**

```json
{
  "irrigation_needed": true,
  "irrigation_duration": 14.0,
  "risk_level": "high",
  "confidence_score": 78.5,
  "explanation": "Sulama öneriliyor. Nem %28, yağış ihtimali %10, son sulama 36 saat önce.",
  "moisture_24h": 24.5,
  "moisture_48h": 21.0,
  "moisture_72h": 17.5
}
```

### 5.2 Sonra: Scikit-learn / XGBoost (P2)

| Ne | Detay |
|----|--------|
| Nerede | Aynı backend Python süreci; model dosyası (ör. `ai/models/*.joblib`) |
| Ne değişir | Eşik kurallarının yerine veya hibrit: RF/XGBoost sınıflandırma (sulama evet/hayır, risk) + regresyon (süre / 24–72s nem) |
| Dış “AI API” | Gerekmez; eğitim offline, çıkarım sunucu içi. (İleride ayrı GPU servisi opsiyonel.) |
| Sonuç tipi | Aynı JSON şema tercih edilir — frontend kırılmaz |
| Açıklama | MVP’de kural metni; SHAP P2 |
| Güvenlik | Hibrit: model skoru + kural güvenlik sınırları + confidence &lt; 60 otomasyon yasağı **aynı kalır** |

**Önemli:** Canlıya alma için ML eğitimi / hosting **zorunlu değildir**. Kural motoru prod’da da geçerlidir.

---

## 6. Endpoint’ler canlıda

### 6.1 Aynı kalanlar (path değişmez)

MVP öneksiz kök yollar (`techstack.md` / `prd.md`). Canlıda yalnızca **host** değişir:

```text
/auth/*          /farms/*         /sensor-readings/{farm_id}
/iot/simulate    /predict/...     /predictions/{farm_id}
/anomalies/{farm_id}
/simulate/scenario
/irrigation/*    /devices/*       /labs/*         /datasets/*
/health          /admin/* (rol korumalı)
```

Frontend `NEXT_PUBLIC_API_URL` ile aynı path’leri çağırır — go-live için API sözleşmesi kırmak gerekmez.

### 6.2 Yeni dış API çağrıları (sonra eklenecek)

| Tetik | Dış çağrı | AgriTwin’e dönüş |
|-------|-----------|------------------|
| E-posta doğrulama (P0/P1) | Resend/SendGrid/SMTP | Kod gönderimi; endpoint path aynı kalabilir |
| Hava (P1) | OpenWeather `onecall` / current | Backend nem/yağış alanını doldurur |
| OCR (P2) | Vision/Document AI | Preview JSON → kullanıcı onayı → lab kayıt |
| Tile (P2) | OSM / MapTiler | Tarayıcı tile isteği (backend şart değil) |
| MQTT (P2) | Broker | Ingest → mevcut sensor tablosu |

Bunlar yeni **dış** bağımlılıktır; mevcut REST yüzeyi mümkün olduğunca genişletilir, değiştirilmez.

---

## 7. Adım adım: nasıl eklerim?

### A. Hesaplar

1. GitHub repo erişimi (deploy bağlamak için).
2. [Supabase](https://supabase.com) proje oluştur.
3. [Render](https://render.com) veya [Railway](https://railway.app) hesap.
4. [Vercel](https://vercel.com) hesap (GitHub ile).
5. (Önerilen) Resend/SendGrid hesap — e-posta için.

### B. Veritabanı

1. Supabase → Database password kaydet (bir kez gösterilir).
2. SQL Editor’da `001_initial_schema.sql` + `002_lab_zones_iot.sql` çalıştır **veya** create_all’a güven.
3. Connection string kopyala.
4. `psycopg2-binary`’yi `requirements.txt`’e ekle ve commit et (deploy öncesi).

### C. Backend deploy

1. Render Web Service → repo → root `backend`.
2. Env: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS` (geçici olarak `*` koyma; Vercel URL sonrası netleştir).
3. Deploy → `/health` kontrol.
4. İsteğe bağlı: one-off shell ile `python -m scripts.seed_demo` (**yalnızca demo DB**).

### D. Frontend deploy

1. Vercel → `frontend` root.
2. `NEXT_PUBLIC_API_URL=<backend-https>`.
3. Deploy → login sayfası açılır mı bak.

### E. CORS + son ayar

1. Vercel production URL’ini kopyala.
2. Backend `CORS_ORIGINS=https://…vercel.app` (preview için ek origin gerekebilir).
3. Redeploy backend.

### F. Seed kısıtları

| Ortam | Seed |
|-------|------|
| Yerel demo | `seed_demo` serbest |
| Prod “jüri demosu” | Tek seferlik seed; şifreleri dar dairede paylaş |
| Gerçek uç kullanıcı | **Seed çalıştırma**; kullanıcılar `/auth/register` ile gelsin; demo kod politikasını kapat |

### G. Smoke checklist

- [ ] `/health` 200  
- [ ] Kayıt → verify → login (demo kod veya gerçek mail)  
- [ ] Arazi oluştur → manuel / simulate okuma  
- [ ] Sulama önerisi + 72s nem  
- [ ] Senaryo karşılaştır  
- [ ] `user_approved=false` red; `true` + confidence ≥ 60 ile sanal sulama  
- [ ] UI’da simülasyon verisi “simülasyon” etiketli  
- [ ] HTTPS (kilit ikonu)  
- [ ] `DEMO_CHECKLIST.md` kısa prova  

Başarılı URL’leri `Progress.md` Faz 10’a işle (secret yazma).

---

## 8. Maliyet ve güvenlik checklist

### Maliyet (tipik free tier — fiyatlar değişebilir)

| Servis | Tipik giriş maliyeti |
|--------|----------------------|
| Vercel Hobby | Ücretsiz (hobby limitleri) |
| Render Free / Railway trial | Ücretsiz veya düşük; **free tier uyuyabilir** (ilk istek yavaş) |
| Supabase Free | Ücretsiz kota; DB boyutu / pause politikasına dikkat |
| E-posta | Resend vb. ücretsiz kota |
| Sentry / OCR / OpenWeather | Kullanımda ücretlenebilir |

Prod için uzun süre açık kalacaksa Render **paid** veya Railway aylık plan düşünün (cold start jüri demosunu bozar).

### Güvenlik

- [ ] `SECRET_KEY` üretildi ve commit edilmedi  
- [ ] `.env` / platform secret’ları git dışı  
- [ ] `CORS_ORIGINS` yalnızca bilinen frontend  
- [ ] HTTPS her iki uçta  
- [ ] Prod’da sabit `123456` kodu kapatıldı veya “demo modu” açıkça işaretli  
- [ ] Supabase service role / anon key yalnızca gerektiğinde; şu an JWT için zorunlu değil  
- [ ] Admin uçları rol korumalı; bootstrap secret’ı varsa rotate  
- [ ] Demo şifresi `Secret12` gerçek müşteriye verilmez  
- [ ] Simüle IoT / OCR gerçek gibi sunulmaz  

---

## 9. Demo vs production veri politikası

| | Demo / jüri | Production (uç kullanıcı) |
|--|-------------|---------------------------|
| DB | Seed + sabit senaryolar (`ai/datasets`) | Kullanıcıya ait veriler |
| IoT | `source_type: simulation` + etiket | Gerçek ingest gelene kadar simülasyon veya manuel |
| Lab | Simüle OCR + onay kapısı | Aynı onay kapısı; gerçek OCR sonra |
| Auth kodu | `123456` kabul edilebilir (etiketli) | E-posta ile rastgele kod |
| Seed | Evet | Hayır (veya yalnızca staging) |
| Veri iddiası | “Prototip / simülasyon” | Simüle veriyi “saha sensörü” diye gösterme |
| Yedek | Supabase otomatik / snapshot | Düzenli backup + retention politikası |

---

## 10. P0 / P1 / P2 özet tablosu

### P0 — Canlıya çıkmak için dışarıdan şart

1. Supabase PostgreSQL + `DATABASE_URL`  
2. `psycopg2-binary` (veya eşdeğer) bağımlılığı  
3. Backend host (Render/Railway) + `SECRET_KEY` + `CORS_ORIGINS`  
4. Frontend host (Vercel) + `NEXT_PUBLIC_API_URL`  
5. HTTPS (platform varsayılanı)  
6. Smoke test + (isteğe bağlı) kontrollü `seed_demo`  

### P1 — Canlı sonrası erken

- Gerçek e-posta (SMTP/Resend) — demo kodu kaldırma  
- Hava durumu API  
- Supabase Storage (lab dosyaları)  
- Sentry / temel log paneli  
- Uptime (Render paid) / custom domain  

### P2 — Sonraki ürün fazı

- MQTT / gerçek IoT ingest  
- Google Vision vb. OCR  
- Leaflet + tile sağlayıcı  
- Scikit-learn / XGBoost model artifact  
- Supabase Auth migrasyonu  
- SHAP  

---

## 11. İlgili dokümanlar

| Dosya | Rol |
|-------|-----|
| `.env.example` | Env isimleri |
| `techstack.md` §25–34 | Deploy tercihleri |
| `plan.md` Faz 10 | Görev listesi |
| `Progress.md` Faz 10 | Durum (henüz deploy yok) |
| `DEMO_USERS.md` / `DEMO_CHECKLIST.md` | Demo provası |
| `TEST_PLAN.md` | Smoke / E2E beklentileri |
| `veri-mimarisi.md` / `iot-mimarisi.md` | Veri kaynakları ve saha yolu |

---

## 12. Bu plandan sonra yapılacaklar (uygulama değil)

1. Cloud hesaplarını açmak (insan + ödeme yöntemi gerekebilir).  
2. `psycopg2-binary` PR’ı.  
3. Deploy + `Progress.md` Faz 10 kutularını işaretlemek.  
4. Auth e-posta entegrasyonu PR’ı.  

**Bu dosya yalnızca plan dokümanıdır; deploy henüz yapılmamıştır.**
