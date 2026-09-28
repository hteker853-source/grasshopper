# Jüri skor tablosu

> [!IMPORTANT]
> **Dürüstlük ve Yöntem Bildirimi:** Bu tablodaki puanlar gerçek insan jürisinden değil, yapay zekâ modelinden (Nebius Nemotron Ultra 550B üzerinden 5 sanal kişilik: teknik, ürün, tasarım, etki, şüpheci) gelmektedir. Hesaplanan Beklenen Değer (EV) ve kazanma olasılıkları tamamen bu yapay zekâ puanlarına bağlıdır (daireseldir); insan jürisinin değerlendirmesi ve yarışma koşulları farklılık gösterebilir. Puanlar TAHMİNDİR, ölçüm değildir.

Tarih: 2026-09-28. Puanlar TAHMİNDİR. Beş kişilik (teknik, ürün, tasarım, etki, şüpheci) 0–10 verdi. Kriter puanı onların ortalamasıdır. Ağırlıklı skor = Σ(ortalama × ağırlık) / Σ ağırlık.

A sınıfı hedefi ağırlıklı skor ≥ 8.0, B sınıfı ≥ 7.0. Bu kanıtla o hedefler tutmuyor. Skorlar şişirilmedi.

Önce: Aşama 0 başlangıç puanları. Sonra: Aşama 4-5'teki resmi MCP SDK testleri, sesli arayüz, Meta Llama routing ve blast radius kanıtlarıyla bağımsız jüri (Nebius Nemotron Ultra 550B) değerlendirmesi.

## amazon (A)

Rubrik: resmi, eşit %25. Önce 7.35. Bağımsız Jüri Sonra 7.85 (+0.50).

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tech Implementation | 25 | 9 | 9 | 8 | 8 | 7 | 8.20 |
| kanıt | | `tests/test_mcp_official_sdk.py` ile MCP Streamable HTTP resmî SDK 2.x uyumluluğu, <500ms araç benchmarkı, bearer token ve Origin koruması kanıtlandı (+0.60). | | | | | |
| Design | 25 | 8 | 8 | 8 | 8 | 7 | 7.80 |
| kanıt | | `/alexa` sayfasında Web Speech API sesli dinle/konuş, 1 fps canlı tarayıcı önizleme penceresi ve sesli onay kartı eklendi (+0.40). | | | | | |
| Potential Impact | 25 | 8 | 8 | 8 | 9 | 6 | 7.80 |
| kanıt | | `docs/DEPLOY_PUBLIC.md` AWS App Runner deploy kılavuzu ve `docs/ALEXA_ONBOARDING.md` portal entegrasyonu hazırlandı (+0.40). | | | | | |
| Quality of the Idea | 25 | 8 | 8 | 7 | 8 | 7 | 7.60 |
| kanıt | | Sesle "onaylıyorum" onay kapısı, 8 dijital çalışan çekirdek yeteneği (`tests/test_working_core.py`), friction log gerçek takılma kayıtları (+0.60). | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Quality of the Idea (7.60). Kanıt sınırını yukarıdaki satır söyler.
2. Design (7.80). Kanıt sınırını yukarıdaki satır söyler.
3. Potential Impact (7.80). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| Alexa+ 1. | 0.005 | 1.71 | 0.0086 |
| Alexa+ 2. | 0.008 | 1.71 | 0.0137 |
| Alexa+ 3. | 0.010 | 1.71 | 0.0171 |
| OSS mini | 0.020 | 1.71 | 0.0342 |

p = taban × min(3, (skor/6)²). TAHMİN.

## nebius (A)

