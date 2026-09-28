# Gizlilik ve Yayınlama Kontrol Listesi (Publish Checklist)

> **Tarih**: 2026-09-28  
> **Kural**: Depo yayınlanmadan önce tüm hassas veriler, API anahtarları, kullanıcı kimlikleri ve geçici çalışma dosyaları taranmış ve doğrulanmıştır.

---

## 1. Gizlilik Taraması Bulguları (Privacy Scan)

| Kategori / Kalıp | Hedef / regex | Taranan Alan | Sonuç / Durum |
| :--- | :--- | :--- | :--- |
| **Kullanıcı Kimliği** | `658866****` (Telegram User ID) | Tüm izlenen dosyalar & git geçmişi | **TEMİZ** (Hiçbir izlenen dosyada ve git geçmişinde bulunmadı; yalnızca yerel `.env` içinde tutulur) |
| **Telegram Bot Token** | `\b\d{8,12}:[A-Za-z0-9_-]{30,}\b` | Tüm izlenen dosyalar & git geçmişi | **TEMİZ** (Gerçek token sızıntısı yok) |
| **AWS Erişim Anahtarları** | `AKIA[0-9A-Z]{16}` | Tüm izlenen dosyalar & git geçmişi | **TEMİZ** (Yalnızca `grasshopper/config.py` ve `scripts/audit.py` içindeki sansür regex kalıpları mevcut; gerçek anahtar yok) |
| **OpenAI / API Anahtarları** | `sk-[A-Za-z0-9]{16,}` | Tüm izlenen dosyalar & git geçmişi | **TEMİZ** (Yalnızca `scripts/audit.py` sansür deseni; gerçek anahtar yok) |
| **Özel Anahtarlar (Private Key)** | `-----BEGIN [A-Z ]*PRIVATE KEY-----` | Tüm izlenen dosyalar & git geçmişi | **TEMİZ** (Yok) |
| **Ortam Değişkenleri** | `.env` dosyasındaki değerler | İzlenen tüm dosyalar | **TEMİZ** (`.env` gitignore edilmiş, `.env.example` yalnızca yer tutucu değerler içerir) |

---

## 2. `.gitignore` Bütünlük Kontrolü

Aşağıdaki dosya ve dizinlerin depoda izlenmediği (`git status` ve `git ls-files` ile) teyit edilmiştir:

- [x] `runs/` (Çalışma izleri ve ekran görüntüleri)
- [x] `profiles/` (Tarayıcı profil oturumları)
- [x] `data/*.db` & `data/*.db*` (SQLite veritabanları, `-shm` ve `-wal` dosyaları)
- [x] `videos/` (Demo videoları ve kit kayıtları, `git rm --cached` ile çıkarıldı)
- [x] `.env` (Gerçek sırlar ve yapılandırmalar)
- [x] `docs/INSAN_ISLERI.md` (İç operasyonel insan işleri dokümanı)
- [x] `docs/HANDOFF.md` (Ajan devir teslim ve dahili durum notları)

---

## 3. Git Geçmişi Durumu

- **Commit Yapısı**: Git geçmişi temiz tek bir başlangıç commit'ine (`b0e70c1 Initial commit of Grasshopper.`) dayanmaktadır.
- **Geçmiş Temizliği**: `git log -S "658866****"` ve anahtar aramaları 0 eşleşme üretmiştir.
- **Son Durum**: İzlenmeyen geçici dosyalar ve gizli belgeler depodan tamamen yalıtılmıştır. Kamuya açık yayın (`gh repo create`) için hazırdır.
