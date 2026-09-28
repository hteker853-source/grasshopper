# Grasshopper — ASUS UGen AI League, Stage I

20 sayfa. Markdown sunum. YouTube yüklemesi yapılmadı. UGen300 bu makinede yok. Donanım entegrasyonu ölçülmedi.

<!-- sayfa 1 -->
## 1. Kapak

Grasshopper, bir cümleyi adımlara bölüp tarayıcıda çalıştıran, her adımı kontrol eden ve para harcamadan önce duran açık kaynaklı bir işçidir. Lisans MIT. Bu sunum Stage I içindir. Gönderilmedi. Halil gözden geçirir.

<!-- sayfa 2 -->
## 2. Tek cümle

Kırılan bir sayfada aynı işi ikinci kez model parasız tekrar edebilen, harcaması tavanla kesilen bir tarayıcı işçisi.

<!-- sayfa 3 -->
## 3. Kim için

Kendi sitesinde tekrarlayan işi olan bir kişi: eski ilan, form, kontrol listesi. Jüri bir işletme müşterisi görmez. Kullanıcı sayısı ölçülmedi.

<!-- sayfa 4 -->
## 4. Sorun

Tarayıcı ajanları ilk denemede pahalıdır, ikinci denemede de aynı parayı öder, ve bir seçici değişince sessizce yanlış yere tıklar. Grasshopper ikinci başarılı izi yeniden oynatır ve seçici kaybolunca görüntüye bakar.

<!-- sayfa 5 -->
## 5. Ürün

Dashboard, onay kapısı, MCP ile Alexa benzeri sayfa, sandbox siteler, gerçek site için allowlist. Varsayılan mod mock'tur. Anahtar olmadan `make test` çalışır.

<!-- sayfa 6 -->
## 6. Üç komut

`bash scripts/setup.sh`, ardından `.env` kopyası, ardından `make test`. Ayrıntı CONTRIBUTING.md ve README içindedir.

<!-- sayfa 7 -->
## 7. Mimari

Kanallar kuyruğa düşer. Planlayıcı playbook'a bakar, yoksa modele sorar. Tarayıcı eylemi çalıştırır. Doğrulayan bakar. Explainer nedenini yazar. Ayrıntı docs/ARCHITECTURE.md ve oradaki Mermaid diyagramıdır.

<!-- sayfa 8 -->
## 8. Öğrenme

İlk koşu model çağırır. İz kaydolur. İkinci koşu aynı sayfada 0 çağrı hedefler. Fixtürde bu `tests/test_realweb.py` ile geçti. Canlı sitede bench bitene kadar sayı ölçülmedi.

<!-- sayfa 9 -->
## 9. Maliyet

Günlük tavan 0.50 $, koşu başı 0.05 $. Router çağrıdan önce token fiyatını sayar. Aşılırsa görev durur ve bildirim gider. Mock faturası 0'dır. Canlı fatura ölçülmedi. docs/COST.md.

<!-- sayfa 10 -->
## 10. Görme

OpenCV 5 fark ve bölge bulur. Kontrollü sette değişen kart değişmiş, aynı kart aynı sayılır. Kimliği silinen Continue düğmesi görme ile seçilir. O setin dışında doğruluk ölçülmedi. docs/AGENTIC_VISION.md.

<!-- sayfa 11 -->
## 11. Güvenlik

Allowlist kodda sabittir. Etsy, Amazon perakende, sosyal medya, Google giriş ve ödeme sayfaları reddedilir. robots.txt ve istek arası bekleme vardır. Mainnet cüzdan adresi reddedilir.

<!-- sayfa 12 -->
## 12. Onay

Para, paylaşım ve dışarı aktarma onay ister. Reddedilirse durur. Mock banka aynı üç kapıyı gösterir: limit, onay, denetim izi. ING konusu 9 Ekim'de gelince bu şablon uyarlanır.

<!-- sayfa 13 -->
## 13. Patlama yarıçapı

Her koşunun sonunda dokunulan dosyalar, gidilen alan adları, süre ve maliyet JSON olur. Docker varsa isteğe bağlıdır. Yoksa uyarıyla yerel çalışır. Gerçek Vultr makinesi bu oturumda açılmadı.

<!-- sayfa 14 -->
## 14. Demo

videos/demo.mp4 yaklaşık 64 saniye, 1280x720. Üç dakikanın altında. YouTube'a Halil yükler. Bu dosya yükleme kanıtı değildir.

<!-- sayfa 15 -->
## 15. Test

Son tam turda `make test` yeşildi ve `make audit` kırmızı değildi. Sayılar docs/HANDOFF.md ve docs/AUDIT.md içindedir. Yer tutucu test yok.

<!-- sayfa 16 -->
## 16. Kenar cihaz

UGen300 yok. Model bu kasada çalışıyor, kenarda bir NPU'ya bağlanmadı. Bağlantı ölçülmedi. Stage II cihazı gelirse ilk iş, aynı gözlem döngüsünü o kutuda bir kez koşup süreyi yazmaktır.

<!-- sayfa 17 -->
## 17. Ne ölçülmedi

Canlı Nebius faturası, canlı Bedrock çağrısı, AWS'ye konmuş görme servisi, UGen300 gecikmesi, gerçek kullanıcı, YouTube izlenmesi. Bunlar uydurulmadı.

<!-- sayfa 18 -->
## 18. Risk

Sandbox jüriye küçük görünebilir. Gerçek site bench'i bu sunum yazılırken sürüyor olabilir. Sayı yoksa "ölçülmedi" denir. Donanım şartı bu paketle kapanmaz.

<!-- sayfa 19 -->
## 19. İstenen karar

Stage I için sunum ve kısa video yeter. Cihaz iddiası yok. Değerlendirme, tekrarlanabilir test ve tavanlı maliyet üzerinedir.

<!-- sayfa 20 -->
## 20. Kapanış

Grasshopper MIT. Gönderim insan işi. İletişim ve form Halil'de. Tarih sırası docs/INSAN_ISLERI.md içindedir.
