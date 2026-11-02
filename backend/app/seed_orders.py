import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import Base, SessionLocal, engine
from app.models.database_models import Order

Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing_ids = [12345, 54321]
db.query(Order).filter(Order.id.in_(existing_ids)).delete(synchronize_session=False)

orders = [
    Order(
        id=12345,
        user_id=1,
        status="shipped",
        carrier="Fan Courier",
        estimated_delivery="2 business days",
        can_cancel=False
    ),
    Order(
        id=54321,
        user_id=2,
        status="processing",
        carrier="Sameday",
        estimated_delivery="3 business days",
        can_cancel=True
    )
]

db.add_all(orders)
db.commit()
db.close()

print("Orders created.")