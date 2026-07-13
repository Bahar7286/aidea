# TOPRAK DİJİTAL İKİZİ PROJE ANALİZİ

> **Kapsam notu (önemli):** Bu dosya erken stratejik analizdir ve uydu, gübreleme, tam dijital ikiz gibi uzun vadeli fikirler içerir. **AgriTwin MVP’de uygulanacak kapsam değildir.** Güncel bağlayıcı kaynaklar: `mvp.md`, `prd.md`, `veri-mimarisi.md`, `plan.md`, `Progress.md`, `AGENTS.md`. Laboratuvar verisi P1’de IoT’yi tamamlar; gübre reçetesi MVP dışıdır.

1. Fikrin Kısa Tanımı
Toprak Dijital İkizi, tarım arazisinden alınan sensör verileri, hava durumu bilgileri, laboratuvar analizleri ve uydu görüntülerini bir araya getirerek toprağın dijital ortamda sürekli güncellenen bir modelini oluşturan yapay zekâ destekli tarım sistemidir.
Sistem yalnızca toprağın mevcut durumunu göstermez. Aynı zamanda:
•	Toprak nemini takip eder.
•	Sulama ihtiyacını tahmin eder.
•	Tuzlanma ve verim kaybı riskini analiz eder.
•	Farklı bölgelerdeki toprak değişimlerini haritalar.
•	Sulama veya gübreleme kararlarının olası sonuçlarını önceden simüle eder.
•	Gerekli durumlarda sulama sistemini otomatik çalıştırır.
Projenin temel amacı, çiftçinin kararlarını yalnızca deneyime ve genel tahminlere bırakmak yerine gerçek verilerle desteklemektir.
________________________________________
2. Görünen Problem
İlk bakışta görünen problem şudur:
Çiftçiler, toprağın nem, sıcaklık, pH, tuzluluk ve besin durumunu anlık olarak takip edememektedir.
Bu nedenle sulama ve gübreleme kararları çoğu zaman:
•	Gözleme,
•	Genel hava tahminlerine,
•	Geçmiş deneyimlere,
•	Belirli aralıklarla yapılan laboratuvar analizlerine
dayanmaktadır.
Bunun sonucunda:
•	Gereğinden fazla sulama yapılabilir.
•	Gübre yanlış miktarda kullanılabilir.
•	Toprak sorunları geç fark edilebilir.
•	Üretim maliyetleri artabilir.
•	Su ve enerji israfı oluşabilir.
Ancak bu tanım, problemin yalnızca görünen kısmıdır.
________________________________________
3. Gerçek Problem
Asıl problem yalnızca çiftçinin toprak verisini görememesi değildir.
Gerçek problem şudur:
Tarımsal kararların, toprağın sürekli değişen yapısını temsil eden bütünleşik ve güvenilir bir modele dayanmaması nedeniyle çiftçi, sulama ve gübreleme kararlarının gelecekteki sonuçlarını önceden görememektedir.
Bir çiftçinin nem sensörü kullanması, problemi tamamen çözmez. Çünkü nem verisi yalnızca o andaki durumu gösterir.
Gerçek karar için şu bilgilerin birlikte değerlendirilmesi gerekir:
•	Toprak nemi
•	Toprak sıcaklığı
•	Hava tahmini
•	Yağış ihtimali
•	Bitki türü
•	Bitkinin gelişim dönemi
•	Toprak yapısı
•	Buharlaşma oranı
•	Önceki sulama miktarı
•	Tarla içindeki bölgesel farklılıklar
Dolayısıyla gerçek problem veri eksikliğinden daha büyüktür.
Gerçek problem üç katmandan oluşmaktadır
3.1. Karar problemi
Çiftçi, “Sulama yapmalı mıyım?” sorusuna cevap vermektedir ancak şu soruların cevabını bilmemektedir:
•	Ne kadar sulama yapılmalı?
•	Hangi bölge sulanmalı?
•	Sulama ertelenirse ne olur?
•	Yağış gerçekleşirse yapılan sulama boşa gider mi?
•	Fazla sulama toprağın tuzluluğunu artırır mı?
3.2. Veri bütünlüğü problemi
Toprak verileri farklı kaynaklarda dağınıktır.
Örneğin:
•	Sensör verisi ayrı sistemdedir.
•	Laboratuvar sonucu ayrı belgededir.
•	Hava tahmini farklı bir uygulamadadır.
•	Uydu verisi başka bir platformdadır.
Bu veriler tek karar sisteminde birleşmediği için çiftçinin elinde veri bulunmasına rağmen anlamlı içgörü oluşmamaktadır.
3.3. Uzun vadeli toprak sağlığı problemi
Yanlış sulama ve gübreleme kısa vadede ürün verebilir ancak uzun vadede:
•	Tuzlanmaya,
•	Toprak sıkışmasına,
•	Organik madde kaybına,
•	Verim düşüşüne,
•	Yer altı suyu kirliliğine
neden olabilir.
Bu nedenle gerçek problem yalnızca “bu yıl verim almak” değil, toprağın gelecek yıllarda da üretken kalmasını sağlamaktır.
________________________________________
4. Problem Bir Semptom mu, Ana Problem mi?
“Toprak verilerinin anlık olarak görülememesi” bir semptomdur.
Asıl problem şudur:
Çiftçinin, toprağın mevcut ve gelecekteki durumuna ilişkin güvenilir bir karar destek sistemine sahip olmaması.
Toprak Dijital İkizi fikri bu nedenle yalnızca veri gösteren bir panel olmamalıdır.
Sistem:
•	Veriyi toplamalı,
•	Veriyi yorumlamalı,
•	Geleceği tahmin etmeli,
•	Alternatif kararları simüle etmeli,
•	Uygulanabilir öneri sunmalı,
•	Gerekirse otomasyonu çalıştırmalıdır.
Bunlar yapılmadığında proje, dijital ikiz değil, yalnızca sensör takip sistemi olur.
________________________________________
5. Proje Geliştiriliyor Olsaydı Şu Anda Ne Yapılmalıydı?
Projeyi geliştiriyor olsaydık ilk yapılması gereken, bütün tarım problemlerini aynı anda çözmeye çalışmak olmazdı.
İlk karar şu olmalıdır:
Toprak Dijital İkizi hangi tek ve ölçülebilir problemi ilk aşamada çözecek?
En mantıklı başlangıç problemi:
Toprak nemi ve hava tahmini verilerini kullanarak doğru sulama zamanının ve miktarının belirlenmesi.
Bu seçim yapılmalıdır çünkü:
•	Sensör verisi üretilebilir.
•	Prototip kurulabilir.
•	Sonuç ölçülebilir.
•	Otomasyon gösterilebilir.
•	Yapay zekâ modeli geliştirilebilir.
•	Su tasarrufu karşılaştırılabilir.
•	Jüriye çalışan demo sunulabilir.
İlk aşamada pH, tuzluluk, gübreleme, uydu, drone, verim tahmini ve hastalık analizi birlikte yapılmaya çalışılırsa proje genişler ancak çalışmaz.
Hackathonda geniş fikir değil, çalışan dar çözüm daha değerlidir.
________________________________________
6. Alternatif Karar Seçenekleri
Projenin geliştirilmesi için dört temel alternatif bulunmaktadır.
________________________________________
Alternatif 1: Sadece Sensör Verisi Gösteren İzleme Sistemi
Tanım
Toprak nemi ve sıcaklık değerleri sensörlerden alınır ve mobil veya web panelinde gösterilir.
Olası sonuçlar
•	Hızlı geliştirilebilir.
•	Düşük maliyetlidir.
•	Çalışan demo sunulabilir.
•	Ancak karar desteği zayıf kalır.
•	Yapay zekâ kullanımı sınırlı olur.
•	Dijital ikiz iddiasını karşılamaz.
Kime fayda sağlar?
•	Temel ölçüm ihtiyacı olan çiftçilere
•	Küçük üreticilere
•	Eğitim amaçlı prototiplere
Kime zarar veya dezavantaj getirir?
Doğrudan zarar oluşturmaz ancak kullanıcı yalnızca veriyi görür ve yine kararı kendisi vermek zorunda kalır.
Çevre kültürüne etkisi
Olumludur ancak sınırlıdır. Farkındalık yaratır fakat otomatik kaynak tasarrufu garanti etmez.
________________________________________
Alternatif 2: Eşik Değerine Göre Otomatik Sulama Sistemi
Tanım
Toprak nemi belirli bir seviyenin altına düştüğünde sulama otomatik başlar.
Olası sonuçlar
•	Basit otomasyon sağlanır.
•	Çiftçinin manuel müdahalesi azalır.
•	Gereksiz sulama kısmen önlenebilir.
•	Ancak yağış tahmini dikkate alınmaz.
•	Bitki türü ve gelişim dönemi hesaba katılmaz.
•	Sabit eşik her koşulda doğru sonuç vermez.
Kime fayda sağlar?
•	Küçük sera üreticilerine
•	Bahçe ve düşük ölçekli tarım uygulamalarına
Kime zarar veya dezavantaj getirir?
Yanlış sensör verisi veya hatalı eşik, fazla ya da yetersiz sulamaya neden olabilir.
Çevre kültürüne etkisi
Su tasarrufuna katkı sağlar. Ancak sistem yalnızca otomatik çalıştığı için kullanıcıya neden-sonuç ilişkisini öğretmeyebilir.
________________________________________
Alternatif 3: Yapay Zekâ Destekli Sulama Karar Sistemi
Tanım
Sistem, toprak nemi, hava tahmini, yağış olasılığı, sıcaklık, ürün türü ve önceki sulama verilerini analiz ederek sulama önerisi oluşturur.
Olası sonuçlar
•	Daha doğru karar verilebilir.
•	Gereksiz sulama azaltılabilir.
•	Sistem zamanla öğrenebilir.
•	Çiftçiye açıklanabilir öneriler sunulabilir.
•	Yapay zekâ kullanımı somut biçimde gösterilebilir.
•	Prototip kapsamı yönetilebilir kalır.
Kime fayda sağlar?
•	Çiftçilere
•	Sera üreticilerine
•	Tarım işletmelerine
•	Sulama birliklerine
•	Su kaynaklarını yöneten kurumlara
Kime zarar veya dezavantaj getirir?
Yanlış model veya eksik veri, hatalı öneri üretebilir. Bu nedenle sistem ilk aşamada tam otomatik değil, kullanıcı onaylı çalışmalıdır.
Çevre kültürüne etkisi
Güçlüdür. Su tüketimini ölçülebilir hâle getirir ve çiftçiye gereksiz sulamanın çevresel etkisini gösterir.
________________________________________
Alternatif 4: Tam Kapsamlı Toprak Dijital İkizi
Tanım
Sistem:
•	Nem,
•	pH,
•	Tuzluluk,
•	Besin değerleri,
•	Uydu verileri,
•	Drone görüntüleri,
•	Verim tahmini,
•	Gübreleme,
•	Sulama,
•	Toprak sağlığı
gibi bütün bileşenleri tek platformda birleştirir.
Olası sonuçlar
•	Uzun vadede güçlü bir ürün ortaya çıkar.
•	Büyük tarım işletmeleri için değerli olabilir.
•	Ancak hackathon süresinde tamamlanması gerçekçi değildir.
•	Veri ihtiyacı çok yüksektir.
•	Sensör ve entegrasyon maliyeti artar.
•	Demo yüzeysel kalabilir.
Kime fayda sağlar?
•	Büyük tarım işletmelerine
•	Kooperatiflere
•	Kamu kurumlarına
•	Tarım danışmanlarına
Kime zarar veya dezavantaj getirir?
Küçük çiftçiler için pahalı ve karmaşık olabilir. Proje ekibi açısından ise kaynakların dağılmasına ve çalışan demo çıkarılamamasına neden olabilir.
Çevre kültürüne etkisi
Potansiyel olarak çok yüksektir. Ancak yalnızca sistem gerçekten çalışır ve çiftçi tarafından kullanılırsa anlamlıdır.
________________________________________
7. Alternatiflerin Karşılaştırılması
Alternatif	Yapılabilirlik	Yapay zekâ kullanımı	Yenilikçilik	Çalışan demo	Çevresel etki
Sensör takip sistemi	Çok yüksek	Düşük	Düşük	Çok yüksek	Orta
Eşik tabanlı sulama	Yüksek	Çok düşük	Orta	Yüksek	Orta
AI destekli sulama kararı	Yüksek	Yüksek	Yüksek	Yüksek	Yüksek
Tam dijital ikiz	Düşük	Çok yüksek	Çok yüksek	Düşük	Çok yüksek
________________________________________
8. Zorunlu Karar
Alınacak karar
İlk aşamada tam kapsamlı bir toprak dijital ikizi geliştirmek yerine, yapay zekâ destekli sulama kararına odaklanan sınırlı bir dijital ikiz MVP’si geliştirilmelidir.
Bu sistem:
•	Toprak nemini ölçmeli,
•	Hava tahminini takip etmeli,
•	Ürün türünü dikkate almalı,
•	Sulama ihtiyacını tahmin etmeli,
•	Kullanıcıya gerekçeli öneri sunmalı,
•	Kullanıcı onayıyla sulama sistemini çalıştırmalıdır.
________________________________________
Bu kararın gerekçesi
Bu kararın alınmasının temel nedenleri şunlardır:
1. Problem ölçülebilirdir
Su tüketimi, sulama sıklığı ve toprak nemi sayısal olarak ölçülebilir.
2. Çalışan prototip üretilebilir
ESP32, nem sensörü, röle ve su pompası kullanılarak fiziksel demo yapılabilir.
3. Yapay zekâ gerçekten kullanılabilir
Sistem yalnızca eşik değerine göre değil; geçmiş veri, hava tahmini ve ürün ihtiyacına göre tahmin yapabilir.
4. Çevresel etki somuttur
Su tasarrufu litre veya yüzde olarak gösterilebilir.
5. Proje ölçeklenebilir
İlk aşamada sulama çözüldükten sonra:
•	Tuzluluk,
•	Gübreleme,
•	Toprak sağlığı,
•	Uydu görüntüsü,
•	Verim tahmini
eklenebilir.
________________________________________
Kararın doğuracağı sonuçlar
Olumlu sonuçlar
•	Proje kapsamı kontrol altında tutulur.
•	Çalışan prototip çıkarılabilir.
•	Jüriye net değer önerisi sunulur.
•	Yapay zekâ kullanımı gösterilebilir.
•	Çevresel etki ölçülebilir.
•	Ekip görevleri daha kolay paylaşılabilir.
Olumsuz sonuçlar
•	Sistem ilk aşamada tam dijital ikiz olmayacaktır.
•	Toprağın tüm kimyasal ve biyolojik özellikleri analiz edilemeyecektir.
•	Proje iddiası sınırlı tutulmalıdır.
•	Uzun dönem saha verisi olmadığı için tahmin modeli başlangıçta zayıf olabilir.
Bu olumsuzluk kabul edilmelidir. Hackathonda eksik ama çalışan sistem, kapsamlı ama göstermelik projeden daha değerlidir.
________________________________________
9. Stratejik Körlüklerin Tespiti
9.1. Sensör koymanın dijital ikiz olduğunu düşünmek
En büyük stratejik hata budur.
Sensörden veri almak yalnızca dijital izleme sağlar.
Dijital ikiz için sistem:
•	Gerçek sistemle sürekli veri alışverişi yapmalı,
•	Geleceği tahmin etmeli,
•	Senaryoları simüle etmeli,
•	Gerçek sonuçlarla modelini güncellemelidir.
________________________________________
9.2. Yapay zekâyı gereksiz yere kullanmak
Nem seviyesi yüzde 30’un altına düştüğünde pompayı açmak yapay zekâ değildir.
Bu basit otomasyondur.
Yapay zekâ ancak şu durumda anlamlıdır:
•	Geçmiş sulama davranışını öğrenirse,
•	Yağış ihtimalini hesaba katarsa,
•	Ürün türüne göre farklı karar verirse,
•	Nem düşüşünü önceden tahmin ederse,
•	Sulama miktarını optimize ederse.
________________________________________
9.3. Çiftçinin teknoloji kullanmak isteyeceğini varsaymak
Teknik açıdan iyi bir sistem, kullanıcı benimsemezse başarısız olur.
Çiftçi şu soruları sorabilir:
•	Bu sistem bana ne kadar para kazandıracak?
•	Sensör bozulursa ne olacak?
•	İnternet yoksa çalışacak mı?
•	Öneri yanlış çıkarsa zararı kim karşılayacak?
•	Sistemin kullanımı zor mu?
Bu nedenle proje yalnızca teknolojiye değil, güven ve kullanım kolaylığına da odaklanmalıdır.
________________________________________
9.4. Her toprağın aynı davrandığını varsaymak
Toprak türleri birbirinden farklıdır.
•	Kumlu toprak
•	Killi toprak
•	Tınlı toprak
•	Tuzlu toprak
aynı nem seviyesinde farklı davranabilir.
Bu nedenle tek bir genel model her bölgede doğru çalışmayabilir.
Modelin bölgesel ve ürün bazlı özelleştirilmesi gerekir.
________________________________________
9.5. Sensör verisini tamamen doğru kabul etmek
Düşük maliyetli toprak sensörleri:
•	Zamanla bozulabilir.
•	Tuzluluktan etkilenebilir.
•	Yanlış yerleştirilebilir.
•	Hatalı veri üretebilir.
Sistem sensör arızasını tespit etmeli ve kullanıcıya güven skoru göstermelidir.
________________________________________
9.6. Küçük çiftçi için maliyeti göz ardı etmek
Çok fazla sensör, drone ve gelişmiş cihaz kullanılırsa proje teknik olarak iyi, ekonomik olarak anlamsız olabilir.
Bu nedenle ilk ürün:
•	Düşük maliyetli,
•	Modüler,
•	Kiralanabilir,
•	Kooperatif üzerinden paylaşılabilir
olmalıdır.
________________________________________
9.7. Tam otomasyonu erken aşamada kullanmak
Yanlış bir model doğrudan sulamayı kontrol ederse ürün zarar görebilir.
Bu nedenle ilk aşamada:
Sistem öneri üretir, çiftçi onaylar, ardından otomasyon çalışır.
İlerleyen aşamalarda güvenilirlik kanıtlanırsa tam otomasyona geçilebilir.
________________________________________
9.8. Gerçek problem yerine teknolojiye âşık olmak
Projenin amacı dijital ikiz yapmak değildir.
Projenin amacı:
•	Su israfını azaltmak,
•	Yanlış sulamayı önlemek,
•	Toprak sağlığını korumak,
•	Çiftçinin karar kalitesini artırmaktır.
Dijital ikiz yalnızca bu amaçlara ulaşmak için kullanılan araçtır.
________________________________________
10. Çevre Kültürüne Etkisi
Proje yalnızca çiftçiye ekonomik kazanç sağlamamalı, çevresel davranış biçimini de değiştirmelidir.
Sistem kullanıcıya şunları göstermelidir:
•	Ne kadar su kullanıldığı
•	Ne kadar su tasarruf edildiği
•	Gereksiz sulamanın kaç kez önlendiği
•	Kullanılan enerjinin ne kadar azaldığı
•	Toprak sağlığının nasıl değiştiği
•	Sulamanın çevresel etkisi
Bu sayede çiftçi yalnızca “daha az maliyet” değil, “daha sürdürülebilir üretim” düşüncesiyle hareket eder.
Ancak çevre kültürü yalnızca kullanıcıya yeşil rozet vermekle oluşmaz.
Gerçek davranış değişikliği için sistem:
•	Sonuçları ölçmeli,
•	Tasarrufu görünür kılmalı,
•	Kullanıcıyı suçlamadan yönlendirmeli,
•	Ekonomik faydayı çevresel faydayla birleştirmelidir.
________________________________________
11. Hackathon İçin MVP
MVP’nin adı
TerraTwin Mini — Yapay Zekâ Destekli Sulama Dijital İkizi
MVP’nin amacı
Toprağın nem değişimini dijital ortamda modellemek ve gelecekteki sulama ihtiyacını tahmin etmek.
Donanım bileşenleri
•	ESP32
•	İki veya üç toprak nem sensörü
•	Sıcaklık ve nem sensörü
•	Röle
•	Mini su pompası
•	İki farklı toprak veya saksı bölgesi
Yazılım bileşenleri
•	Python
•	Basit makine öğrenmesi modeli
•	Hava durumu verisi
•	Streamlit veya web paneli
•	Gerçek zamanlı veri ekranı
•	Sulama önerisi
•	Otomatik pompa kontrolü
Demo senaryosu
İki farklı saksı veya toprak bölgesi kullanılır.
•	Birinci bölge kuru,
•	İkinci bölge yeterince nemlidir.
Sistem:
1.	Her iki bölgeden veri alır.
2.	Hava tahminini kontrol eder.
3.	Kuruma riskini hesaplar.
4.	Yalnızca ihtiyacı olan bölge için sulama önerir.
5.	Kullanıcı onayından sonra ilgili pompayı çalıştırır.
6.	Kullanılan su miktarını kaydeder.
7.	Geleneksel tüm-alan sulama ile karşılaştırma yapar.
________________________________________
12. Yapay Zekâ Kullanımı
Yapay zekâ modeli şu girdileri kullanabilir:
•	Mevcut toprak nemi
•	Son saatlerdeki nem değişimi
•	Toprak sıcaklığı
•	Hava sıcaklığı
•	Hava nemi
•	Yağış ihtimali
•	Ürün türü
•	Önceki sulama süresi
Modelin çıktısı:
•	Sulama gerekli mi?
•	Ne zaman gerekli?
•	Ne kadar süre yapılmalı?
•	Hangi bölge sulanmalı?
Model ilk aşamada:
•	Random Forest,
•	XGBoost,
•	Regresyon,
•	Basit zaman serisi modeli
ile geliştirilebilir.
Hackathon için gereksiz yere karmaşık derin öğrenme modeli kullanmak hata olur. Veri azsa karmaşık model daha iyi değil, daha kötü sonuç verir.
________________________________________
13. Robotik ve Otomasyon Kullanımı
Robotik bölüm şu bileşenlerle gösterilebilir:
•	Sensörlerden otomatik veri toplama
•	Röle üzerinden pompa kontrolü
•	Bölgesel sulama
•	Kullanıcı onayı
•	Acil durdurma
•	Sensör arızası uyarısı
Proje daha ileri aşamada:
•	Hareketli tarla robotu,
•	Otomatik numune alma,
•	Drone ile görüntü toplama
özelliklerine genişletilebilir.
Ancak hackathon MVP’sinde hareketli robot eklemek şart değildir. Gereksiz robotik, problemi çözmek yerine sunumu karmaşıklaştırabilir.
________________________________________
14. Toplumsal Etki
Proje başarılı olursa:
•	Su kaynakları daha verimli kullanılabilir.
•	Çiftçinin girdi maliyetleri düşebilir.
•	Kuraklık dönemlerinde su yönetimi iyileşebilir.
•	Küçük çiftçiler dijital tarım araçlarına erişebilir.
•	Toprak sağlığı uzun vadede korunabilir.
•	Tarımsal üretimde veri temelli karar kültürü gelişebilir.
•	Gıda üretiminin iklim değişikliğine dayanıklılığı artabilir.
Ancak toplumsal etkinin oluşması için ürünün yalnızca büyük tarım işletmelerine değil, küçük üreticilere de uygun olması gerekir.
Bu nedenle:
•	Kooperatif modeli,
•	Sensör kiralama,
•	Ortak kullanım,
•	Düşük maliyetli paket
geliştirilmelidir.
________________________________________
15. Kullanıcı Deneyimi ve Tasarım
Arayüz teknik verilerle doldurulmamalıdır.
Çiftçiye onlarca grafik göstermek yerine üç temel soru cevaplanmalıdır:
1.	Toprağın durumu nasıl?
2.	Ne yapmalıyım?
3.	Bunu neden yapmalıyım?
Örnek ekran
Toprak durumu: Orta risk
Öneri: Kuzey bölgesini bugün 18 dakika sulayın.
Neden: Nem seviyesi düşüyor ve önümüzdeki 48 saatte yağış beklenmiyor.
Beklenen sonuç: Yaklaşık 20 litre su tasarrufu.
Arayüzde:
•	Yeşil, sarı ve kırmızı risk göstergesi
•	Basit harita
•	Sesli bildirim
•	Büyük butonlar
•	Açıklanabilir öneriler
bulunmalıdır.
________________________________________
16. Ekip İçi Görev Paylaşımı
Yapay zekâ ve veri sorumlusu
•	Veri temizleme
•	Tahmin modeli
•	Risk skoru
•	Model doğrulama
Donanım ve IoT sorumlusu
•	ESP32
•	Sensörler
•	Röle ve pompa
•	Veri iletişimi
Yazılım ve arayüz sorumlusu
•	Web paneli
•	Veritabanı
•	API
•	Kullanıcı ekranları
Tarım ve araştırma sorumlusu
•	Toprak ve sulama kriterleri
•	Kullanıcı görüşmeleri
•	Rakip analizi
•	Çevresel etki
Sunum ve iş modeli sorumlusu
•	Hikâyeleştirme
•	Proje anlatımı
•	İş modeli
•	Sunum süresi
•	Demo akışı
Ekip küçükse görevler birleştirilebilir ancak her işin sorumlusu net olmalıdır.
________________________________________
17. Jüri Kriterlerine Göre Projenin Konumlandırılması
Jüri kriteri	Projede nasıl karşılanacak?
Problemin doğru tanımlanması	Sorun yalnızca nem ölçümü değil, karar desteği ve uzun vadeli toprak sağlığı olarak tanımlanır.
Yapay zekâ ve robotik kullanımı	AI sulama ihtiyacını tahmin eder; ESP32 ve pompa otomasyonu uygular.
Özgünlük ve yenilik	Sensör verisi, hava tahmini ve dijital ikiz simülasyonu birleştirilir.
Uygulanabilirlik	Küçük sera veya saksı üzerinde çalışan MVP geliştirilir.
Toplumsal etki	Su tasarrufu, maliyet azalması ve sürdürülebilir tarım etkisi gösterilir.
Çalışan demo	Sensör, panel ve otomatik pompa birlikte çalıştırılır.
Kullanıcı deneyimi	Basit, açıklanabilir ve çiftçi odaklı arayüz hazırlanır.
Sunum kalitesi	Problem, çözüm, demo ve ölçülen sonuç sırasıyla anlatılır.
Süre yönetimi	Teknik ayrıntıya boğulmadan tek kullanım senaryosu gösterilir.
Ekip çalışması	Donanım, AI, yazılım, araştırma ve sunum görevleri ayrılır.
________________________________________
18. Sunumda Kullanılabilecek Ana Mesaj
Bugün çiftçiler toprağın mevcut durumunu sınırlı ölçümlerle görebiliyor ancak verdikleri kararların yarın toprağı nasıl etkileyeceğini göremiyor. TerraTwin Mini, toprağın nem durumunu dijital ortamda modelleyerek sulama ihtiyacını önceden tahmin ediyor ve yalnızca gerekli bölgenin sulanmasını sağlıyor. Böylece su israfını azaltırken toprağın uzun vadeli sağlığını koruyor.
________________________________________
19. Sonuç
Toprak Dijital İkizi fikrinin görünen problemi, çiftçilerin toprak verilerine yeterince erişememesidir. Ancak gerçek problem, farklı verilerin bir araya getirilerek güvenilir bir tarımsal karara dönüştürülememesidir.
Projede alınması gereken stratejik karar, ilk aşamada tüm toprak sistemini modellemek yerine sulama kararına odaklanan dar kapsamlı fakat çalışan bir dijital ikiz geliştirmektir.
Bu yaklaşım:
•	Daha uygulanabilir,
•	Daha ölçülebilir,
•	Daha anlaşılır,
•	Daha güçlü bir demo üretmeye uygun,
•	Yapay zekâ ve otomasyonu gerçekten kullanan
bir proje ortaya çıkarır.
Projenin başarısı teknolojinin karmaşıklığıyla değil, şu soruya verdiği cevapla ölçülmelidir:
Çiftçi bu sistemi kullandığında daha doğru karar verecek, daha az su kullanacak ve toprağını daha uzun süre koruyabilecek mi?
Bu soruya çalışan prototip ve ölçülebilir sonuçlarla cevap verilebiliyorsa proje güçlüdür.




