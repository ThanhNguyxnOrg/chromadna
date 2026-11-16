from scripts.import_community_presets import build_profile_ids


def test_duplicate_upstream_slugs_get_stable_collision_safe_ids():
    items = [
        {"slug": "kodak-portra-400-1", "file": "Presets/Color-Negative/Kodak Portra 400 +1.xmp"},
        {"slug": "kodak-portra-400-1", "file": "Presets/Color-Negative/Kodak Portra 400 -1.xmp"},
    ]

    first = build_profile_ids(items)
    second = build_profile_ids(items)

    assert first == second
    assert len(set(first)) == 2
    assert all(profile_id.startswith("emulsion_kodak_portra_400_1_") for profile_id in first)


def test_normalized_slug_collisions_are_also_detected():
    items = [
        {"slug": "Portra 400", "file": "Presets/a.xmp"},
        {"slug": "portra-400", "file": "Presets/b.xmp"},
    ]

    profile_ids = build_profile_ids(items)

    assert len(set(profile_ids)) == 2
    assert all(profile_id.startswith("emulsion_portra_400_") for profile_id in profile_ids)


def test_unique_upstream_slugs_keep_readable_legacy_ids():
    items = [{"slug": "kodak-gold-200", "file": "Presets/Kodak Gold 200.xmp"}]

    assert build_profile_ids(items) == ["emulsion_kodak_gold_200"]