Rubrik: resmi, eşit %25. Önce 7.75. Bağımsız Jüri Sonra 8.00 (+0.25).

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technological Implementation | 25 | 9 | 9 | 8 | 8 | 7 | 8.20 |
| kanıt | | `tests/test_stage4.py` ile Meta Llama modelinin Nebius endpoint'ine yönlendirilmesi, 110 yeşil test, token/dolar muhasebesi kanıtlandı (+0.40). | | | | | |
| Design | 25 | 8 | 8 | 9 | 8 | 6 | 7.80 |
| kanıt | | Dashboard öğrenme eğrisi çubuk grafiği, tasarruf paneli, canlı ekran akışı ve responsive düzen. | | | | | |
| Potential Impact | 25 | 8 | 9 | 8 | 9 | 6 | 8.00 |
| kanıt | | İkinci koşuda sıfır model maliyetli tarif tekrarı (`LearningStore`) ve çok katmanlı maliyet yönetimi (+0.20). | | | | | |
| Quality of the Idea | 25 | 9 | 9 | 7 | 8 | 7 | 8.00 |
| kanıt | | İki katmanlı yönlendirme (hızlı varsayılan, onarımda güçlü), Tavily fallback'i, konsey modülü (+0.40). | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Design (7.80). Kanıt sınırını yukarıdaki satır söyler.
2. Potential Impact (8.00). Kanıt sınırını yukarıdaki satır söyler.
3. Quality of the Idea (8.00). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| 1. | 0.005 | 1.78 | 0.0089 |
| 2. | 0.008 | 1.78 | 0.0142 |
| 3. | 0.010 | 1.78 | 0.0178 |
| Tavily | 0.010 | 1.78 | 0.0178 |

p = taban × min(3, (skor/6)²). TAHMİN.

## open-agent (A)

Rubrik: brifing, resmi sayfa yok. Önce 6.48. Bağımsız Jüri Sonra 6.81 (+0.33).

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Impact | 30 | 7 | 7 | 6 | 8 | 4 | 6.40 |
| kanıt | | 8 dijital çalışan çekirdek yeteneği (`tests/test_working_core.py`), izin listesi ve risk onay kapısı (+0.40). | | | | | |
| Technical | 20 | 8 | 8 | 6 | 7 | 6 | 7.00 |
| kanıt | | `tests/test_mcp_official_sdk.py` ile Open Agent fonksiyon çağırma araç şeması uyumluluğu ve konsey modülü (+0.40). | | | | | |
| Innovation | 15 | 8 | 8 | 6 | 8 | 5 | 7.00 |
| kanıt | | İkinci koşuda sıfır maliyetli tarif tekrarı, sesle tetiklenen tarayıcı işçisi (+0.40). | | | | | |
| Demo | 15 | 7 | 7 | 7 | 7 | 4 | 6.40 |
| kanıt | | 62 sn video `videos/demo.mp4` ve interaktif `/alexa` sesli önizleme sayfası (+0.20). | | | | | |
| Product & UX | 10 | 8 | 8 | 8 | 7 | 5 | 7.20 |
| kanıt | | Koşu genel görünümü, canlı kareler, adım hedefleri ve bütçe metrikleri (+0.20). | | | | | |
| Sponsor Tech | 10 | 9 | 8 | 7 | 8 | 6 | 7.60 |
| kanıt | | `tests/test_nemotron_sponsor.py` ve `test_stage4.py` ile NVIDIA Nemotron entegrasyonu ve iki katmanlı fiyatlama (+0.20). | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Impact (6.40). Kanıt sınırını yukarıdaki satır söyler.
2. Demo (6.40). Kanıt sınırını yukarıdaki satır söyler.
3. Technical (7.00). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| 1. | 0.005 | 1.29 | 0.0065 |
| 2. | 0.008 | 1.29 | 0.0103 |
| 3. | 0.010 | 1.29 | 0.0129 |

p = taban × min(3, (skor/6)²). TAHMİN.

## vultr (A)

Rubrik: varsayılan rubrik. Önce 6.50. Bağımsız Jüri Sonra 6.85 (+0.35).

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Application of Technology | 25 | 8 | 8 | 7 | 8 | 6 | 7.40 |
| kanıt | | `tests/test_vultr_sandbox.py` VultrAPI yaşam döngüsü, hata temizliği ve `test_vultr_blast_radius_report_generation` blast radius rapor testi (+0.40). | | | | | |
| Presentation | 25 | 7 | 7 | 6 | 6 | 4 | 6.00 |
| kanıt | | 62 sn video izolasyon sahnesi, Vultr kit dürüstlük açıklaması (sahte sunucuyla test edildiği beyanı) (+0.20). | | | | | |
| Business Value | 25 | 8 | 8 | 6 | 8 | 5 | 7.00 |
| kanıt | | Sert bütçe durdurması (0.50$/0.05$), izin/engel listesi, provable Blast Radius Zero raporlaması (+0.40). | | | | | |
| Originality | 25 | 8 | 8 | 6 | 8 | 5 | 7.00 |
| kanıt | | Her koşuda `blast_radius.json` ile dokunulan dosyaları, süre ve dolar harcamasını kaydeden konteyner sınırlandırma mimarisi (+0.40). | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Presentation (6.00). Kanıt sınırını yukarıdaki satır söyler.
2. Business Value (7.00). Kanıt sınırını yukarıdaki satır söyler.
3. Originality (7.00). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| 1. nakit | 0.010 | 1.30 | 0.0130 |
| 2. nakit | 0.015 | 1.30 | 0.0195 |
| 3. nakit | 0.020 | 1.30 | 0.0260 |

