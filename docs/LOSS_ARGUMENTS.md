# Jüri Gözüyle Kaybetme Argümanları ve Çözüm Planı (Loss Arguments & Win Strategy)

Tarih: 2026-09-28  
Son Güncelleme: Görev 10 Aşama 2  
Kural: "Neden bizi 1. seçmezler?" sorusu 5 jüri kişiliğinin (teknik, ürün, tasarım, etki/iş, şüpheci) en sert eleştirileriyle analiz edilmiştir. Puan kazançları `TAHMİN` etiketlidir.

---

## 1. Yarışma Bazında Kaybetme Argümanları ve Çözümleri

### 1. Amazon Build, Ship, Shape (Alexa+ & Open Source)
- **Argüman 1 (Teknik & Ürün):** "MCP sunucusu HTTP üzerinde çalışıyor ancak gerçek bir Alexa-AI CLI veya Echo cihazında uçtan uca test edilmedi; gecikme ölçümleri yok."
  - *Çözüm:* Resmî MCP Python SDK istemcisiyle (spec 2025-11-25) otomatik uyumluluk testleri yazmak, hızlı araçların (tool) yanıt sürelerini 500 ms altında ölçmek, asenkron görev durum sorgulamasını `speech` alanı ile bağlamak.
  - *Ölçülebilir Kabul Kriteri:* `tests/test_mcp_official_sdk.py` testinin 100% yeşil olması, benchmark tablosunda araç gecikmelerinin <500ms çıkması.
  - *Emek:* 3.0 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.65 puan.
- **Argüman 2 (Şüpheci & Tasarım):** "Sürtünme günlüğü (friction log) samimi ancak karşılaşılan kütüphane sorunlarının çözüldüğüne dair test kanıtı sunulmamış."
  - *Çözüm:* `docs/FRICTION_LOG.md` ve `submissions/amazon/FRICTION_LOG.md` içine gerçek hata kodları ve bu hataları çözen regresyon testlerinin adlarını eklemek.
  - *Ölçülebilir Kabul Kriteri:* 5 somut hatanın (arXiv 406, httpx Bearer, lifespan session, selector body, token limit) kod ve test linkleriyle belgelenmesi.
  - *Emek:* 1.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.40 puan.
- **Argüman 3 (Etki / İş):** "Gerçek tüketici platformlarında (Google, Amazon Store) canlı alışveriş gösterilmiyor."
  - *Çözüm:* Gerçek hesap girişleri ve ödeme sistemlerinin güvenlik gereği bilinçli olarak engellendiğini (`DENYLIST`), izin listesindeki 5 gerçek sitede $0.0238 harcamayla çalışan güvenli otomasyon sınırını savunmak.
  - *Ölçülebilir Kabul Kriteri:* `docs/COST.md` ve `README.md` güvenlik mimarisi referansı; 88+ test yeşil.
  - *Emek:* 1.0 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.30 puan.
- **1. Olmak İçin Gerekenler:** Streamable HTTP MCP SDK 2.x standardının harici istemcilerle sıfır hatayla konuşması, `/alexa` akıllı ekran simülatöründe ses ve görsel kartların kusursuz çalışması, friction log'un jüriye somut açık kaynak katkısı sunması.

---

### 2. Nebius x NVIDIA Global AI Hackathon
- **Argüman 1 (Teknik):** "NVIDIA Nemotron hızlı model olarak web navigasyonunda kullanılmış ancak karar katmanında akıl yürütme derinliği gösterilmemiş."
  - *Çözüm:* Nemotron'u konsey karar katmanına ve hata onarımına bağlamak; görev başına maliyeti "fast vs strong" karşılaştırmasıyla canlı token faturası üzerinden ölçmek.
  - *Ölçülebilir Kabul Kriteri:* `tests/test_nemotron_sponsor.py` içinde iki katmanlı yönlendirme ve maliyet tasarrufu testleri; pano `#savings` telemetrisi.
  - *Emek:* 2.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.55 puan.
- **Argüman 2 (Şüpheci):** "Tavily arama bonusu canlı anahtar olmadan test edilmiş (mock)."
  - *Çözüm:* Canlı web arama motoru arayüzünü bir araştırma senaryosuna bağlamak; Tavily anahtarı olduğunda otomatik canlıya geçen, olmadığında mock düşen mimariyi testle kanıtlamak.
  - *Ölçülebilir Kabul Kriteri:* `test_search_provider_fallback` testi; Tavily API arayüz testi.
  - *Emek:* 1.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.35 puan.
