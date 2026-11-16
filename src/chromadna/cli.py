"""Command-Line Interface for ChromaDNA."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from .blender import blend_dna_profiles
from .compiler import write_xmp_atomic
from .matcher import adapt_dna_to_image, analyze_image_metrics, recommend_dna_profiles
from .miner import mine_directory, save_catalog
from .previewer import render_before_after

DEFAULT_CATALOG = Path("data/color_dna_catalog.json")


def load_catalog(catalog_path: Path) -> List[Dict[str, Any]]:
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog not found at '{catalog_path}'. Run `chromadna mine` first.")
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return data.get("profiles", [])


def find_profile_by_id(catalog: List[Dict[str, Any]], dna_id: str) -> Dict[str, Any]:
    for p in catalog:
        if p["id"] == dna_id:
            return p
    raise KeyError(f"Color DNA ID '{dna_id}' not found in catalog.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="chromadna", description="Adobe Lightroom Color DNA Engine & XMP Compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_mine = subparsers.add_parser("mine", help="Extract & deduplicate Color DNA from local .xmp/.dng/.lrtemplate folder")
    p_mine.add_argument("input_dir", type=Path)
    p_mine.add_argument("--out", type=Path, default=DEFAULT_CATALOG)
    p_mine.add_argument("--threshold", type=float, default=0.992)
    p_list = subparsers.add_parser("list", help="List extracted Color DNA profiles")
    p_list.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    p_list.add_argument("--tag", type=str, default=None)
    p_comp = subparsers.add_parser("compile", help="Compile a Color DNA profile into a Lightroom .xmp file")
    p_comp.add_argument("--dna", type=str, required=True)
    p_comp.add_argument("--name", type=str, required=True)
    p_comp.add_argument("--out", type=Path, required=True)
    p_comp.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    p_blend = subparsers.add_parser("blend", help="Mathematically blend 2+ Color DNA profiles")
    p_blend.add_argument("--mix", nargs="+", required=True)
    p_blend.add_argument("--name", type=str, required=True)
    p_blend.add_argument("--out", type=Path, required=True)
    p_blend.add_argument("--preview-img", type=Path, default=None)
    p_blend.add_argument("--preview-out", type=Path, default=Path("preview_blend.jpg"))
    p_blend.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    p_ana = subparsers.add_parser("analyze", help="Analyze input photo lighting & recommend Color DNA")
    p_ana.add_argument("image", type=Path)
    p_ana.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    p_match = subparsers.add_parser("match", help="Auto-adapt Exposure/WB of a Color DNA to an input photo")
    p_match.add_argument("image", type=Path)
    p_match.add_argument("--dna", type=str, required=True)
    p_match.add_argument("--name", type=str, default="ChromaDNA Matched")
    p_match.add_argument("--out", type=Path, required=True)
    p_match.add_argument("--preview", type=Path, default=None)
    p_match.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    if args.command == "mine":
        profiles = mine_directory(args.input_dir, similarity_threshold=args.threshold)
        save_catalog(profiles, args.out)
        print(f"Extracted {len(profiles)} unique Color DNA profiles -> {args.out}")
    elif args.command == "list":
        profiles = load_catalog(args.catalog)
        for p in profiles:
            if args.tag and args.tag not in p.get("tags", []):
                continue
            print(f"{p['id']:28s} | {p['category']:24s} | tags={','.join(p['tags'])}")
    elif args.command == "compile":
        profiles = load_catalog(args.catalog)
        dna = find_profile_by_id(profiles, args.dna)
        out_file = write_xmp_atomic(dna, args.out, preset_name=args.name)
        print(f"Compiled XMP preset -> {out_file}")
    elif args.command == "blend":
        profiles = load_catalog(args.catalog)
        weighted: List[Tuple[Dict[str, Any], float]] = []
        for item in args.mix:
            dna_id, weight_str = item.split(":")
            weighted.append((find_profile_by_id(profiles, dna_id), float(weight_str)))
        blended = blend_dna_profiles(weighted)
        out_file = write_xmp_atomic(blended, args.out, preset_name=args.name)
        print(f"Blended XMP preset -> {out_file}")
        if args.preview_img:
            prev_file = render_before_after(args.preview_img, blended, args.preview_out)
            print(f"Rendered Before/After preview -> {prev_file}")
    elif args.command == "analyze":
        metrics = analyze_image_metrics(args.image)
        print(json.dumps({"metrics": metrics}, indent=2))
        if args.catalog.exists():
            profiles = load_catalog(args.catalog)
            recs = recommend_dna_profiles(metrics, profiles, top_k=3)
            print("Recommended DNA IDs:", [r["id"] for r in recs])
    elif args.command == "match":
        profiles = load_catalog(args.catalog)
        base_dna = find_profile_by_id(profiles, args.dna)
        adapted_dna, metrics = adapt_dna_to_image(base_dna, args.image)
        out_file = write_xmp_atomic(adapted_dna, args.out, preset_name=args.name)
        print(f"Matched XMP preset -> {out_file} (Metrics: {metrics})")
        if args.preview:
            prev_file = render_before_after(args.image, adapted_dna, args.preview)
            print(f"Rendered Before/After preview -> {prev_file}")


if __name__ == "__main__":
    main()
