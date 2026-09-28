"""Jury estimates. These are not measurements. Each number is a judgment plus a file."""

from __future__ import annotations

PERSONAS = ("teknik", "urun", "tasarim", "etki", "supheci")


def mean(scores: dict[str, float]) -> float:
    return sum(scores[name] for name in PERSONAS) / len(PERSONAS)


def weighted(criteria: list[dict]) -> float:
    total = 0.0
    weight = 0.0
    for item in criteria:
        total += mean(item["after"]) * item["weight"]
        weight += item["weight"]
    return total / weight if weight else 0.0


def weighted_before(criteria: list[dict]) -> float:
    total = 0.0
    weight = 0.0
    for item in criteria:
        total += mean(item["before"]) * item["weight"]
        weight += item["weight"]
    return total / weight if weight else 0.0


def _row(name: str, weight: int, before: tuple[int, ...], after: tuple[int, ...], evidence: str) -> dict:
    return {
        "name": name,
        "weight": weight,
        "before": dict(zip(PERSONAS, before)),
        "after": dict(zip(PERSONAS, after)),
        "evidence": evidence,
    }


# Five-tuples are teknik, urun, tasarim, etki, supheci.
# Evaluated by independent jury (Nebius Nemotron Ultra 550B).
# Before is initial independent jury evaluation; After is after closing the lowest criteria with tests & UX evaluation.

AMAZON = [
    _row("Tech Implementation", 25, (9, 8, 7, 8, 6), (9, 8, 7, 8, 6),
         "MCP SDK 2.x Streamable HTTP mounted at /mcp/ with 7 tools, 97 passing pytest tests, hard budget ledger enforced, live Nebius Nemotron loop."),
    _row("Design", 25, (7, 6, 6, 7, 4), (8, 7, 8, 8, 6),
         "tests/test_dashboard_ux.py (#learning, #savings, #isolated, viewport responsive) ve docs/UX_EVALUATION.md yapay zekâ kişilikleriyle simüle edilmiş sezgisel inceleme (gerçek kullanıcı testi değil) hazırlandı."),
    _row("Potential Impact", 25, (8, 8, 7, 9, 5), (8, 8, 7, 9, 5),
         "docs/RELIABILITY_REAL.md: 5 gerçek sitede ölçülen $0.0238 harcama, onay kapıları, ikinci koşuda sıfır LLM çağrılı tarif tekrarı."),
    _row("Quality of the Idea", 25, (8, 8, 6, 8, 5), (8, 8, 6, 8, 5),
         "Onay kapısı mimarisi, bütçe muhasebesi, docs/FRICTION_LOG.md gerçek SDK/Playwright takılma kayıtları."),
]

NEBIUS = [
    _row("Technological Implementation", 25, (9, 8, 7, 8, 7), (9, 8, 7, 8, 7),
         "Canlı Nebius Token Factory (Nemotron 3.5 Lightning & Nemotron Ultra 550B), faturalı dolar/token muhasebesi ($0.0238/41 çağrı), 97 yeşil test."),
    _row("Design", 25, (8, 8, 9, 8, 6), (8, 8, 9, 8, 6),
         "Dashboard öğrenme eğrisi çubuk grafiği, tasarruf paneli, canlı ekran akışı ve responsive düzen."),
    _row("Potential Impact", 25, (8, 9, 8, 9, 5), (8, 9, 8, 9, 5),
         "Tarif önbellekleme ve bütçe tavanı ile tekrarlanan işlerde marjinal model maliyetini sıfırlama kanıtı."),
    _row("Quality of the Idea", 25, (9, 8, 7, 8, 6), (9, 8, 7, 8, 6),
         "İki katmanlı yönlendirme (hızlı varsayılan, onarımda güçlü), CV geri dönüşlü DOM toparlama."),
]

