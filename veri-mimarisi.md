# AGRITWIN AI — VERİ MİMARİSİ VE LABORATUVAR ANALİZİ

> **Bağlayıcı kapsam:** Bu doküman veri platformu mimarisini tanımlar.  
> Sulama MVP’si (`mvp.md` / `prd.md`) nem + sulama kararına odaklanır.  
> Laboratuvar verisi IoT’nin **yerine geçmez**; sensör verisini **tamamlar**.  
> Gübre reçetesi, uydu/drone, tam toprak biyolojisi **MVP dışıdır**.

---

## 1. Kritik mimari karar

AgriTwin AI yalnızca bir IoT paneli değildir.

> Sensör, laboratuvar, kullanıcı ve dış veri kaynaklarını birleştiren bir **toprak veri platformu** olmalıdır.

Bütün verileri sensörden almaya çalışmak sistemi pahalı veya güvenilmez yapar.

### Dört giriş yolu

1. Manuel tarla ve ürün verisi  
2. IoT sensör entegrasyonu (MVP’de simülasyon)  
3. Laboratuvar raporu yükleme ve doğrulama  
4. Hava durumu / dış veri (MVP’de manuel veya test; sonra API)

---

## 2. Toprak verilerinin dört grubu

### A. IoT ile sürekli ölçülebilecek veriler

| Veri | Nasıl ölçülür? | Kullanım amacı |
|------|----------------|----------------|
| Toprak nemi | Kapasitif / TDR / FDR | Sulama ihtiyacı |
| Toprak sıcaklığı | Sıcaklık probu | Buharlaşma, kök ortamı |
| Hava sıcaklığı | Meteoroloji sensörü | Su kaybı tahmini |
| Hava nemi | Nem sensörü | Buharlaşma analizi |
| Yağış | Yağmur ölçer veya API | Sulamayı erteleme |
| Toprak EC | EC probu | Tuzluluk / iyon yoğunluğu göstergesi |
| Sulama suyu miktarı | Debi sensörü | Su tüketimi |
| Vana durumu | Akıllı vana / röle | Otomasyon |
| Işık / güneşlenme | Işık sensörü veya meteo | Bitki su tüketimi |
| Toprak su potansiyeli | Tansiyometre | Suya erişim zorluğu |

**Not:** EC tuzluluk ve çözünmüş iyon yoğunluğu hakkında bilgi verir; “şu kadar azot/fosfor var” anlamına gelmez. Nem, sıcaklık, doku ve tuzlardan etkilenir.

### B. Laboratuvarda dönemsel ölçülen veriler

Düşük maliyetli IoT ile sürekli ve güvenilir ölçülmemeli:

- Organik madde, organik karbon  
- Yarayışlı fosfor / potasyum  
- Toplam azot, Ca, Mg, Na  
- Mikroelementler (Fe, Zn, Mn, Cu, B)  
- Kireç, toprak bünyesi (kum-kil-silt)  
- Katyon değişim kapasitesi  
- Ağır metaller, mikrobiyal aktivite  
- Hacim ağırlığı, agregat stabilitesi  

Türkiye’de standart verimlilik paketlerinde yaygın: saturasyon, toplam tuz, pH, kireç, fosfor, potasyum, organik madde; kapsamlı paketlerde Ca, Mg, toplam N ve mikroelementler.

### C. Kullanıcının gireceği işletme verileri

Sensörden gelmez; AI için kritiktir:

- Ürün türü, çeşit, ekim/dikim tarihi, gelişim dönemi  
- Arazi büyüklüğü, sulama yöntemi, son sulama, süre  
- (İleri) gübre türü/miktarı, önceki ürün, toprak işleme, verim geçmişi  
- Gözlenen stres, drenaj, eğim, koordinat, numune derinliği  

Aynı nemde domates ile buğday farklı karar üretir; ürün ve dönem zorunludur.

### D. Dış sistemlerden alınacak veriler

- Hava durumu, yağış tahmini, güneşlenme, rüzgâr, buharlaşma  
- Arazi koordinatı  
- İleride: uydu indeksleri, sulama suyu kalitesi, bölgesel toprak haritaları (**MVP dışı**)

---

## 3. Laboratuvar raporu — “Toprak Analizi Ekle”

Ayrı bir bölüm olmalıdır. Kullanıcı üç yöntemden biriyle veri ekler:

