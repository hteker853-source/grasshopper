# Yarışma Envanter Matrisi (Competition Matrix)

Tarih: 2026-09-28  
Son Güncelleme: Görev 10 Aşama 1  
Kural: "Çalışıyor" demek için kanıt (test adı, koşu kimliği veya ölçüm) şarttır; kanıtsız durumlar "ölçülmedi" veya "test edilmedi" olarak etiketlenmiştir. Uydurma veri yoktur.

---

## 1. Genel Envanter Tablosu (19 Yarışma)

| No | Yarışma | Ödül | Tarih / Build Penceresi | Katılım & Ekip | Jüri Kriterleri & Ağırlıkları | Koddaki Karşılığı | Durum & Kanıt | Eksikler & Beklentiler | Doğrulama Durumu |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Amazon Build, Ship, Shape (Alexa+)** | 25K/15K/4K$ nakit + AWS kredisi; OSS mini 5K$, AWS Builder 5K$ | 23 Ekim 2026 12:00 PT | Bireysel veya ekip (1-5 kişi) | Tech (%25), Design (%25), Impact (%25), Quality (%25) | `grasshopper/mcp_server/`, `grasshopper/channels/alexa_sim.py`, `/alexa` | **ÇALIŞIYOR** (`test_s9_mcp_client`, `test_dashboard_ux.py`, 97 test yeşil) | Alexa-AI CLI cihaz testi insan işidir; canlı Bedrock anahtarı yok. | doğrulanmadı (brifing ~15.800 kişi; Devpost resmi sayfa kuralları esas alındı) |
| **2** | **Nebius x NVIDIA Global AI** | 20K/10K/6K$ nakit + Tavily 3K$ + Jetson | 30 Ekim 2026 23:59 PT | Bireysel veya ekip | Tech (%25), Design (%25), Impact (%25), Quality (%25) | `grasshopper/providers/factory.py`, `grasshopper/core/router.py` | **ÇALIŞIYOR** (41 canlı LLM çağrısı, $0.0238 harcama, `test_nemotron_sponsor.py`) | Tavily canlı anahtarı boş (mock arama aktif). | doğrulanmadı (nakit basamakları brifing; eşit ağırlık resmi Devpost'tan) |
| **3** | **Open Agent Hackathon** | 8K/4K/2K$ nakit (20K$ havuz) | Kayıt 13 Ekim, Build 15-20 Ekim | Tinkerer Track (mevcut projeler) | Impact (%30), Tech (%20), Innovation (%15), Demo (%15), UX (%10), Sponsor (%10) | `grasshopper/core/explainer.py`, `docs/OPEN_AGENT_PLAN.md` | **ÇALIŞIYOR** (`test_s5_council`, `test_explainer_records_step`, `test_nemotron_sponsor.py`) | 15 Ekim'e kadar yeni modül kodu yazılamaz (kural gereği donduruldu). | doğrulanmadı (brifing basamakları; genai.works resmi rubrik) |
| **4** | **OpenCV AI Competition** | 5K/3K/2K$ + 1K$ Agentic Vision | 26 Ekim 2026 | Bireysel veya ekip | Tech Execution (%30), Innovation (%20), Impact (%20), UX (%10), Presentation (%20) | `grasshopper/browser/vision.py`, `vision_service/` | **ÇALIŞIYOR** (`test_vision_finds_button`, `test_vision_service_app`, OpenCV 5.0.0.93) | Canlı AWS bulut dağıtımı yapılmadı (`docs/OPENCV_AWS.md` rehberdir). | doğrulanmadı (ödüller ve rubrik resmi siteden; teklif aşaması doğrulanmadı) |
| **5** | **Vultr Agent Rush** | 9K$ nakit + 5K$ kredi (1.: 5K$) | 3–8 Kasım 2026 | Bireysel veya ekip | Tech (%25), Presentation (%25), Business (%25), Originality (%25) | `grasshopper/sandbox_runner/vultr.py`, `runs/blast_radius.json` | **ÇALIŞIYOR (MOCK/FAKE)** (`tests/test_vultr_sandbox.py` fake server ile 3/3 yeşil) | Gerçek fonlanmış Vultr hesabı bağlanmadı; canlı VM deploy edilmedi. | doğrulanmadı (lablab.ai ikincil kaynak kuralları) |
| **6** | **IEEE ClimateChain** | 1.5K/1K/0.5K$ nakit (3K$ havuz) | 5–25 Ekim 2026 | Bireysel veya ekip | İklim etkisi, blockchain doğrulaması, uygulanabilirlik | `grasshopper/realweb/climate.py` | **ÇALIŞIYOR (SİMÜLASYON)** (`tests/test_climate.py`) | Gerçek IoT/iklim sensör verisi yok; Türkiye uygunluğu doğrulanmadı. | doğrulanmadı (Devpost sayfası esas alındı) |
| **7** | **YTU x Meta Student Hackathon** | 6.000 $ ödül havuzu | Başvuru 11 Ekim, Final 4-6 Aralık (Yerinde) | Öğrenci ekibi (İstanbul yerinde katılım) | Teknik yenilik, Llama kullanımı, prototip kalitesi | `grasshopper/providers/factory.py` (`meta` sağlayıcı) | **ANAHTAR BEKLİYOR** (`WHATSAPP_TOKEN`, `META_API_KEY` boş) | Yerinde katılım insan işidir; jüri puanlama tablosu henüz ilan edilmedi. | doğrulanmadı (YTU Startup House duyurusu) |
| **8** | **ING Hubs Agentic AI** | 2 MacBook Neo / 2 iPad / 2 Apple Watch | Başvuru 4 Ekim, Build 9-18 Ekim, Final 3 Kas | 2-4 kişilik ekip, Türkiye | İş etkisi, teknik mimari, finansal güvenlik | `grasshopper/core/gate.py`, `grasshopper/core/budget.py` | **ÇALIŞIYOR** (`test_gate_approvals`, `test_wallet_limits`) | Nakit ödül yok (cihaz ödülü); konular 9 Ekim'de açıklanacak. | doğrulanmadı (ING Hubs Türkiye resmi duyurusu) |
| **9** | **Kestra Hacktober** | MacBook Neo / iPad / Swag | 1–31 Ekim 2026 | Bireysel GitHub katkısı | PR kalitesi, eklenti (plugin) veya blueprint kullanışlılığı | `submissions/kestra/` | **İNSAN İŞİ** (Bu repodan Kestra reposuna PR açılması insan işidir) | Kestra resmi reposuna PR gönderilmedi. | doğrulanmadı (kestra.io duyurusu) |
| **10** | **ASUS UGen AI League** | 4.5K$ + UGen300 (Hailo-10H 40 TOPS) | Stage I: 14 Ekim 2026 | Bireysel veya ekip | Donanım uyumu, yerel NPU performansı, yenilik | `submissions/asus/PRESENTATION.md` | **TEST EDİLMEDİ (DONANIM YOK)** | UGen300 donanımı veya Hailo NPU'su bulunmadığı için yerel çıkarım ölçülmedi. | doğrulanmadı (ASUS UGen AI League / Bhuntr) |
| **11** | **Microsoft Imagine Cup 2027** | 100.000 $ büyük ödül | Son başvuru: 8 Ocak 2027 | Öğrenci ekibi, küresel | Etki, teknoloji derinliği (Azure AI), iş modeli | `docs/IMAGINE_CUP_PLAN.md` | **ANAHTAR BEKLİYOR** (`AZURE_OPENAI_ENDPOINT`, `AZURE_SPEECH_KEY`) | Canlı Azure aboneliği ve anahtarları bağlanmadı; 2027 kuralları doğrulanmadı. | doğrulanmadı (Microsoft resmi kaynakları) |
| **12** | **Meta Global AI Developer** | Büyük ödül havuzu (nakit + Llama teşvikleri) | TBA (Henüz ilan edilmedi) | Bireysel veya ekip | Llama modelleriyle geliştirme, küresel etki | `grasshopper/providers/factory.py` | **ANAHTAR BEKLİYOR** | Tarih ve resmi kurallar resmi sayfada henüz netleşmedi. | doğrulanmadı |
| **13** | **Build With AI: Basics** | 2.500 $ nakit | 26 Ekim 2026 | Bireysel / genel | Çalışan prototip, problem çözme | Çekirdek ajan motoru (`grasshopper/`) | **ÇALIŞIYOR** (97 test yeşil, `make run`) | Prototip hazır, başvuru formunun doldurulması insan işidir. | doğrulanmadı (Devpost sayfası) |
| **14** | **AI GENESIS (lablab.ai)** | Sertifika + hızlandırıcı imkanı | 2 Kasım 2026 | lablab ekibi | Ajan otonomisi, çoklu adım yürütme | `grasshopper/core/orchestrator.py` | **ÇALIŞIYOR** (`test_stage4.py`, `test_orchestrator`) | Nakit ödül net değil; topluluk oylaması gerektirir. | doğrulanmadı (lablab.ai) |
| **15** | **Rise of AI Agents (lablab.ai)**| Sertifika + sponsor teşvikleri | 3 Kasım 2026 | lablab ekibi | Ajan mimarisi, güvenilirlik | `grasshopper/realweb/engine.py` | **ÇALIŞIYOR** (`test_realweb.py`) | Nakit ödül net değil. | doğrulanmadı (lablab.ai) |
| **16** | **Kaggle Gemma 4 Paper Track** | 35.000 $ nakit | 12 Kasım 2026 | Bireysel veya ekip | Akademik yenilik, Gemma mimarisi, makale formatı | `grasshopper/providers/llm_mock.py` | **TEST EDİLMEDİ (ZAYIF UYUM)** | GEMMA_MODEL boş; akademik makale yazılmadı; repoya uyumu zayıf. | doğrulanmadı (Kaggle) |
| **17** | **HETIC AI Agents for Founders** | 1.100 $ nakit | 18 Aralık 2026 | Girişimciler / kurucular | Kurucu odaklı otomasyon, maliyet tasarrufu | `grasshopper/publish/live_feed.py`, shop playbooks | **ÇALIŞIYOR** (`test_s3_old_listings`, `#savings` paneli) | Başvuru metninin Fransızca/İngilizce uyarlanması insan işidir. | doğrulanmadı (brifing) |
| **18** | **AssemblyAI Voice Agent** | 10.000 $ nakit + kredi | 30 Eylül 2026 23:59 PT | Bireysel veya ekip | Ses doğruluğu, gecikme, akıllı ajan | `grasshopper/providers/stt_assemblyai.py` | **ANAHTAR BEKLİYOR** (`ASSEMBLYAI_API_KEY` boş) | Süre çok dar (30 Eylül); canlı ses pipeline'ı anahtarsız test edilemez. | doğrulanmadı (Devpost) |
| **19** | **Colosseum / Arbiter** | Çeşitli | Ekim / Aralık 2026 | Özel | - | `eligible=false` | **GİRİLMEYECEK** | Karar: Colosseum ve Arbiter kapsam dışı bırakıldı (olasılık = 0). | doğrulanmadı |

---

## 2. Yapılmamış veya Yarım Kalanlar (Gaps & Incomplete Items)

Aşağıdaki liste koddaki gerçek durumu ve tamamlanmamış parçaları eksiksiz beyan eder:

1. **Yalnızca Mock / Fake Üzerinde Çalışan Yollar:**
   - **Vultr Bulut Dağıtımı:** `grasshopper/sandbox_runner/vultr.py` içerisindeki API entegrasyonu yalnızca `tests/fakes/vultr_app.py` sahte sunucusu ve yerel Docker ile test edilmiştir. Canlı bir Vultr API anahtarı ve kredi kartıyla gerçek sanal makine açılmamış ve SSH tüneli kurulmamıştır.
   - **Amazon Bedrock:** `botocore.stub.Stubber` ile sahte yanıt test edilmiş olup (`ALLOW_BEDROCK=1`), canlı AWS hesabı üzerinden faturalı Bedrock çağrısı yapılmamıştır.
   - **Tavily Arama:** `TAVILY_API_KEY` tanımlı olmadığı için arama katmanı çevrimdışı yerel dizine (mock) düşmektedir.
   - **Meta / WhatsApp:** `WHATSAPP_TOKEN` ve `META_API_KEY` bulunmadığından canlı WhatsApp Webhook testi yapılamamış, yalnızca simüle router açık tutulmuştur.
   - **Solana Devnet Cüzdanı:** `WALLET_KEYPAIR_PATH` tanımlanmadığı için cüzdan işlemleri mock defter üzerinde simüle edilmektedir.

2. **Kanıtsız İddialar ve Düzeltmeler:**
   - **Kullanıcı Testi:** Gerçek insan kullanıcılarla saha testi yapılmamıştır. [docs/UX_EVALUATION.md](docs/UX_EVALUATION.md) içindeki veriler yapay zekâ kişilikleriyle simüle edilmiş sezgisel inceleme ve otomatik DOM testleridir.
   - **Canlı Web Öğrenmesi:** Öğrenilen tariflerle sıfır model çağrısı yerel fixtürlerde (`tests/test_realweb.py`) kanıtlanmış; canlı sitelerde (saucedemo, books.toscrape) eylem tekrarları nedeniyle takılma tespitine girilerek 2. koşuda sıfır çağrıya tam ulaşılamadığı dürüstçe belgelenmiştir ([RELIABILITY_REAL.md](docs/RELIABILITY_REAL.md)).
   - **Jüri Puanları ve EV:** Puanlar insan jürisinin kararı değil, yapay zekâ modelinin (Nebius Nemotron Ultra 550B) tahminidir. Monte Carlo EV hesabı bu puanlara dairesel olarak bağımlıdır.

3. **İnsan Eline Kalan Maddeler (Otomasyon Kapsamı Dışındakiler):**
   - **Yarışma Başvuru Formları:** Hiçbir yarışma platformuna (Devpost, lablab.ai, genai.works vb.) otomatik form gönderimi yapılamaz; son başvuru insan tarafından yapılmalıdır.
   - **Kestra PR Gönderimi:** Kestra Hacktober ödülü için resmi depoya PR açılması insan işidir.
   - **YTU x Meta Hackathon:** 4–6 Aralık tarihlerinde İstanbul Maslak'ta yerinde fiziki katılım gerekmektedir.
   - **ASUS UGen Donanım Testi:** Hailo-10H NPU donanımı olmadan yerel çıkarım süresi ölçülemez.
