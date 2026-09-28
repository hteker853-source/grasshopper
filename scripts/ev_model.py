#!/usr/bin/env python3
"""Monte Carlo expected value with correlation and 3 scenarios (Bear, Base, Bull)."""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.scores import COMPETITIONS, place_probability, weighted

WARNING = (
    "UYARI: Yarışmalar birbirinden bağımsız çizildiğinde sonuçlar aşırı iyimser olur. "
    "Aynı jüri, aynı kod tabanı ve aynı takvim yüzünden sonuçlar pozitif korelasyonla "
    "birlikte hareket eder. Gerçekte tam bağımsızlık varsayımı fazlasıyla iyimserdir; "
    "kötü günde genel bir hata veya jüri şüphesi toplu elemeye neden olur."
)


def contest_outcomes(contest: dict, multiplier: float = 1.0) -> list[tuple[str, float, float]]:
    """Mutually exclusive places. Probabilities are scaled if they would exceed 1."""
    score = weighted(contest["criteria"])
    rows = []
    for name, dollars, base in contest["prizes"]:
        prob = place_probability(base, score) * multiplier
        rows.append((name, float(dollars), min(1.0, prob)))
    total = sum(item[2] for item in rows)
    if total > 1:
        rows = [(name, dollars, prob / total) for name, dollars, prob in rows]
    return rows


def run_scenario(scenario: str, draws: int = 20000, seed: int = 20260928) -> dict:
    """Run Monte Carlo for 'bear', 'base', or 'bull' scenario with quality correlation."""
    rng = random.Random(seed)

    sc_mult = {"bear": 0.55, "base": 1.00, "bull": 1.45}[scenario]
    prepared = [(contest["id"], contest["prizes"], weighted(contest["criteria"])) for contest in COMPETITIONS if contest["prizes"]]

    totals = []
    for _ in range(draws):
        # Latent day/run quality shock (correlation factor Q around 1.0)
        quality = 1.0 + rng.uniform(-0.35, 0.35)
        run_mult = max(0.1, sc_mult * quality)

        money = 0.0
        for _cid, prizes, score in prepared:
            roll = rng.random()
            cursor = 0.0
            for _name, dollars, base in prizes:
                prob = min(1.0, place_probability(base, score) * run_mult)
                cursor += prob
                if roll < cursor:
                    money += float(dollars)
                    break
        totals.append(money)

    any_prize = sum(1 for value in totals if value > 0) / draws
    over_10 = sum(1 for value in totals if value >= 10000) / draws
    over_20 = sum(1 for value in totals if value >= 20000) / draws
    expected = sum(totals) / draws

    return {
        "scenario": scenario,
        "draws": draws,
        "seed": seed,
        "expected_usd": expected,
        "p_any": any_prize,
        "p_10k": over_10,
        "p_20k": over_20,
        "warning": WARNING,
    }


def simulate(draws: int = 20000, seed: int = 20260928) -> dict:
    """Standard base simulation compatible with test_scorecard."""
    return run_scenario("base", draws=draws, seed=seed)


def simulate_all() -> dict[str, dict]:
    return {
        "bear": run_scenario("bear"),
        "base": run_scenario("base"),
        "bull": run_scenario("bull"),
    }


def render(result: dict | None = None) -> str:
    if result is not None and "expected_usd" in result and "bear" not in result:
        return "\n".join([
            "# Beklenen değer (TAHMİN)",
            "",
            "Bu bir ölçüm değildir. TAHMİNDİR.",
            "",
            result.get("warning", WARNING),
            "",
            f"Çekiliş: {result['draws']}. Tohum: {result.get('seed', 20260928)}.",
            "",
            "| Sonuç | Değer |",
            "| --- | --- |",
            f"| Beklenen değer | ${result['expected_usd']:.0f} |",
            f"| En az 1 ödül | {result['p_any']:.1%} |",
            f"| 10.000$+ | {result['p_10k']:.1%} |",
            f"| 20.000$+ | {result['p_20k']:.1%} |",
            "",
            "Yarışmalar arası bağımsız çiziliş varsayımı fazlasıyla iyimserdir.",
            "",
        ])

    results = simulate_all()
    bear = results["bear"]
    base = results["base"]
    bull = results["bull"]

    lines = [
        "# Kazanç Modeli ve Beklenen Değer (EV) Raporu",
        "",
        "> [!IMPORTANT]",
        "> Bu bir kesin gelir taahhüdü değildir. Yapay zekâ jüri puanlarına ve Monte Carlo simülasyonuna dayanan TAHMİNDİR.",
        "",
        WARNING,
        "",
        "## 1. Üç Senaryo Analizi (Korelasyonlu Model)",
        "",
        "| Metrik | Ayı (Bear) | Taban (Base) | Boğa (Bull) |",
        "| --- | --- | --- | --- |",
        f"| **Beklenen Değer (EV)** | **${bear['expected_usd']:.0f}** | **${base['expected_usd']:.0f}** | **${bull['expected_usd']:.0f}** |",
        f"| **En Az 1 Ödül İhtimali** | {bear['p_any']:.1%} | {base['p_any']:.1%} | {bull['p_any']:.1%} |",
        f"| **10.000$+ Gelir İhtimali** | {bear['p_10k']:.1%} | {base['p_10k']:.1%} | {bull['p_10k']:.1%} |",
        f"| **20.000$+ Gelir İhtimali** | {bear['p_20k']:.1%} | {base['p_20k']:.1%} | {bull['p_20k']:.1%} |",
        "",
        "## 2. '20.000$ Ortalama' Varsayımının Gerçeklik Testi",
        "",
        "- **19 yarışmada 20.000$ ortalama:** Toplam 380.000$ nakit ödül demektir. Bu varsayım **İMKÂNSIZDIR**; çünkü 19 yarışmanın tüm birincilik ödüllerinin toplam nakit havuzu bile ~180.000$ civarındadır ve birçok yarışma (ING, Kestra, Arbiter, Nordic) nakit değil kredi veya sertifika verir.",
        "- **Toplamda 20.000$+ kazanma ihtimali:**",
        f"  - Taban senaryoda toplam gelirin 20.000$ veya üzerine çıkma ihtimali **%{base['p_20k']*100:.1f}**, Boğa senaryoda **%{bull['p_20k']*100:.1f}**'dir.",
        "- **Hangi yarışmalar olmadan 20.000$ imkânsız?**",
        "  - **Amazon (Alexa+ 1.: 25.000$)** ve **Nebius (1.: 20.000$)** bu hedefin omurgasıdır. Bu iki yarışma olmadan portföydeki diğer tüm yarışmalar kazanılsa dahi 20.000$ nakite ulaşmak neredeyse imkânsızdır (Vultr 9K + Open Agent 8K = 17K).",
        "",
        "## 3. Varsayımlar ve Notlar",
        "- Simülasyon her senaryo için 20.000 çekiliş ile yapılmıştır.",
        "- Aynı yarışma içindeki dereceler birbirini dışlar (aynı anda 1. ve 2. olunamaz).",
        "- Kalite faktörü korelasyonu (±0.35 şok) ile yarışmaların birlikte başarı/başarısızlık eğilimi modellenmiştir.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    text = render()
    dest = ROOT / "docs" / "EV.md"
    dest.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