| Yöntem | MVP | Açıklama |
|--------|-----|----------|
| Rapor yükleme | Evet (P1) | PDF, JPG, PNG, Excel, CSV |
| Manuel sonuç girişi | Evet (P1) | Rapor değerlerini forma yazar |
| Laboratuvar API | Hayır (P2) | Otomatik entegrasyon |

### 3.1. Rapor bilgileri

- Laboratuvar adı, rapor numarası  
- Analiz tarihi, numune alma tarihi  
- Arazi, numune bölgesi, numune derinliği  
- Koordinat (opsiyonel), akreditasyon (opsiyonel)  
- Rapor dosyası  

### 3.2. Temel analiz değerleri (MVP opsiyonel paketi)

- pH  
- EC veya toplam tuz  
- Organik madde  
- Kireç  
- Fosfor  
- Potasyum  
- Toprak bünyesi  
- Saturasyon / işba  

### 3.3. Gelişmiş değerler (P2)

N, Ca, Mg, Na, Fe, Zn, Mn, Cu, B, organik karbon, KDK  

### 3.4. Birim zorunluluğu

Yalnızca `fosfor: 12` kaydedilmez. Her parametre şöyle saklanır:

```text
Parametre: Yarayışlı fosfor
Değer: 12
Birim: mg/kg
Analiz metodu: Olsen
Analiz tarihi: 12.07.2026
Numune derinliği: 0–20 cm
```

Olası birimler: `%`, `ppm`, `mg/kg`, `kg/da`, `dS/m`, `meq/100 g`

---

## 4. Rapor otomatik okuma politikası

MVP yaklaşımı:

1. Kullanıcı raporu yükler.  
2. Sistem metin çıkarmayı **dener** (opsiyonel OCR / PDF text).  
3. Önerilen değerler forma yerleştirilir.  
4. Kullanıcı **tüm değerleri kontrol eder**.  
5. Kullanıcı onayından sonra kayıt yapılır.  

**Doğrudan otomatik kaydetme yasaktır.**

UI uyarısı:

> Belgeden çıkarılan değerleri kontrol edin.

Raporlar farklı tasarım, birim, parametre adı ve tarama kalitesinde olabilir.

---

## 5. Numune bağlamı

Laboratuvar sonucu tek başına yeterli değildir. Kayda bağlanmalıdır:

```text
Arazi
→ Yönetim bölgesi (MVP: sanal bölge adı)
→ Numune noktası / alan
→ Numune derinliği
```

Yanlış alınmış numunenin doğru laboratuvar sonucu bile tarla kararını bozar.

Türkiye rehberlerinde benzer özellikteki ~20 da alan için çok noktadan birleşik örnek ve ürün durumuna göre 0–20 / 20–40 cm derinlikleri vurgulanır.

---

## 6. Bölgesel temsil (tarla tek değer olmamalı)

Tarlanın tamamına tek pH/nem atamak stratejik hatadır.

MVP’de gerçek harita zorunlu değildir. Kullanıcı arazisini sanal bölgelere ayırabilir:

```text
Kuzey Bölgesi | Orta Bölge | Güney Bölgesi
```

Her bölgede nem, toprak türü, pH, EC, organik madde ve sulama ihtiyacı farklı olabilir. Harita/Leaflet **P2**.

---

## 7. Beş katmanlı veri mimarisi

| Katman | Örnek | Kaynak | Değişim sıklığı |
|--------|-------|--------|-----------------|
| 1 — Statik temel | Bünye, OM, kireç, P, K, Ca, Mg | Laboratuvar | Dönemsel |
| 2 — Dinamik sensör | Nem, sıcaklık, EC, debi, vana | IoT | Sık |
| 3 — Operasyon | Ekim, sulama, (ileride gübre/hasat) | Kullanıcı | Olay bazlı |
| 4 — Dış veri | Hava, yağış, buharlaşma | API / manuel | Günlük |
| 5 — Türetilmiş AI | Sulama ihtiyacı, risk, nem tahmini, güven, anomali, senaryo | Karar motoru | İstek üzerine |

---

## 8. AI kullanım kuralları

### A. Sulama analizi (MVP çekirdeği)

**Girdiler:** nem, bünye (varsa), hava sıcaklığı/nemi, yağış, ürün, dönem, son sulama, yöntem  
**Çıktı:** sulama gerekli mi, ne zaman, süre, risk, açıklama, güven  

### B. Laboratuvar yorumu (P1 — sınırlı)

