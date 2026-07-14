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

- **Proje Aşaması:** Go-live sonrası — yerel + canlı MVP çalışır
- **Ürün Adı:** AgriTwin AI
- **MVP Durumu:** Uçtan uca demo (auth → farm → veri → AI → senaryo → onaylı sulama) + lab/zones/devices/materials/hub/admin/subscription
- **AI Durumu:** Kural motoru (güvenlik tabanı) + isteğe bağlı OpenRouter Türkçe açıklama; ML henüz yok
- **Canlı Uygulama:** Vercel + Render + Supabase — https://aidea-three.vercel.app / https://aidea-f8ji.onrender.com
- **UX:** AppShell + AdminShell, lucide, Recharts, Leaflet OSM, SourceBadge/ConfirmGate kalıpları
- **Ekim geçmişi:** Shipped on main (`058a205`) — sezon kaydı + kural tabanlı sonraki ürün önerisi (reçete değil)

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
- Arazi gübre/ilaç **sınıf** kataloğu + farm association (yorum bağlamı; reçete yok)
- Admin paneli, hub/KPI, abonelik plan seçimi (ödeme yok)
- Open-Meteo hava + Leaflet OSM haritalar
- Demo kullanıcıları + `SEED_DEMO_USERS` / `/auth/demo-login`

- Ürün sezon geçmişi + kural tabanlı sonraki ürün önerileri (rotasyon bağlamı; reçete değil)

### MVP dışı

- Gerçek uydu analizi
- Drone görüntü analizi
- Gerçek zamanlı pH kalibrasyonu
- Gübre **reçetesi** / doz optimizasyonu (malzeme kataloğu ≠ reçete)
- Hastalık tespiti
- Verim tahmini
- Tam otomatik sulama (onaysız)
- Gerçek tarla robotu
- Gerçek ödeme / faturalama
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
- [x] Ürün sezon geçmişi (CropHistory CRUD + UI)
- [x] Sonraki ürün önerileri (kural tabanlı rotasyon + isteğe bağlı LLM açıklama)

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
- [x] Dosya zorunlu `lab_report` yolu + metin/CSV heuristik çıkarım; simüle sahte analiz kaldırıldı
- [x] Toprak-lab kabul kapısı (fatura/alakasız PDF reddi; örnek `ai/datasets/sample_soil_lab_report.txt`)
- [x] OpenRouter lab ayrıştırma + onay sonrası anlatım (`OPENROUTER_API_KEY`; yoksa heuristik)
- [x] AI yorum yalnızca kullanıcı onayından sonra
- [x] Lab UI F22–F25 + kural tabanlı yorum (+ isteğe bağlı AI anlatım)
- [x] Field Node ingest API (`POST /iot/ingest`)
- [x] Çift derinlik nem alanları
- [x] Cihaz güncelleme/silme API (`PUT/DELETE /devices/detail/{id}`)

**Durum:** Lab/zone/device CRUD tamam; dosya zorunlu + toprak-gate + onay sonrası AI; alakasız dosyadan sahte analiz yok

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
- [x] Leaflet OSM arazi haritası (dashboard / twin / landing)
- [ ] Risk ısı haritası / poligon çizimi (ileri)

**Durum:** Backend + UI tamam; Leaflet OSM canlı; risk alanı ısı haritası yok

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

**Durum:** Backend + onay modalı UI + durum/geri sayım yüzeyi tamam

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

**Durum:** Dashboard + farm hub/overview KPI; ayrı “kurumsal rapor” ürünü yok

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

**Not:** Backend API/unit pytest çalışıyor; frontend otomasyon P1 (`TEST_PLAN.md` §5). Demo: `DEMO_CHECKLIST.md`. Canlı URL mevcut (aşağı Faz 10).

### Deploy notları

1. Frontend: Vercel — `frontend/` + `NEXT_PUBLIC_API_URL`
2. Backend: Render — `DATABASE_URL`, `SECRET_KEY`, CORS, `SEED_DEMO_USERS`, opsiyonel `OPENROUTER_API_KEY`
3. HTTPS platform varsayılanı; URL’ler bu dokümanda
4. Secret / cloud credential bu repoya yazılmaz
5. Tam plan: [`GO_LIVE_PLAN.md`](GO_LIVE_PLAN.md)

**Durum:** Canlı ortam çalışıyor; sertleştirme (Sentry, SMTP, backup politikası) açık

---

## Faz 10 — Canlıya Alma

- [x] Frontend deploy (Vercel — `aidea-three.vercel.app`)
- [x] Backend deploy (Render — `aidea-f8ji.onrender.com`)
- [x] Veritabanı prod bağlantısı (Supabase Postgres)
- [x] Ortam değişkenleri (CORS, secrets host’ta)
- [x] Demo kullanıcı hesabı (`DEMO_USERS.md` + `scripts.seed_demo`) — 4 persona; startup + `/auth/demo-login`
- [x] Landing hero + dashboard harita/grafik
- [x] HTTPS (platform)
- [ ] Hata logları (Sentry vb.)
- [x] Canlı URL
- [ ] Yedekleme politikası (ürün)
- [ ] Son jüri / sunum canlı testi

**Durum:** Prod stack canlı; demo seed ve OpenRouter opsiyonel. Sunum provası açık.

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
- [x] Dijital ikiz ekranı (Leaflet OSM + şematik twin)

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

