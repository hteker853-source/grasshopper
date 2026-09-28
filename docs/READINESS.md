# Hazırlık ve kazanma potansiyeli

Tarih: 2026-09-28. Kanıt: `make test` 110 passed, `make audit` 22 ✅ / 8 ⏳ / 0 ❌, `docs/PROVIDERS_VERIFIED.md`, `docs/AUDIT.md`, `submissions/amazon/` taslakları, `runs/demo-record` kayıtları (`run_ed76f4a16239`, `run_2036d34900f2`, `run_9f24d8fa5fad`), `videos/demo.mp4` (audit: 62 sn).

Olasılıklar TAHMİNDİR. Aralıklar kesinlik değildir. Bilinmeyen yer "bilinmiyor" diye durur. DOĞRULANMADI satırlarına dayanarak elenmiş veya kazanılmış sayılmadı.

Güçlü yan: mock modda anahtarsız 110 yeşil test, MCP resmi SDK 2.x testleri (`tests/test_mcp_official_sdk.py`), 8 dijital çalışan çekirdek yeteneği (`tests/test_working_core.py`), Web Speech API sesli kontrol arayüzü (`/alexa`), 1 fps canlı önizleme, risk onay kapısı, 3 dakikanın altında demo videosu (62 sn), blast radius konteyner sınırlandırma raporu, ASUS 20 sayfalık sunum taslağı.

## 1. Yarışma durumları

