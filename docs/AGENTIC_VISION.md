# Agentic Vision notu

OpenCV 5 algısı bir sonraki kararı değiştirir. Akış: ekran görüntüsü → `detect_regions` / `change_percent` → seçici kırıldıysa Continue yazan kontrol → tıklama. İnsan onayı pahalı adımda durur.

## Ölçüm

`tests/test_vision_change_and_dom_recovery_are_measured` kontrollü bir set ister: 10 aynı kart değişmemiş, 10 kaymış kart değişmiş, 20 konumda kimlik silinmiş Continue dikdörtgeni. Test, doğru sayının setin tamamına eşit olmasını bekler ve geçti. Bu, o setin sonucudur. Başka bir kamera veya canlı site için oran ölçülmedi.

Canlı üçüncü parti sayfanın HTML'i kasıtlı bozulmadı. Yerel REC senaryosu `tests/test_realweb.py` içinde seçici kaybolduktan sonra metinle toparlanır ve görme çağrısını sayar.

## Jüri kanıtı

Diyagram `docs/ARCHITECTURE.md` içinde. İz: koşu klasöründeki `*_regions.png` ve `blast_radius.json`. AWS'ye koyma adımları `docs/OPENCV_AWS.md`. Deploy ölçülmedi.
