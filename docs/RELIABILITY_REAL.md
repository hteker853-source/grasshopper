# Gerçek site güvenilirliği

N=3. Provider: nebius (nvidia/Nemotron-3_5-Lightning). Gecikme: 0.35s.
1. koşu canlı LLM ile kararları üretir ve iz kaydeder; 2. koşu öğrenilen tarifi 0 model çağrısıyla yeniden oynatır.

## Güvenilirlik Tablosu

| Senaryo | Hedef | Koşu | Başarı Oranı | Ort. Adım | 1. Koşu LLM | 1. Koşu Token | 1. Koşu $ | 1. Koşu Süre | 2. Koşu (Tarif) | Not / Hata |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **R1** | books.toscrape üzerinde en ucuz 4 yıldız | 3 | 0/3 (0.0%) | 20.3 | 22 | 19272 | $0.003814 | 230.2s | 20 çağrı | stuck; time budget |
| **R2** | saucedemo'ya gir, iki ürün ekle, ödeme ö | 3 | 0/3 (0.0%) | 3.0 | 3 | 702 | $0.000140 | 10.9s | 3 çağrı | stuck |
| **R3** | Hacker News ilk üç başlığı özetle | 3 | 0/3 (0.0%) | 3.7 | 2 | 2220 | $0.000444 | 40.7s | 3 çağrı | stuck; time budget |
| **R4** | arXiv 'browser agents' aramasındaki son  | 3 | 0/3 (0.0%) | 4.0 | 6 | 2941 | $0.000588 | 39.2s | 3 çağrı | stuck |
| **R5** | the-internet dinamik yükleme, açılır lis | 3 | 0/3 (0.0%) | 2.0 | 5 | 1834 | $0.000108 | 41.6s | 5 çağrı | stuck |

## Bozulan Sayfa Toparlanma Tablosu

| Test Metriği | Deneme | Başarılı Toparlanma | Yüzde |
| :--- | :---: | :---: | :---: |
| Kontrollü görüntü seti (değişiklik ayrımı) | 20 | 20 | 100% |
| DOM kimliği silinmiş kontrolde Continue seçimi | 20 | 20 | 100% |
| Canlı sitede kasıtlı HTML değişikliği | - | - | ölçülmedi (üçüncü parti sayfa değiştirilmedi) |
| REC senaryosu (yerel bozuk sayfa toparlanması) | 1 | 1 | 100% |

## Senaryo Detayları

## R1

- Koşu: 3
- Başarı: 0/3 (0.0%)
- Ortalama adım: 20.3
- Ortalama token: 24247
- Toplam gerçek harcama: $0.013914
- 1. koşu LLM çağrısı: 22
- 1. koşu token: 19272
- 1. koşu $: $0.003814
- 1. koşu süre: 230.2s
- 2. koşu (tarif) LLM çağrısı: 20
- Hatalar: stuck; time budget

## R2

- Koşu: 3
- Başarı: 0/3 (0.0%)
- Ortalama adım: 3.0
- Ortalama token: 702
- Toplam gerçek harcama: $0.000421
- 1. koşu LLM çağrısı: 3
- 1. koşu token: 702
- 1. koşu $: $0.000140
- 1. koşu süre: 10.9s
- 2. koşu (tarif) LLM çağrısı: 3
- Hatalar: stuck

## R3

- Koşu: 3
- Başarı: 0/3 (0.0%)
- Ortalama adım: 3.7
- Ortalama token: 3280
- Toplam gerçek harcama: $0.001968
- 1. koşu LLM çağrısı: 2
- 1. koşu token: 2220
- 1. koşu $: $0.000444
- 1. koşu süre: 40.7s
- 2. koşu (tarif) LLM çağrısı: 3
- Hatalar: stuck; time budget

## R4

- Koşu: 3
- Başarı: 0/3 (0.0%)
- Ortalama adım: 4.0
- Ortalama token: 1840
- Toplam gerçek harcama: $0.001104
- 1. koşu LLM çağrısı: 6
- 1. koşu token: 2941
- 1. koşu $: $0.000588
- 1. koşu süre: 39.2s
- 2. koşu (tarif) LLM çağrısı: 3
- Hatalar: stuck

## R5

- Koşu: 3
- Başarı: 0/3 (0.0%)
- Ortalama adım: 2.0
- Ortalama token: 1831
- Toplam gerçek harcama: $0.000323
- 1. koşu LLM çağrısı: 5
- 1. koşu token: 1834
- 1. koşu $: $0.000108
- 1. koşu süre: 41.6s
- 2. koşu (tarif) LLM çağrısı: 5
- Hatalar: stuck

## Okuma

Ölçülen 15 koşunun 0'i başarılı: %0. Provider: nebius (nvidia/Nemotron-3_5-Lightning). 1. koşularda toplam 38 canlı LLM çağrısı yapıldı ve BudgetLedger ile harcama $0.017731 olarak ölçüldü. Canlı LLM çağrılarında döngü takılma tespiti (stuck) ve süre bütçesi tetiklendi; başarılı iz tamamlanamadığında 2. koşuda tarif oynatılamadı.

## Harcama

Bu bankonun gerçek `cost_usd` toplamı: $0.017731.
Canlı Nebius Nemotron çağrılarının gerçek maliyeti BudgetLedger'dan geçmiştir. Mock çağrılarda maliyet 0 iken gerçek çağrılarda non-zero harcama doğrulanmıştır.
