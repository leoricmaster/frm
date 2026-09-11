#!/usr/bin/env python3
"""教程静态自检：图片引用存在、无外部资源、骨架齐全。用法: check.py file.html ..."""
import re, sys, pathlib

BASE = pathlib.Path(__file__).parent
SKELETON = {  # 每类页必须包含的 <h2> 文案片段
    "index":  ["通用入门", "术语速查", "日常运维", "代码交付", "需求管理"],
    "developer":     ["你是谁", "能做", "任务流", "自救", "红线"],
    "owner":         ["你是谁", "能做", "任务流", "自救", "红线"],
    "viewer":        ["你是谁", "能做", "任务流", "自救", "红线"],
    "platform":      ["你是谁", "能做", "任务流", "自救", "红线"],
    "submitter":     ["你是谁", "能做", "任务流", "自救", "红线"],
    "ops":           ["你是谁", "能做", "实施主线", "查阅", "红线"],
    "governance":    ["你是谁", "能做", "治理", "红线"],
}
def pagetype(name):
    if name == "index.html": return "index"
    return name.replace(".html", "")

fails = 0
for arg in sys.argv[1:]:
    p = BASE / arg
    html = p.read_text(encoding="utf-8")
    errs = []
    for src in re.findall(r'(?:src|href)="([^"]+)"', html):
        if src.startswith(("http://", "https://", "//")):
            errs.append(f"外部资源引用: {src}")
        elif src.startswith(("assets/", "index.html")) and not (BASE / src).exists():
            errs.append(f"引用的文件不存在: {src}")
    pt = pagetype(p.name)
    for frag in SKELETON.get(pt, []):
        if frag not in html:
            errs.append(f"缺少骨架小节: {frag}")
    n_img = len(re.findall(r'<img ', html))
    if pt not in ("index", "ops") and n_img < 2:
        errs.append(f"图片过少({n_img}), 图文并茂要求 >=2")
    if errs:
        fails += 1
        print(f"[FAIL] {arg} — " + "; ".join(errs))
    else:
        print(f"[OK] {arg} — {n_img} imgs, skeleton ✓")
sys.exit(1 if fails else 0)