- **Argüman 3 (Tasarım / Ürün):** "Canlı sitelerde ilk koşuda eylem tekrarları (stuck) nedeniyle 2. koşuda sıfır çağrıya tam inilemedi."
  - *Çözüm:* Tekrarlanan tıklama tespit algoritmasını iyileştirmek, SPA rota geçişlerinde bekleme sürelerini optimize ederek temiz tarif kaydını artırmak.
  - *Ölçülebilir Kabul Kriteri:* Playwright SPA geçişlerinde 150ms DOM oturma gecikmesi; takılma tespitinde akıllı geri adım.
  - *Emek:* 2.0 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.45 puan.
- **1. Olmak İçin Gerekenler:** Hızlı ve ucuz Nemotron ile güçlü model arasındaki maliyet ve token tasarrufunu grafiklerle kanıtlamak, canlı web sitelerinde sıfır maliyetli tarif tekrarını göstermek.

---

### 3. Open Agent Hackathon 2026
- **Argüman 1 (Kural / Uygunluk):** "Tinkerer track kuralı: Mevcut projelerde yalnızca 15–20 Ekim build penceresinde yazılan yeni işler puanlanır; öncesinde yazılan kodlar diskalifiye sebebi olabilir."
  - *Çözüm:* 15 Ekim'e kadar projeye yeni modül kodu eklemeyi dondurmak. `docs/OPEN_AGENT_PLAN.md` dosyasında mimari planı ve 15–20 Ekim commit takvimini hazırlamak.
  - *Ölçülebilir Kabul Kriteri:* Git loglarında 15 Ekim öncesi yeni modül olmaması; `docs/OPEN_AGENT_PLAN.md` dosyasının hazır olması.
  - *Emek:* 1.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.80 puan.
- **Argüman 2 (Teknik):** "Çoklu ajan muhakemesi kapalı kutu; kararların gerekçesi açıkça izlenemiyor."
  - *Çözüm:* Her adımda `runs/<id>/explain.jsonl` kütüğüne neden, alternatifler, ekran görüntüsü kanıtı ve doğrulama sonucunu yazmak; pano üzerinde görselleştirmek.
  - *Ölçülebilir Kabul Kriteri:* `test_explainer_records_step` testinin yeşil olması; run sayfasında explain akışının render edilmesi.
  - *Emek:* 1.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.40 puan.
- **Argüman 3 (Etki / İş):** "Ajanın hata anında kendi kendini onarma yeteneği canlı sitelerde denenmedi."
  - *Çözüm:* Kırık seçici senaryosunda (S7) ajanın alternatif arama ve yama önerme adımlarını testle kanıtlamak.
  - *Ölçülebilir Kabul Kriteri:* `tests/test_realweb.py` içinde REC senaryosunun 100% toparlanması.
  - *Emek:* 1.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.35 puan.
- **1. Olmak İçin Gerekenler:** 15–20 Ekim build penceresinde temiz bir commit geçmişiyle konsey uzlaşı motorunun çoklu ajan koordinasyonunu ve şeffaf muhakeme izlerini sergilemek.

---

### 4. Vultr Agent Rush Hackathon
- **Argüman 1 (Teknik & Şüpheci):** "Vultr API entegrasyonu gerçek bir bulut hesabında denenmedi; yalnızca sahte yerel sunucuyla test edildi."
  - *Çözüm:* Dürüstlük bildirimini açıkça yapmak; VultrAPI yaşam döngüsünü (oluşturma, başlatma betiği `user_data`, sorgulama, temizleme) ve hata durumlarını sahte sunucu üzerinde eksiksiz test etmek; deploy betiğini (`scripts/deploy_vultr.sh`) hazır tutmak.
  - *Ölçülebilir Kabul Kriteri:* `tests/test_vultr_sandbox.py` (3 test) 100% yeşil; `README.md` ve kit dosyalarında dürüstlük notu.
  - *Emek:* 2.0 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.50 puan.
