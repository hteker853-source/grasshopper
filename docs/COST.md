# Maliyet tavanı

Tarih: 2026-09-28. Fiyatlar katalog tahminidir. Mock çağrının gerçek faturası 0'dır. Canlı sağlayıcı faturası bu dosyada ölçülmedi.

## Tavan

| Kapı | Değer | Nerede |
| --- | --- | --- |
| Günlük | 0.50 $ | `BUDGET_USD_DAILY` |
| Koşu başına | 0.05 $ | `BUDGET_USD_PER_RUN` |

Router her çağrıdan önce istem uzunluğundan token sayar (`len/4`) ve kısa bir yanıt payı (64 token) ekler. Tahmin tavanı aşarsa çağrı yapılmaz, görev `failed` olur, bildirim `kind=budget` ile gider. Telegram ancak token ve izinli kullanıcı ikisi de doluysa o bildirimi iletir.

Mock çağrı da katalog fiyatını rezerve eder. Böylece anahtar sonradan açılınca aynı iş tavanı delmez. Çağrı satırındaki `cost_usd` mock için 0 kalır. Günlük "harcama" raporu gerçek `cost_usd` toplamıdır. Bu oturumda o toplam 0'dır çünkü faturalı çağrı yapılmadı.

## Katalog (1.000 token)

| Katman | $ |
| --- | --- |
| fast | 0.0002 |
| strong | 0.003 |
| vision | 0.004 |
| repair | 0.0004 |

Kaynak: `grasshopper/core/budget.py` `PRICE_PER_1K`. Nebius faturasıyla karşılaştırma ölçülmedi.

## Bedrock

Varsayılan kapalı. `ALLOW_BEDROCK=1` olmadan anahtarlar dolu olsa da istemci mock'tur. Kanıt: `test_bedrock_converse_is_stubbed`.

## Gerçek site

Kod listesi `grasshopper/realweb/policy.py` `CODE_ALLOWLIST`: books.toscrape.com, quotes.toscrape.com, saucedemo.com, the-internet.herokuapp.com, webscraper.io, wikipedia.org, arxiv.org, news.ycombinator.com, github.com. Alt alan adları dahildir. Ortam değişkeni `REAL_SITES_ALLOWLIST` yalnızca bu kümeyi daraltır.

Reddedilenler: etsy.com, amazon.* perakende alanları, sosyal medya, Google giriş, PayPal/Stripe, allowlist dışındaki ödeme yolları, github.com/login. `robots.txt` Disallow uygulanır. İstekler arasında `REAL_SITE_DELAY_SEC` (varsayılan 1) beklenir. Crawl-delay daha büyükse o uygulanır. Localhost sandbox dışarıdadır.

Kanıt: `tests/test_budget_policy.py`.

## Kapsam Dışı Alanlar ve Güvenlik Gerekçeleri (Out of Scope)

Aşağıdaki kategoriler Grasshopper'ın otonom yürütme kapsamı dışına çıkarılmıştır:

1. **Canlı Finansal Ödemeler ve Kredi Kartı İşlemleri:**
   - *Gerekçe:* Otonom ajanların yetkisiz para transferi, kart çekimi veya bakiye tüketimi riskini sıfıra indirmek. Para hareketleri yalnızca sandbox veya Solana devnet üzerinde simüle edilir; her işlem mutlaka `ApprovalGate` ile insan onayına sunulur.
2. **Giriş Gerektiren Gerçek Hesaplar (Google Login, E-posta, Bankacılık vb.):**
   - *Gerekçe:* Kullanıcı kimlik bilgilerinin (parola, 2FA, session token) sızma riskini önlemek ve sitelerin anti-bot kullanım koşullarına (ToS) tam uyum sağlamak.
3. **Sosyal Medya Platformları (Twitter/X, LinkedIn, Meta/Instagram vb.):**
   - *Gerekçe:* Otonom spam, yetkisiz içerik paylaşımı ve platform kazıma engellerine takılmamak. Ajan yalnızca izin listesindeki açık kaynaklarda (arXiv, Wikipedia, HN, kitap katalogları) gezinir.

