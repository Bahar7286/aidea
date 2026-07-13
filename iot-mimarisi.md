# AgriTwin AI — Topraktan Veri Alma / IoT Saha Mimarisi

> **Bağlayıcı kapsam:** Bu doküman gerçek saha donanımı ve IoT veri yolunu tanımlar.  
> MVP yazılımı şu an **simülasyon + REST** ile çalışır; donanım aşamaları aşağıda önceliklidir.  
> IoT yalnızca **dinamik** değerleri ölçer. Organik madde, P, K, mikroelement, bünye → `veri-mimarisi.md` (laboratuvar).  
> Gübre reçetesi, uydu/drone MVP dışıdır.

---

## Kritik karar

Tek cihaz toprağın her özelliğini ölçmemelidir.

Doğru zincir:

```text
Modüler sensör düğümü → kablosuz iletişim → ağ geçidi → bulut
→ veri doğrulama → dijital ikiz → AI analizi
```

---

## 1. Genel mimari

```text
TOPRAK VE ÇEVRE
├── Toprak nem sensörü (çoklu derinlik)
├── Toprak sıcaklık sensörü
├── EC sensörü (ikinci faz)
├── Hava sıcaklık/nem sensörü
├── Debi sensörü
└── Vana/pompa durumu
        │
        ▼
SAHA IoT DÜĞÜMÜ (ESP32-S3)
├── Sensör arabirimleri
├── Yerel veri hafızası
├── Güç yönetimi
└── LoRa / Wi-Fi
        │
        ▼
AĞ GEÇİDİ (LoRaWAN / Wi-Fi / 4G)
        │
        ▼
BULUT VE BACKEND
├── MQTT / REST API
├── Veri doğrulama
├── PostgreSQL / Supabase
├── Ham + doğrulanmış zaman serisi
└── Cihaz yönetimi
        │
        ▼
AGRITWIN AI
├── Sulama ihtiyacı
├── 24–72 saat nem tahmini
├── Anomali
├── Senaryo
└── Onaylı sulama otomasyonu
```

---

## 2. Hangi veriler sensörden alınır?

### 2.1. MVP saha cihazı (zorunlu / önemli)

| Veri | Sensör | Öncelik |
|------|--------|---------|
| Toprak nemi (VWC %) | Kapasitif / FDR — ideally 2 derinlik | Zorunlu |
| Toprak sıcaklığı | Dijital prob | Zorunlu |
| Hava sıcaklığı | Ortam sensörü | Zorunlu |
| Hava nemi | Ortam sensörü | Zorunlu |
| Sulama suyu miktarı | Debi | Önemli |
| Vana durumu | Röle / geri bildirim | Önemli |
| Toprak EC | EC sensörü | İkinci faz |

**Not:** Aynı VWC farklı toprak dokularında bitkinin kullanabileceği suyu aynı göstermeyebilir. Nem; toprak türü, kök derinliği ve laboratuvar profiliyle birlikte değerlendirilir.

### 2.2. Cihazdan alınmayacaklar

Organik madde, N, P, K, kireç, bünye, mikroelementler, mikrobiyal aktivite, KDK → laboratuvar (`veri-mimarisi.md`).

### 2.3. pH

MVP’de sürekli saha pH probu önerilmez (kalibrasyon, kirlenme, ucuz prob güvenilmezliği).  
**Laboratuvar raporu + manuel giriş.** İleri fazda profesyonel pH probu modüler eklenebilir.

---

## 3. Bölgesel yerleşim

Tek sensör bütün araziyi temsil etmez.

```text
Arazi
├── Bölge A
├── Bölge B
└── Bölge C
```

MVP yazılımında sanal bölge adları yeterlidir (harita P2).

Her pilot bölgede öneri:

- 1 × yüzeye yakın nem  
- 1 × kök bölgesi nem  
- 1 × toprak sıcaklığı  

Örnek derinlikler (ürün köküne göre seçilir, sabit kodlanmaz):

- Sebze/sera: 15–20 cm ve 30–40 cm  
- Ağaç/bağ: 20–30 cm ve 50–60 cm  

---

## 4. AgriTwin Field Node — fiziksel yapı

### Kontrol kartı

- **ESP32-S3** (Wi-Fi/BT, GPIO, I²C/UART/SPI, deep-sleep, OTA)

### Arabirimler

- 2 × analog, 1 × I²C, 2 × UART, 1 × RS-485/Modbus  
- Opsiyonel SDI-12, dijital giriş, röle/MOSFET çıkışı  

Uzun kabloda analog gürültü riski → üretime yakın cihazlarda RS-485/Modbus veya SDI-12 tercih edilir.

---

## 5. Cihaz varyantları

### A. Field Node Lite — MVP / hackathon

- ESP32-S3, 2× kapasitif nem, sıcaklık, hava T/RH  
- Opsiyonel debi, röle, Wi-Fi, 5 V / powerbank, IP65  
- 15 dk ölçüm, HTTPS REST, offline kuyruk, sanal/küçük vana  

### B. Field Node LoRa — saha pilotu

- LoRaWAN Class A, RS-485, flash/SD, RTC  
- Güneş + LiFePO₄, IP67, anten  
- Offline buffer, batarya/sağlık mesajı, uzak ayar  

### C. Control Node — sulama kontrolü (ayrı tut)

- Solenoid sürücü, debi/basınç, acil durdurma, manuel anahtar  
- Maks süre, kaçak uyarısı, bağlantı kesilince güvenli mod  

---

## 6. Güç ve ölçüm sıklığı

**MVP güç:** USB / 5 V / powerbank  
**Pilot:** panel → şarj → LiFePO₄ → regülatör → ESP32  

