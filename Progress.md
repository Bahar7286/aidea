# AGRITWIN AI — PROGRESS / İLERLEME TAKİP DOKÜMANI

## 1. Doküman Amacı

Bu doküman, AgriTwin AI projesinin ürün, yazılım, yapay zekâ, veri, IoT simülasyonu, kullanıcı deneyimi ve sunum süreçlerindeki ilerlemeyi takip etmek için hazırlanmıştır.

Doküman düzenli olarak güncellenmelidir.

---

## 2. Proje Özeti

AgriTwin AI; çiftçinin manuel olarak girdiği arazi, ürün ve toprak verilerini, IoT/bulut sistemlerinden gelen veya prototipte simüle edilen sensör verilerini ve ekip tarafından hazırlanmış test veri setlerini tek platformda birleştiren yapay zekâ destekli tarım karar sistemidir.

MVP şu probleme odaklanmaktadır:

> Toprak nemi ve sulama davranışını dijital olarak temsil ederek sulama ihtiyacını, riskleri ve alternatif karar senaryolarını analiz etmek.

---

## 3. Genel Proje Durumu

- **Proje Aşaması:** Sprint 5 — backend end-user hazır (CRUD + dikey dilim)
- **Ürün Adı:** AgriTwin AI
- **MVP Durumu:** Yerel uçtan uca demo + P1 lab/bölge + test dataset load + `/iot/ingest`
- **Canlı Uygulama Durumu:** Prod deploy başlamadı
- **IoT Durumu:** Simülasyon + Field Node JSON ingest (`simulation` / `iot`); donanım henüz yok
- **AI Durumu:** Kural motoru + anomali kuralları; ML henüz yok
- **Veri Durumu:** 6 test senaryosu; lab raporları (manuel, birimli, onaylı); çift derinlik nem alanları
- **Dokümantasyon Durumu:** `veri-mimarisi.md` + `iot-mimarisi.md` kodla hizalanıyor

## 4. Tamamlanan Dokümanlar

- [x] İş geliştirme canvası
- [x] MVP dokümanı
- [x] PRD
- [x] Geliştirme planı
- [x] Veri kaynakları ayrımı
- [x] AI ve otomasyon görev ayrımı
- [x] Kullanıcı akışı
- [x] MVP kapsamı
- [x] Demo senaryosu
- [x] Teknik mimari önerisi
- [x] Veri tabanı şeması
- [x] Yol haritası
- [x] Cursor rules (`.cursor/rules/`) ve `AGENTS.md`
- [x] Doküman tutarlılık düzeltmeleri (dosya adları, P0, Recharts)
- [x] Veri mimarisi ve laboratuvar analizi dokümanı (`veri-mimarisi.md`)
- [x] IoT saha düğümü mimarisi (`iot-mimarisi.md`)
- [x] Ekran haritası ve UX/UI spesifikasyonu (`ekran-haritasi.md`)
- [x] Design system shell / SourceBadge / ConfirmGate güncellemesi

---

## 5. Mevcut Ürün Kapsamı

### MVP’ye dahil

- Kullanıcı kayıt ve giriş
- Arazi oluşturma
- Ürün bilgisi ekleme
- Manuel veri girişi
- IoT/bulut veri simülasyonu
- Hazır test veri seti
- Veri doğrulama
- Sulama ihtiyacı tahmini
- 24/48/72 saat nem tahmini
- Risk sınıflandırması
- Sensör anomalisi tespiti
- Açıklanabilir AI önerisi
- Senaryo simülasyonu
- Sanal sulama otomasyonu
- Dashboard
- Sulama geçmişi
- Tahmini su kullanımı ve tasarruf
- Laboratuvar analizi (P1 — rapor/manuel, birimli; gübre reçetesi yok)

### MVP dışı

- Gerçek uydu analizi
- Drone görüntü analizi
- Gerçek zamanlı pH kalibrasyonu
- Gübre optimizasyonu
- Hastalık tespiti
- Verim tahmini
- Tam otomatik sulama
- Gerçek tarla robotu
- Çoklu kooperatif paneli
- Gelişmiş kurumsal raporlama