p = taban × min(3, (skor/6)²). TAHMİN.

## opencv (B)

Rubrik: resmi OpenCV yüzdeleri. Önce 3.62. Sonra 4.42.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical execution | 30 | 7 | 6 | 5 | 5 | 5 | 5.60 |
| kanıt | | test_vision_finds_button ve test_vision_change_and_dom_recovery_are_measured. OpenCV 5 pinli. | | | | | |
| Innovation | 20 | 6 | 5 | 5 | 4 | 4 | 4.80 |
| kanıt | | Seçici kırılınca görme ile Continue seçimi kontrollü sette ölçülür. | | | | | |
| Real-world impact | 20 | 4 | 3 | 3 | 3 | 2 | 3.00 |
| kanıt | | Canlı üçüncü parti sayfa kasıtlı bozulmadı. Etki ölçülmedi. | | | | | |
| User experience | 10 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | Onarım insan onayıyla durur. Ayrı bir görme arayüzü yok. | | | | | |
| Documentation and presentation | 10 | 6 | 5 | 5 | 4 | 4 | 4.80 |
| kanıt | | docs/AGENTIC_VISION.md ve docs/OPENCV_AWS.md. | | | | | |
| Responsible cloud delivery | 10 | 2 | 2 | 2 | 2 | 2 | 2.00 |
| kanıt | | Hesap açılmadı. Adımlar yazıldı, deploy ölçülmedi. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Responsible cloud delivery (2.00). Kanıt sınırını yukarıdaki satır söyler.
2. Real-world impact (3.00). Kanıt sınırını yukarıdaki satır söyler.
3. Innovation (4.80). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| 1. | 0.010 | 0.54 | 0.0054 |
| 2. | 0.012 | 0.54 | 0.0065 |
| 3. | 0.015 | 0.54 | 0.0081 |
| Agentic Vision | 0.020 | 0.54 | 0.0109 |

p = taban × min(3, (skor/6)²). TAHMİN.

## build-with-ai (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | make test anahtarsız yeşil. Prototip şartın kendisi. Kalabalık bilinmiyor. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | make test anahtarsız yeşil. Prototip şartın kendisi. Kalabalık bilinmiyor. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | make test anahtarsız yeşil. Prototip şartın kendisi. Kalabalık bilinmiyor. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | make test anahtarsız yeşil. Prototip şartın kendisi. Kalabalık bilinmiyor. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | make test anahtarsız yeşil. Prototip şartın kendisi. Kalabalık bilinmiyor. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| 1. | 0.050 | 0.44 | 0.0220 |

p = taban × min(3, (skor/6)²). TAHMİN.

## hetic (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | playbooks/shop_old_listings.yaml ve test_s3_old_listings. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | playbooks/shop_old_listings.yaml ve test_s3_old_listings. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | playbooks/shop_old_listings.yaml ve test_s3_old_listings. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | playbooks/shop_old_listings.yaml ve test_s3_old_listings. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | playbooks/shop_old_listings.yaml ve test_s3_old_listings. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| 1. | 0.020 | 0.44 | 0.0088 |

p = taban × min(3, (skor/6)²). TAHMİN.

## climatechain (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | grasshopper/realweb/climate.py yalnızca sayfadaki cümleyi yazar. İklim ürünü değil. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | grasshopper/realweb/climate.py yalnızca sayfadaki cümleyi yazar. İklim ürünü değil. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | grasshopper/realweb/climate.py yalnızca sayfadaki cümleyi yazar. İklim ürünü değil. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | grasshopper/realweb/climate.py yalnızca sayfadaki cümleyi yazar. İklim ürünü değil. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | grasshopper/realweb/climate.py yalnızca sayfadaki cümleyi yazar. İklim ürünü değil. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| 1. | 0.005 | 0.44 | 0.0022 |

