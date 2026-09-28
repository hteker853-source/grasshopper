# Alexa+ & Model Context Protocol (MCP) Toolkit Product Feedback

> **Tarih**: 2026-09-28  
> **Konu**: Grasshopper projesinde Alexa+ simülatörü ve resmî MCP Python SDK (`mcp.server.mcpserver`) entegrasyonu sırasında elde edilen ürün geri bildirimleri, karşılaşılan mimari pürüzler ve öneriler.

---

## 1. Yönetici Özeti

Grasshopper, tarayıcı otomasyonunu ve web görevlerini harici ajanlarla paylaşmak için Anthropic ve Amazon'un benimsediği Model Context Protocol (MCP) Streamable HTTP standardını (`/mcp`) kullanmaktadır. Bu entegrasyon sırasında geliştirici deneyimini (DX) olumlu yönde etkileyen güçlü yönlerin yanı sıra, özellikle sesli arayüzler ve insan denetimli (Human-in-the-loop) sistemlerde karşılaşılan bazı eksikler ve iyileştirme fırsatları tespit edilmiştir.

---

## 2. Olumlu Yönler (Neler Çok İyi Çalıştı?)

1. **Streamable HTTP Standardı**: WebSocket yerine standart HTTP POST üzerinden JSON-RPC 2.0 ve SSE desteği sunması, Starlette/FastAPI mikro servisleri içine kolayca monte edilmesini (`streamable_http_app`) sağladı.
2. **Dekoratör Odaklı Araç Tanımlama**: `@mcp_server.tool()` ile Python tip ipuçlarının otomatik olarak JSON şemasına dönüştürülmesi entegrasyon süresini ciddi oranda kısalttı.
3. **Protokol Şeffaflığı**: Alexa+ veya Claude gibi harici istemcilerin aracın yeteneklerini (`initialize`, `tools/list`) dinamik olarak keşfedebilmesi kusursuz çalıştı.

---

## 3. Karşılaşılan Pürüzler ve Zorluklar (Friction Points)

### 3.1. ASGI Lifespan ve Session Manager Başlatma
- **Sorun**: MCP Python SDK 2.x sürümünde `FastMCP` yerine `MCPServer` sınıfına geçildiğinde, doğrudan Starlette uygulaması monte edildiğinde arka plan görev grubu (`session_manager.run()`) başlatılmadığı için istemciden gelen ilk çağrıda `RuntimeError: Task group is not initialized` hatası alındı.
- **Çözüm**: FastAPI `lifespan` yöneticisi içinde `asyncio.create_task(mcp_server.session_manager.run())` çağrılarak oturum yöneticisinin sunucuyla birlikte yaşaması sağlandı.
- **Öneri**: `streamable_http_app` fonksiyonu kendi lifespan'ını yönetebilmeli veya ebeveyn ASGI uygulamasına bağlanırken bu gereksinimi açık bir uyarı veya hazır bir lifespan context manager ile sağlamalıdır.

### 3.2. Çift Yönlü İnsan Onayı (Human-in-the-Loop Elicitation)
- **Sorun**: MCP protokolü şu an istemciden sunucuya doğru bir RPC modeli sunmaktadır. Ancak otonom bir tarayıcı ajanı kritik bir butona (örn. "Satın Al", "Sil", "Ödeme Yap") basmadan önce kullanıcıdan veya Alexa'dan sesli onay almak zorundadır. Sunucunun istemciye "Onay bekliyorum" şeklinde proaktif bildirim göndermesi standart bir şemaya sahip değildir.
- **Çözüm**: Grasshopper'da `list_pending_approvals` ve `approve` adında iki yönlü yoklama (polling) araçları tanımlandı ve `/alexa` arayüzü bu araçları 3 saniyede bir yoklayarak sesli onay kartını tetikledi.
- **Öneri**: MCP spesifikasyonuna resmî bir `notifications/request_approval` veya `tools/elicit` akışı eklenerek istemcinin kullanıcıya interaktif onay kartı açması standartlaştırılmalıdır.

### 3.3. Sesli Yanıtlar ve Blast Radius Standardizasyonu
- **Sorun**: Alexa+ gibi sesli asistanlar için araç yanıtlarının hem makine tarafından işlenebilir JSON verisi hem de kullanıcıya seslendirilebilir kısa, anlaşılır bir metin (`speech`) içermesi gerekir.
- **Çözüm**: Grasshopper MCP araçları yanıtlarında `speech` ve `blast_radius` ("2 dosya, 1 domain, $0.00 maliyet") alanlarını birleştirerek döndürdü.
- **Öneri**: MCP Tool şemasına opsiyonel `metadata.speech_summary` veya `display_text` standardı eklenmesi, sesli asistan geliştiricileri için büyük bir standartlaşma sağlar.

---

## 4. Sonuç ve Önerilen Yol Haritası

| Öncelik | Öneri | Etki |
| :---: | :--- | :--- |
| **Yüksek** | ASGI Lifespan entegrasyonu için tek satırlık bağlayıcı helper | Başlangıç hatalarını (%100) önler |
| **Yüksek** | Standart Human-in-the-Loop Onay / Elicitation spesifikasyonu | Ajan güvenliğini ekosistem genelinde artırır |
| **Orta** | Sesli arayüzler için `speech` / seslendirme şablonu standardı | Alexa+ entegrasyonunu hızlandırır |