- **Argüman 2 (Tasarım & Demo):** "Tema 'Blast Radius Zero' ancak videoda bu izolasyon anı yeterince vurgulanmamış."
  - *Çözüm:* Demo videosunda veya ekran akışında ajanın bütçe aşımı veya yetkisiz erişim denemesinde sert kapıya çarpıp durdurulduğunu ve `blast_radius.json` kütüğünün üretildiğini net biçimde göstermek.
  - *Ölçülebilir Kabul Kriteri:* `blast_radius.json` dosyasında dosya, alan adı, süre ve harcama sınırlarının kayıt altına alınması.
  - *Emek:* 1.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.45 puan.
- **Argüman 3 (Ürün):** "Vultr Serverless Inference LLM çağrıları henüz bağlanmadı."
  - *Çözüm:* Vultr Serverless Inference uyumlu OpenAI-compatible endpoint desteğini router'a eklemek.
  - *Ölçülebilir Kabul Kriteri:* `Router` sınıfında `vultr` sağlayıcı konfigürasyonu.
  - *Emek:* 1.0 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.30 puan.
- **1. Olmak İçin Gerekenler:** "Blast Radius Zero" mimarisini izole Docker/Vultr ortamında kanıtlamak, ajanın kaçak işlem yapamayacağını `blast_radius.json` ile belgelemek.

---

### 5. OpenCV AI Competition
- **Argüman 1 (Teknik):** "Görüntü işleme yalnızca fark alma ve kontur bulmadan ibaret; derin bilgisayarlı görü veya nesne tanıma yok."
  - *Çözüm:* OpenCV 5 (5.0.0.93) kütüphanesini buton ve tıklama hedefi tespitinde, DOM kırılmalarında görsel Continue tespitiyle hibrit karar mekanizmasında kullanmak.
  - *Ölçülebilir Kabul Kriteri:* `tests/test_vision.py` ve `tests/test_vision_service.py` testlerinin yeşil olması.
  - *Emek:* 2.0 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.45 puan.
- **Argüman 2 (Etki / Şüpheci):** "Canlı AWS bulut dağıtımı yapılmamış."
  - *Çözüm:* `docs/OPENCV_AWS.md` rehberinde ECS/Fargate ve Lambda üzerinde OpenCV servisinin canlıya alınma adımlarını eksiksiz belgelemek.
  - *Ölçülebilir Kabul Kriteri:* AWS CloudFormation/CLI adımlarının dokümante edilmesi.
  - *Emek:* 1.0 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.30 puan.
- **Argüman 3 (Demo):** "Görsel tespitin tarayıcı adımını kurtardığı video sahnesi eksik."
  - *Çözüm:* Kontrollü görüntü setinde DOM seçicisi silindiğinde OpenCV'nin doğru butonu bulup tıkladığını gösteren test ve ekran kütüğü.
  - *Ölçülebilir Kabul Kriteri:* `test_vision_change_and_dom_recovery_are_measured` testinin %100 başarı vermesi.
  - *Emek:* 1.5 saat | *Beklenen Puan Kazancı (TAHMİN):* +0.35 puan.
- **1. Olmak İçin Gerekenler:** Web otomasyonunda DOM bozulduğunda OpenCV 5 tabanlı görsel onarımın görevi kesintisiz devam ettirdiğini kanıtlamak.

---

### 6. IEEE ClimateChain, YTU x Meta, ING, ASUS, Imagine Cup, Kestra
- **ClimateChain:**
  - *Kaybetme Nedeni:* Gerçek karbon veya iklim verisi olmaması; sahte defter.
  - *Çözüm:* Web sitelerindeki iklim iddialarını doğrulayan senaryo (`grasshopper/realweb/climate.py`) ve simüle defter kaydı; raporda açıkça "simülasyon" yazılması. Emek: 1.5s, Kazanç: +0.40.
- **YTU x Meta:**
  - *Kaybetme Nedeni:* Yerinde katılım şartı; Llama modelinin canlı çalışmaması.
  - *Çözüm:* Meta Llama modelini Nebius API üzerinden bir seçenek olarak eklemek; 4-6 Aralık yerinde katılım planını `INSAN_ISLERI.md` içine koymak. Emek: 1.5s, Kazanç: +0.45.
