from sqlalchemy.orm import Session
from database.models.sku_model import SKU
from database.schemas.sku_schema import SKUCreate, SKUUpdate

def get_sku(db: Session, sku_id: int):
    return db.query(SKU).filter(SKU.id == sku_id).first()

def get_skus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SKU).offset(skip).limit(limit).all()

def update_sku(db: Session, sku_id: int, sku_update: SKUUpdate):
    db_sku = get_sku(db, sku_id)
    if not db_sku:
        return None
    
    update_data = sku_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sku, key, value)
        
    db.commit()
    db.refresh(db_sku)
    return db_sku

def delete_sku(db: Session, sku_id: int):
    db_sku = get_sku(db, sku_id)
    if db_sku:
        db.delete(db_sku)
        db.commit()
    return db_sku


_UNSET = object()

def get_sku_by_exact_match(db: Session, category: str, brand: str, model_name: str, series=_UNSET):
    """精确查找是否存在相同的 SKU。series 不传则忽略，传 None 匹配空值，传字符串精确匹配"""
    query = db.query(SKU).filter(
        SKU.category == category,
        SKU.brand == brand,
        SKU.model_name == model_name
    )
    if series is not _UNSET:
        if series is None:
            query = query.filter(SKU.series.is_(None))
        else:
            query = query.filter(SKU.series == series)
    return query.first()

def create_sku(db: Session, sku_in: SKUCreate):
    """在数据库中真正创建一条 SKU 记录"""
    db_sku = SKU(
        category=sku_in.category,
        brand=sku_in.brand,
        series=sku_in.series,
        model_name=sku_in.model_name,
        properties=sku_in.properties
    )
    db.add(db_sku)
    db.commit()
    db.refresh(db_sku)
    return db_sku

def search_skus(db: Session, category: str, brand: str = None, keyword: str = "", limit: int = 10):
    """模糊搜索数据库：在品牌、系列、型号中匹配关键词"""
    db_query = db.query(SKU).filter(SKU.category == category)
    
    if brand:
        db_query = db_query.filter(SKU.brand == brand)
    if keyword:
        like = f"%{keyword}%"
        db_query = db_query.filter(
            (SKU.model_name.ilike(like)) |
            (SKU.series.ilike(like)) |
            (SKU.brand.ilike(like))
        )
        
    return db_query.limit(limit).all()


def get_distinct_categories(db: Session):
    """获取所有不重复的分类"""
    results = db.query(SKU.category).distinct().all()
    return [r[0] for r in results]


def get_brands_by_category(db: Session, category: str):
    """获取某分类下所有不重复的品牌"""
    results = db.query(SKU.brand).filter(SKU.category == category).distinct().all()
    return [r[0] for r in results]


def get_models_by_category_brand(db: Session, category: str, brand: str):
    """获取某分类+品牌下的所有型号（含 series 和 properties）"""
    return db.query(SKU).filter(
        SKU.category == category,
        SKU.brand == brand
    ).all()


def fuzzy_search_skus(db: Session, keyword: str, limit: int = 10):
    """全局模糊搜索：在分类、品牌、系列、型号中匹配关键词"""
    like = f"%{keyword}%"
    return db.query(SKU).filter(
        (SKU.category.ilike(like)) |
        (SKU.brand.ilike(like)) |
        (SKU.series.ilike(like)) |
        (SKU.model_name.ilike(like))
    ).limit(limit).all()
