# OpenCV — AWS kanıt adımları

Hesap bu oturumda açılmadı. Aşağısı Halil'in izleyeceği sıra. Komutlar örnek isim kullanır. Gizli değer yazılmaz.

1. AWS hesabına Halil girer. Yeni hesap bu dosyadan açılmaz.
2. Bölge seçer. `AWS_REGION` değerini `.env` içine kendi yazar.
3. IAM kullanıcısına ECR'ye push ve bir servisi çalıştırma izni verir. Anahtar repoya girmez.
4. `vision_service/Dockerfile` imajını kendi makinesinde derler.
5. ECR deposu açar, imajı oraya iter.
6. Servisi App Runner ya da ECS/Fargate üzerinde 8081 portuyla çalıştırır. Sağlık yolu `/health`.
7. Servis adresini `VISION_SERVICE_URL` olarak `.env`e yazar. Uygulama o adres doluysa `grasshopper/browser/vision.py` aynı görüntüyü oraya yollar. Boşsa işlem yerelde kalır.
8. `tests/test_vision_service.py` yerel servisle geçer. Canlı AWS adresi bu oturumda ölçülmedi.

Sorumlu bulut teslimi jüri maddesi, bu adımlar yapılmadan kapanmaz.
