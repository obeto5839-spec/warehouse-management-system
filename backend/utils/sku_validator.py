
from typing import Dict, Any, Tuple

def validate_sku_properties(category: str, properties: Dict[str, Any]) -> Tuple[bool, str]:
    """
    验证 SKU 的 properties 字段是否符合规范
    
    Args:
        category: 配件分类 (显卡, CPU, 内存, 主板, 硬盘)
        properties: 前端传入的 JSON 属性
        
    Returns:
        (is_valid, error_message)
    """
    if properties is None:
        properties = {}

    # 定义不同分类的必填字段和规范
    # 这里可以扩展更多校验逻辑，比如数据类型检查、枚举值检查等
    required_fields_map = {
        "显卡": ["chipset_manufacturer", "memory_size", "interface"],  # 例如: NVIDIA, 12G, PCI-E 4.0
        "CPU": ["socket_type", "cores", "threads", "base_clock"],     # 例如: LGA1700, 10, 16, 2.5GHz
        "内存": ["generation", "frequency", "capacity", "type"],       # 例如: DDR4, 3200MHz, 16G, Desktop
        "主板": ["socket_type", "form_factor", "chipset"],             # 例如: LGA1700, ATX, B760
        "硬盘": ["type", "interface", "capacity", "form_factor"],      # 例如: SSD, M.2 NVMe, 1TB, 2280
        "电源": ["wattage", "certification", "modularity"],            # 例如: 750W, 80Plus Gold, Full Modular
        "机箱": ["form_factor_support", "dimensions"],                 # 例如: ATX/MATX, 400x200x450mm
        "散热器": ["type", "socket_support"],                          # 例如: Air/Liquid, LGA1700/AM5
    }
    
    # 如果分类不在我们的规范列表中，暂时允许通过（或者可以配置为严格模式拒绝）
    # 这里我们选择宽容模式，只对已知分类做强校验
    if category not in required_fields_map:
        return True, ""
        
    required_fields = required_fields_map[category]
    missing_fields = [field for field in required_fields if field not in properties]
    
    if missing_fields:
        return False, f"分类【{category}】缺少必要属性: {', '.join(missing_fields)}"
        
    # TODO: 可以在这里添加更细致的校验，比如 memory_size 必须是以 G/GB 结尾的字符串
    
    return True, ""
