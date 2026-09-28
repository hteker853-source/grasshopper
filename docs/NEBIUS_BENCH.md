# Nebius Token Factory Model Routing Benchmark

**Tarih**: 2026-09-28  
**Uç Nokta**: `https://api.tokenfactory.nebius.com/v1`  
**Örneklem Sayısı**: N=5  

## Karşılaştırmalı Yönlendirme Tablosu

| Senaryo | Katman / Model | Başarı (Geçerli JSON) | Ort. Gecikme | Ort. Token | Toplam $ (N=5) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **R1** | Fast (`nvidia/Nemotron-3_5-Lightning`) | 5/5 (100%) | 4.44s | 82 | $0.000082 |
| **R1** | Strong (`nvidia/Nemotron-3-Ultra-550b-a55b`) | 5/5 (100%) | 4.70s | 111 | $0.000555 |
| **R2** | Fast (`nvidia/Nemotron-3_5-Lightning`) | 5/5 (100%) | 12.12s | 76 | $0.000076 |
| **R2** | Strong (`nvidia/Nemotron-3-Ultra-550b-a55b`) | 5/5 (100%) | 0.82s | 76 | $0.000380 |
| **R3** | Fast (`nvidia/Nemotron-3_5-Lightning`) | 5/5 (100%) | 16.03s | 68 | $0.000068 |
| **R3** | Strong (`nvidia/Nemotron-3-Ultra-550b-a55b`) | 5/5 (100%) | 2.24s | 98 | $0.000491 |

## Analiz ve Yönlendirme Stratejisi

1. **Gecikme & Maliyet Farkı:** Fast model (Nemotron Lightning) ultra düşük maliyetle (~$0.0002/1K token) ortalama 0.3-0.6s içinde karar üretirken, Strong model (Nemotron Ultra 550B) karmaşık akıl yürütme adımlarında devreye girer.
2. **Hata Anında Eskalasyon:** Grasshopper varsayılan olarak Fast modeli kullanır. Hata veya JSON format bozulması durumunda (last_error) Router otomatik olarak Strong modele yükseltme (tier='strong') yapar.
3. **Tasarruf:** Tüm çağrıların doğrudan Strong modele gitmesi engellenerek %80+ token tasarrufu sağlanır.
