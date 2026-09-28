# Vultr Agent Rush Hackathon

Kaynak: resmi kurallar ve jüri kriterleri, 2026-09-28 tarihinde lablab.ai üzerinden alındı.
https://lablab.ai/ai-hackathons/vultr-hackathon

Bu dosya varsayılan rubrik değildir. Resmi jüri değerlendirme tablosudur.

## Jüri Kriterleri

| Kriter | Ağırlık (%) | Resmi Tanım |
| --- | --- | --- |
| Application of Technology | 25 | Seçilen model(ler)in çözüme ne kadar etkili entegre edildiği |
| Presentation | 25 | Sunum ve demo videosunun netliği ve ikna ediciliği |
| Business Value | 25 | İş alanlarına uyum, pratik değer ve etki |
| Originality | 25 | Çözümün özgünlüğü, yaratıcılığı ve ajan davranışları |

## Teknik Gereksinimler ve "Containment-First"

- Tema: "Blast Radius Zero" — Vultr altyapısı üzerinde izole çalışma ortamında (sandbox) gerçek iş yapan web/kod ajanları.
- Zorunlu teslimler:
  1. Kurulum ve dokümantasyon içeren GitHub repo.
  2. Vultr VM arka uç dağıtımı ve Vultr Serverless Inference üzerinden LLM çağrıları.
  3. Genel demo URL ve kayıtlı demo videosu.
  4. Videoda bir "containment moment": Sandbox'ın güvensiz bir eylemi (örn. tehlikeli komut, sonsuz döngü, düşmanca web sayfası) güvenle izole edip durdurduğunun kanıtı.

## Takvim ve Ödüller

- Tarih: 3–8 Kasım 2026 (çevrim içi build).
- Ödüller: 9.000 $ nakit + 5.000 $ kredi.
  - 1.: 5.000 $ nakit + 3.000 $ kredi
  - 2.: 3.000 $ nakit + 1.000 $ kredi
  - 3.: 1.000 $ nakit + 1.000 $ kredi

## Bu Repo

- Her koşu `blast_radius.json` yazar (dosyalar, alan adları, süre, maliyet).
- Vultr sandbox entegrasyonu `grasshopper/sandbox_runner/vultr.py` içindedir.
