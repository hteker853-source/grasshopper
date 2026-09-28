# Kazanç Modeli ve Beklenen Değer (EV) Raporu

> [!IMPORTANT]
> Bu bir kesin gelir taahhüdü değildir. Yapay zekâ jüri puanlarına ve Monte Carlo simülasyonuna dayanan TAHMİNDİR.

UYARI: Yarışmalar birbirinden bağımsız çizildiğinde sonuçlar aşırı iyimser olur. Aynı jüri, aynı kod tabanı ve aynı takvim yüzünden sonuçlar pozitif korelasyonla birlikte hareket eder. Gerçekte tam bağımsızlık varsayımı fazlasıyla iyimserdir; kötü günde genel bir hata veya jüri şüphesi toplu elemeye neden olur.

## 1. Üç Senaryo Analizi (Korelasyonlu Model)

| Metrik | Ayı (Bear) | Taban (Base) | Boğa (Bull) |
| --- | --- | --- | --- |
| **Beklenen Değer (EV)** | **$903** | **$1601** | **$2290** |
| **En Az 1 Ödül İhtimali** | 14.0% | 23.7% | 33.1% |
| **10.000$+ Gelir İhtimali** | 2.6% | 4.7% | 6.9% |
| **20.000$+ Gelir İhtimali** | 1.1% | 2.0% | 2.8% |

## 2. '20.000$ Ortalama' Varsayımının Gerçeklik Testi

- **19 yarışmada 20.000$ ortalama:** Toplam 380.000$ nakit ödül demektir. Bu varsayım **İMKÂNSIZDIR**; çünkü 19 yarışmanın tüm birincilik ödüllerinin toplam nakit havuzu bile ~180.000$ civarındadır ve birçok yarışma (ING, Kestra, Arbiter, Nordic) nakit değil kredi veya sertifika verir.
- **Toplamda 20.000$+ kazanma ihtimali:**
  - Taban senaryoda toplam gelirin 20.000$ veya üzerine çıkma ihtimali **%2.0**, Boğa senaryoda **%2.8**'dir.
- **Hangi yarışmalar olmadan 20.000$ imkânsız?**
  - **Amazon (Alexa+ 1.: 25.000$)** ve **Nebius (1.: 20.000$)** bu hedefin omurgasıdır. Bu iki yarışma olmadan portföydeki diğer tüm yarışmalar kazanılsa dahi 20.000$ nakite ulaşmak neredeyse imkânsızdır (Vultr 9K + Open Agent 8K = 17K).

## 3. Varsayımlar ve Notlar
- Simülasyon her senaryo için 20.000 çekiliş ile yapılmıştır.
- Aynı yarışma içindeki dereceler birbirini dışlar (aynı anda 1. ve 2. olunamaz).
- Kalite faktörü korelasyonu (±0.35 şok) ile yarışmaların birlikte başarı/başarısızlık eğilimi modellenmiştir.