Ölçüm döngüsü: uyan → sensör güç → stabilize → 3–5 örnek → filtre → gönder → güç kes → deep-sleep → ~15 dk  

| Veri | Sıklık |
|------|--------|
| Toprak nemi / sıcaklık | 10–15 dk |
| Hava T/RH | 5–15 dk |
| EC | 30–60 dk |
| Debi | Sulama sırasında 5–10 sn |
| Vana | Durum değişiminde |
| Batarya / sağlık | 1 saat |

Dashboard her okumayı gösterebilir; AI için 15 dk / saatlik özet yeterlidir.

---

## 7. Firmware işlevleri

1. **Okuma:** kalibrasyon katsayısı, birim, hata kodu  
2. **Doğrulama:** aralık, yanıt, ani sıçrama, stuck değer, voltaj  
3. **Yerel kayıt:** timestamp, sensor_id, value, unit, error  
4. **Haberleşme:** MQTT veya HTTPS, retry, paket no, device_id  
5. **Yönetim:** ölçüm sıklığı, reboot, OTA, kalibrasyon güncelleme  

---

## 8. Örnek cihaz JSON paketi

```json
{
  "device_id": "AT-FN-001",
  "farm_id": "1",
  "zone_id": "ZONE-A",
  "timestamp": "2026-07-13T14:30:00+03:00",
  "source": "iot",
  "simulation": false,
  "measurements": {
    "soil_moisture_20cm": { "value": 31.4, "unit": "percent_vwc" },
    "soil_moisture_40cm": { "value": 38.1, "unit": "percent_vwc" },
    "soil_temperature": { "value": 24.6, "unit": "celsius" },
    "air_temperature": { "value": 32.2, "unit": "celsius" },
    "air_humidity": { "value": 41.0, "unit": "percent" }
  },
  "battery": 82,
  "signal_quality": -94,
  "status": "normal"
}
```

Simülasyonda `"simulation": true` **zorunlu**.

---

## 9. Bulut veri akışı

```text
Cihaz → kimlik → şema → birim standardı → aralık → anomali
→ ham kayıt → temizlenmiş kayıt → özet → AI → dashboard
```

İki tablo tutulmalı:

- **Ham veri** (silinmez)  
- **Doğrulanmış veri** (filtre/kalibrasyon sonrası)  

---

## 10. Laboratuvar bağlantısı

IoT = güncel dinamik durum  
Lab = temel referans profili  

Akış: rapor yükle → parametre çıkar → kullanıcı doğrula → birim → arazi+bölge+derinlik → toprak profili  

Detay: `veri-mimarisi.md`

---

## 11. AI girdi özeti

**Dinamik:** 20/40 cm nem, toprak/hava sıcaklığı, hava nemi, trend, yağış, son sulama, debi  
**Statik:** bünye, OM, tarla kapasitesi/solma (lab veya varsayılan), ürün, dönem, kök derinliği, sulama yöntemi  

**Çıktı:** sulama gerekli mi, zaman, süre, su miktarı, risk, güven, açıklama  

---

## 12. Kalibrasyon (kısa)

Kuru → kademeli nem → referans (mümkünse gravimetrik) → eğri → katsayı cihaza/buluta.  
Sensör–toprak hava boşluğu ölçümü bozar.

---

## 13. Arıza senaryoları

| Durum | Davranış |
|-------|----------|
| Cihaz arızası | Son geçerli veri; “güncel değil”; düşük güven; otomasyon kapalı |
| İnternet yok | Yerel kuyruk; sonra backfill |
| Anormal değer | Hamda kalsın; doğrulanmışa alma; uyarı |
| Vana açık kaldı | Max süre; debi yoksa kapat; kaçak uyarısı; manuel kapatma |

---

## 14. MVP kesin donanım kararı

> İki derinlikten toprak nemi + toprak sıcaklığı + çevre verisi; Wi-Fi → HTTPS REST; offline kuyruk; kullanıcı onayıyla vana/röle.

| Bileşen | Seçim |
|---------|--------|
| MCU | ESP32-S3 |
| Sensör | 2× nem, 1× toprak T, 1× hava T/RH, opsiyonel debi |
| Aktüatör | Düşük voltaj solenoid veya sanal vana |
| Link | Wi-Fi HTTPS (sonra LoRaWAN) |
| Güç | Adaptör/powerbank → sonra güneş+LiFePO₄ |
| Aralık | 15 dk |

---

## 15. Geliştirme sırası (donanım + yazılım)

| Aşama | İçerik | Yazılım durumu |
|-------|--------|----------------|
| 1 Masaüstü | ESP32 nem/sıcaklık okuma | Donanım |
| 2 API | JSON → FastAPI | Simülasyon hazır; gerçek cihaz ingest P1 |
| 3 Dashboard | Son değer, grafik, cihaz durumu | Kısmi (simüle) |
| 4 Doğrulama | Aralık, ani değişim, güven | Kısmi |
| 5 AI | Sulama / risk / 72s | Hazır (kural) |
| 6 Otomasyon | Onay + vana | Sanal hazır |
| 7 Saha pilotu | Kalibrasyon, birkaç gün veri | P2 |

---

## 16. Öncelik özeti

| Öncelik | İş |
|---------|-----|
| **P0 yazılım** | Mevcut sulama dilimi + simülasyon |
| **P1 yazılım** | Cihaz ingest şeması (çoklu derinlik), ham/doğrulanmış, bölgeler, lab modülü |
| **P1 donanım** | Field Node Lite (Wi-Fi) |
| **P2** | LoRaWAN, Control Node, EC sürekli, gerçek pH probu |

Referanslar: `veri-mimarisi.md`, `prd.md`, `mvp.md`, `plan.md`, `Progress.md`, `techstack.md`