---

## 6. Faz Bazlı İlerleme

## Faz 0 — Kapsam ve Strateji

- [x] Problem tanımı
- [x] Görünen ve gerçek problem ayrımı
- [x] MVP kapsamı
- [x] Hedef kullanıcı
- [x] Veri kaynakları
- [x] AI görevleri
- [x] Otomasyon görevleri
- [x] Demo senaryosu
- [ ] Ekip içi görev dağılımının kesinleştirilmesi
- [ ] Sprint takviminin kesinleştirilmesi

**Durum:** Büyük ölçüde tamamlandı

---

## Faz 1 — UX/UI ve Teknik Altyapı

- [x] Wireframe / ekran haritası (`ekran-haritasi.md` — 38 ekran; MVP-20 UX; as-built rota §7)
- [x] Design system app shell + SourceBadge/ConfirmGate kalıpları (`designsystem.md` §28A)
- [x] Auth onboarding UI (F01–F05: login, register, role, verify, forgot) + API
- [x] Arazi oluşturma ekranı
- [x] Veri kaynağı seçim ekranı (F17 — `/farms/[id]/data/sources`)
- [x] Manuel veri giriş ekranı
- [x] Dashboard tasarımı
- [x] App shell (sidebar + mobil alt nav) + arazi yönetimi UI (F07–F12)
- [x] Dijital ikiz / canlı sensör / geçmiş / manuel / veri kaynakları (F13–F17)
- [x] AI öneri kartı
- [x] Senaryo simülasyonu ekranı
- [x] IoT cihaz ekranı (F18–F21: liste, ekle, detay, kalibrasyon)
- [x] Sulama otomasyonu ekranı
- [x] F26–F30 AI/liste/detay, senaryo, sulama, rapor hub
- [x] Admin shell A01–A08 (`/admin`)
- [x] MVP-20 App Router ayrıştırması (çoğu rota ayrı; F11 hafif legacy kalabilir)
- [x] Frontend projesi kurulumu
- [x] Backend projesi kurulumu
- [x] Veritabanı bağlantısı

**Durum:** Ekran haritası as-built kod ile senkron (`ekran-haritasi.md` §7). Doküman güncellemesi; UI redesign yok.

---

## Faz 2 — Kullanıcı ve Arazi Yönetimi

- [x] Kullanıcı kayıt sistemi
- [x] Giriş sistemi
- [x] Çıkış sistemi
- [x] Rol yönetimi
- [x] Arazi oluşturma
- [x] Arazi listeleme
- [x] Arazi düzenleme (API + `/farms/[id]/edit` UI)
- [x] Arazi silme (soft-delete `is_active=false` + UI)
- [x] Ürün bilgisi ekleme
- [x] Gelişim dönemi seçme

**Durum:** Farm CRUD tamam (soft-delete + pasif filtre `include_inactive` + pasif arazi mutasyon 403). Zone/device/lab U/D + admin farm/device/ticket patch; auth `PATCH /me`. Sensör okuma geçmişi silinmez (bilinçli).

---

## Faz 3 — Veri Katmanı

### Manuel veri

- [x] Manuel veri giriş formu
- [x] Veri aralık kontrolü
- [x] Opsiyonel veri alanları
- [x] Veri kaynağı etiketi
- [x] Zaman damgası
- [x] Veri kaydı

### IoT simülasyonu

- [x] IoT cihaz ekleme ekranı (F18–F21)
- [x] Cihaz kimliği
- [x] API anahtarı alanı
- [x] Bağlantı testi
- [x] Kontrollü veri akışı
- [x] Son veri zamanı
- [x] Bağlantı durumu
- [ ] Veri kesintisi uyarısı

### Test veri seti

