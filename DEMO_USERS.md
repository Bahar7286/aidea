# Demo kullanıcıları

MVP sunumu için **4 giriş**. Ortak şifre: `Secret12`

Her hesap **farklı, gerçekçi** arazi verisi taşır (klon değil).

| # | E-posta | Rol | Arazi / veri özeti |
|---|---------|-----|-------------------|
| 1 | `admin@agritwin.demo` | admin | `/admin` paneli + küçük **Yönetim Demo Arazisi** (Ankara). Kullanıcı/filo/destek ticket’ları dolu. |
| 2 | `ciftci@agritwin.demo` | farmer | **Domates Serası** (Antalya/Serik, tinli, damla). Kuruyan nem serisi → sulama ihtiyacı; 2 cihaz, lab onaylı, sera malzemeleri. |
| 3 | `ziraat@agritwin.demo` | agronomist | **Karapınar Buğday Tarlası** (~18.5 da, kumlu, yağmurlama). Orta nem; **manuel + simülasyon** karışımı; açık alan gübre sınıfları. |
| 4 | `kooperatif@agritwin.demo` | cooperative | **2 arazi:** Yeşilova Merkez (biber, 3 zon farklı nem) + Kuzey Bahçe (elma, yüksek nem). Bölgesel sulama hikâyesi. |

Simülasyon okumaları API/UI’da `source_type: simulation` ile etiketlenir. Sanal sulama kullanıcı onayı olmadan başlamaz.

Canlı: `https://aidea-three.vercel.app` (API: `https://aidea-f8ji.onrender.com`). Agro malzemeler demo tarlalarda kullanım kaydı olarak seed edilir; gübre reçetesi yoktur.

## Oluşturma

```bash
cd backend
# Windows
.venv\Scripts\python.exe -m scripts.seed_demo
```

**Canlı (Render / Supabase):**

1. Environment: `SEED_DEMO_USERS=1` (veya boş bırakın — Postgres’te startup’ta otomatik upsert).
2. **Manual Deploy** (restart) veya login sayfasındaki demo butonları → `POST /auth/demo-login` aynı zengin seed’i çalıştırır.

Hesaplar e-posta doğrulanmış gelir; doğrulama kodu gerekmez.

## Önerilen demo sırası

1. **Admin** → KPI, kullanıcılar, cihaz filosu, destek  
2. **Çiftçi** → Domates Serası → canlı sensör / AI / senaryo / sulama (onay şart)  
3. **Ziraat** → kumlu tarla, orta nem, manuel+sim kaynak rozetleri  
4. **Kooperatif** → arazi seçici ile 2 farm / zon nem farkı  
