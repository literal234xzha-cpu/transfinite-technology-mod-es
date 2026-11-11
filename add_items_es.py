#!/usr/bin/env python3
"""
Traduce y añade ítems, líquidos y estados al bundle_es.properties
"""
import translators as ts
import time
import re

OUTPUT = "bundles/bundle_es.properties"

BACKENDS = ["alibaba", "baidu", "bing"]

def translate(text):
    if not text.strip():
        return text
    if not re.search(r'[\u4e00-\u9fff]', text):
        return text  # no tiene chino, skip
    for backend in BACKENDS:
        for attempt in range(2):
            try:
                result = ts.translate_text(text, translator=backend, from_language="zh", to_language="es")
                if result and result.strip():
                    return result.strip()
            except Exception as e:
                time.sleep(2)
    return text

# Datos extraídos del content/
ITEMS = [
    ("00磁暴合金",  "泽塔合金",    "Posee tenacidad y dureza absolutas, es el material de los equipos centrales del consejo, un recurso de combate importante."),
    ("0铜铅合金",   "基础合金",    "简易的坚固"),
    ("1共振石",     "共振石",      "意外中发现的奇特矿石，是超限集团一些尖端设备的重要原材料"),
    ("1复合物",     "复合物",      "柔软而稳定的空间材料"),
    ("1绝缘钢",     "绝缘钢",      "绝缘，硬度不错，适合当做多种材料"),
    ("1集成电路",   "集成电路",    "精密电路，用于一些高级超限技术的设施"),
    ("2阻断合金",   "阻断合金",    "阻断合金，稳定，反电光武器，较高硬度"),
    ("2高能芯片",   "高能芯片",    "精密芯片，制作工艺复杂，用于一些尖端超限技术设施"),
    ("6风暴催化剂", "风暴催化剂",  "以共振石为基础而研发出来的催化剂，其特殊的性质甚至能使物质与能量发生转化"),
    ("敬请期待",    "敬请期待",    "前面的区域以后再来探索吧"),
]

LIQUIDS = [
    ("00再构流体", "再构流体", "具有机械性的流体，可以通过人工控制"),
    ("00冷凝流体", "冷凝流体", "低温，适合用于散热"),
]

STATUS = [
    ("不灭",   "不灭"),
    ("僚机加速", "僚机加速"),
    ("冲刺",   "冲刺"),
    ("凋零",   "凋零"),
    ("列阵",   "列阵"),
    ("协攻",   "协攻"),
    ("弹性防御", "弹性防御"),
    ("战术",   "战术"),
    ("掩体无效", "掩护无效"),
    ("斩杀",   "斩杀"),
    ("煅烧",   "煅烧"),
    ("狂化",   "狂热"),
    ("甲板损坏", "甲板损坏"),
    ("破甲",   "破甲"),
    ("脆裂",   "物理脆弱"),
    ("自毁",   "自毁"),
    ("蜂群",   "蜂群护卫"),
    ("量子锁定", "量子锁定"),
    ("闪电突袭", "闪电突袭"),
    ("静止",   "静止"),
    ("饱和打击", "饱和打击"),
]

lines = []
lines.append("\n# === ÍTEMS DEL MOD ===")

for (id_, name_zh, desc_zh) in ITEMS:
    print(f"[item] {id_}: {name_zh}")
    name_es = translate(name_zh)
    desc_es = translate(desc_zh)
    time.sleep(1)
    lines.append(f"item.{id_}.name={name_es}")
    lines.append(f"item.{id_}.description={desc_es}")
    print(f"  -> {name_es}")

lines.append("\n# === LÍQUIDOS DEL MOD ===")

for (id_, name_zh, desc_zh) in LIQUIDS:
    print(f"[liquid] {id_}: {name_zh}")
    name_es = translate(name_zh)
    desc_es = translate(desc_zh)
    time.sleep(1)
    lines.append(f"liquid.{id_}.name={name_es}")
    lines.append(f"liquid.{id_}.description={desc_es}")
    print(f"  -> {name_es}")

lines.append("\n# === ESTADOS DE UNIDADES ===")

for (id_, name_zh) in STATUS:
    print(f"[status] {id_}: {name_zh}")
    name_es = translate(name_zh)
    time.sleep(0.8)
    lines.append(f"status.{id_}.name={name_es}")
    print(f"  -> {name_es}")

# Añadir al final del bundle_es.properties
with open(OUTPUT, "a", encoding="utf-8") as f:
    f.write("\n" + "\n".join(lines) + "\n")

print(f"\n✓ Añadidas {len(lines)} líneas a {OUTPUT}")
