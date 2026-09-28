# Yarışma Portföyü, Gelir Modeli ve Emek Planı (INCOME PLAN)

> [!IMPORTANT]
> **Dürüstlük ve Yöntem Bildirimi:** Bu belgedeki olasılık ve Beklenen Değer (EV) hesaplamaları yapay zekâ jürisi puanlarına ve korelasyonlu Monte Carlo simülasyonuna (`scripts/ev_model.py`) dayanır. Finansal bir taahhüt değil, stratejik planlama kılavuzudur.

---

## 1. 19 Yarışmanın Takvimi ve Nakit Potansiyeli

| Sınıf | Yarışma | Son Tarih | 1. Ödülü (Nakit) | Toplam Havuz | Zorunlu Sponsor Teknolojisi |
| --- | --- | --- | --- | --- | --- |
| **A** | **Amazon Build, Ship, Shape** | 23 Ekim 2026 | $25.000 (Alexa+) + $5.000 (OSS) | $54.000 | Alexa+ / MCP Streamable HTTP |
| **A** | **Nebius Token Factory** | 30 Ekim 2026 | $20.000 | $45.000 | NVIDIA Nemotron / Nebius Studio API |
| **A** | **Vultr Agent Rush** | 08 Kasım 2026 | $9.000 | $15.000 | Vultr Cloud API / Sandbox Runner |
| **A** | **Open Agent Hackathon** | 20 Ekim 2026 | $8.000 | $15.000 | Open Agent Function Calling |
| **B** | **ASUS UGen AI (Stage I)** | 14 Ekim 2026 | Stage II Cihazı + $10.000 | $20.000 | ROG NPU / Yerel Donanım |
| **B** | **OpenCV AI Competition** | 26 Ekim 2026 | $5.000 | $12.000 | OpenCV 5 + AWS Cloud |
| **B** | **Build With AI** | 26 Ekim 2026 | $3.000 | $8.000 | Gemini / Multi-agent |
| **B** | **ClimateChain** | 31 Ekim 2026 | $2.000 | $5.000 | Yeşil İddia Doğrulama + Web3 |
| **B** | **Imagine Cup 2027** | 08 Ocak 2027 | $100.000 | $100.000 | Azure AI Foundry + Azure Speech |
| **C** | **ING Hackathon** | 04–09 Ekim | Staj / İş Teklifi (Nakit Yok) | - | ING Bankacılık Sandbox |
| **C** | **YTU x Meta Llama** | 11 Ekim 2026 | 50.000 TL (~$1.400) | ~$3.000 | Meta Llama 3 (İstanbul Yerinde Katılım) |
| **C** | **Kestra Automation** | 15 Ekim 2026 | Bulut Kredisi | Kredi | Kestra Workflows |
| **C** | **Hackster Nordic** | 20 Ekim 2026 | Donanım Kiti | Donanım | Nordic nRF54 |
| **C** | **AssemblyAI Voice** | 30 Eylül 2026 | $2.500 | $5.000 | AssemblyAI Lemur |
| **C** | **Arbiter Protocol** | 01 Kasım 2026 | Kredi / Token | Kredi | Arbiter Consensus |
| **C** | **HETİC Digital** | 15 Kasım 2026 | Sertifika | - | Paris Yerinde |
| **D** | **Gemma Sprint** | 18 Ekim 2026 | Kredi ($1.000) | Kredi | Gemma 2 |
| **D** | **Solana Radar / Colosseum** | Kapsam Dışı | $25.000 | $500.000 | Devnet kuralı gereği girilmez |

---

## 2. '20.000$ Ortalama' Varsayımının Gerçeklik Testi

Halil'in *"19 yarışmadan 20.000$ ortalama ile kazanç"* varsayımı analiz edilmiştir:

1. **Matematiksel İmkânsızlık:** 19 yarışmada 20.000$ ortalama, toplam **380.000$** nakit kazanç gerektirir. 19 yarışmanın tüm 1.lik ödülleri toplansa dahi nakit havuz ~$180.000'dir (Imagine Cup hariç, o da Ocak 2027'de öğrenci/kurucu şartlıdır). Dolayısıyla bu varsayım **gerçekçi değildir**.
2. **Toplamda 20.000$+ Nakit Kazanma İhtimali:**
   - **Ayı (Bear) Senaryosu:** %1.1
   - **Taban (Base) Senaryosu:** **%2.0** (Beklenen Değer: **$1.601**)
   - **Boğa (Bull) Senaryosu:** **%2.8** (Beklenen Değer: **$2.290**)