AGRITWIN AI — İŞ GELİŞTİRME CANVASI
1. Problem
Tarım arazilerinde toprağın nem, sıcaklık, pH, tuzluluk, organik madde ve besin durumu sürekli değişmektedir. Aynı tarlanın farklı bölgelerinde bile ihtiyaçlar farklı olabilir.
Buna rağmen çiftçiler çoğunlukla:
•	Genel hava tahminlerine,
•	Kişisel deneyimlerine,
•	Belirli aralıklarla yapılan laboratuvar analizlerine,
•	Tek noktadan alınan sensör verilerine
dayanarak sulama ve gübreleme kararı vermektedir.
Bu durum:
•	Gereğinden fazla su kullanımına,
•	Yanlış veya aşırı gübrelemeye,
•	Toprak verimliliğinin azalmasına,
•	Tuzlanma ve toprak bozulmasına,
•	Enerji ve üretim maliyetlerinin yükselmesine,
•	Verim kaybına,
•	İklim değişikliğine karşı zayıf üretim planlamasına
neden olmaktadır.
Görünen problem
Çiftçi toprağın anlık durumunu yeterince görememektedir.
Gerçek problem
Çiftçi, farklı kaynaklardan gelen verileri birleştirerek toprağın gelecekte nasıl davranacağını ve aldığı kararların sonucunu önceden görebileceği güvenilir bir karar destek sistemine sahip değildir.
________________________________________
2. Çözüm
AgriTwin AI, tarım arazilerinden gelen sensör verilerini, hava durumu bilgilerini, laboratuvar analizlerini ve uydu görüntülerini birleştirerek toprağın sürekli güncellenen dijital ikizini oluşturan yapay zekâ destekli tarım platformudur.
Sistem:
•	Toprağın mevcut durumunu gösterir.
•	Tarla içindeki farklı bölgeleri analiz eder.
•	Sulama ihtiyacını önceden tahmin eder.
•	Tuzlanma ve kuraklık riskini belirler.
•	Farklı sulama ve gübreleme senaryolarını simüle eder.
•	Çiftçiye açıklanabilir öneriler sunar.
•	Kullanıcı onayıyla sulama sistemini otomatik çalıştırabilir.
•	Yapılan uygulamaların sonuçlarını ölçerek modelini geliştirir.
İlk aşama çözümü
İlk ürün, tam kapsamlı toprak dijital ikizi yerine şu probleme odaklanacaktır:
Toprak nemi, hava tahmini ve ürün ihtiyacını birlikte analiz ederek doğru sulama zamanını ve miktarını belirlemek.
________________________________________
3. Benzersiz Değer Önerisi
AgriTwin AI, çiftçiye yalnızca toprağın bugünkü durumunu göstermez; toprağın gelecekte nasıl değişeceğini tahmin eder ve sulama kararlarının sonucunu uygulamadan önce simüle eder.
Çiftçi için temel değer
•	Ne zaman sulama yapması gerektiğini öğrenir.
•	Ne kadar su kullanması gerektiğini görür.
•	Tarlanın yalnızca ihtiyacı olan bölgesini sular.
•	Gereksiz sulamayı azaltır.
•	Girdi maliyetlerini düşürür.
•	Toprak sağlığını uzun vadede korur.
Rakiplerden farklılaşma
AgriTwin AI:
•	Yalnızca sensör verisi göstermez.
•	Sabit eşik değerine göre çalışmaz.
•	Hava tahminini sisteme dahil eder.
•	Geleceğe yönelik tahmin üretir.
•	Tarla içi bölgesel farklılıkları değerlendirir.
•	Senaryo simülasyonu sunar.
•	Karar desteği ve otomasyonu birleştirir.
________________________________________
4. Müşteri Segmentleri
Birincil müşteriler
•	Küçük ve orta ölçekli çiftçiler
•	Sera üreticileri
•	Sulama maliyeti yüksek üreticiler
•	Kuraklık riski bulunan bölgelerdeki çiftçiler
•	Hassas tarım uygulamak isteyen işletmeler
İkincil müşteriler
•	Büyük tarım işletmeleri
•	Tarım kooperatifleri
•	Üretici birlikleri
•	Ziraat odaları
•	Sulama birlikleri
•	Belediyeler
•	Tarım il ve ilçe müdürlükleri
•	Üniversiteler ve araştırma merkezleri
•	Tarım danışmanlığı şirketleri
Potansiyel kurumsal müşteriler
•	Gübre üreticileri
•	Sulama sistemi firmaları
•	Tarım makineleri şirketleri
•	Gıda tedarik zinciri şirketleri
•	Tarım sigortası şirketleri
•	Bankalar ve tarım finansmanı kuruluşları
________________________________________
5. Erken Benimseyen Kullanıcılar
İlk kullanıcı kitlesi tüm çiftçiler olmamalıdır. En uygun erken kullanıcılar:
•	Sera üreticileri
•	Damla sulama sistemi kullanan çiftçiler
•	Su maliyeti yüksek bölgelerde üretim yapanlar
•	Dijital tarım teknolojilerine açık üreticiler
•	Kooperatif üyesi çiftçiler
•	Üniversite veya teknoparkla çalışan pilot işletmeler
•	Su stresi yaşayan ürünlerde çalışan üreticiler
İlk pilot için uygun ürünler
•	Domates
•	Biber
•	Çilek
•	Salatalık
•	Bağ ve meyve bahçeleri
Bu ürünlerde sulama yönetimi doğrudan kalite ve verimi etkilediği için kullanıcı değeri daha görünür olur.
________________________________________
6. Mevcut Alternatifler
Çiftçiler bugün şu yöntemleri kullanmaktadır:
•	Manuel toprak kontrolü
•	Sabit saatli sulama
•	Toprak nem sensörleri
•	Laboratuvar analizleri
•	Hava durumu uygulamaları
•	Ziraat mühendisi danışmanlığı
•	Temel akıllı sulama sistemleri
•	Uydu tabanlı tarla izleme platformları
Mevcut çözümlerin eksikleri
•	Veriler farklı sistemlerde dağınıktır.
•	Çoğu sistem yalnızca mevcut durumu gösterir.
•	Toprağın gelecekteki durumu tahmin edilmez.
•	Sensör ve hava verileri birlikte kullanılmaz.
•	Küçük üretici için maliyet yüksek olabilir.
•	Kullanıcıya teknik fakat uygulanması zor veriler sunulur.
•	Tarımsal kararın sonucu önceden simüle edilmez.
________________________________________
7. Temel Ürün Özellikleri
İlk sürüm özellikleri
•	Toprak nemi ölçümü
•	Toprak sıcaklığı ölçümü
•	Hava sıcaklığı ve nem takibi
•	Yağış tahmini entegrasyonu
•	Sulama ihtiyacı tahmini
•	Bölgesel nem haritası
•	Kullanıcıya sulama önerisi
•	Kullanıcı onaylı otomatik sulama
•	Günlük ve haftalık su tüketimi
•	Sensör arızası uyarısı
•	Mobil ve web kontrol paneli
İleri sürüm özellikleri
•	pH ve tuzluluk analizi
•	Uydu ve drone entegrasyonu
•	Gübreleme önerisi
•	Verim tahmini
•	Toprak sağlığı puanı
•	Erozyon ve kuraklık risk analizi
•	Çoklu tarla yönetimi
•	Kooperatif paneli
•	Senaryo simülasyonu
•	Tam otomatik sulama
________________________________________
8. Müşteri Kanalları
Doğrudan satış kanalları
•	Tarım fuarları
•	Saha ziyaretleri
•	Tarla ve sera demonstrasyonları
•	Kooperatif toplantıları
•	Ziraat odaları
•	Tarım danışmanları
•	Üniversite iş birlikleri
•	Belediyeler ve kamu kurumları
Dijital kanallar
•	Web sitesi
•	Mobil uygulama
•	Sosyal medya
•	Tarım odaklı dijital platformlar
•	WhatsApp destek hattı
•	Eğitim videoları
•	Çiftçi başarı hikâyeleri
En etkili kanal
Tarım teknolojilerinde en güçlü satış yöntemi reklam değil, sahada kanıtlanan sonuçtur.
Bu nedenle pazara girişte şu yöntem kullanılmalıdır:
Pilot arazi kurulumu → su tasarrufu ölçümü → çiftçi referansı → kooperatif ve bölgesel yayılım.
________________________________________
9. Müşteri İlişkileri
Kurulum öncesi
•	Arazi ihtiyacı analizi
•	Ürün ve sulama sistemi değerlendirmesi
•	Sensör yerleşim planı
•	Kullanıcı eğitimi
Kullanım sırasında
•	Mobil bildirimler
•	Teknik destek
•	Sesli veya sade öneriler
•	Periyodik performans raporları
•	Sensör bakım uyarıları
•	Ziraat mühendisi desteği
Uzun vadeli ilişki
•	Sezonluk değerlendirme
•	Tasarruf raporu
•	Yeni ürün veya tarla ekleme
•	Paket yükseltme
•	Kooperatif üyelik modeli
•	Kullanıcı topluluğu ve bilgi paylaşımı
________________________________________
10. Gelir Modeli
10.1. Donanım satış modeli
Müşteriye sensör, ESP32, vana ve kontrol biriminden oluşan başlangıç kiti satılır.
Gelir kaynakları:
•	Sensör kiti
•	Kurulum
•	Vana ve otomasyon modülü
•	Güneş enerjili güç sistemi
•	Ek sensör satışı
10.2. Abonelik modeli
Aylık veya yıllık yazılım aboneliği alınır.
Temel paket
•	Sensör verisi görüntüleme
•	Hava durumu entegrasyonu
•	Basit uyarılar
Akıllı paket
•	Yapay zekâ tahmini
•	Sulama önerisi
•	Tasarruf raporu
•	Anomali tespiti
Profesyonel paket
•	Çoklu tarla yönetimi
•	Dijital ikiz simülasyonu
•	Kurumsal raporlama
•	Otomasyon yönetimi
•	API entegrasyonu
10.3. Kooperatif modeli
Kooperatif sistemi toplu olarak satın alır ve üyelerine hizmet verir.
Bu model:
•	Donanım maliyetini düşürür.
•	Küçük üreticilerin erişimini artırır.
•	Bölgesel veri oluşturur.
•	Toplu teknik destek sağlar.
10.4. Hizmet modeli
•	Kurulum
•	Sensör kalibrasyonu
•	Teknik bakım
•	Tarla analizi
•	Veri raporlama
•	Ziraat danışmanlığı
•	Özel model geliştirme
10.5. Kurumsal lisanslama
Büyük tarım işletmelerine ve kamu kurumlarına özel panel, entegrasyon ve çoklu kullanıcı lisansı sunulur.
________________________________________
11. Maliyet Yapısı
Sabit maliyetler
•	Yazılım geliştirme
•	Yapay zekâ model geliştirme
•	Sunucu ve bulut altyapısı
•	Mobil ve web uygulaması
•	Ar-Ge çalışmaları
•	Personel giderleri
•	Veri güvenliği
Değişken maliyetler
•	Sensörler
•	ESP32 ve iletişim modülleri
•	Kurulum
•	Saha ziyareti
•	Sensör kalibrasyonu
•	Teknik bakım
•	Lojistik
•	Mobil veri bağlantısı
•	Kullanıcı desteği
Gizli maliyetler
•	Sensör arızaları
•	Zorlu hava koşulları
•	Kırsal internet problemi
•	Kullanıcı eğitimi
•	Farklı toprak türleri için model uyarlaması
•	Pilot saha bulma
•	Uzun dönem veri toplama
________________________________________
12. Temel Kaynaklar
•	Toprak ve hava sensörleri
•	ESP32 ve iletişim altyapısı
•	Yapay zekâ modelleri
•	Toprak ve sulama veri setleri
•	Uydu ve hava durumu verileri
•	Yazılım geliştiriciler
•	Yapay zekâ uzmanları
•	Ziraat mühendisleri
•	Toprak bilimciler
•	Pilot tarım alanları
•	Bulut ve veri tabanı altyapısı
•	Satış ve saha destek ekibi
________________________________________
13. Temel Faaliyetler
•	Sensör ağı geliştirme
•	Sensör kurulumu ve kalibrasyonu
•	Tarla verisi toplama
•	Veri temizleme ve analiz
•	Yapay zekâ modeli geliştirme
•	Dijital ikiz modelleme
•	Web ve mobil uygulama geliştirme
•	Sulama otomasyonu entegrasyonu
•	Kullanıcı testleri
•	Pilot saha çalışmaları
•	Performans ve tasarruf ölçümü
•	Teknik destek
•	Pazarlama ve satış
________________________________________
14. Temel İş Ortakları
•	Çiftçiler
•	Sera üreticileri
•	Tarım kooperatifleri
•	Ziraat odaları
•	Üniversiteler
•	Ziraat fakülteleri
•	Toprak araştırma laboratuvarları
•	Sensör üreticileri
•	Sulama sistemi firmaları
•	Telekomünikasyon şirketleri
•	Bulut hizmet sağlayıcıları
•	Belediyeler
•	Tarım ve Orman Bakanlığı birimleri
•	Teknokentler
•	Tarım teknolojisi girişimleri
________________________________________
15. Anahtar Başarı Göstergeleri
Teknik göstergeler
•	Sensör veri doğruluğu
•	Veri sürekliliği
•	Sulama tahmin doğruluğu
•	Sistem çalışma süresi
•	Sensör arıza oranı
•	Otomasyon başarı oranı
Çevresel göstergeler
•	Su tüketimindeki azalma
•	Gereksiz sulama sayısındaki düşüş
•	Enerji tüketimindeki azalma
•	Toprak nem dengesindeki iyileşme
•	Tuzlanma riskindeki azalma
Ticari göstergeler
•	Pilot kullanıcı sayısı
•	Ücretli müşteriye dönüşüm
•	Müşteri edinme maliyeti
•	Abonelik yenileme oranı
•	Kullanıcı başına gelir
•	Kurulum başına maliyet
•	Kooperatif anlaşması sayısı
Kullanıcı göstergeleri
•	Günlük aktif kullanıcı
•	Öneri uygulama oranı
•	Kullanıcı memnuniyeti
•	Teknik destek talebi
•	Sisteme duyulan güven
________________________________________
16. Rekabet Avantajı
AgriTwin AI’ın rekabet avantajı tek bir teknolojiden değil, sistem bütünlüğünden gelir.
Temel avantajlar
•	Sensör, hava ve geçmiş verileri birleştirmesi
•	Geleceğe yönelik tahmin yapması
•	Senaryo simülasyonu sunması
•	Bölgesel sulama sağlaması
•	Çiftçiye sade ve açıklanabilir öneriler vermesi
•	Düşük maliyetli ve modüler olması
•	Kooperatif modeline uygunluğu
•	Otomasyonla doğrudan bağlantı kurması
•	Küçük üreticiye uyarlanabilmesi
Savunulabilir avantaj
Uzun vadede en önemli avantaj, farklı toprak ve ürünlerden toplanacak saha verisidir.
Rakipler donanımı kopyalayabilir ancak:
•	Bölgesel veri,
•	Çiftçi kullanım alışkanlıkları,
•	Ürün bazlı modeller,
•	Tarla geçmişi
kolayca kopyalanamaz.
________________________________________
17. Pazara Giriş Stratejisi
Aşama 1 — Problem doğrulama
•	En az 10–15 çiftçiyle görüşme
•	Sulama kararlarının nasıl verildiğinin incelenmesi
•	Su ve enerji maliyetlerinin belirlenmesi
•	Teknoloji kullanım engellerinin öğrenilmesi
Aşama 2 — Pilot geliştirme
•	Tek sera veya küçük tarla
•	Tek ürün
•	Nem ve hava verisi
•	Sulama tahmini
•	Kullanıcı onaylı otomasyon
Aşama 3 — Etki ölçümü
•	Geleneksel sulama ile karşılaştırma
•	Su tasarrufu
•	Enerji tasarrufu
•	Bitki gelişimi
•	Kullanıcı memnuniyeti
Aşama 4 — Referans müşteri
Pilot sonuçları saha başarı hikâyesine dönüştürülür.
Aşama 5 — Kooperatif yayılımı
Birden fazla üreticiye aynı bölgede hizmet sunulur.
Aşama 6 — Kurumsal ölçekleme
•	Büyük tarım işletmeleri
•	Belediyeler
•	Sulama birlikleri
•	Kamu kurumları
hedeflenir.
________________________________________
18. Minimum Uygulanabilir Ürün
MVP adı
TerraTwin Mini
MVP kapsamı
•	İki veya üç toprak nem sensörü
•	Toprak sıcaklığı
•	Hava durumu entegrasyonu
•	Sulama ihtiyacı tahmini
•	Mobil veya web paneli
•	Kullanıcı onaylı otomatik pompa
•	Su tüketimi raporu
MVP kullanıcı senaryosu
1.	Sensörler toprağın nem durumunu ölçer.
2.	Sistem hava tahminini kontrol eder.
3.	Yapay zekâ kuruma riskini hesaplar.
4.	Kullanıcıya hangi bölgenin sulanması gerektiğini açıklar.
5.	Kullanıcı öneriyi onaylar.
6.	Sistem yalnızca ilgili bölgeyi sular.
7.	Kullanılan su miktarı kaydedilir.
8.	Geleneksel sulamayla karşılaştırma yapılır.
Başarı kriteri
Sistem, bitkinin ihtiyaç duyduğu nem seviyesini korurken geleneksel sulama yöntemine göre daha az su kullanmalıdır.
________________________________________
19. Riskler ve Önlemler
Sensör verisinin hatalı olması
Risk: Yanlış sulama kararı oluşabilir.
Önlem: Sensör kalibrasyonu, çoklu sensör doğrulaması ve anomali tespiti kullanılmalıdır.
Çiftçinin sistemi kullanmaması
Risk: Teknik olarak iyi ürün sahada başarısız olabilir.
Önlem: Basit arayüz, sesli kullanım, saha eğitimi ve ekonomik fayda gösterilmelidir.
Maliyetin yüksek olması
Risk: Küçük çiftçiler ürünü satın alamayabilir.
Önlem: Kooperatif, kiralama ve abonelik modeli kullanılmalıdır.
İnternet bağlantısının olmaması
Risk: Veri aktarımı kesilebilir.
Önlem: LoRa, GSM ve çevrimdışı kayıt sistemi kullanılmalıdır.
Yapay zekâ önerisinin yanlış olması
Risk: Ürün ve toprak zarar görebilir.
Önlem: İlk aşamada kullanıcı onayı olmadan otomasyon çalışmamalıdır.
Proje kapsamının fazla genişlemesi
Risk: Çalışan ürün geliştirilemez.
Önlem: İlk aşamada yalnızca sulama problemine odaklanılmalıdır.
________________________________________
20. Çevresel ve Toplumsal Etki
Çevresel etki
•	Su tüketiminin azaltılması
•	Enerji kullanımının düşürülmesi
•	Toprak bozulmasının önlenmesi
•	Tuzlanma riskinin azaltılması
•	Gübre ve kimyasal kullanımının optimize edilmesi
•	İklim değişikliğine dayanıklı üretim
Ekonomik etki
•	Çiftçinin girdi maliyetlerinin azalması
•	Verim kaybının düşmesi
•	Üretim planlamasının iyileşmesi
•	Kaynak kullanımının ölçülebilir hâle gelmesi
Sosyal etki
•	Küçük üreticinin teknolojiye erişimi
•	Kırsal bölgelerde dijital dönüşüm
•	Tarımsal bilgiye erişimin artması
•	Gıda güvenliğinin desteklenmesi
•	Gençlerin tarım teknolojilerine yönelmesi
________________________________________
21. Stratejik Karar
AgriTwin AI için alınması gereken temel iş geliştirme kararı şudur:
İlk aşamada tam kapsamlı bir toprak dijital ikizi satmaya çalışmak yerine, su tasarrufu sağlayan yapay zekâ destekli sulama karar sistemiyle pazara girilmelidir.
Kararın gerekçesi
•	Problem nettir.
•	Kullanıcı faydası ölçülebilir.
•	Pilot hızlı kurulabilir.
•	Donanım maliyeti kontrol edilebilir.
•	Yapay zekâ kullanımı anlamlıdır.
•	Su tasarrufu ticari değer üretir.
•	Daha sonra diğer modüller eklenebilir.
Uzun vadeli büyüme
1.	Sulama optimizasyonu
2.	Tuzluluk ve toprak sağlığı
3.	Gübreleme önerisi
4.	Uydu ve drone entegrasyonu
5.	Verim tahmini
6.	Çoklu çiftlik dijital ikizi
7.	Bölgesel tarım karar platformu
________________________________________
22. Tek Cümlelik İş Modeli
AgriTwin AI, çiftçilere düşük maliyetli sensör kiti ve abonelik tabanlı yapay zekâ platformu sunarak sulama kararlarını optimize eder; su ve enerji tasarrufu sağlarken toprağın uzun vadeli sağlığını korur.
________________________________________
23. İş Geliştirme Canvası Özet Tablosu
Alan	AgriTwin AI
Problem	Tarımsal kararların eksik ve dağınık verilere dayanması
Çözüm	Yapay zekâ destekli toprak dijital ikizi
İlk kullanım alanı	Sulama zamanı ve miktarı tahmini
Müşteri	Çiftçiler, seralar, kooperatifler, tarım işletmeleri
Değer önerisi	Daha az su, daha düşük maliyet, daha sağlıklı toprak
Gelir modeli	Donanım satışı, abonelik, kurulum ve bakım
Kanallar	Kooperatifler, tarım fuarları, saha demonstrasyonları
Temel ortaklar	Ziraat mühendisleri, üniversiteler, sensör ve sulama firmaları
Temel maliyetler	Donanım, yazılım, saha kurulumu, bakım ve veri altyapısı
Rekabet avantajı	Tahmin, simülasyon, bölgesel yönetim ve otomasyon
MVP	Nem sensörü, hava tahmini, AI sulama önerisi ve pompa kontrolü
Başarı ölçütü	Su tasarrufu, tahmin doğruluğu ve kullanıcı benimsemesi