- [x] Normal durum senaryosu
- [x] Kuruma riski senaryosu
- [x] Aşırı sulama senaryosu
- [x] Sensör anomalisi senaryosu
- [x] Tuzluluk riski senaryosu
- [x] Sulama sonrası beklenmeyen durum senaryosu
- [x] Test veri yükleme ekranı (`GET /datasets` + `POST /datasets/load` → `source_type: test_dataset`; canlı sensör UI)

### Laboratuvar ve bölgeler (P1)

- [x] Yönetim bölgesi API + UI
- [x] Bölge güncelleme/silme API (`PUT/DELETE /zones/detail/{id}`)
- [x] Manuel lab girişi (birim + kullanıcı onayı)
- [x] Lab rapor listesi
- [x] Lab rapor güncelleme/silme API
- [x] PDF/Excel dosya yükleme (saklama; gerçek OCR yok)
- [x] Lab UI F22–F25 + simüle çıkarım + kural tabanlı yorum
- [x] Field Node ingest API (`POST /iot/ingest`)
- [x] Çift derinlik nem alanları
- [x] Cihaz güncelleme/silme API (`PUT/DELETE /devices/detail/{id}`)

**Durum:** Lab/zone/device CRUD tamam; çıkarım simüle (OCR iddiası yok)

---

## Faz 4 — Veri Doğrulama

### Veri Doğrulama

- [x] Eksik veri kontrolü
- [x] Gerçekçi aralık kontrolü
- [x] Eski veri kontrolü
- [x] Ani değişim kontrolü
- [x] Çelişkili veri kontrolü (IoT vs onaylı lab EC/pH; tamamlayıcı uyarı)
- [x] Veri güven skoru
- [x] Uyarı mesajları
- [x] Analize uygunluk kontrolü

**Durum:** Temel doğrulama aktif; anomali kuralları sonraki sprint

---

## Faz 5 — Yapay Zekâ ve Karar Motoru

### Kural tabanlı sistem

- [x] Sulama karar kuralları
- [x] Risk eşikleri
- [x] Güvenlik sınırları
- [x] Açıklama üretimi

### Makine öğrenmesi

- [x] Test veri seti hazırlama
- [ ] Özellik mühendisliği
- [ ] Eğitim/test ayrımı
- [ ] Random Forest modeli
- [ ] XGBoost modeli
- [ ] Regresyon modeli
- [ ] Model karşılaştırması
- [ ] Model API entegrasyonu

### Anomali tespiti

- [x] Ani nem değişimi
- [x] Sensör hatası
- [ ] Veri kesintisi
- [x] Sulama sonrası beklenmeyen sonuç

### Açıklanabilir AI

- [x] Karar gerekçesi
- [x] Güven skoru
- [ ] En etkili değişkenler
- [x] Düşük güven uyarısı

**Durum:** Kural motoru canlı; ML sonraki sprint

---

## Faz 6 — Dijital İkiz ve Senaryo Simülasyonu

- [x] Mevcut durum modeli
- [x] Geçmiş veri grafiği (Recharts F15 + 72s dönem)
- [x] 24 saatlik tahmin
- [x] 48 saatlik tahmin
- [x] 72 saatlik tahmin
- [ ] Tarla bölge görünümü
- [ ] Risk alanı gösterimi
- [x] Şimdi sulama senaryosu
- [x] 12 saat sonra sulama
- [x] 24 saat sonra sulama
- [x] Sulama yapmama
- [x] Süre artırma/azaltma
- [x] Senaryo karşılaştırma tablosu

**Durum:** Backend + farm detay UI tamamlandı; harita/grafik yok

---

## Faz 7 — Sanal Sulama Otomasyonu

- [x] Sulamayı başlat
- [x] Sulamayı durdur
- [x] Sanal vana
- [x] Pompa durumu
- [x] Geri sayım
- [x] Sulama süresi
- [x] Su miktarı
- [x] Olay kaydı
- [x] Sulama sonrası nem güncelleme
- [x] AI yeniden analiz

**Durum:** Backend + onay modalı UI tamamlandı; pompa/geri sayım yok

---

