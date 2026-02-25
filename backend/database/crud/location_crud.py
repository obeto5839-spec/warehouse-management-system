from sqlalchemy.orm import Session
from database.models.location_model import Location
from database.schemas.location_schema import LocationCreate, LocationUpdate

def create_location(db: Session, location: LocationCreate):
    db_location = Location(
        location_code=location.location_code,
        location_name=location.location_name,
        parent_id=location.parent_id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_location(db: Session, location_id: int):
    return db.query(Location).filter(Location.id == location_id).first()

def get_location_by_code(db: Session, location_code: str):
    return db.query(Location).filter(Location.location_code == location_code).first()

def get_locations(db: Session, skip: int = 0, limit: int = 100, parent_id: int = None):
    query = db.query(Location)
    if parent_id is not None:
        query = query.filter(Location.parent_id == parent_id)
    return query.offset(skip).limit(limit).all()

def update_location(db: Session, location_id: int, location_update: LocationUpdate):
    db_location = get_location(db, location_id)
    if not db_location:
        return None
    
    update_data = location_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_location, key, value)
        
    db.commit()
    db.refresh(db_location)
    return db_location

def delete_location(db: Session, location_id: int):
    db_location = get_location(db, location_id)
    if db_location:
        db.delete(db_location)
        db.commit()
    return db_location