OPEN_AGENT = [
    _row("Impact", 30, (6, 7, 5, 8, 4), (6, 7, 5, 8, 4),
         "İzin listesi ve onay kapısıyla güvenli tarayıcı otomasyonu; docs/OPEN_AGENT_PLAN.md Tinkerer takvimi."),
    _row("Technical", 20, (8, 7, 5, 7, 6), (8, 7, 5, 7, 6),
         "Çoklu ajan konsey uzlaşısı (council_ask), muhakeme izleri (explain.jsonl), 97 geçen test."),
    _row("Innovation", 15, (8, 7, 5, 8, 5), (8, 7, 5, 8, 5),
         "Tekrar koşuda sıfır maliyetli tarif oynatma, sert bütçe koruması."),
    _row("Demo", 15, (6, 7, 7, 7, 4), (6, 7, 7, 7, 4),
         "62 saniyelik video videos/demo.mp4; dashboard, öğrenme eğrisi ve koruma demosu."),
    _row("Product & UX", 10, (7, 8, 8, 7, 5), (7, 8, 8, 7, 5),
         "Koşu genel görünümü, canlı kareler, adım hedefleri ve bütçe metrikleri."),
    _row("Sponsor Tech", 10, (7, 6, 5, 7, 4), (9, 8, 6, 8, 6),
         "tests/test_nemotron_sponsor.py ile NVIDIA Nemotron entegrasyonu, Open Agent fonksiyon şeması ve iki katmanlı fiyatlama kanıtlandı."),
]

VULTR = [
    _row("Application of Technology", 25, (6, 7, 5, 6, 4), (8, 8, 6, 7, 6),
         "tests/test_vultr_sandbox.py: VultrAPI yaşam döngüsü (get, list, user_data), hata toparlanması, sandbox temizliği ve izole çalıştırma testle kanıtlandı."),
    _row("Presentation", 25, (6, 7, 6, 6, 4), (6, 7, 6, 6, 4),
         "62 sn video videos/demo.mp4 içindeki izolasyon anı, docs/rules/vultr.md tam kural dokümantasyonu."),
    _row("Business Value", 25, (7, 8, 5, 8, 5), (7, 8, 5, 8, 5),
         "Sert bütçe durdurması (0.50$/0.05$), izin/engel listesi, hassas eylemlerde onay kapısı ile kurumsal güvenlik."),
    _row("Originality", 25, (7, 8, 6, 7, 5), (7, 8, 6, 7, 5),
         "Her koşuda blast_radius.json dosyalar, alan adları, süre ve harcamayı kaydeden Blast Radius Zero mimarisi."),
]

OPENCV = [
    _row("Technical execution", 30, (6, 5, 4, 4, 4), (7, 6, 5, 5, 5),
         "test_vision_finds_button ve test_vision_change_and_dom_recovery_are_measured. OpenCV 5 pinli."),
    _row("Innovation", 20, (5, 4, 4, 4, 3), (6, 5, 5, 4, 4),
         "Seçici kırılınca görme ile Continue seçimi kontrollü sette ölçülür."),
    _row("Real-world impact", 20, (3, 3, 2, 3, 2), (4, 3, 3, 3, 2),
         "Canlı üçüncü parti sayfa kasıtlı bozulmadı. Etki ölçülmedi."),
    _row("User experience", 10, (5, 5, 6, 4, 3), (6, 5, 6, 4, 4),
         "Onarım insan onayıyla durur. Ayrı bir görme arayüzü yok."),
    _row("Documentation and presentation", 10, (4, 4, 4, 3, 3), (6, 5, 5, 4, 4),
         "docs/AGENTIC_VISION.md ve docs/OPENCV_AWS.md."),
    _row("Responsible cloud delivery", 10, (1, 1, 1, 1, 1), (2, 2, 2, 2, 2),
         "Hesap açılmadı. Adımlar yazıldı, deploy ölçülmedi."),
]

DEFAULT = [
    _row("Teknik", 25, (4, 4, 3, 3, 3), (6, 5, 4, 4, 4), "İlgili test dosyası ve varsayılan rubrik."),
    _row("Yenilik", 20, (4, 3, 3, 3, 2), (5, 4, 4, 3, 3), "Mevcut ajan döngüsü. Yarışmaya özel yeni tez sınırlı."),
    _row("Etki", 20, (3, 3, 2, 2, 2), (3, 3, 2, 2, 2), "Kullanıcı veya gelir ölçülmedi."),
    _row("Demo", 20, (4, 4, 4, 3, 3), (5, 5, 4, 4, 3), "videos/demo.mp4 64 sn. Yarışma videosu başlık kopyası ayrıca üretilir."),
    _row("UX", 15, (5, 5, 6, 4, 3), (6, 5, 6, 4, 4), "Dashboard öğrenme ve maliyet panosu."),
]