## Faz 8 — Dashboard ve Raporlama

- [x] Ana dashboard
- [x] Mevcut nem kartı
- [x] Risk kartı
- [x] AI önerisi
- [x] Veri kaynağı bilgisi
- [x] Güven skoru
- [ ] Son güncelleme (kısmi)
- [x] Sensör durumu (cihaz listesi / detay F18–F20)
- [x] 72 saatlik tahmin (Recharts grafik + metin)
- [x] Sulama geçmişi
- [x] Su kullanımı raporu (hub + overview KPI)
- [x] Tahmini tasarruf (kural tabanlı takvim baseline)
- [x] Anomali kayıtları

**Durum:** Temel kartlar farm/dashboard üzerinde; rapor ekranı yok

---

## Faz 9 — Test ve Kalite Güvence

- [x] Fonksiyonel testler (plan: `TEST_PLAN.md`; pytest yeşil)
- [x] Kullanıcı kayıt testi
- [ ] Arazi oluşturma testi
- [ ] Veri giriş testi
- [ ] IoT simülasyon testi
- [ ] AI tahmin testi
- [ ] Senaryo testi
- [ ] Otomasyon testi
- [ ] Hatalı veri testi
- [ ] Eksik veri testi
- [ ] UX testi
- [ ] Performans testi
- [ ] Mobil görünüm testi

**Not:** Backend API/unit pytest çalışıyor; frontend otomasyon P1 (`TEST_PLAN.md` §5). Deploy/HTTPS canlı URL kullanıcı hesabı bekliyor. Demo provası: `DEMO_CHECKLIST.md`.

### Deploy notları (kullanıcı hesabı gerekir)

1. Frontend: Vercel — `frontend/` + `NEXT_PUBLIC_API_URL`
2. Backend: Render/Railway/Fly — `DATABASE_URL`, `SECRET_KEY`, CORS
3. HTTPS ve canlı URL deploy sonrası `Progress.md` işaretlenir
4. Secret / cloud credential bu repoya yazılmaz
5. Tam plan: [`GO_LIVE_PLAN.md`](GO_LIVE_PLAN.md)

**Durum:** Başlanmadı (plan dokümanı hazır; prod deploy bekliyor)

---

## Faz 10 — Canlıya Alma

- [ ] Frontend deploy
- [ ] Backend deploy
- [ ] Veritabanı prod bağlantısı
- [ ] Ortam değişkenleri
- [x] Demo kullanıcı hesabı (`DEMO_USERS.md` + `scripts.seed_demo`)
- [ ] HTTPS
- [ ] Hata logları
- [ ] Canlı URL
- [ ] Yedekleme
- [ ] Son canlı test

**Durum:** Başlanmadı

---

## Faz 11 — Sunum ve Demo

- [ ] Problem anlatımı
- [ ] Gerçek problem
- [ ] Çözüm
- [ ] AI rolü
- [ ] Veri kaynakları
- [ ] Dijital ikiz açıklaması
- [ ] Canlı demo akışı
- [ ] İş modeli
- [ ] Etki
- [ ] Yol haritası
- [ ] Sunum provası
- [ ] Zaman kontrolü
- [ ] Yedek demo videosu

**Durum:** İçerik altyapısı hazır, sunum hazırlanmadı

---

## 7. Sprint Bazlı Durum

## Sprint 1 — Altyapı ve Tasarım

### Hedefler

- Proje kurulumu
- Veritabanı
- Kullanıcı akışı
- Temel ekranlar

### Durum

- [x] Kapsam belirlendi
- [x] Veri modeli taslağı hazır
- [x] Wireframe / ekran haritası (`ekran-haritasi.md`)
- [x] Frontend kurulumu
- [x] Backend kurulumu
- [x] Veritabanı kurulumu

---

## Sprint 2 — Veri Katmanı

### Hedefler

- Manuel veri girişi
- IoT simülasyonu
- Test senaryoları
- Veri doğrulama

### Durum

