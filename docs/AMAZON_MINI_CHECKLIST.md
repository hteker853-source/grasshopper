# Amazon Build, Ship, Shape — Open Source Mini Checklist

> **Önemli Not**: Bu dosya insan incelemesi içindir (Halil gözden geçirmeli). Otomatik başvuru yapılmaz.
> Seçilen Mini: **Open Source Mini** ($5,000 nakit + $5,000 AWS kredisi). Bedrock'a çağrı yapılmaz (`ALLOW_BEDROCK=0`), tamamen açık kaynak bileşenlerle çalışır.

## 1. Katılım ve Uygunluk Kriterleri

- [x] **Açık Kaynak Lisansı**: MIT Lisansı repo kökünde (`LICENSE`) mevcuttur.
- [x] **Kamuya Açık Depo**: Kod kamuya açık GitHub reposu veya incelenebilir yerel git deposu olarak hazırlanmıştır.
- [x] **Hackathon Zaman Penceresi**: Tüm geliştirmeler, friction log kayıtları ve benchmark ölçümleri hackathon süresi içinde üretilmiştir.
- [x] **Bağımsız Çalışabilirlik (0 API Anahtarı)**: Grasshopper varsayılan olarak `mock` modunda çalışır (`MODE=mock`, `LLM_FAST_PROVIDER=mock`). Sıfır harcama ve sıfır dış bağımlılıkla `make test` ve `make judge` çalıştırılabilir.
- [x] **Bedrock Ayrımı**: Open Source mini track seçildiği için Bedrock kullanılmaz (`ALLOW_BEDROCK=0`). Açık model ağırlıkları (Ollama, HuggingFace veya OpenAI-uyumlu yerel/açık modeller) desteklenir.

## 2. Teknik Gereksinimler (Alexa+ MCP ve Açık Mimari)

- [x] **Resmî MCP Python SDK Entegrasyonu**: Starlette/FastAPI üzerine kurulu `mcp.server.mcpserver.MCPServer` ile `/mcp` uç noktasında Streamable HTTP standardı.
- [x] **Sesli Hero Flow (`/alexa`)**:
  1. Sesli komut veya doğal dil girdisi (`orb` / `btn-listen` / metin kutusu)
  2. MCP Araç çağrısı (`start_task` / `get_task_status`)
  3. Canlı tarayıcı önizlemesi (1 FPS `/live/frame.png`)
  4. Sesli ve görsel insan onay kartı (`approval-card` / `list_pending_approvals` / `approve`)
  5. Konuşma özeti ve blast radius geri bildirimi (`speech` ve `blast_radius.json`)
- [x] **Güven Katmanı (Trust & Safety)**:
  - `get_audit_log` MCP aracı ile yapılan işlemlerin geriye dönük denetimi.
  - Blast radius özeti: Değiştirilen dosya sayısı, ziyaret edilen domain sayısı ve harcanan dolar tutarı.
  - Onay kapısı (Approval Gate): Harici API çağrıları, dosya değişiklikleri veya hassas buton tıklamaları öncesinde insan onayı bekleme.
  - Bütçe tavanı (Budget Cap): Günlük $0.50 ve koşu başına $0.05 tavan limitleri (`BudgetLedger`).
- [x] **Tek Komutla Tekrarlanabilirlik**:
  - `make judge`: Tohumlanmış 60 saniyelik jüri demosu.
  - `make test`: Tüm birim ve entegrasyon testleri yeşil (110+ test).
  - `make audit`: Uygunluk ve güvenlik denetimi yeşil.

## 3. Teslim Varlıkları (Submission Assets)

- [x] **Proje Açıklaması**: `submissions/amazon/DESCRIPTION.md` (İngilizce, mimari detayları, gerçek koşu kimlikleri).
- [x] **Video Senaryosu**: `submissions/amazon/VIDEO_SCRIPT.md` (180 saniyenin altında, adım adım zaman çizelgesi: 0:00–0:20 giriş, 2:45–3:00 kapanış).
- [x] **Friction Log**: `submissions/amazon/FRICTION_LOG.md` (Geliştirme esnasında karşılaşılan gerçek sorunlar: MCP SDK 2.x session task group, Playwright Chromium yol ayrımı, DOM selector repair `run_9f24d8fa5fad`, arXiv API ve token limitleri).
- [x] **Statik Replay Sayfası**: `site/index.html` (Jüri için ekran görüntüleri ve adım adım oynatma).

## 4. İnsan İşleri Özeti (Halil'in Yapacakları)

1. Devpost portalına giriş yap (`https://amazonappdev2026.devpost.com/`).
2. Birincil kategori: **Alexa+ Track**, Mini kategori: **Open Source Mini** seç.
3. `submissions/amazon/DESCRIPTION.md` metnini forma yapıştır.
4. Çekilen demoyu (`videos/amazon_demo.mp4`) YouTube/Vimeo/Loom'a yükleyip video linkini gir.
5. GitHub repo linkini (`https://github.com/.../grasshopper`) ekle.
6. Son onayı ver ve gönder.
