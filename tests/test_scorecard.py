"""The scorecard math and the Monte Carlo warning. Scores are judgments, not a claim of 8."""

from __future__ import annotations

from scripts.ev_model import contest_outcomes, render, simulate
from scripts.scores import COMPETITIONS, PERSONAS, mean, place_probability, weighted


def test_weights_sum_and_the_probability_cap_holds():
    for contest in COMPETITIONS:
        assert sum(item["weight"] for item in contest["criteria"]) == 100
        for item in contest["criteria"]:
            assert set(item["after"]) == set(PERSONAS)
            assert item["evidence"]
            assert 0 <= mean(item["after"]) <= 10
        score = weighted(contest["criteria"])
        assert score < 8.0
        for _name, _dollars, base in contest["prizes"]:
            assert place_probability(base, score) <= base * 3 + 1e-9


def test_place_probabilities_inside_one_contest_do_not_overlap():
    for contest in COMPETITIONS:
        if not contest["prizes"]:
            continue
        total = sum(prob for _name, _dollars, prob in contest_outcomes(contest))
        assert total <= 1 + 1e-9


def test_monte_carlo_is_stable_and_states_the_correlation_warning():
    first = simulate(draws=4000, seed=7)
    second = simulate(draws=4000, seed=7)
    assert first == second
    text = render(first)
    assert "TAHMİN" in text
    assert "bağımsız" in text
    assert "iyimser" in text
    assert 0 <= first["p_20k"] <= 1
    assert first["expected_usd"] >= 0