- [x] Veri türleri belirlendi
- [x] Veri kaynakları ayrıştırıldı
- [x] Manuel veri formu
- [x] IoT simülasyonu
- [x] Test veri seti
- [x] Veri güven skoru

---

## Sprint 3 — AI Katmanı

### Hedefler

- Sulama tahmini
- Risk sınıflandırması
- Nem tahmini
- Açıklanabilir öneri

### Durum

- [x] AI görevleri tanımlandı
- [x] Model seçenekleri belirlendi
- [x] Kural tabanlı motor
- [ ] ML modeli
- [x] Anomali tespiti
- [x] Açıklama motoru

---

## Sprint 4 — Dijital İkiz ve Simülasyon

### Hedefler

- 72 saatlik tahmin
- Senaryo karşılaştırması
- Görsel dijital ikiz ekranı

### Durum

- [x] Senaryolar tanımlandı
- [x] Tahmin grafikleri (Recharts)
- [x] Senaryo motoru
- [x] Dijital ikiz ekranı (şematik; Leaflet P2)

---

## Sprint 5 — Otomasyon ve Raporlama

### Hedefler

- Sanal sulama
- Sulama geçmişi
- Su kullanımı
- Tasarruf raporu

### Durum

- [x] Otomasyon akışı tanımlandı
- [x] Sanal vana
- [x] Olay kaydı
- [x] Rapor ekranı (F30 hub + su kullanım/tasarruf)

---

## Sprint 6 — Test ve Canlıya Alma

### Hedefler

- Hata düzeltme
- Canlıya alma
- Demo hazırlığı

### Durum

- [ ] Testler
- [ ] Deploy
- [x] Demo hesabı (4 persona, ortak şifre Secret12)
- [ ] Sunum provası

---

## 8. Mevcut Engeller

### 1. Gerçek saha verisinin olmaması

**Etkisi:** Model gerçek koşullarda doğrulanamaz.

**Geçici çözüm:** Ekip tarafından hazırlanmış kontrollü test veri seti kullanılacak.

### 2. Gerçek IoT cihazının olmaması

**Etkisi:** Donanım entegrasyonu gösterilemez.

**Geçici çözüm:** IoT/bulut veri akışı simülasyonu kullanılacak.

### 3. Ekip teknik kapasitesinin net olmaması

**Etkisi:** Görev dağılımı ve teknoloji seçimi gecikebilir.

**Çözüm:** Her ekip üyesinin teknik becerileri çıkarılmalı.

### 4. Kapsam büyümesi riski

**Etkisi:** MVP tamamlanamayabilir.

**Çözüm:** P0 dışı özellikler ertelenmeli.

---

## 9. Kritik Riskler

| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Kapsam büyümesi | Yüksek | Yüksek | MVP dışı özellikleri dondurmak |
| AI modelinin zayıf olması | Orta | Yüksek | Hibrit kural + ML kullanmak |
| IoT simülasyonunun yanlış anlaşılması | Orta | Orta | Simülasyon etiketi kullanmak |
| Demo sırasında hata | Orta | Yüksek | Kontrollü demo verisi ve yedek video |
| UX’in karmaşık olması | Orta | Orta | Basit ekran ve kullanıcı testi |
| Veri güvenilirliği | Yüksek | Yüksek | Veri doğrulama ve güven skoru |

---

## 10. Öncelikli Sonraki Adımlar

### P0 — Hemen yapılmalı

1. Demo provası (`DEMO_CHECKLIST.md` + Domates Serası) — canlı kayıt kullanıcıda
2. Prod deploy (Vercel + backend) — **cloud hesabı / secret gerekir** → [`GO_LIVE_PLAN.md`](GO_LIVE_PLAN.md)
3. ~~Su tasarrufu / rapor derinliği~~ (hub + overview KPI)
4. ~~Recharts ile 72s nem grafiği~~
5. F11 legacy monolit içeriğini temizlemek (opsiyonel)

### P1 — Sonraki adım