3. **Hangi Yarışmalar Olmadan 20.000$ İmkânsız?**
   - **Amazon ($25.000) ve Nebius ($20.000)** portföyün nakit motorudur.
   - Bu iki yarışmada 1.lik alınmadığı sürece portföydeki diğer tüm yarışmalar kazanılsa bile (Vultr $9.000 + Open Agent $8.000 + OpenCV $5.000 = $22.000 ama hepsi aynı anda kazanılamaz) 20.000$ nakite ulaşmak istatistiksel olarak mümkün değildir.

---

## 3. Emek Bütçesi (Kişi-Saat Dağılımı)

Toplam Halil Emek Bütçesi: **60 Saat** (Günde ortalama 2.5 saat, 24 gün boyunca).

| Kategori | Saat Bütçesi | Açıklama |
| --- | --- | --- |
| **Amazon Alexa+ & OSS Mini** | 18 saat | Canlı video çekimi, AWS App Runner deploy, Alexa Developer Console portal testi, friction log. |
| **Nebius Token Factory** | 10 saat | Canlı Nebius API anahtarı testi, video seslendirmesi, Devpost formu. |
| **Vultr Agent Rush** | 8 saat | Gerçek Vultr sunucu testi, sandbox video ekran kaydı, form. |
| **Open Agent** | 8 saat | 15-20 Ekim arası yeni modül commitleri, Tinkerer videosu. |
| **ASUS Stage I** | 4 saat | 20 sayfalık sunumun (`submissions/asus/PRESENTATION.md`) PDF'e çevrilmesi, sesli slayt videosu. |
| **OpenCV AI** | 4 saat | Vision service AWS App Runner testi, 2 dakikalık video. |
| **Tüm Diğerleri (Form/Yedek)**| 8 saat | Hızlı başvuru ve yedek kontrol. |
| **TOPLAM** | **60 saat** | |

---

## 4. Kritik Riskler

1. **Tek Elenme Nedeni (Disqualification):**
   - *Video süresi:* 3 dakikayı 1 saniye bile aşan videolar birçok jüride (Amazon, ASUS, Vultr) otomatik 0 puan alır. Çözüm: `videos/demo.mp4` 62 saniyedir.
   - *Zorunlu sponsor teknolojisi:* Amazon'da MCP kullanılmazsa veya Nebius'ta Nemotron kullanılmazsa proje değerlendirmeye dahi alınmaz.
   - *Tarih ihlali:* Open Agent yarışmasında 15 Ekim öncesi commit'ler yeni sayılamaz. `docs/OPEN_AGENT_PLAN.md` takvimine sadık kalınmalıdır.
2. **Sponsor Anahtarı Riski:**
   - Bedrock veya Vultr için canlı bakiye sağlanamazsa, proje sahte sunucu modunda kalır. Dürüstlük kuralı gereği bu durum formda açıkça beyan edilmeli, puan kırılması göze alınmalıdır.
3. **Yerinde Katılım Şartı:**
   - YTU x Meta (İstanbul Aralık finali) ve HETİC (Paris) fiziki varlık gerektirebilir. Halil gidemeyecekse bu yarışmalara emek harcanmamalıdır.

---

## 5. Net Stratejik Öneri: Nereye Odaklanmalı?

### ✅ Odaklanılacak 5 Yarışma (Tüm Enerjiyi Buraya Verin):
1. **Amazon Build, Ship, Shape (23 Ekim):** En yüksek EV ve nakit potansiyeli ($30.000 nakit havuzu). MCP sunucumuz ve Web Speech arayüzümüz tam hazırdır.
2. **Nebius Token Factory (30 Ekim):** $20.000 nakit birincilik ödülü. Nemotron entegrasyonu, token muhasebesi ve sıfır maliyetli tarif mimarisi kusursuz oturmuştur.
3. **Vultr Agent Rush (08 Kasım):** $9.000 nakit birincilik. Blast Radius Zero raporlaması ve sandbox container izolasyonu tam uyumludur.
4. **Open Agent Hackathon (20 Ekim):** $8.000 nakit birincilik. 15–20 Ekim arasında temiz bir commit serisi ile kazanılabilir.
5. **ASUS UGen AI Stage I (14 Ekim):** 20 sayfalık hazır sunumla sıfır kod geliştirme maliyetiyle Stage II cihazına hak kazanma potansiyeli.

### ❌ Kesinlikle Atlanması Gereken Yarışmalar:
- **Solana Radar / Colosseum:** Mainnet RPC şartı veya kısıtları nedeniyle AGENTS.md kuralı gereği elenmiştir.
- **AssemblyAI:** 30 Eylül tarihi için anahtar ve test yoktur; emek yetişmez.
- **Kestra, Arbiter, HETİC, Nordic:** Nakit ödül yoktur (yalnızca donanım, kredi veya sertifika). Zaman kaybıdır.
- **ING:** 2. ekip üyesi bulunamıyorsa veya kurumsal staj hedefi yoksa pas geçilmelidir.