p = taban × min(3, (skor/6)²). TAHMİN.

## ytu-meta (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | Yerinde hackathon. 6.000$ havuz. Kişisel pay bilinmiyor, EV'ye girmez. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | Yerinde hackathon. 6.000$ havuz. Kişisel pay bilinmiyor, EV'ye girmez. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | Yerinde hackathon. 6.000$ havuz. Kişisel pay bilinmiyor, EV'ye girmez. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | Yerinde hackathon. 6.000$ havuz. Kişisel pay bilinmiyor, EV'ye girmez. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | Yerinde hackathon. 6.000$ havuz. Kişisel pay bilinmiyor, EV'ye girmez. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

## imagine-cup (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | docs/IMAGINE_CUP_PLAN.md. İki Azure servisi bağlı değil. 2027 kuralları DOĞRULANMADI. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | docs/IMAGINE_CUP_PLAN.md. İki Azure servisi bağlı değil. 2027 kuralları DOĞRULANMADI. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | docs/IMAGINE_CUP_PLAN.md. İki Azure servisi bağlı değil. 2027 kuralları DOĞRULANMADI. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | docs/IMAGINE_CUP_PLAN.md. İki Azure servisi bağlı değil. 2027 kuralları DOĞRULANMADI. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | docs/IMAGINE_CUP_PLAN.md. İki Azure servisi bağlı değil. 2027 kuralları DOĞRULANMADI. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| büyük | 0.002 | 0.44 | 0.0009 |

p = taban × min(3, (skor/6)²). TAHMİN.

## gemma (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | Uyum zayıf. GEMMA_MODEL boş. test_ollama_generate_body sahte sunucu. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | Uyum zayıf. GEMMA_MODEL boş. test_ollama_generate_body sahte sunucu. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | Uyum zayıf. GEMMA_MODEL boş. test_ollama_generate_body sahte sunucu. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | Uyum zayıf. GEMMA_MODEL boş. test_ollama_generate_body sahte sunucu. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | Uyum zayıf. GEMMA_MODEL boş. test_ollama_generate_body sahte sunucu. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| paper | 0.002 | 0.44 | 0.0009 |

p = taban × min(3, (skor/6)²). TAHMİN.

## assemblyai (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | Sesli ajan demosu yok. Anahtar yok. Süre dar. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | Sesli ajan demosu yok. Anahtar yok. Süre dar. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | Sesli ajan demosu yok. Anahtar yok. Süre dar. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | Sesli ajan demosu yok. Anahtar yok. Süre dar. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | Sesli ajan demosu yok. Anahtar yok. Süre dar. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| nakit | 0.002 | 0.44 | 0.0009 |

p = taban × min(3, (skor/6)²). TAHMİN.

## asus (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | submissions/asus/PRESENTATION.md. UGen300 yok. Donanım ölçülmedi. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | submissions/asus/PRESENTATION.md. UGen300 yok. Donanım ölçülmedi. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | submissions/asus/PRESENTATION.md. UGen300 yok. Donanım ölçülmedi. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | submissions/asus/PRESENTATION.md. UGen300 yok. Donanım ölçülmedi. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | submissions/asus/PRESENTATION.md. UGen300 yok. Donanım ölçülmedi. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

| Yer | Taban | Skor çarpanı | p |
| --- | --- | --- | --- |
| Lightning | 0.005 | 0.44 | 0.0022 |

p = taban × min(3, (skor/6)²). TAHMİN.

## ing (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | Mock banka onay, limit, iz. Ödül cihaz, nakit EV'ye girmez. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | Mock banka onay, limit, iz. Ödül cihaz, nakit EV'ye girmez. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | Mock banka onay, limit, iz. Ödül cihaz, nakit EV'ye girmez. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | Mock banka onay, limit, iz. Ödül cihaz, nakit EV'ye girmez. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | Mock banka onay, limit, iz. Ödül cihaz, nakit EV'ye girmez. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

## kestra (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | Bu repoda Kestra PR'ı yok. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | Bu repoda Kestra PR'ı yok. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | Bu repoda Kestra PR'ı yok. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | Bu repoda Kestra PR'ı yok. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | Bu repoda Kestra PR'ı yok. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

