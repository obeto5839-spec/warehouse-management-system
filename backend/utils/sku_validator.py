from typing import Dict, Any, Tuple, List

# ---------------------------------------------------------------
# 各分类的规格字段定义（简化版）
# SKU 录入规则：品牌 + 系列 + 型号 + 规格
# 规格只保留简单的文本描述，不再要求填写详细硬件参数
# 
# 示例：
#   CPU：英特尔(品牌) 酷睿(系列) i5-13490F(型号)
#   显卡：华硕(品牌) 雪豹(系列) RTX 4060 Ti(型号) O16G(规格)
#   内存：宏碁(品牌) 凌霜(系列) 32G(16*2)6400C32(规格) 海力士A-DIE(规格)
# ---------------------------------------------------------------
CATEGORY_PROPERTY_SCHEMA: Dict[str, List[Dict[str, Any]]] = {
    "显卡": [
        {"key": "spec", "label": "规格", "placeholder": "如 O16G / 12G OC", "required": False, "type": "input"},
    ],
    "CPU": [
        {"key": "spec", "label": "规格", "placeholder": "如 盒装 / 散片", "required": False, "type": "select", "options": ["盒装", "散片"]},
    ],
    "内存": [
        {"key": "spec", "label": "规格", "placeholder": "如 32G(16*2)6400C32", "required": False, "type": "input"},
        {"key": "spec2", "label": "颗粒/补充", "placeholder": "如 海力士A-DIE", "required": False, "type": "input"},
    ],
    "主板": [
        {"key": "spec", "label": "规格", "placeholder": "如 WIFI-D5 / WIFI", "required": False, "type": "input"},
    ],
    "硬盘": [
        {"key": "spec", "label": "规格", "placeholder": "如 1TB PCIE4.0 7200M/S", "required": False, "type": "input"},
    ],
    "电源": [
        {"key": "spec", "label": "规格", "placeholder": "如 750W 金牌全模黑色", "required": False, "type": "input"},
    ],
    "机箱": [
        {"key": "spec", "label": "规格", "placeholder": "如 银色 / 白色", "required": False, "type": "input"},
    ],
    "散热器": [
        {"key": "spec", "label": "规格", "placeholder": "如 白色 / 黑色", "required": False, "type": "input"},
    ],
    "显示器": [
        {"key": "spec", "label": "规格", "placeholder": "如 27寸 2K 165Hz", "required": False, "type": "input"},
    ],
    "键盘": [
        {"key": "spec", "label": "规格", "placeholder": "如 红轴 三模 白色", "required": False, "type": "input"},
    ],
    "鼠标": [
        {"key": "spec", "label": "规格", "placeholder": "如 三模 白色", "required": False, "type": "input"},
    ],
    "耳机": [
        {"key": "spec", "label": "规格", "placeholder": "如 头戴式 无线", "required": False, "type": "input"},
    ],
}


def get_property_schema(category: str = None) -> Dict:
    """
    返回属性字段定义。
    category 为空则返回全部；否则返回指定分类的。
    """
    if category:
        return {category: CATEGORY_PROPERTY_SCHEMA.get(category, [])}
    return CATEGORY_PROPERTY_SCHEMA


def validate_sku_properties(category: str, properties: Dict[str, Any]) -> Tuple[bool, str]:
    """
    验证 SKU 的 properties 字段是否符合规范
    简化版：所有规格参数均为选填，不做强制校验
    """
    if properties is None:
        properties = {}

    schema = CATEGORY_PROPERTY_SCHEMA.get(category)
    if not schema:
        return True, ""

    # 简化版不再强制要求必填字段，所有规格参数均为选填
    return True, ""
