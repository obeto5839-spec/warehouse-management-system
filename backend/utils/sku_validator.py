from typing import Dict, Any, Tuple, List

# ---------------------------------------------------------------
# 各分类的属性字段定义（元数据）
# 每个字段包含：key(英文键), label(中文标签), placeholder, required,
#               type(input/select), options(select 时的候选值)
# ---------------------------------------------------------------
CATEGORY_PROPERTY_SCHEMA: Dict[str, List[Dict[str, Any]]] = {
    "显卡": [
        {"key": "chipset_manufacturer", "label": "芯片厂商", "placeholder": "如 NVIDIA / AMD", "required": True, "type": "select", "options": ["NVIDIA", "AMD", "Intel"]},
        {"key": "memory_size", "label": "显存", "placeholder": "如 12G", "required": True, "type": "input"},
        {"key": "interface", "label": "接口", "placeholder": "如 PCI-E 4.0", "required": True, "type": "select", "options": ["PCI-E 3.0", "PCI-E 4.0", "PCI-E 5.0"]},
        {"key": "tdp", "label": "功耗(W)", "placeholder": "如 170", "required": False, "type": "input"},
    ],
    "CPU": [
        {"key": "socket_type", "label": "插槽", "placeholder": "如 LGA1700", "required": True, "type": "select", "options": ["LGA1700", "LGA1200", "LGA1151", "AM5", "AM4"]},
        {"key": "cores", "label": "核心数", "placeholder": "如 10", "required": True, "type": "input"},
        {"key": "threads", "label": "线程数", "placeholder": "如 16", "required": True, "type": "input"},
        {"key": "base_clock", "label": "基础频率", "placeholder": "如 2.5GHz", "required": True, "type": "input"},
    ],
    "内存": [
        {"key": "generation", "label": "代数", "placeholder": "如 DDR4", "required": True, "type": "select", "options": ["DDR3", "DDR4", "DDR5"]},
        {"key": "frequency", "label": "频率", "placeholder": "如 3200MHz", "required": True, "type": "input"},
        {"key": "capacity", "label": "容量", "placeholder": "如 16G", "required": True, "type": "input"},
        {"key": "type", "label": "类型", "placeholder": "台式机/笔记本", "required": True, "type": "select", "options": ["台式机", "笔记本"]},
    ],
    "主板": [
        {"key": "socket_type", "label": "CPU插槽", "placeholder": "如 LGA1700", "required": True, "type": "select", "options": ["LGA1700", "LGA1200", "LGA1151", "AM5", "AM4"]},
        {"key": "form_factor", "label": "板型", "placeholder": "如 ATX", "required": True, "type": "select", "options": ["ATX", "M-ATX", "ITX", "E-ATX"]},
        {"key": "chipset", "label": "芯片组", "placeholder": "如 B760", "required": True, "type": "input"},
    ],
    "硬盘": [
        {"key": "type", "label": "类型", "placeholder": "如 SSD", "required": True, "type": "select", "options": ["SSD", "HDD", "SSHD"]},
        {"key": "interface", "label": "接口", "placeholder": "如 M.2 NVMe", "required": True, "type": "select", "options": ["M.2 NVMe", "M.2 SATA", "SATA 2.5寸", "SATA 3.5寸"]},
        {"key": "capacity", "label": "容量", "placeholder": "如 1TB", "required": True, "type": "input"},
        {"key": "form_factor", "label": "规格", "placeholder": "如 2280", "required": False, "type": "input"},
    ],
    "电源": [
        {"key": "wattage", "label": "功率", "placeholder": "如 750W", "required": True, "type": "input"},
        {"key": "certification", "label": "认证", "placeholder": "如 80Plus Gold", "required": True, "type": "select", "options": ["80Plus", "80Plus Bronze", "80Plus Silver", "80Plus Gold", "80Plus Platinum", "80Plus Titanium"]},
        {"key": "modularity", "label": "模组", "placeholder": "如 全模组", "required": True, "type": "select", "options": ["全模组", "半模组", "非模组"]},
    ],
    "机箱": [
        {"key": "form_factor_support", "label": "支持板型", "placeholder": "如 ATX/MATX", "required": True, "type": "input"},
        {"key": "dimensions", "label": "尺寸(mm)", "placeholder": "如 400x200x450", "required": False, "type": "input"},
    ],
    "散热器": [
        {"key": "type", "label": "散热方式", "placeholder": "风冷/水冷", "required": True, "type": "select", "options": ["风冷", "水冷-120", "水冷-240", "水冷-360"]},
        {"key": "socket_support", "label": "兼容插槽", "placeholder": "如 LGA1700/AM5", "required": True, "type": "input"},
    ],
    "显示器": [
        {"key": "size", "label": "尺寸", "placeholder": "如 27寸", "required": True, "type": "input"},
        {"key": "resolution", "label": "分辨率", "placeholder": "如 2560x1440", "required": True, "type": "select", "options": ["1920x1080", "2560x1440", "3840x2160", "3440x1440"]},
        {"key": "refresh_rate", "label": "刷新率", "placeholder": "如 165Hz", "required": False, "type": "select", "options": ["60Hz", "75Hz", "144Hz", "165Hz", "240Hz"]},
        {"key": "panel_type", "label": "面板类型", "placeholder": "如 IPS", "required": False, "type": "select", "options": ["IPS", "VA", "TN", "OLED", "Mini LED"]},
    ],
    "键盘": [
        {"key": "switch_type", "label": "轴体", "placeholder": "如 红轴/茶轴", "required": False, "type": "select", "options": ["红轴", "茶轴", "青轴", "黑轴", "银轴", "薄膜", "其他"]},
        {"key": "connection", "label": "连接方式", "placeholder": "有线/无线", "required": False, "type": "select", "options": ["有线", "无线2.4G", "蓝牙", "三模"]},
        {"key": "layout", "label": "配列", "placeholder": "如 104键", "required": False, "type": "select", "options": ["104键", "87键", "68键", "61键", "小键盘"]},
    ],
    "鼠标": [
        {"key": "connection", "label": "连接方式", "placeholder": "有线/无线", "required": False, "type": "select", "options": ["有线", "无线2.4G", "蓝牙", "三模"]},
        {"key": "dpi", "label": "DPI", "placeholder": "如 25600", "required": False, "type": "input"},
    ],
    "耳机": [
        {"key": "type", "label": "类型", "placeholder": "头戴/入耳", "required": False, "type": "select", "options": ["头戴式", "入耳式", "耳挂式"]},
        {"key": "connection", "label": "连接方式", "placeholder": "有线/无线", "required": False, "type": "select", "options": ["有线3.5mm", "有线USB", "无线2.4G", "蓝牙", "三模"]},
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
    """
    if properties is None:
        properties = {}

    schema = CATEGORY_PROPERTY_SCHEMA.get(category)
    if not schema:
        return True, ""

    required_fields = [f["key"] for f in schema if f.get("required")]
    missing = [f for f in required_fields if f not in properties or not properties[f]]

    if missing:
        labels = {f["key"]: f["label"] for f in schema}
        missing_labels = [labels.get(k, k) for k in missing]
        return False, f"分类【{category}】缺少必要属性: {', '.join(missing_labels)}"

    return True, ""