| Yarışma | Durum | Sağlam çalışan (kanıt) | Eksik | Kalan emek |
| --- | --- | --- | --- | --- |
| Amazon Alexa+ | İNSAN İŞİ | MCP Streamable HTTP resmî SDK testi (`test_mcp_official_sdk.py`, `test_s9_mcp_client`), <500ms araç benchmarkı, `/alexa` Web Speech API sesli dinle/konuş ve 1 fps canlı önizleme, sesli onay kartı, `make share-mcp` tüneli, video 62 sn. `docs/DEPLOY_PUBLIC.md` ve `docs/ALEXA_ONBOARDING.md`. | Halil video ve metni gözden geçirmeli. AWS App Runner deploy ve portal testi insan işi. Gerçek Alexa+ cihazı yok. | 8–16 saat, insan |
| Amazon Open Source mini | İNSAN İŞİ | MIT `LICENSE`. `make test` 110 yeşil. Audit "LICENSE is MIT" ✅. | Remote ve public repo kanıtı (Halil'in push yapması). Başvuru formu. | 4–8 saat, insan |
| Amazon AWS Builder mini | ANAHTAR BEKLİYOR | Bedrock `converse` yolu stub ile duruyor (`test_bedrock_converse_is_stubbed`). | `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ID`. Canlı çağrı yok. | Anahtar gelince 4–8 saat |
| Nebius x NVIDIA | ANAHTAR BEKLİYOR | OpenAI-uyumlu istemci sahte sunucuda, Meta Llama Nebius yönlendirmesi (`test_meta_llama_routing_and_nebius_fallback`), 110 yeşil test. Canlı token muhasebesi ($0.0238/41 çağrı). | Canlı `NEBIUS_API_KEY` ve Nebius Studio model adı. Halil video ve form teslimi. | Anahtar ve form ile 6–10 saat |
| Nebius Tavily bonusu | ANAHTAR BEKLİYOR | Tavily fallback ve mock arama (`test_capability_c_research_and_report_generation`). | Canlı `TAVILY_API_KEY`. | Anahtar gelince 1 saat |
| Open Agent Hackathon | İNSAN İŞİ | MCP araç şemaları Open Agent protokolüyle uyumlu (`test_nemotron_open_agent_tool_schema_compliance`), 8 dijital çalışan çekirdek yeteneği. Takvim `docs/OPEN_AGENT_PLAN.md`. | 15–20 Ekim arasında görünür yeni commit serisi şart. Kayıt 13 Ekim. | Pencerede 15–25 saat |
| OpenCV AI Competition | KURAL BELİRSİZ | OpenCV 5 diff ve bölge (`test_vision_finds_button`), `test_vision_service.py`, `docs/OPENCV_AWS.md` dağıtım adımları. | Halil AWS hesabı açmalı ve servisi çalıştırmalı. | 4–8 saat |
| Vultr Agent Rush | KURAL BELİRSİZ | `LocalRunner`, Docker limitleri, sahte Vultr API'de yaşam döngüsü, blast radius raporu üretimi (`test_vultr_blast_radius_report_generation`). Dürüstlük bildirimi mevcut. | Gerçek hesapta denenmedi (fake sunucu testi). Canlı Vultr kutusu açma Halil'de. | 6–10 saat |
| ASUS UGen AI League | İNSAN İŞİ | `submissions/asus/PRESENTATION.md` 20 sayfalık tam sunum taslağı hazır. 62 sn video hazır. | Slayt videosu seslendirme, YouTube yüklemesi. | 3–4 saat insan |
| ING Hubs | İNSAN İŞİ | Ajan iskeleti var. | Başvuru 4 Ekim, 2 kişilik takım, konular 9 Ekim'e kadar bilinmiyor. Ödül cihaz. | Başvuru birkaç saat; konu gelmeden kod tahmini yok |
| Kestra Hacktober | İNSAN İŞİ | Bu repoda Kestra PR'ı yok. | Merge edilmiş, kendi yazdığın Kestra PR'ları. Bu ürünün işi değil. | Ayrı iş, saatlik tahmin yok |
| YTU x Meta | İNSAN İŞİ | Meta ve WhatsApp istemcileri sahte sunucuda. | Başvuru, eğitim, Aralık'ta İstanbul'da yerinde hackathon. Öğrenci şartı brifingde net değil; yerinde olmak insan işi. | Başvuru birkaç saat; hackathon haftası ayrı |
| Imagine Cup 2027 | KURAL BELİRSİZ | Azure OpenAI ve Azure Speech sahte sunucuda (`test_azure_openai_sends_api_key_header_not_bearer`, `test_azure_speech_posts_the_audio_and_key`). | İki servisin canlı anahtarı yok. 2027 kuralları DOĞRULANMADI. | Anahtar ve kural sonrası 16–30 saat |
| Kaggle Gemma 4 | ANAHTAR BEKLİYOR | Ollama istemcisi sahte `/api/generate` ile. Onarım yaması S7'de üretilip uygulanmadı. | `GEMMA_MODEL` boş. Uyum zayıf: paper veya Kaggle yarışması bu sandbox demosu değil. | Uyum düşük; 30 saat+ ve yine zayıf |
| Build With AI Basics | İNSAN İŞİ | Uçtan uca sandbox demosu ve 68 test. Audit prototype ✅. | Başvuru formu ve insan onayı. | 4–8 saat |
| AssemblyAI Voice Agent | ANAHTAR BEKLİYOR | AssemblyAI upload+transcript sahte sunucuda. | 30 Eylül'e 2 gün. `ASSEMBLYAI_API_KEY` yok. Ürün sesli ajan demosu değil; STT varsayılanı mock. | Bu süre ve bu demoyla kapanmaz |
| HETIC | İNSAN İŞİ | Shop ve araştırma playbook'ları (`test_s3_old_listings`, `test_s1_account_research_share`). | Başvuru. Ödül küçük. | 4–6 saat |
| Arbiter | İNSAN İŞİ | Ajan kodu var. | `data/competitions.json` içinde `eligible=false`. Bağımsız takım teyidi yok. | Girme |
| Colosseum | İNSAN İŞİ | Devnet cüzdan kodu ve mainnet reddi (`test_mainnet_refused`). | Karar: girilmeyecek. Anahtar da yok. | 0, ATLA |

## 2. Olasılıklar (TAHMİN)

Katılımcı sayısı bilinen yerlerde bile track içi dağılım bilinmiyor. Aralık, "bu haliyle, sandbox demosuyla, zamanında teslim edilirse" içindir.

- Amazon Alexa+ 25.000 $: <1%. Yaklaşık 15.800 kişi. Jüri tasarım ve etki de bakıyor. MCP ve simüle sayfa teknik kutuyu doldurur; gerçek Alexa+ ve gerçek site olmadığı için etki zayıf. 15.000 $ ve 4.000 $ kademeleri de <1%. Track başına kişi sayısı bilinmiyor; yine de ilk 3, binlerce kişi içinde <1% ile 1–3% arasında kalır. Üst bandı kullanmak için kanıt yok, o yüzden <1% yazıyorum.
- Amazon Open Source mini 5.000 $: 1–3%. Teknik şart (MIT, çalışan test) duruyor. Public repo ve başvuru durmuyor. Mini'ye kaç proje gireceği bilinmiyor.
- Amazon AWS mini 5.000 $: <1% bugün. Canlı Bedrock çağrısı yok.
- Nebius birincilik 20.000 $ ve diğer kademeler: <1%. Katılımcı bilinmiyor. Canlı Nebius + NVIDIA modeli yok. Bu, o yarışmanın şartının kendisi.
- Tavily 3.000 $: <1% anahtarsız. Anahtarla bile bu demoda arama yan rol.
- Open Agent 8.000 / 4.000 / 2.000 $: mevcut repo ile <1%, çünkü puan yeni işe gidiyor ve yaklaşık 1.200 kayıtlı var. Pencerede görünür yeni bir parça çıkarsa 1–3% olabilir; bu da TAHMİN.
- OpenCV 5.000 $ ve alt kademeler: kural DOĞRULANMADI diye sayı vermiyorum. Teklif aşaması kaçırıldıysa olasılık 0. Kaçırılmadıysa ve AWS yoksa yine <1%.
- Vultr 5.000 $ nakit: kurallar DOĞRULANMADI. Tema koda yakın. Gerçek Vultr üzerinde koştuğumuz bir kayıt yok. TAHMİN vermek için erken; üst sınır olarak, kural bizim temaysa ve teslim Vultr'da çalışırsa 1–3%, aksi halde <1%.
- IEEE 1.500 $: <1%, ve büyük ihtimalle 0'a yakın. Proje iklim değil. Öğrenci ve Türkiye şartı DOĞRULANMADI.
- ASUS 4.500 $: <1%. Donanım entegrasyonu yok.
- ING cihaz ödülü: konu bilinmiyor, 2 kişilik takım ve başvuru insan işi. Olasılık bilinmiyor.
- Kestra cihaz/kart: bu repo ile ilişkisi yok. <1%.
- YTU 6.000 $ havuzu: yerinde öğrenci hackathon'u. Bu demoyu götürmek yetmez. Olasılık bilinmiyor; uzaktan teslim diye bir kanıt yok.
- Imagine Cup 100.000 $: <1%. Kurallar DOĞRULANMADI, iki canlı Microsoft servisi yok, tarih uzak.
- Gemma 37.000 / 35.000 $: <1%. Uyum zayıf ve model bağlı değil.
- Build With AI 2.500 $: 3–8%. Kalabalık bilinmiyor. Eldeki prototip şartın kendisi gibi duruyor; yine de jüri sandbox'ı zayıf bulabilir, o yüzden 15%+ yazmıyorum.
- AssemblyAI 5.000 $ nakit: <1%. İki gün var ve sesli ajan demosu yok.
- HETIC 1.100 $: 1–3%. İş küçük, kalabalık bilinmiyor, demo playbook'ları var.
- Arbiter 3.800 $: <1%. JSON'da eligible=false.

Bu yarışmada kazanma ihtimalimiz düşük çünkü sandbox dışı kanıt yok: Nebius, Gemma, OpenCV (AWS'siz), AssemblyAI Voice Agent, IEEE, ASUS, Imagine Cup birinciliği, Amazon Alexa+ birinciliği.

## 3. Ödül büyüklüğüne göre tablo

Beklenen değer = olasılık aralığı × nakit ödül. <1% için üst uç %1 alındı, alt uç 0'a yakın diye 0 yazıldı. Nakit olmayan ödülde çarpım yok.

| Yarışma | Ödül | Olasılık aralığı | Beklenen değer | Kalan emek | Öneri |
| --- | --- | --- | --- | --- | --- |
| Imagine Cup 2027 | 100.000 $ | <1% | 0–1.000 $ | 16–30 saat | ATLA (şimdilik) |
| Kaggle Gemma ana | 37.000 $ | <1% | 0–370 $ | 30 saat+ | ATLA |
| Gemma Paper | 35.000 $ | <1% | 0–350 $ | 30 saat+ | ATLA |
| Amazon Alexa+ 1. | 25.000 $ | <1% | 0–250 $ | 8–16 saat | ÖNCELİK (track olarak, birincilik değil) |
| Nebius 1. | 20.000 $ | <1% | 0–200 $ | 12–24 saat | ATLA (anahtarsız) |
| Amazon Alexa+ 2. | 15.000 $ | <1% | 0–150 $ | aynı teslim | ÖNCELİK |
| Open Agent 1. | 8.000 $ | <1% (yeni işle 1–3%) | 0–240 $ | 20–40 saat | BONUS |
| YTU x Meta havuz | 6.000 $ | bilinmiyor | hesaplanmadı | başvuru | BONUS (yerinde gidilecekse) |
| Amazon AWS mini | 5.000 $ | <1% | 0–50 $ | 4–8 saat | BONUS (anahtar gelirse) |
| Amazon OSS mini | 5.000 $ | 1–3% | 50–150 $ | 4–8 saat | ÖNCELİK |
| OpenCV 1. | 5.000 $ | kural belirsiz | hesaplanmadı | 8–16 saat | ATLA (teyitsiz) |
| Vultr 1. nakit | 5.000 $ | kural belirsiz; tema tutarsa 1–3% | 0–150 $ | 8–16 saat | BONUS |
| AssemblyAI nakit | 5.000 $ | <1% | 0–50 $ | yetişmez | ATLA |
| ASUS Lightning | 4.500 $ | <1% | 0–45 $ | 40 saat + cihaz | ATLA |
| Amazon Alexa+ 3. | 4.000 $ | <1% | 0–40 $ | aynı teslim | ÖNCELİK |
| Arbiter | 3.800 $ | <1% | 0–38 $ | — | ATLA |
| Nebius Tavily | 3.000 $ | <1% | 0–30 $ | 2–4 saat | BONUS |
| Build With AI Basics | 2.500 $ | 3–8% | 75–200 $ | 4–8 saat | ÖNCELİK |
| Open Agent 2. / 3. | 4.000 / 2.000 $ | <1% | 0–40 $ | pencere | BONUS |
| IEEE 1. | 1.500 $ | <1% | 0–15 $ | uyumsuz | ATLA |
| HETIC | 1.100 $ | 1–3% | 11–33 $ | 4–6 saat | BONUS |
| Kestra kart | 150 $ veya cihaz | <1% | nakit değil | ayrı iş | ATLA |
| ING | MacBook / iPad / saat | bilinmiyor | nakit değil | başvuru | BONUS (takım varsa) |
| Colosseum | — | girilmeyecek | 0 | 0 | ATLA |

Alexa+ satırları aynı teslimin parçasıdır. Track + bir mini kuralı yüzünden AWS ve OSS birlikte seçilmez. OSS, anahtar istemediği için AWS'ten önde.

## 4. Gerçekçi hedefler

En yüksek ihtimal, hâlâ mütevazı:

1. Amazon Open Source mini (5.000 $) — teknik şart repoda duruyor, public repo ve form insan işi. Aralık 1–3%.
2. Amazon Alexa+ track'ine girmek — MCP ve simüle sayfa testli. Para ödülü aralığı <1%; yine de aynı paketin asıl vitrini bu. Bir mini ile birlikte tek başvuru.
3. Build With AI Basics (2.500 $) — prototip zaten bu. Aralık 3–8%. Kalabalık bilinmiyor.
4. HETIC (1.100 $) — playbook demosu var, ödül küçük. Aralık 1–3%.
5. Open Agent, yalnız 15–20 Ekim'de yeni bir parça çıkarsa. Bugünkü repo ile uzak.

Uzak ihtimal: Nebius birinciliği, Gemma, Imagine Cup 100.000 $, OpenCV (teklif aşaması bilinmiyor), Alexa+ birinciliği, AssemblyAI (süre ve ses), ASUS (donanım), IEEE (konu ve ülke şartı).

## 5. Eksik teknik işler

Kodla kapananlar, sırayla:

1. Public olmayan hiçbir şey kodla "yayınlandı" olmaz; bu madde insan. Kod tarafında hazır olan paket: test, MIT, MCP, video dosyası.
2. Vultr'da gerçek komut çalıştırma (`docs/rules/vultr.md` gelince SSH veya onların verdiği yol). Şu an oluştur-sil var, uzakta docker yok.
3. Vision servisinin AWS'ye konması, OpenCV şartındaki AWS parçası. Servis ve Dockerfile duruyor, deploy yok.
4. Canlı sağlayıcı smoke'u, anahtarlar `.env`'e girince: Nebius, Tavily, Bedrock, Azure, AssemblyAI, Gemma. İstemci yolu sahte sunucuda geçti; canlı hesap geçmedi.

Bizim yapmamız gerekenler:

1. Repoyu public yapmak ve başvuruları insanın göndermesi. Ajan göndermez.
2. `submissions/amazon/` taslaklarını Halil'in okuması. Video ve friction log taslak.
3. Hangi mini: OSS (anahtarsız) önerilir. AWS ancak anahtar ve 30 saniyelik canlı Bedrock görüntüsü varsa.
4. ING başvurusu 4 Ekim'e kadar, 2. kişiyle, konu gelmeden kod yazmadan.
5. Open Agent'a girilecekse işin pencere içinde yapılması. Eski commit'i "yeni" diye saymamak.
6. OpenCV ve Vultr için kural teyidi. DOĞRULANMADI diye takvime kilitleme.
7. Colosseum, Arbiter, IEEE, ASUS, Gemma, AssemblyAI Voice Agent için vakit ayırmamak.

## Canlı link

Dashboard 127.0.0.1 dışına kendiliğinden açılmaz. Tünel için `make share`. `SHARE_MINUTES` varsayılan 60. Kapatmak için `make unshare`. Token terminale yazılmaz; link yalnızca Telegram'daki izinli kullanıcıya gider.
