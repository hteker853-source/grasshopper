# Alexa+ Geliştirici Portalı MCP Entegrasyon Kılavuzu

Bu belge, Grasshopper'ın Model Context Protocol (MCP) Streamable HTTP sunucusunu Amazon Alexa+ geliştirici konsoluna bağlama adımlarını, manifest şablonunu ve örnek konuşma akışlarını içerir.

---

## 1. Geliştirici Portalı Yapılandırma Adımları

### Adım 1: Alexa Developer Console'a Giriş
1. [developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask) adresine gidin.
2. **Create Skill** butonuna tıklayın.
3. Skill adı: `Grasshopper Worker`.
4. Model seçimi: **Alexa+ AI Assistant / Tool Calling** veya **Custom**.

### Adım 2: MCP Endpoint Bağlama
1. Sol menüden **Tools & Integrations** > **Model Context Protocol (MCP)** sekmesine tıklayın.
2. **Endpoint Type**: `Streamable HTTP` seçin.
3. **Endpoint URL**:
   - Yerel test / Demo için: `make share-mcp` ile üretilen Cloudflare tünel adresi (örn: `https://xyz.trycloudflare.com/mcp/`).
   - Üretim için: AWS App Runner HTTPS adresi (örn: `https://grasshopper.us-east-1.awsapprunner.com/mcp/`).
4. **Authentication**: `Bearer Token` seçin.
   - Header: `Authorization: Bearer <MCP_BEARER_TOKEN>`
5. **Allowed Origins**: `https://alexa.amazon.com`.

### Adım 3: Araç Keşfi (Tool Discovery)
1. **Discover Tools** butonuna basın.
2. Konsol `/mcp/` endpoint'ine `tools/list` isteği atarak Grasshopper'ın 8 aracını otomatik olarak listeler:
   - `start_task(text)`
   - `get_task_status(task_id)`
   - `get_task_result(task_id)`
   - `run_task(text)`
   - `list_pending_approvals()`
   - `approve(approval_id, decision)`
   - `store_check_old_listings(months)`
   - `council_ask(question)`

---

## 2. Geliştirici Doğrulama (cURL Komutları)

Alexa+ konsoluna bağlamadan önce uç noktanızı terminalden test edin:

### A. Sunucu Başlatma ve Protokol El Sıkışması
```bash
curl -X POST https://your-domain.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {},
      "clientInfo": {"name": "alexa-plus-tester", "version": "1.0.0"}
    }
  }'
```

### B. Araç Listeleme (tools/list)
```bash
curl -X POST https://your-domain.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

### C. Sesli Görev Başlatma (start_task)
```bash
curl -X POST https://your-domain.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "start_task",
      "arguments": {
        "text": "books.toscrape.com üzerinde 4 yıldızlı en ucuz kitabı bul"
      }
    }
  }'
```
*Dönen Yanıt:*
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"task_id\": \"task_01j...\", \"status\": \"queued\", \"speech\": \"Göreviniz alındı: books.toscrape.com üzerinde 4 yıldızlı.... Tarayıcıda başlatılıyor.\"}"
      }
    ]
  }
}
```

---

## 3. Skill Manifest Şablonu (`skill.json`)

```json
{
  "manifest": {
    "publishingInformation": {
      "locales": {
        "en-US": {
          "name": "Grasshopper Browser Worker",
          "summary": "Autonomous web browser agent connected via MCP",
          "description": "Multi-step web automation, price checking, and shop administration with risk-gated human approvals."
        },
        "tr-TR": {
          "name": "Grasshopper Tarayıcı İşçisi",
          "summary": "MCP üzerinden bağlanan otonom web ajanı",
          "description": "Çok adımlı web otomasyonu, fiyat araştırması ve insan onay kapılı mağaza yönetimi."
        }
      }
    },
    "apis": {
      "custom": {
        "endpoint": {
          "uri": "https://your-domain.com/mcp/",
          "sslCertificateType": "Wildcard"
        },
        "interfaces": [
          {
            "type": "MODEL_CONTEXT_PROTOCOL",
            "version": "2025-11-25"
          }
        ]
      }
    }
  }
}
```

---

## 4. Örnek Diyalog Akışları

### Senaryo 1: Mağaza İlan Denetimi
> **Kullanıcı:** "Alexa, Grasshopper'a söyle eski ilanlarımı kontrol etsin."
>
> **Alexa (MCP -> `store_check_old_listings(months=4)`):** "Göreviniz alındı. Mağazanıza giriş yapılıyor ve 4 aydan eski ilanlar taranıyor."
>
> *(Ajan arka planda çalışır, 3 eski ilan tespit eder)*
>
> **Kullanıcı:** "Alexa, Grasshopper ne durumda?"
>
> **Alexa (MCP -> `get_task_status(task_id)`):** "Göreviniz tamamlandı. 4 aydan eski 3 adet pasif ilan bulundu, fiyat güncelleme önerileri panonuzda hazır."

### Senaryo 2: Fiyat Araştırması ve Çok Adımlı Veri Aktarımı
> **Kullanıcı:** "Alexa, Grasshopper'a en ucuz 4 yıldızlı kitabı bulmasını ve yazarını özetlemesini söyle."
>
> **Alexa (MCP -> `start_task(...)`):** "Göreviniz alındı: En ucuz 4 yıldızlı kitap aranıyor ve Wikipedia'dan yazar özeti derleniyor."
>
> **Alexa (Tamamlandığında):** "Araştırma bitti. Bulunan kitap 'A Light in the Attic', fiyatı 51.77 Pound. Yazarı Shel Silverstein, Amerikalı şair ve karikatürist."

### Senaryo 3: Riskli İşlemde Sesli Onay Kapısı
> **Alexa:** "Dikkat, Grasshopper'dan bildirim: 0.50 SOL tutarında abonelik ödemesi için onayınız gerekiyor. Onaylıyor musunuz?"
>
> **Kullanıcı:** "Evet, onaylıyorum."
>
> **Alexa (MCP -> `approve(approval_id, 'approved')`):** "İşlem onaylandı. Ödeme güvenli sınır dahilinde devnet üzerinde tamamlandı."