AgriTwin AI Prototip Veri Yapısı
Platformda üç farklı veri giriş yöntemi bulunmalı:
1. Çiftçinin Manuel Veri Girişi
Çiftçi kendi elindeki bilgileri sisteme girebilmeli.
Bu alan gerçek kullanım senaryosunu temsil eder.
Kullanıcının gireceği temel veriler
Arazi bilgileri
•	Arazi adı 
•	Konum 
•	Arazi büyüklüğü 
•	Açık tarla, sera veya bahçe 
•	Sulama sistemi türü 
•	Toprak türü 
Ürün bilgileri
•	Ürün türü 
•	Ekim tarihi 
•	Gelişim dönemi 
•	Tahmini hasat tarihi 
Toprak verileri
•	Toprak nemi 
•	Toprak sıcaklığı 
•	pH 
•	Elektriksel iletkenlik 
•	Tuzluluk 
•	Organik madde oranı 
•	Son toprak analiz tarihi 
Sulama verileri
•	Son sulama tarihi 
•	Sulama süresi 
•	Kullanılan su miktarı 
•	Sulama yöntemi 
Gözlemsel bilgiler
•	Bitkide sararma var mı? 
•	Toprak yüzeyi kuru mu? 
•	Su birikmesi var mı? 
•	Bitki gelişiminde yavaşlama var mı? 
Burada tüm alanlar zorunlu olmamalı. Çiftçi bazı değerleri bilmiyorsa sistem çalışmaya devam etmeli ancak veri güven seviyesi düşmelidir.
Örneğin:
Veri güven seviyesi: %64
pH ve tuzluluk değerleri girilmediği için analiz sınırlıdır.
Bu yaklaşım sistemin daha gerçekçi görünmesini sağlar.
________________________________________
2. IoT ve Bulut Sistemlerinden Otomatik Veri Alma
Platformda gerçek sensör entegrasyonu varmış gibi çalışan bir otomatik veri akış bölümü bulunmalı.
Bu bölüm prototipte simüle edilebilir.
Ancak kullanıcıya “sistem yapay veri üretiyor” gibi gösterilmemeli. Bunun yerine teknik olarak:
IoT veri akışı simülasyonu
olarak tanımlanmalı.
Gerçek sistemde veri nereden gelir?
•	Toprak nem sensörü 
•	Toprak sıcaklık sensörü 
•	pH sensörü 
•	EC sensörü 
•	Tuzluluk sensörü 
•	Hava sıcaklığı sensörü 
•	Hava nem sensörü 
•	Yağış sensörü 
•	Debi sensörü 
•	Sulama vanası 
•	ESP32 veya benzeri kontrolcü 
•	LoRa, Wi-Fi veya GSM bağlantısı 
•	IoT bulut platformu 
Prototipte nasıl gösterilir?
Platformda bir cihaz yönetim ekranı olur.
Örnek cihazlar
Cihaz	Bağlantı	Durum	Son veri
Toprak Nem Sensörü 01	IoT Cloud	Aktif	%34
Toprak Sıcaklık Sensörü	IoT Cloud	Aktif	23,8 °C
pH Sensörü	IoT Cloud	Bağlı değil	Veri yok
Sulama Vanası	IoT Cloud	Beklemede	Kapalı
Kullanıcı arayüzü
•	Cihaz ekle 
•	API anahtarı gir 
•	Cihaz kimliği gir 
•	Veri kaynağı seç 
•	Bağlantıyı test et 
•	Son veri zamanını göster 
•	Sensörü aktif veya pasif yap 
Prototipte gerçek cihaz olmadığı için arka planda belirli bir test veri akışı çalışabilir.
Ancak bu yalnızca otomatik bağlantı senaryosunu göstermek için kullanılmalıdır.
________________________________________
3. Ekip Tarafından Hazırlanan Test Veri Seti
Bu veri, platformun çalışabilirliğini göstermek için sizin tarafınızdan önceden hazırlanmalıdır.
Sistem her seferinde rastgele veri üretmemelidir.
Bunun yerine kontrollü test senaryoları bulunmalıdır.
Örnek test senaryoları
Senaryo 1: Normal toprak durumu
•	Nem: %48 
•	Sıcaklık: 22 °C 
•	Yağış ihtimali: %40 
•	Sulama riski: Düşük 
Senaryo 2: Kuruma riski
•	Nem: %26 
•	Sıcaklık: 34 °C 
•	Yağış ihtimali: %5 
•	Sulama riski: Yüksek 
Senaryo 3: Aşırı sulama riski
•	Nem: %82 
•	Toprak sıcaklığı: 19 °C 
•	Son sulama: 2 saat önce 
•	Sulama riski: Gereksiz sulama 
Senaryo 4: Sensör anomalisi
•	Önceki nem: %42 
•	Yeni nem: %3 
•	Geçen süre: 5 dakika 
•	Sonuç: Sensör arızası ihtimali 
Senaryo 5: Tuzluluk riski
•	EC değeri yüksek 
•	Nem düşük 
•	Sık sulama kaydı var 
•	Sonuç: Tuz birikimi riski 
Bu senaryolar veri tabanına hazır olarak eklenebilir.
Kullanıcı veya jüri:
•	Normal senaryo 
•	Kuraklık senaryosu 
•	Aşırı sulama senaryosu 
•	Sensör arızası senaryosu 
seçerek sistemi test edebilir.
Bu yöntem rastgele veri üretmekten çok daha kontrollü ve güvenlidir.
________________________________________
Platformdaki Veri Kaynağı Seçimi
Arazi oluşturulurken kullanıcıya şu seçenekler verilmelidir:
Veri kaynağı
Manuel veri girişi
Çiftçi değerleri kendisi girer.
IoT cihazından otomatik veri
Sensör ve bulut bağlantısı kullanılır.
Test veya demo verisi
Sistemin özelliklerini görmek için hazır senaryolar kullanılır.
Bu ayrım kullanıcıya açıkça gösterilmelidir.
Örneğin:
Veri kaynağı: IoT simülasyonu
Son veri güncellemesi: 14:32
Cihaz durumu: Aktif
________________________________________
Doğru Veri Akış Mimarisi
Sistem şu şekilde çalışmalı:
Manuel Veri
      \
       \
