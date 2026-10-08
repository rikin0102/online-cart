import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_PRODUCTS = [
    {
        "name": "Wireless Mouse",
        "price": Decimal("499.00"),
        "category": "Accessories",
        "description": "Ergonomic 2.4GHz wireless optical mouse with quiet click and high-precision tracking."
    },
    {
        "name": "USB Keyboard",
        "price": Decimal("799.00"),
        "category": "Accessories",
        "description": "Full-size spill-resistant USB wired keyboard with comfortable low-profile keys."
    },
    {
        "name": "Laptop Stand",
        "price": Decimal("1200.00"),
        "category": "Office",
        "description": "Adjustable aluminum ergonomic laptop riser with heat-dissipation ventilation slots."
    },
    {
        "name": "HD Webcam",
        "price": Decimal("1899.00"),
        "category": "Peripherals",
        "description": "1080p Full HD video webcam with integrated noise-cancelling dual microphones."
    },
    {
        "name": "Wireless Headphones",
        "price": Decimal("2499.00"),
        "category": "Audio",
        "description": "Over-ear Bluetooth 5.2 headphones with active noise cancellation and 30-hour battery life."
    },
    {
        "name": "Power Bank",
        "price": Decimal("1299.00"),
        "category": "Power",
        "description": "10000mAh slim fast-charging portable power bank with dual USB-A and USB-C output."
    },
    {
        "name": "Phone Stand",
        "price": Decimal("299.00"),
        "category": "Accessories",
        "description": "Compact foldable desktop phone and tablet stand with anti-slip silicone padding."
    },
    {
        "name": "HDMI Cable",
        "price": Decimal("399.00"),
        "category": "Cables",
        "description": "High-speed 4K 60Hz braided 2-meter HDMI 2.0 cable with gold-plated connectors."
    },
    {
        "name": "Mouse Pad",
        "price": Decimal("199.00"),
        "category": "Accessories",
        "description": "Extended gaming mouse pad with stitched edges and non-slip textured rubber base."
    },
    {
        "name": "Desk Lamp",
        "price": Decimal("899.00"),
        "category": "Lighting",
        "description": "Dimmable LED desk lamp with 3 color temperatures, touch control, and flexible gooseneck."
    },
]


def seed_products(db: Session = None) -> None:
    """Seed the database with 10 default products idempotently."""
    close_session = False
    if db is None:
        init_db()
        db = SessionLocal()
        close_session = True

    try:
        created_count = 0
        for item in INITIAL_PRODUCTS:
            existing = db.query(Product).filter(Product.name == item["name"]).first()
            if not existing:
                product = Product(
                    name=item["name"],
                    price=item["price"],
                    category=item["category"],
                    description=item["description"],
                )
                db.add(product)
                created_count += 1

        db.commit()
        if created_count > 0:
            logger.info(f"Successfully seeded {created_count} new products into the database.")
        else:
            logger.info("All seed products already exist in the database. No duplicates created.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    logger.info("Running standalone database product seeding...")
    seed_products()
    logger.info("Seeding complete.")