def _default(evidence: str) -> list[dict]:
    rows = []
    for item in DEFAULT:
        copy = {
            "name": item["name"],
            "weight": item["weight"],
            "before": dict(item["before"]),
            "after": dict(item["after"]),
            "evidence": evidence,
        }
        rows.append(copy)
    return rows


COMPETITIONS = [
    {"id": "amazon", "class": "A", "rubric": "resmi, eşit %25", "criteria": AMAZON,
     "prizes": [("Alexa+ 1.", 25000, 0.005), ("Alexa+ 2.", 15000, 0.008), ("Alexa+ 3.", 4000, 0.01), ("OSS mini", 5000, 0.02)]},
    {"id": "nebius", "class": "A", "rubric": "resmi, eşit %25", "criteria": NEBIUS,
     "prizes": [("1.", 20000, 0.005), ("2.", 10000, 0.008), ("3.", 6000, 0.01), ("Tavily", 3000, 0.01)]},
    {"id": "open-agent", "class": "A", "rubric": "brifing, resmi sayfa yok", "criteria": OPEN_AGENT,
     "prizes": [("1.", 8000, 0.005), ("2.", 4000, 0.008), ("3.", 2000, 0.01)]},
    {"id": "vultr", "class": "A", "rubric": "varsayılan rubrik", "criteria": VULTR,
     "prizes": [("1. nakit", 5000, 0.01), ("2. nakit", 3000, 0.015), ("3. nakit", 1000, 0.02)]},
    {"id": "opencv", "class": "B", "rubric": "resmi OpenCV yüzdeleri", "criteria": OPENCV,
     "prizes": [("1.", 5000, 0.01), ("2.", 3000, 0.012), ("3.", 2000, 0.015), ("Agentic Vision", 1000, 0.02)]},
    {"id": "build-with-ai", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("make test anahtarsız yeşil. Prototip şartın kendisi. Kalabalık bilinmiyor."),
     "prizes": [("1.", 2500, 0.05)]},
    {"id": "hetic", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("playbooks/shop_old_listings.yaml ve test_s3_old_listings."),
     "prizes": [("1.", 1100, 0.02)]},
    {"id": "climatechain", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("grasshopper/realweb/climate.py yalnızca sayfadaki cümleyi yazar. İklim ürünü değil."),
     "prizes": [("1.", 1500, 0.005)]},
    {"id": "ytu-meta", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("Yerinde hackathon. 6.000$ havuz. Kişisel pay bilinmiyor, EV'ye girmez."),
     "prizes": []},
    {"id": "imagine-cup", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("docs/IMAGINE_CUP_PLAN.md. İki Azure servisi bağlı değil. 2027 kuralları DOĞRULANMADI."),
     "prizes": [("büyük", 100000, 0.002)]},
    {"id": "gemma", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("Uyum zayıf. GEMMA_MODEL boş. test_ollama_generate_body sahte sunucu."),
     "prizes": [("paper", 35000, 0.002)]},
    {"id": "assemblyai", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("Sesli ajan demosu yok. Anahtar yok. Süre dar."),
     "prizes": [("nakit", 5000, 0.002)]},
    {"id": "asus", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("submissions/asus/PRESENTATION.md. UGen300 yok. Donanım ölçülmedi."),
     "prizes": [("Lightning", 4500, 0.005)]},
    {"id": "ing", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("Mock banka onay, limit, iz. Ödül cihaz, nakit EV'ye girmez."),
     "prizes": []},
    {"id": "kestra", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("Bu repoda Kestra PR'ı yok."),
     "prizes": []},
    {"id": "hackster-nordic", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("Ödül ve tarih bilinmiyor. EV'ye nakit girmez."),
     "prizes": []},
    {"id": "arbiter", "class": "B", "rubric": "varsayılan rubrik", "criteria": _default("eligible=false. Girilmez. Olasılık 0."),
     "prizes": []},
]


def place_probability(base: float, score: float) -> float:
    factor = min(3.0, (score / 6.0) ** 2)
    return base * factor


def lowest_three(criteria: list[dict]) -> list[dict]:
    ranked = sorted(criteria, key=lambda item: (mean(item["after"]), -item["weight"]))
    return ranked[:3]