IoT veya Bulut Verisi → Veri Doğrulama Katmanı → Veri Tabanı
       /
      /
Test Veri Seti
Ardından:
Veri Tabanı
   ↓
Ön İşleme
   ↓
Yapay Zekâ Modeli
   ↓
Tahmin ve Risk Analizi
   ↓
Dijital İkiz Ekranı
   ↓
Sulama Önerisi veya Otomasyon
________________________________________
Veriler Sisteme Geldiğinde Ne Yapılacak?
Veri doğrudan yapay zekâya gönderilmemelidir.
Önce kontrol edilmelidir.
Veri doğrulama aşaması
Sistem şu kontrolleri yapar:
•	Değer eksik mi? 
•	Değer gerçekçi aralıkta mı? 
•	Önceki ölçümle aşırı fark var mı? 
•	Veri güncel mi? 
•	Sensör bağlantısı aktif mi? 
•	Manuel veri mi, IoT verisi mi? 
•	Aynı zaman aralığında çelişkili ölçüm var mı? 
Örnek
Toprak nemi sensörü bir anda:
•	%45’ten 
•	%2’ye 
düşmüşse sistem bunu doğrudan gerçek kabul etmemeli.
Şu uyarıyı vermeli:
Olağan dışı nem değişimi tespit edildi. Sensör veya veri girişi kontrol edilmelidir.
________________________________________
Yapay Zekânın Net Görevleri
Burada yapay zekâ ile otomasyon birbirinden ayrılmalıdır.
Yapay zekâ görevleri
1. Sulama ihtiyacı tahmini
Model şu soruya cevap verir:
Sulama gerekiyor mu?
Girdiler:
•	Toprak nemi 
•	Toprak sıcaklığı 
•	Hava sıcaklığı 
•	Hava nemi 
•	Yağış ihtimali 
•	Toprak türü 
•	Ürün türü 
•	Gelişim dönemi 
•	Son sulama bilgisi 
Çıktılar:
•	Sulama gerekli 
•	Sulama gereksiz 
•	Sulama ertelenebilir 
•	Yüksek kuruma riski 
________________________________________
2. Gelecekteki nem seviyesini tahmin etme
Sistem:
•	24 saat 
•	48 saat 
•	72 saat 
sonraki nem seviyesini tahmin eder.
Bu özellik dijital ikizin tahmin tarafıdır.
________________________________________
3. Anomali tespiti
Yapay zekâ:
•	Sensör arızasını 
•	Olağan dışı nem düşüşünü 
•	Aşırı sulamayı 
•	Sulama sonrası beklenmeyen sonucu 
tespit eder.
________________________________________
4. Risk sınıflandırması
Sistem riskleri sınıflandırır:
•	Düşük 
•	Orta 
•	Yüksek 
•	Kritik 
Risk türleri:
•	Kuruma riski 
•	Aşırı sulama riski 
•	Tuzlanma riski 
•	Sensör arızası riski 
•	Bitki su stresi riski 
________________________________________
5. Senaryo analizi
Kullanıcı şu seçenekleri deneyebilir:
•	Şimdi sulama 
•	12 saat sonra sulama 
•	24 saat sonra sulama 
•	Sulama yapmama 
•	Daha kısa sulama 
•	Daha uzun sulama 
Sistem her senaryonun sonucunu tahmin eder.
________________________________________
6. Açıklanabilir öneri üretme
Sistem yalnızca sonuç vermemelidir.
Örnek:
Sulama öneriliyor. Çünkü toprak nemi %27 seviyesinde, son 24 saatte %8 azaldı, sıcaklık yüksek ve önümüzdeki iki gün yağış beklenmiyor.
Bu açıklamanın kural tabanlı veya model özellik önemine dayalı olması daha güvenilir olur.
________________________________________
Otomasyonun Görevleri
Otomasyon yapay zekâ değildir.
Otomasyon şu görevleri yapar:
•	IoT sisteminden veri çekmek 
•	Verileri belirli aralıklarla güncellemek 
•	Kritik durumda bildirim göndermek 
•	Kullanıcı onayı sonrası sanal vanayı açmak 
•	Sulama süresini başlatmak 
•	Sulama bitince işlemi kaydetmek 
•	Yeni nem değerini sisteme aktarmak 
•	Cihaz bağlantı durumunu kontrol etmek 
Örnek iş akışı
AI: Sulama gerekli
↓
Kullanıcıya öneri göster
↓
Kullanıcı onay verir
↓
Otomasyon vanayı açar
↓
Sulama süresi başlar
↓
İşlem kaydedilir
↓
Yeni veri alınır
↓
AI yeniden analiz yapar
________________________________________
Kullanıcı Kayıt Akışı
1. Kullanıcı hesap oluşturur
•	Ad 
•	E-posta 
•	Kullanıcı türü 
2. Arazi ekler
•	Arazi adı 
•	Konum 
•	Alan 
•	Toprak türü 
•	Ürün türü 
•	Sulama sistemi 
3. Veri kaynağı seçer
•	Manuel giriş 
•	IoT bağlantısı 
•	Demo verisi 
4. Başlangıç verisini girer
Manuel modda değerleri doldurur.
IoT modunda cihaz bağlantısı yapar.
Demo modunda hazır senaryo seçer.
5. Dijital ikiz oluşturulur
Sistem:
•	Verileri doğrular. 
•	Risk skorunu hesaplar. 
•	Tahmin üretir. 
•	Dashboard’u oluşturur. 
________________________________________
Arayüzde Bulunması Gereken Temel Sayfalar
1. Kayıt ve giriş
Kullanıcı hesabı.
2. Arazi oluşturma
Toprak, ürün ve sulama bilgileri.
3. Veri kaynağı yönetimi
•	Manuel giriş 
•	IoT cihazları 
•	Demo senaryosu 
•	Dosyadan veri yükleme 
4. Dijital ikiz paneli
•	Toprak nemi 
•	Sıcaklık 
•	pH 
•	Tuzluluk 
•	Risk seviyesi 
•	72 saatlik tahmin 
•	Bölgesel durum 
5. Yapay zekâ önerileri
•	Öneri 
•	Gerekçe 
•	Güven skoru 
•	Veri eksikleri 
6. Senaryo simülasyonu
•	Sulama yap 
•	Bekle 
•	Sulama süresini değiştir 
•	Sonuçları karşılaştır 
7. IoT cihaz yönetimi
•	Cihaz adı 
•	Bağlantı durumu 
•	Son veri zamanı 
•	API durumu 
•	Aktif veya pasif 
8. Sulama otomasyonu
•	Vana durumu 
•	Sulama süresi 
•	Başlat 
•	Durdur 
•	Kullanılan su miktarı 
________________________________________
Prototip İçin En Doğru Veri Kullanımı
Manuel veri
Kullanıcının girdiği gerçek veya tahmini değerler.
IoT simülasyon verisi
Otomatik veri akışını göstermek için kontrollü olarak üretilen veri.
Hazır test veri seti
Modeli eğitmek ve sistem senaryolarını test etmek için sizin oluşturduğunuz veri.
Bu üçü birbirine karıştırılmamalıdır.
________________________________________
Önerilen Teknik Yapı
Frontend
Daha profesyonel prototip için:
•	React veya Next.js 
Daha hızlı geliştirme için:
•	Streamlit 
Backend
•	FastAPI 
•	Python 
Veri tabanı
•	PostgreSQL 
•	Supabase 
•	Firebase 
Hackathon için Supabase hızlı olabilir.
IoT simülasyonu
•	MQTT 
•	Belirli aralıklarla çalışan Python scripti 
•	REST API üzerinden veri gönderimi 
Yapay zekâ
•	Random Forest 
•	XGBoost 
•	Regresyon modeli 
•	Isolation Forest 
Canlıya alma
•	Frontend: Vercel 
•	Backend: Render veya Railway 
•	Veri tabanı: Supabase 
________________________________________
Prototipte Kullanılacak Net Demo Senaryosu
Senaryo
Kullanıcı “Domates Serası” adlı araziyi oluşturur.
Veri kaynağı
IoT bulut bağlantısı seçilir.
Prototip arka planda kontrollü veri akışı gönderir:
•	Nem: %34 
•	Toprak sıcaklığı: 25 °C 
•	Hava sıcaklığı: 33 °C 
•	Yağış ihtimali: %4 
AI analiz yapar:
Kuruma riski yüksek. Önümüzdeki 18 saat içinde sulama öneriliyor.
Kullanıcı “24 saat bekle” senaryosunu seçer.
Sistem gösterir:
•	Tahmini nem: %24 
•	Risk: Kritik 
Kullanıcı “Sulamayı başlat” seçeneğine basar.
Sanal vana açılır.
•	Sulama süresi: 14 dakika 
•	Tahmini su kullanımı: 90 litre 
•	Sulama sonrası nem: %46 
Bu işlem geçmişe kaydedilir.
________________________________________
Güncellenmiş MVP Tanımı
AgriTwin AI MVP, çiftçinin arazi ve toprak verilerini manuel olarak girebildiği, IoT ve bulut sistemlerinden otomatik veri alımını simüle eden, önceden hazırlanmış test verileriyle yapay zekâ modelini çalıştıran, sulama ihtiyacını ve toprak risklerini tahmin eden, farklı kararları simüle eden ve sanal sulama otomasyonu sunan web tabanlı toprak dijital ikiz platformudur.
En Kritik Ayrım
Şu üç yapıyı sunumda açıkça ayırın:
Katman	Görevi
Veri kaynağı	Manuel giriş, IoT sensörü veya test verisi
Yapay zekâ	Tahmin, anomali tespiti, risk analizi ve öneri
Otomasyon	Veri çekme, bildirim ve sulama sistemini çalıştırma
Bu ayrımı doğru kurarsanız jüri, projenin gerçekten yapay zekâ kullandığını ve yalnızca basit bir sensör paneli olmadığını anlayacaktır.





