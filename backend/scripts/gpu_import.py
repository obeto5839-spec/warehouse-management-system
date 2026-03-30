"""
GPU SKU 批量录入脚本

输入格式：JSON 数组，每条记录包含以下字段：
  - brand: 制造品牌（华硕、蓝宝石、微星...）
  - series: 子系列（ROG Strix、超白金、魔龙...）
  - chip_brand: 芯片品牌（NVIDIA、AMD）
  - product_line: 产品大类（GeForce、Radeon）
  - tech_prefix: 技术前缀（RTX、RX、GTX...）
  - core_model: 核心型号（4070、7900、4060...）
  - core_suffix: 核心后缀（Ti SUPER、XTX、Ti...），可为空字符串
  - vram: 显存容量（16GB、24GB、12GB...）
  - edition: 特殊版本标识（OC、GAMING、白色...），可选字段

使用方式：
  # 从文件导入
  python scripts/gpu_import.py gpu_data.json

  # 交互式粘贴（粘贴后 Windows 按 Ctrl+Z 回车，Linux/Mac 按 Ctrl+D）
  python scripts/gpu_import.py

示例输入：
[
  {
    "brand": "华硕",
    "series": "ROG Strix",
    "chip_brand": "NVIDIA",
    "product_line": "GeForce",
    "tech_prefix": "RTX",
    "core_model": "4070",
    "core_suffix": "Ti SUPER",
    "vram": "16GB",
    "edition": "OC"
  }
]
"""

import sys
import json
import os

# 将 backend 目录加入 Python 路径，以便复用项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal, engine
from database.models.base import Base
from database.crud.sku_crud import get_sku_by_exact_match, create_sku
from database.schemas.sku_schema import SKUCreate

# 确保表存在
Base.metadata.create_all(bind=engine)

REQUIRED_FIELDS = ["brand", "series", "chip_brand", "product_line", "tech_prefix", "core_model", "vram"]


def build_sku(gpu: dict) -> SKUCreate:
    """将 GPU 结构化数据转换为 SKUCreate 对象"""
    # 拼接 model_name：技术前缀 + 核心型号 + 核心后缀
    parts = [gpu["tech_prefix"], gpu["core_model"]]
    core_suffix = gpu.get("core_suffix", "").strip()
    if core_suffix:
        parts.append(core_suffix)
    model_name = " ".join(parts)

    # 构建 properties
    properties = {
        "chip_brand": gpu["chip_brand"],
        "product_line": gpu["product_line"],
        "vram": gpu["vram"],
    }
    edition = gpu.get("edition", "").strip()
    if edition:
        properties["edition"] = edition

    return SKUCreate(
        category="显卡",
        brand=gpu["brand"],
        series=gpu.get("series") or None,
        model_name=model_name,
        properties=properties,
    )


def validate_entry(gpu: dict, index: int) -> list[str]:
    """校验单条记录，返回错误列表"""
    errors = []
    for field in REQUIRED_FIELDS:
        if not gpu.get(field, "").strip():
            errors.append(f"第 {index + 1} 条：缺少必填字段 '{field}'")
    return errors


def main():
    # 读取输入
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        print("请粘贴 JSON 数据（Windows: Ctrl+Z 回车结束, Linux/Mac: Ctrl+D 结束）：")
        raw = sys.stdin.read()

    # 解析 JSON
    try:
        gpu_list = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败：{e}")
        sys.exit(1)

    if not isinstance(gpu_list, list):
        print("输入必须是 JSON 数组")
        sys.exit(1)

    print(f"\n共读取 {len(gpu_list)} 条 GPU 数据")

    # 校验所有记录
    all_errors = []
    for i, gpu in enumerate(gpu_list):
        all_errors.extend(validate_entry(gpu, i))

    if all_errors:
        print("\n数据校验失败：")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    # 录入数据库
    db = SessionLocal()
    success = 0
    skipped = 0
    failed = 0

    try:
        for i, gpu in enumerate(gpu_list):
            sku_data = build_sku(gpu)
            label = f"{sku_data.brand} {sku_data.series or ''} {sku_data.model_name}".strip()

            # 查重（category + brand + series + model_name）
            existing = get_sku_by_exact_match(
                db,
                category=sku_data.category,
                brand=sku_data.brand,
                model_name=sku_data.model_name,
                series=sku_data.series,
            )
            if existing:
                print(f"  [跳过] {label} （已存在，ID={existing.id}）")
                skipped += 1
                continue

            # 写入
            try:
                result = create_sku(db, sku_data)
                print(f"  [录入] {label} （ID={result.id}）")
                success += 1
            except Exception as e:
                print(f"  [失败] {label} （{e}）")
                db.rollback()
                failed += 1
    finally:
        db.close()

    # 汇总
    print(f"\n录入完成：成功 {success}，跳过 {skipped}，失败 {failed}")


if __name__ == "__main__":
    main()
