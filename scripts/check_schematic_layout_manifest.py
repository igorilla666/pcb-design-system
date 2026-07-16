#!/usr/bin/env python3
"""Validate a declarative schematic-layout manifest and its component coverage."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


MANIFEST = Path("docs/schematic-layout.json")
PAPER_MM = {
    "A4": (297, 210), "A3": (420, 297), "A2": (594, 420),
    "A1": (841, 594), "A0": (1189, 841),
}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("root must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--require-accepted", action="store_true")
    parser.add_argument("--electrical-manifest", type=Path, help="Verify every electrical component is assigned once")
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    path = root / MANIFEST
    errors: list[str] = []
    try:
        data = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Schematic layout manifest: FAIL\n- {exc}")
        return 1

    sheet = data.get("sheet")
    if not isinstance(sheet, dict):
        errors.append("sheet must be an object")
        sheet = {}
    size, orientation, grid = sheet.get("size"), sheet.get("orientation"), sheet.get("grid_mm")
    if size not in PAPER_MM or orientation not in {"landscape", "portrait"}:
        errors.append("sheet requires a supported size and landscape or portrait orientation")
        width = height = 0.0
    else:
        width, height = PAPER_MM[size]
        if orientation == "portrait":
            width, height = height, width
    if not isinstance(grid, (int, float)) or grid <= 0:
        errors.append("sheet.grid_mm must be positive")
        grid = 1.0
    if not isinstance(sheet.get("reading_flow"), str) or not sheet["reading_flow"].strip():
        errors.append("sheet.reading_flow is required")

    generation = data.get("generation", {})
    if not isinstance(generation, dict) or generation.get("mode") not in {"manual", "generator"}:
        errors.append("generation.mode must be manual or generator")
    elif generation["mode"] == "generator":
        source = generation.get("source")
        if not isinstance(source, str) or not source.startswith("tools/pcb_design/generators/"):
            errors.append("generator source must be under tools/pcb_design/generators/")
        elif not (root / source).is_file():
            errors.append(f"generator source is missing: {source}")

    blocks = data.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        errors.append("at least one functional block is required")
        blocks = []
    ids: set[str] = set()
    refs: set[str] = set()
    rectangles: list[tuple[str, float, float, float, float]] = []
    for index, block in enumerate(blocks, start=1):
        if not isinstance(block, dict):
            errors.append(f"block {index} must be an object")
            continue
        block_id, title = block.get("id"), block.get("title")
        if not isinstance(block_id, str) or not block_id or block_id in ids:
            errors.append(f"block {index} has a missing or duplicate id")
        else:
            ids.add(block_id)
        if not isinstance(title, str) or not title.strip():
            errors.append(f"block {block_id or index} needs a title")
        bounds = block.get("bounds_mm")
        if not isinstance(bounds, list) or len(bounds) != 4 or not all(isinstance(value, (int, float)) for value in bounds):
            errors.append(f"block {block_id or index} needs numeric [x, y, width, height] bounds_mm")
            continue
        x, y, block_width, block_height = map(float, bounds)
        if block_width <= 0 or block_height <= 0 or x < 0 or y < 0 or x + block_width > width or y + block_height > height:
            errors.append(f"block {block_id or index} is outside the selected sheet")
        if any(not math.isclose(value / grid, round(value / grid), abs_tol=1e-6) for value in bounds):
            errors.append(f"block {block_id or index} is not aligned to the declared grid")
        rectangles.append((block_id or str(index), x, y, block_width, block_height))
        components = block.get("components", [])
        if not isinstance(components, list) or not all(isinstance(ref, str) and ref for ref in components):
            errors.append(f"block {block_id or index} components must be a list of references")
            continue
        for ref in components:
            if ref in refs:
                errors.append(f"component reference assigned more than once: {ref}")
            refs.add(ref)
    for index, (left_id, x1, y1, w1, h1) in enumerate(rectangles):
        for right_id, x2, y2, w2, h2 in rectangles[index + 1:]:
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                errors.append(f"functional blocks overlap: {left_id} and {right_id}")

    if args.require_accepted:
        if data.get("status") != "accepted":
            errors.append("manifest status must be accepted for batch review")
        review = data.get("visual_review")
        if not isinstance(review, list) or len([item for item in review if isinstance(item, str) and item.strip()]) < 3:
            errors.append("accepted manifest needs at least three visual_review entries")
    if args.electrical_manifest:
        electrical_path = args.electrical_manifest if args.electrical_manifest.is_absolute() else root / args.electrical_manifest
        try:
            electrical = load_json(electrical_path)
            actual = {item["ref"] for item in electrical.get("components", []) if isinstance(item, dict) and item.get("ref")}
            if missing := actual - refs:
                errors.append("components missing from layout blocks: " + ", ".join(sorted(missing)))
            if extra := refs - actual:
                errors.append("layout blocks reference absent components: " + ", ".join(sorted(extra)))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"cannot validate electrical component coverage: {exc}")

    if errors:
        print("Schematic layout manifest: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(
        "Schematic layout manifest: PASS "
        f"({size} {orientation}; grid={grid:g} mm; blocks={len(blocks)}; components={len(refs)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