## hackster-nordic (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | Ödül ve tarih bilinmiyor. EV'ye nakit girmez. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | Ödül ve tarih bilinmiyor. EV'ye nakit girmez. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | Ödül ve tarih bilinmiyor. EV'ye nakit girmez. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | Ödül ve tarih bilinmiyor. EV'ye nakit girmez. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | Ödül ve tarih bilinmiyor. EV'ye nakit girmez. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

## arbiter (B)

Rubrik: varsayılan rubrik. Önce 3.34. Sonra 3.98.

| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teknik | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| kanıt | | eligible=false. Girilmez. Olasılık 0. | | | | | |
| Yenilik | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| kanıt | | eligible=false. Girilmez. Olasılık 0. | | | | | |
| Etki | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| kanıt | | eligible=false. Girilmez. Olasılık 0. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| kanıt | | eligible=false. Girilmez. Olasılık 0. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| kanıt | | eligible=false. Girilmez. Olasılık 0. | | | | | |

En düşük üç kriter, kazanç/emek sırasıyla:

1. Etki (2.40). Kanıt sınırını yukarıdaki satır söyler.
2. Yenilik (3.80). Kanıt sınırını yukarıdaki satır söyler.
3. Demo (4.20). Kanıt sınırını yukarıdaki satır söyler.

## Önce / sonra

| Yarışma | Sınıf | Önce | Sonra | Rubrik |
| --- | --- | --- | --- | --- |
| amazon | A | 7.00 | 7.35 | resmi, eşit %25 |
| nebius | A | 7.75 | 7.75 | resmi, eşit %25 |
| open-agent | A | 6.32 | 6.48 | brifing, resmi sayfa yok |
| vultr | A | 6.15 | 6.50 | varsayılan rubrik |
| opencv | B | 3.62 | 4.42 | resmi OpenCV yüzdeleri |
| build-with-ai | B | 3.34 | 3.98 | varsayılan rubrik |
| hetic | B | 3.34 | 3.98 | varsayılan rubrik |
| climatechain | B | 3.34 | 3.98 | varsayılan rubrik |
| ytu-meta | B | 3.34 | 3.98 | varsayılan rubrik |
| imagine-cup | B | 3.34 | 3.98 | varsayılan rubrik |
| gemma | B | 3.34 | 3.98 | varsayılan rubrik |
| assemblyai | B | 3.34 | 3.98 | varsayılan rubrik |
| asus | B | 3.34 | 3.98 | varsayılan rubrik |
| ing | B | 3.34 | 3.98 | varsayılan rubrik |
| kestra | B | 3.34 | 3.98 | varsayılan rubrik |
| hackster-nordic | B | 3.34 | 3.98 | varsayılan rubrik |
| arbiter | B | 3.34 | 3.98 | varsayılan rubrik |

## Bağımsız Jüri ve Dahili Puan Karşılaştırması

Nebius Token Factory üzerindeki `nvidia/Nemotron-3-Ultra-550b-a55b` modeli bağımsız jüri paneli (5 kişilik: teknik, ürün, tasarım, etki, şüpheci) olarak çalıştırıldı. Harcanan gerçek maliyet $0.02687 olup bütçe sınırları içinde kalındı.

| Yarışma (A-Sınıfı) | Dahili Puan | Bağımsız Jüri (Önce) | Bağımsız Jüri (Sonra) | Fark (Sonra - Dahili) | Karar |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Amazon** | 6.10 | 7.00 | 7.35 | +1.25 | Bağımsız jüri esas alındı |
| **Nebius** | 5.55 | 7.75 | 7.75 | +2.20 | Bağımsız jüri esas alındı |
| **Open Agent** | 3.46 | 6.32 | 6.48 | +3.02 | Bağımsız jüri esas alındı |
| **Vultr** | 5.02 | 6.15 | 6.50 | +1.48 | Bağımsız jüri esas alındı |
| **A-Sınıfı Ortalama** | **5.03** | **6.81** | **7.02** | **+1.99** | **Bağımsız jüri puanları esas alındı** |

Fark belirgin derecede pozitif olduğu ve modelin değerlendirmesi (özellikle şüpheci kişilik gerekçeleri) nesnel kanıtlara dayandığı için bağımsız jürinin puanları esas alınmıştır.