**Girdiler:** pH, EC, OM, P, K, kireç, ürün  
**Çıktı:** düşük / yeterli / yüksek etiketleri, eksikler, uzman kontrolü gereken alanlar  

**Yasak (MVP):** doğrudan gübre reçetesi. Reçete için hedef verim, yöntem, bölgesel öneri, önceki gübreleme vb. gerekir → Faz 3+.

### C. Anomali

- Ani nem düşüşü / sabit sensör  
- Sulama sonrası nem artmama  
- IoT ile laboratuvar aşırı çelişkisi (P1)  

### D. Veri güven skoru (genişletilmiş hedef)

Örnek puanlama:

```text
Sensör verisi güncel: +25
Laboratuvar raporu son 12 ay içinde: +25
Numune derinliği mevcut: +15
Ürün bilgisi mevcut: +15
Son sulama bilgisi mevcut: +10
Eksik EC: -10
```

---

## 9. MVP’de hangi veriler?

### Zorunlu kullanıcı verisi

Arazi konumu, alan, toprak türü, ürün, gelişim dönemi, sulama yöntemi, son sulama  

### Zorunlu dinamik veri

Toprak nemi, hava sıcaklığı, hava nemi (mümkünse), yağış ihtimali  

### Opsiyonel laboratuvar (P1)

pH, EC, organik madde, fosfor, potasyum, kireç — **birimli** + kullanıcı onayı  

### İleri faz (P2+)

Mikroelementler, NPK optimizasyonu, toprak biyolojisi, uydu/drone  

---

## 10. Veri menüsü (hedef UI)

### Veri Kaynakları

1. **Manuel veri girişi** — ölçüm ve operasyon  
2. **IoT cihazları** — sensör ekle, durum, son veri, geçmiş  
3. **Laboratuvar analizleri** — rapor yükle, manuel sonuç, derinliği, bölge, birim, onay  
4. **Hava durumu** — konum, güncel, yağış (MVP: manuel/test)  
5. **Veri kalitesi** — eksikler, eski analizler, anomali, güven skoru  

---

## 11. Sistem akışı

```text
Çiftçi verileri
  + IoT sensör verileri
  + Laboratuvar raporları
  + Hava durumu
       ↓
Veri standardizasyonu (birim, tarih)
       ↓
Veri kalite skoru
       ↓
Yapay zekâ analizi
       ↓
Sulama önerisi + risk + senaryo
(+ opsiyonel lab yorum etiketleri)
```

---

## 12. Veri modeli taslağı (P1 uygulama için)

### ManagementZones (opsiyonel MVP)

- id, farm_id, name, notes  

### LabReports

- id, farm_id, zone_id (nullable)  
- lab_name, report_number  
- analysis_date, sample_date  
- sample_depth_cm, sample_region  
- file_path, file_type  
- source_type: `lab_report` | `lab_manual`  
- user_confirmed: bool  
- created_at  

### LabParameters

- id, report_id  
- parameter_code (ph, ec, om, p, k, lime, …)  
- value, unit, method  
- extracted_auto: bool  

`source_type` genişlemesi (API/UI etiketleri):

`manual | simulation | test_dataset | lab_report | lab_manual`

---

## 13. Önceliklendirme

| Öncelik | İş | Not |
|---------|-----|-----|
| **P0** | Mevcut sulama dilimi | Zaten çalışıyor |
| **P1** | Lab manuel giriş + rapor yükleme + birim + onay | IoT’yi tamamlar |
| **P1** | Güven skoruna “lab son 12 ay” puanı | |
| **P2** | OCR önerisi, lab API, mikroelementler, harita bölgeleri | |
| **Dışı** | Gübre reçetesi, uydu, drone, tam biyoloji | |

---

## 14. Net karar

> IoT, laboratuvar analizinin yerine geçmemeli; laboratuvar sonuçlarını zaman içinde güncellenen sensör verileriyle tamamlamalıdır.

**MVP doğru yapı:**

- Nem ve sıcaklık → IoT simülasyonu  
- Hava → manuel veya test  
- pH, EC, OM, P, K, kireç → rapor yükleme veya manuel lab girişi (P1)  
- Ürün ve sulama geçmişi → kullanıcı  
- Tahmin ve risk → kural tabanlı AI  

Referans dokümanlar: `prd.md`, `mvp.md`, `plan.md`, `Progress.md`, `AGENTS.md`
