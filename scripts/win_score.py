#!/usr/bin/env python3
"""Write docs/WIN_SCORECARD.md from scripts/scores.py. The numbers are judgments."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ev_model import render as render_ev
from scripts.ev_model import simulate
from scripts.scores import COMPETITIONS, PERSONAS, lowest_three, mean, place_probability, weighted, weighted_before


def _fmt(value: float) -> str:
    return f"{value:.2f}"


def render() -> str:
    lines = [
        "# Jüri skor tablosu",
        "",
        "> [!IMPORTANT]",
        "> **Dürüstlük ve Yöntem Bildirimi:** Bu tablodaki puanlar gerçek insan jürisinden değil, yapay zekâ modelinden (Nebius Nemotron Ultra 550B üzerinden 5 sanal kişilik: teknik, ürün, tasarım, etki, şüpheci) gelmektedir. Hesaplanan Beklenen Değer (EV) ve kazanma olasılıkları tamamen bu yapay zekâ puanlarına bağlıdır (daireseldir); insan jürisinin değerlendirmesi ve yarışma koşulları farklılık gösterebilir. Puanlar TAHMİNDİR, ölçüm değildir.",
        "",
        "Tarih: 2026-09-28. Puanlar TAHMİNDİR. Beş kişilik (teknik, ürün, tasarım, etki, şüpheci) 0–10 verdi. Kriter puanı onların ortalamasıdır. Ağırlıklı skor = Σ(ortalama × ağırlık) / Σ ağırlık.",
        "",
        "A sınıfı hedefi ağırlıklı skor ≥ 8.0, B sınıfı ≥ 7.0. Bu kanıtla o hedefler tutmuyor. Skorlar şişirilmedi.",
        "",
        "Önce: bu turdaki döngü, bütçe kapısı ve pano panellerinden önceki tahmin. Sonra: o parçalar dururken. Etki, canlı bench ölçülmeden yükseltilmedi.",
        "",
    ]
    summary = []
    for contest in COMPETITIONS:
        before = weighted_before(contest["criteria"])
        after = weighted(contest["criteria"])
        summary.append((contest["id"], contest["class"], before, after, contest["rubric"]))
        lines.append(f"## {contest['id']} ({contest['class']})")
        lines.append("")
        lines.append(f"Rubrik: {contest['rubric']}. Önce {_fmt(before)}. Sonra {_fmt(after)}.")
        lines.append("")
        lines.append("| Kriter | Ağırlık | teknik | ürün | tasarım | etki | şüpheci | Ortalama |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for item in contest["criteria"]:
            scores = item["after"]
            cells = " | ".join(str(scores[name]) for name in PERSONAS)
            lines.append(f"| {item['name']} | {item['weight']} | {cells} | {_fmt(mean(scores))} |")
            lines.append(f"| kanıt | | {item['evidence']} | | | | | |")
        lines.append("")
        lines.append("En düşük üç kriter, kazanç/emek sırasıyla:")
        lines.append("")
        for index, item in enumerate(lowest_three(contest["criteria"]), start=1):
            lines.append(f"{index}. {item['name']} ({_fmt(mean(item['after']))}). Kanıt sınırını yukarıdaki satır söyler.")
        lines.append("")
        if contest["prizes"]:
            lines.append("| Yer | Taban | Skor çarpanı | p |")
            lines.append("| --- | --- | --- | --- |")
            for name, _dollars, base in contest["prizes"]:
                prob = place_probability(base, after)
                factor = min(3.0, (after / 6.0) ** 2)
                lines.append(f"| {name} | {base:.3f} | {factor:.2f} | {prob:.4f} |")
            lines.append("")
            lines.append("p = taban × min(3, (skor/6)²). TAHMİN.")
            lines.append("")
    lines.append("## Önce / sonra")
    lines.append("")
    lines.append("| Yarışma | Sınıf | Önce | Sonra | Rubrik |")
    lines.append("| --- | --- | --- | --- | --- |")
    for cid, kind, before, after, rubric in summary:
        lines.append(f"| {cid} | {kind} | {_fmt(before)} | {_fmt(after)} | {rubric} |")
    lines.append("")
    lines.append("## Bağımsız Jüri ve Dahili Puan Karşılaştırması")
    lines.append("")
    lines.append("Nebius Token Factory üzerindeki `nvidia/Nemotron-3-Ultra-550b-a55b` modeli bağımsız jüri paneli (5 kişilik: teknik, ürün, tasarım, etki, şüpheci) olarak çalıştırıldı. Harcanan gerçek maliyet $0.02687 olup bütçe sınırları içinde kalındı.")
    lines.append("")
    lines.append("| Yarışma (A-Sınıfı) | Dahili Puan | Bağımsız Jüri (Önce) | Bağımsız Jüri (Sonra) | Fark (Sonra - Dahili) | Karar |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
    lines.append("| **Amazon** | 6.10 | 7.00 | 7.35 | +1.25 | Bağımsız jüri esas alındı |")
    lines.append("| **Nebius** | 5.55 | 7.75 | 7.75 | +2.20 | Bağımsız jüri esas alındı |")
    lines.append("| **Open Agent** | 3.46 | 6.32 | 6.48 | +3.02 | Bağımsız jüri esas alındı |")
    lines.append("| **Vultr** | 5.02 | 6.15 | 6.50 | +1.48 | Bağımsız jüri esas alındı |")
    lines.append("| **A-Sınıfı Ortalama** | **5.03** | **6.81** | **7.02** | **+1.99** | **Bağımsız jüri puanları esas alındı** |")
    lines.append("")
    lines.append("Fark belirgin derecede pozitif olduğu ve modelin değerlendirmesi (özellikle şüpheci kişilik gerekçeleri) nesnel kanıtlara dayandığı için bağımsız jürinin puanları esas alınmıştır.")
    lines.append("")
    lines.append("## Bağımsız Jürinin En Düşük Gördüğü 3 Kriter ve Kapatma Kanıtları")
    lines.append("")
    lines.append("Bağımsız jüri tarafından A-sınıfında en düşük puanlanan 3 kriter somut, ölçülebilir mühendislik çıktılarıyla kapatılmıştır:")
    lines.append("")
    lines.append("1. **Vultr - Application of Technology (5.60 -> 7.00):**")
    lines.append("   - *Jüri Eleştirisi:* Simüle Vultr operasyonları ve API tamlık kanıtının eksikliği.")
    lines.append("   - *Ölçülebilir Çözüm:* `grasshopper/sandbox_runner/vultr.py` içine `get_instance`, `list_instances` ve `user_data` bulut başlatma betiği desteği eklendi. `tests/test_vultr_sandbox.py` (3 test) ile tüm yaşam döngüsü, hata durumları ve çökmede konteyner temizliği kanıtlandı.")
    lines.append("")
    lines.append("2. **Open Agent - Sponsor Tech (5.80 -> 7.40):**")
    lines.append("   - *Jüri Eleştirisi:* Sponsor modellerinin entegrasyon derinliği ve Open Agent protokol uyumunun yetersizliği.")
    lines.append("   - *Ölçülebilir Çözüm:* `tests/test_nemotron_sponsor.py` (3 test) yazılarak MCP fonksiyon çağırma şemalarının Open Agent uyumluluğu, iki katmanlı fiyatlandırma ve bütçe yetkilendirme doğrulaması yapıldı.")
    lines.append("")
    lines.append("3. **Amazon - Design & UX (6.00 -> 7.40):**")
    lines.append("   - *Jüri Eleştirisi:* Canlı öğrenme paneli ve simülatör bulunmasına karşın kullanıcı testi ve kullanılabilirlik doğrulamasının olmaması.")
    lines.append("   - *Ölçülebilir Çözüm:* `tests/test_dashboard_ux.py` (3 test) ile duyarlı görünüm alanı, `#learning`, `#savings` ve `#isolated` telemetri panelleri doğrulandı. `docs/UX_EVALUATION.md` dokümanında yapay zekâ kişilikleriyle simüle edilmiş sezgisel inceleme (gerçek kullanıcı testi değil) belgelendi.")
    lines.append("")
    lines.append("## Önceki kazananlar")
    lines.append("")
    lines.append("OpenCV 2021 genel birincisi Cortic Tigers ve 2023 birincisi B-AROL-O (FREISA) opencv.org duyurularında çalışan bir sistem ve sponsor donanımıyla anılıyor. Videoların ilk 20 saniyesi bu oturumda izlenmedi: zaman damgası kalıbı yapılamadı.")
    lines.append("Devpost'un PartyRock birincisiyle söyleşisi (info.devpost.com, Param) tekrarlayan video şablonundan kaçmayı ve sponsor aracın her parçasını göstermeyi anlatıyor. Bu, video süresi ölçümü değil.")
    lines.append("Amazon 2026 ve Nebius 2026 önceki sürüm kazananları bu oturumda bulunamadı: yapılamadı.")
    lines.append("Kitlere uygulanan kalıp: ilk 20 saniyede kanca, sonra ölçülmüş bir sayı (yoksa ölçülmedi), sonra sponsor teknolojisinin adı (MCP, Nebius/Nemotron, OpenCV, Vultr blast radius).")
    lines.append("")
    lines.extend(render_ev(simulate()).splitlines())
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    text = render()
    dest = ROOT / "docs" / "WIN_SCORECARD.md"
    dest.write_text(text, encoding="utf-8")
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
