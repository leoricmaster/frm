#!/usr/bin/env python3
"""原型假训练：读数据集→产"模型权重"。真实 GPU 训练是正式实施项。"""
import hashlib, json, os, sys

data_path = sys.argv[1]
with open(data_path, "rb") as f:
    blob = f.read()
print(f"dataset {len(blob)} bytes loaded")

os.makedirs("outputs", exist_ok=True)
weights = hashlib.sha256(blob).digest() + blob[:1024]   # 内容派生的假权重
with open("outputs/model.pt", "wb") as f:
    f.write(weights)
print(json.dumps({"model": "outputs/model.pt", "params": len(weights)}))
