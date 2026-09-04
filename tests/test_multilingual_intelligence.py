"""
Multilingual AI Product Intelligence Engine Unit Tests
Tests script detection, typo tolerance, Indic transliteration normalization,
budget extraction, 8-tier zero-result recovery, and search intelligence telemetry.
"""
import pytest
from backend.language_service import (
    language_service,
    levenshtein_distance,
    calculate_similarity
)
from backend.discovery_engine import discovery_engine
from backend.agentic_checkout import agentic_checkout


def test_levenshtein_and_similarity():
    # Exact match
    assert levenshtein_distance("shoes", "shoes") == 0
    assert calculate_similarity("shoes", "shoes") == 1.0

    # Common typos
    assert calculate_similarity("snekaers", "sneakers") >= 0.75
    assert calculate_similarity("headphons", "headphones") >= 0.85
    assert calculate_similarity("laptoop", "laptop") >= 0.85
    assert calculate_similarity("iphne", "iphone") >= 0.75


def test_fuzzy_category_matching():
    match, score, syn, typo = language_service.get_fuzzy_category_match("snekaers")
    assert match == "shoes"
    assert score >= 0.75

    match, score, syn, typo = language_service.get_fuzzy_category_match("headphons")
    assert match == "headphones"
    assert score >= 0.85

    match, score, syn, typo = language_service.get_fuzzy_category_match("laptoop")
    assert match == "laptop"
    assert score >= 0.85


def test_script_detection_and_transliterations():
    # Tamil native script
    res_ta = language_service.normalize_multilingual_query("செருப்பு")
    assert res_ta["detected_language"] in ["ta", "en"]
    assert res_ta["category"] == "shoes"

    # Telugu native script
    res_te = language_service.normalize_multilingual_query("చెప్పులు")
    assert res_te["detected_language"] in ["te", "en"]
    assert res_te["category"] in ["shoes", "sandals"]

    # Hindi / Devanagari script
    res_hi = language_service.normalize_multilingual_query("जूता")
    assert res_hi["detected_language"] in ["hi", "en"]
    assert res_hi["category"] == "shoes"

    # Hindi Transliteration (Hinglish)
    for variant in ["juta", "joota", "jotha", "jutha"]:
        res = language_service.normalize_multilingual_query(variant)
        assert res["category"] == "shoes"

    # Tamil Transliteration (Tanglish)
    res_tanglish = language_service.normalize_multilingual_query("seruppu")
    assert res_tanglish["category"] == "shoes"

    # Telugu Transliteration
    res_telugu_rom = language_service.normalize_multilingual_query("cheppulu")
    assert res_telugu_rom["category"] in ["shoes", "sandals"]


def test_multilingual_budget_extraction():
    # Tanglish + Tamil mixed budget
    res_budget1 = language_service.normalize_multilingual_query("₹5000 குள்ள headphones")
    assert res_budget1["budget"] == 5000.0
    assert res_budget1["category"] == "headphones"

    # Hinglish budget
    res_budget2 = language_service.normalize_multilingual_query("sasta joota under 2000")
    assert res_budget2["budget"] == 2000.0
    assert res_budget2["category"] == "shoes"

    # English budget
    res_budget3 = language_service.normalize_multilingual_query("best laptop below 60000")
    assert res_budget3["budget"] == 60000.0
    assert res_budget3["category"] == "laptop"


def test_discovery_engine_8_tier_ladder():
    # Typo match: 'snekaers'
    res_sneakers = discovery_engine.search("snekaers")
    assert res_sneakers["total_count"] > 0
    assert "search_intelligence" in res_sneakers
    assert res_sneakers["search_intelligence"]["recovery_tier"] in [
        "EXACT_MATCH", "TYPO_TOLERANT_MATCH", "NORMALIZED_MATCH", "LANGUAGE_ALIAS_MATCH", "CATEGORY_INTENT_MATCH"
    ]

    # Transliteration match: 'joota'
    res_joota = discovery_engine.search("joota")
    assert res_joota["total_count"] > 0
    assert res_joota["search_intelligence"]["original_query"] == "joota"

    # Native script match: 'செருப்பு'
    res_tamil = discovery_engine.search("செருப்பு")
    assert res_tamil["total_count"] > 0

    # Spanish match: 'zapatos'
    res_es = discovery_engine.search("zapatos")
    assert res_es["total_count"] > 0


def test_agentic_checkout_multilingual_turn():
    # Turn with typo and mixed language
    res = agentic_checkout.process_customer_turn("Show me running snekaers under 5000")
    assert len(res["recommendations"]) > 0
    assert "search_intelligence" in res
    assert res["search_intelligence"]["confidence_score"] >= 80