1. ~~Laboratuvar analizi: manuel lab + birim + onay~~ (API + UI)
2. ~~Ekran haritası / UX specifikasyonu~~ (`ekran-haritasi.md` — as-built senkron)
3. ~~App shell + MVP-20 rota ayrıştırması~~ (`ekran-haritasi.md` §7)
4. Test veri seti seçici UI (6 senaryo picker)
5. ~~Arazi düzenleme/silme UI~~ (API + `/farms/[id]/edit` + soft-delete)
6. ~~Çelişkili veri kontrolü (IoT vs lab)~~
7. Field Node Lite firmware / saha kalibrasyonu (`iot-mimarisi.md`)
8. shadcn/ui bileşenleri
9. Cihaz durumu ekranı (battery / signal from ingest)
10. ~~Profil / ayarlar UI (`PATCH /auth/me` hub)~~
11. F13 şematik dijital ikiz viz (Leaflet P2)
12. Frontend Playwright smoke (`TEST_PLAN.md` §5)

### P2 — Sonraki sürüm

1. ~~Admin panel A01–A08 (`/admin`, bootstrap)~~
2. Lab OCR (gerçek)
3. Gerçek sensör / hava API
4. MQTT
5. Dijital ikiz haritası (Leaflet)
6. Gübre reçetesi (ayrı ürün kararı; MVP dışı)

---

## 11. Haftalık İlerleme Raporu Şablonu

### Hafta

- Tarih:
- Sprint:
- Sorumlu:

### Bu hafta tamamlananlar

- 
- 
- 

### Devam eden işler

- 
- 
- 

### Engeller

- 
- 
- 

### Alınan kararlar

- 
- 
- 

### Gelecek hafta hedefleri

- 
- 
- 

### Risk durumu

- Düşük
- Orta
- Yüksek

---

## 12. Günlük Stand-up Şablonu

### Dün ne yaptım?

- 

### Bugün ne yapacağım?

- 

### Engelim var mı?

- 

### Yardım gereken konu

- 

---

## 13. Demo Hazırlık Durumu

- [x] Demo senaryosu yazıldı
- [x] Kullanıcı akışı tanımlandı
- [x] AI çıktıları tanımlandı
- [x] Otomasyon akışı tanımlandı
- [x] Demo verisi hazırlandı (Domates Serası + sensör/AI seed)
- [x] Demo hesabı oluşturuldu (`python -m scripts.seed_demo`)
- [ ] Canlı uygulama hazır
- [ ] Yedek demo videosu hazır
- [ ] Sunum provası yapıldı

---

## 14. Genel İlerleme Özeti

### Tamamlanan

- Ürün fikri
- Problem tanımı
- MVP kapsamı
- PRD
- Canvas
- Geliştirme planı
- Veri yapısı
- AI görevleri
- IoT simülasyon yaklaşımı
- Demo akışı
- Cursor rules ve AGENTS.md
- Repo scaffold (frontend/backend/ai/iot)
- Supabase SQL şeması
- Kayıt / giriş / arazi / manuel veri / kural tabanlı öneri dikey dilimi
- 6 test senaryosu dataset

### Devam eden

- Prod deploy / canlı ortam (kullanıcı credentials)
- Demo / sunum provası (`DEMO_CHECKLIST.md`)

### Başlanmayan

- ML model eğitimi
- Gerçek OCR / Leaflet harita
- shadcn/ui bileşen kütüphanesi
- Frontend otomatik smoke suite

---

## 15. Genel Durum Değerlendirmesi

AgriTwin AI yerel MVP dilimi çalışır durumda: kayıt, arazi, veri, AI önerisi, senaryo karşılaştırması, onaylı sanal sulama ve anomali uyarıları.

Kalan boşluklar: canlı URL (deploy hesabı), ML modeli, sunum provası. Recharts 72s grafik, su tasarrufu KPI/rapor, profil ayarları, IoT–lab çelişki uyarısı ve sulama geri sayımı tamam. `TEST_PLAN.md` as-built test planı hazır; backend pytest yeşil.