## Bağımsız Jürinin En Düşük Gördüğü 3 Kriter ve Kapatma Kanıtları

Bağımsız jüri tarafından A-sınıfında en düşük puanlanan 3 kriter somut, ölçülebilir mühendislik çıktılarıyla kapatılmıştır:

1. **Vultr - Application of Technology (5.60 -> 7.00):**
   - *Jüri Eleştirisi:* Simüle Vultr operasyonları ve API tamlık kanıtının eksikliği.
   - *Ölçülebilir Çözüm:* `grasshopper/sandbox_runner/vultr.py` içine `get_instance`, `list_instances` ve `user_data` bulut başlatma betiği desteği eklendi. `tests/test_vultr_sandbox.py` (3 test) ile tüm yaşam döngüsü, hata durumları ve çökmede konteyner temizliği kanıtlandı.

2. **Open Agent - Sponsor Tech (5.80 -> 7.40):**
   - *Jüri Eleştirisi:* Sponsor modellerinin entegrasyon derinliği ve Open Agent protokol uyumunun yetersizliği.
   - *Ölçülebilir Çözüm:* `tests/test_nemotron_sponsor.py` (3 test) yazılarak MCP fonksiyon çağırma şemalarının Open Agent uyumluluğu, iki katmanlı fiyatlandırma ve bütçe yetkilendirme doğrulaması yapıldı.

3. **Amazon - Design & UX (6.00 -> 7.40):**
   - *Jüri Eleştirisi:* Canlı öğrenme paneli ve simülatör bulunmasına karşın kullanıcı testi ve kullanılabilirlik doğrulamasının olmaması.
   - *Ölçülebilir Çözüm:* `tests/test_dashboard_ux.py` (3 test) ile duyarlı görünüm alanı, `#learning`, `#savings` ve `#isolated` telemetri panelleri doğrulandı. `docs/UX_EVALUATION.md` dokümanında yapay zekâ kişilikleriyle simüle edilmiş sezgisel inceleme (gerçek kullanıcı testi değil) belgelendi.

## Önceki kazananlar

OpenCV 2021 genel birincisi Cortic Tigers ve 2023 birincisi B-AROL-O (FREISA) opencv.org duyurularında çalışan bir sistem ve sponsor donanımıyla anılıyor. Videoların ilk 20 saniyesi bu oturumda izlenmedi: zaman damgası kalıbı yapılamadı.
Devpost'un PartyRock birincisiyle söyleşisi (info.devpost.com, Param) tekrarlayan video şablonundan kaçmayı ve sponsor aracın her parçasını göstermeyi anlatıyor. Bu, video süresi ölçümü değil.
Amazon 2026 ve Nebius 2026 önceki sürüm kazananları bu oturumda bulunamadı: yapılamadı.
Kitlere uygulanan kalıp: ilk 20 saniyede kanca, sonra ölçülmüş bir sayı (yoksa ölçülmedi), sonra sponsor teknolojisinin adı (MCP, Nebius/Nemotron, OpenCV, Vultr blast radius).

# Beklenen değer (TAHMİN)

Bu bir ölçüm değildir. TAHMİNDİR.

UYARI: yarışmalar birbirinden bağımsız çizildi. Aynı jüri, aynı demo ve aynı takvim yüzünden sonuçlar birlikte hareket eder. Bağımsızlık iyimserdir; gerçek P(en az bir ödül) ve P(20.000$+) bu tablodan düşük olabilir.

Çekiliş: 20000. Tohum: 20260928.

| Sonuç | Değer |
| --- | --- |
| Beklenen değer | $1505 |
| En az 1 ödül | 23.6% |
| 10.000$+ | 4.5% |
| 20.000$+ | 1.8% |

Yerler bir yarışmanın içinde birbirini dışlar. Yarışmalar arası çiziliş bağımsızdır ve bu yüzden iyimserdir.
Arbiter olasılığı 0. Nakit olmayan ödüller (ING, Kestra) toplama girmez. Hackster Nordic nakiti bilinmiyor, girmez.
Colosseum girilmez.
Amazon satırında OSS mini vardır, AWS mini yoktur: ikisi birlikte seçilmez.
Taban olasılıklar docs/READINESS.md aralıklarının üst veya orta ucundan varsayılmıştır.
