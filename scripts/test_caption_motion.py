#!/usr/bin/env python3
"""Lightweight tests for the pure ASS motion-tag builder without importing media dependencies."""
import ast
from pathlib import Path
from typing import Any, Dict, Optional

source_path = Path("backend/video_engine.py")
tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
wanted = {"_safe_caption_float", "build_caption_motion_tags"}
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
if {node.name for node in functions} != wanted:
    raise SystemExit("Caption motion helper definitions were not found")

namespace = {"Any": Any, "Dict": Dict, "Optional": Optional}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(source_path), "exec"), namespace)
build = namespace["build_caption_motion_tags"]

if build({"motion_preset": "none"}) != "":
    raise SystemExit("Static preset must not add animation tags")
if build({"motion_preset": "smooth_pop", "motion_intensity": 0}) != "":
    raise SystemExit("Zero intensity must disable animation")

presets = [
    "cinematic", "punch_impact", "smooth_pop", "kinetic_flow", "bounce_pro",
    "glitch_pro", "type_reveal", "slide_motion", "focus_zoom",
]
for preset in presets:
    tags = build({"motion_preset": preset, "motion_intensity": 55, "motion_speed": 1.0})
    if not tags.startswith(r"\fad("):
        raise SystemExit(f"{preset} did not produce a fade-in/out ASS tag")
    if len(tags) > 300:
        raise SystemExit(f"{preset} generated unexpectedly long tags")

if build({"motion_preset": "untrusted-ass-injection"}) != "":
    raise SystemExit("Unknown motion preset must be rejected")
if build({"motion_preset": "cinematic", "motion_speed": 999}) != build({"motion_preset": "cinematic", "motion_speed": 2}):
    raise SystemExit("Motion speed must be clamped to its supported range")

print("Caption motion preset tests passed (9 presets + static/validation cases).")