- **ING Hubs:**
  - *Kaybetme Nedeni:* Finansal güvenlik ve denetim izinin bankacılık standardına oturmaması.
  - *Çözüm:* Mock banka sandbox şablonunda çift onay kapısı, limit denetimi ve transfer reddi mekanizmasını kanıtlamak. Emek: 1.5s, Kazanç: +0.40.
- **ASUS UGen AI League:**
  - *Kaybetme Nedeni:* Hailo-10H NPU donanım testi olmaması.
  - *Çözüm:* 20 sayfalık teknik mimari sunum taslağı (`submissions/asus/PRESENTATION.md`) hazırlayarak edge AI mimarisini detaylandırmak. Emek: 2.0s, Kazanç: +0.35.
- **Imagine Cup:**
  - *Kaybetme Nedeni:* Canlı Azure AI anahtarlarının olmaması; öğrenci ekibi eksikliği.
  - *Çözüm:* `docs/IMAGINE_CUP_PLAN.md` içinde Azure OpenAI ve Azure Speech servislerinin entegrasyon mimarisini net belgelemek. Emek: 1.0s, Kazanç: +0.30.
- **Kestra Hacktober:**
  - *Kaybetme Nedeni:* Kestra resmi GitHub deposuna PR gönderilmemesi.
  - *Çözüm:* Kestra Grasshopper Plugin / Blueprint taslağını hazırlamak ve `INSAN_ISLERI.md` içinde Halil'in onayına sunmak. Emek: 1.5s, Kazanç: +0.40.

---

## 2. Kazanç / Emek Öncelik Sıralaması (ROI Ranking)

Aşağıdaki tablo tüm çözümleri getireceği tahmini puan kazancı ile harcanacak emek saati oranına göre sıralamaktadır:

| Sıra | Yarışma | Çözüm Konusu | Emek (Saat) | Puan Kazancı (TAHMİN) | Verimlilik (Puan/Saat) | Durum |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | **Open Agent** | 15 Ekim öncesi modül dondurma & mimari plan hazırlama | 1.5 | +0.80 | **0.53** | Plan hazır (`docs/OPEN_AGENT_PLAN.md`) |
| **2** | **Amazon (Alexa+)** | Resmi MCP Python SDK istemci uyumluluk testleri & <500ms gecikme | 3.0 | +0.65 | **0.22** | Aşama 5'te uygulanacak |
| **3** | **Nebius x NVIDIA** | Nemotron karar katmanı & fast vs strong görev başı maliyet ölçümü | 2.5 | +0.55 | **0.22** | Aşama 4'te uygulanacak |
| **4** | **Vultr** | VultrAPI yaşam döngüsü testleri & blast_radius.json izolasyon kanıtı | 2.0 | +0.50 | **0.25** | `tests/test_vultr_sandbox.py` tamamlandı |
| **5** | **Amazon (OSS)** | Gerçek build hatalarından derlenen sürtünme günlüğü kanıtları | 1.5 | +0.40 | **0.27** | `docs/FRICTION_LOG.md` tamamlandı |
| **6** | **OpenCV** | OpenCV 5 tabanlı görsel Continue butonu onarımı & testleri | 2.0 | +0.45 | **0.23** | `tests/test_vision.py` tamamlandı |
| **7** | **YTU x Meta** | Meta Llama modelinin Nebius üzerinden entegrasyonu ve testi | 1.5 | +0.45 | **0.30** | Aşama 4'te uygulanacak |
| **8** | **ING Hubs** | Bankacılık onay kapısı, limit ve denetim izi sandbox şablonu | 1.5 | +0.40 | **0.27** | Aşama 4'te uygulanacak |
| **9** | **ClimateChain** | İklim iddiası doğrulama senaryosu & simüle defter kaydı | 1.5 | +0.40 | **0.27** | Aşama 4'te uygulanacak |
| **10**| **Kestra** | Kestra blueprint/plugin taslağı hazırlığı | 1.5 | +0.40 | **0.27** | `INSAN_ISLERI.md` güncellenecek |
| **11**| **ASUS** | 20 sayfalık teknik mimari sunum taslağı | 2.0 | +0.35 | **0.18** | Aşama 4'te uygulanacak |
| **12**| **Imagine Cup** | Azure AI mimari bağlantı planı dokümantasyonu | 1.0 | +0.30 | **0.30** | `docs/IMAGINE_CUP_PLAN.md` tamamlandı |