- [x] Testler (backend pytest; frontend otomasyon açık)
- [x] Deploy (Vercel + Render canlı)
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

1. Demo / jüri provası (`DEMO_CHECKLIST.md` + Domates Serası)
2. ~~Prod deploy (Vercel + Render + Supabase)~~ — canlı
3. ~~Su tasarrufu / rapor derinliği~~ (hub + overview KPI)
4. ~~Recharts ile 72s nem grafiği~~
5. F11 legacy monolit içeriğini temizlemek (opsiyonel)

### P1 — Sonraki adım

1. ~~Laboratuvar analizi: manuel lab + birim + onay~~ (API + UI; dosya zorunlu path)
2. ~~Ekran haritası / UX specifikasyonu~~ (`ekran-haritasi.md` — as-built senkron)
3. ~~App shell + MVP-20 rota ayrıştırması~~ (`ekran-haritasi.md` §7)
4. Test veri seti seçici UI (6 senaryo picker)
5. ~~Arazi düzenleme/silme UI~~
6. ~~Çelişkili veri kontrolü (IoT vs lab)~~
7. Field Node Lite firmware / saha kalibrasyonu (`iot-mimarisi.md`)
8. shadcn/ui bileşenleri (opsiyonel)
9. Cihaz durumu ekranı (battery / signal from ingest)
10. ~~Profil / ayarlar UI (`PATCH /auth/me` hub)~~
11. ~~Leaflet OSM haritalar~~ (dashboard/twin/landing)
12. Frontend Playwright smoke (`TEST_PLAN.md` §5)
13. ~~Ekim geçmişi + crop suggestions~~

### P2 — Sonraki sürüm

1. ~~Admin panel A01–A08 (`/admin`, bootstrap)~~
2. Lab OCR (gerçek)
3. Gerçek sensör / MQTT
4. Gerçek ödemeler / SMTP
5. Risk ısı haritası / poligon
6. Gübre reçetesi (ayrı ürün kararı; MVP dışı)
7. ML (Scikit-learn / XGBoost) + SHAP

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
- [x] Canlı uygulama hazır (`aidea-three.vercel.app`)
- [ ] Yedek demo videosu hazır
- [ ] Sunum provası yapıldı

---

## 14. Genel İlerleme Özeti

### Tamamlanan

- Ürün dokümanları + Cursor rules
- Repo scaffold + dikey dilim (auth → sulama)
- Lab/zones/devices/datasets/ingest
- Recharts + Leaflet OSM + Open-Meteo
- OpenRouter hibrit açıklama (opsiyonel)
- Agro malzemeler (reçetesiz)
- Admin + hub + abonelik plan UI
- Canlı deploy (Vercel + Render + Supabase)
- 4 demo persona seed

### Devam eden

- Demo / sunum provası
- ~~Ekim geçmişi~~ (shipped; rotasyon önerisi)
- Prod sertleştirme (Sentry, SMTP, backup)

### Başlanmayan / açık

- ML model eğitimi
- Gerçek OCR
- Gerçek ödeme
- shadcn/ui tam kütüphane
- Frontend otomatik smoke suite

---

## 15. Genel Durum Değerlendirmesi

AgriTwin AI **yerel ve canlı** MVP dilimi çalışır: kayıt/demo-login, arazi, veri kaynakları, AI önerisi, senaryo, onaylı sanal sulama, lab, cihazlar, malzemeler, admin.

Kalan boşluklar: sunum provası, ML, gerçek OCR/ödeme, üretim sertleştirme. Leaflet/Recharts/Open-Meteo/deploy tamam. `TEST_PLAN.md` + pytest yeşil.

### 2026-07-14 — Agro malzeme kataloğu

- [x] `AgroMaterial` + `FarmMaterialUse` modelleri + seed katalog
- [x] API: `/agro-materials`, `/farms/{id}/materials`
- [x] Arazi oluştur/düzenle UI (açılır çoklu seçim)
- [x] AI `enrich_explanation` + öneri insight malzemeleri kullanır (doz reçetesi yok)
- [x] `FERTILIZER_PESTICIDE_CATALOG.md` kaynak özeti
- [x] Testler: `test_agro_materials.py`

### 2026-07-14 — Son kullanılan gübre / ilaç

- [x] Genişletilebilir dataset: `backend/ai/datasets/agro_materials.json` → DB seed
- [x] `FarmMaterialUse.is_last_fertilizer` / `is_last_pesticide` + `last_applied_at` (kategori başına tek son)
- [x] UI: create/edit + arazi detay + hub — çoklu seçim + son gübre/ilaç dropdown
- [x] AI summary'de SON GÜBRE / SON İLAÇ vurgusu (reçete yok, yalnızca bağlam)
- [x] Testler güncellendi

### 2026-07-14 — Ekim geçmişi (shipped)

- [x] `CropHistory` API + `CropHistoryPanel` (arazi detay)
- [x] Kural tabanlı `/farms/{id}/crop-suggestions` (rotasyon; reçete değil)
- [x] Demo seed sezon kayıtları

### 2026-07-14 — Doküman as-built senkronu

- Major docs (`canvas`, `mvp`, `prd`, `plan`, `designsystem`, `Progress`, `techstack`, `backend/README`, README/AGENTS/GO_LIVE/ekran-haritasi/DEMO_USERS) as-built’e çekildi.

