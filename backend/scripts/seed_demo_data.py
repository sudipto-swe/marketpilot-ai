import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.entities import (
    User, Workspace, WorkspaceMember, Product, Review, Competitor, CompetitorProduct,
    CompetitorPriceHistory, UserRole
)
from app.analytics.nlp_engine import calculate_review_sentiment, extract_topics

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if admin user already exists
    admin_email = "admin@marketpilot.ai"
    existing_user = db.query(User).filter(User.email == admin_email).first()
    if existing_user:
        print("Demo seed data already present. Skipping.")
        db.close()
        return

    print("Creating Demo Admin, Workspace, and Sample Records...")
    
    # 1. Admin User
    admin = User(
        email=admin_email,
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Alex Mercer (Operations Lead)",
        role=UserRole.ADMIN.value
    )
    db.add(admin)
    db.flush()
    
    # 2. Workspace
    workspace = Workspace(
        name="MarketPilot Electronics Flagship",
        slug="marketpilot-flagship"
    )
    db.add(workspace)
    db.flush()
    
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=admin.id,
        role="admin"
    )
    db.add(member)
    db.flush()
    
    # 3. Products
    products_data = [
        {
            "sku": "HP001",
            "name": "MarketPilot Studio Over-Ear Wireless Headphones",
            "category": "Audio",
            "description": "High-fidelity wireless studio headphones featuring precision dynamic drivers and ergonomic memory foam cushions.",
            "price": 59.99,
            "currency": "USD",
            "brand": "MarketPilot",
            "attributes": {"battery_hours": 30, "driver_size": "40mm", "bluetooth": "5.3", "weight_grams": 240}
        },
        {
            "sku": "SPK002",
            "name": "MarketPilot SoundPulse Waterproof Bluetooth Speaker",
            "category": "Audio",
            "description": "Ultra-portable rugged wireless speaker designed for outdoor adventures with deep bass radiators.",
            "price": 39.99,
            "currency": "USD",
            "brand": "MarketPilot",
            "attributes": {"waterproof_rating": "IPX7", "battery_hours": 16, "output_watts": 20}
        },
        {
            "sku": "WCH003",
            "name": "MarketPilot PulseFit Fitness Smartwatch",
            "category": "Wearables",
            "description": "Comprehensive health tracking smartwatch featuring continuous heart rate, sleep stages, and workout tracking.",
            "price": 79.99,
            "currency": "USD",
            "brand": "MarketPilot",
            "attributes": {"screen_type": "AMOLED 1.4 inch", "battery_days": 7, "water_resistance": "5ATM"}
        }
    ]
    
    created_prods = {}
    for pdata in products_data:
        p = Product(
            workspace_id=workspace.id,
            sku=pdata["sku"],
            name=pdata["name"],
            category=pdata["category"],
            description=pdata["description"],
            price=pdata["price"],
            currency=pdata["currency"],
            brand=pdata["brand"],
            attributes=pdata["attributes"]
        )
        db.add(p)
        db.flush()
        created_prods[pdata["sku"]] = p
        
    # 4. Realistic Reviews (specifically testing battery complaints on HP001)
    reviews_data = [
        ("HP001", 5.0, "Outstanding audio clarity and punchy bass! Extremely comfortable memory foam."),
        ("HP001", 5.0, "Great headphones for the price. Fast pairing with my laptop and phone."),
        ("HP001", 4.0, "Sound quality is superb, build is sturdy. A bit warm around the ears in summer."),
        ("HP001", 2.0, "Battery life is disappointing. Barely lasts 15 hours on high volume, far below advertised 30."),
        ("HP001", 1.0, "Disappointed with battery drain. The battery died after 4 months of light use."),
        ("HP001", 2.0, "Battery drains quickly when left on standby overnight. Needs a better auto-off feature."),
        ("HP001", 4.0, "Solid sound and microphone quality for remote Zoom calls."),
        ("SPK002", 5.0, "Incredible sound for such a small speaker! Survived a drop in the pool without issue."),
        ("SPK002", 4.0, "Super loud and clear outdoors. Great battery life during weekend camping trips."),
        ("SPK002", 2.0, "The bluetooth connection disconnects if I walk into the next room."),
        ("WCH003", 5.0, "AMOLED screen is crystal clear and battery lasts a full week easily."),
        ("WCH003", 4.0, "Accurate step counting and heart rate readings. Companion app is clean.")
    ]
    
    for sku, rating, text in reviews_data:
        prod = created_prods[sku]
        sentiment, score = calculate_review_sentiment(text, rating)
        topics = extract_topics(text)
        r = Review(
            workspace_id=workspace.id,
            product_id=prod.id,
            product_sku=sku,
            rating=rating,
            review_text=text,
            sentiment=sentiment,
            sentiment_score=score,
            topics=topics,
            source="demo"
        )
        db.add(r)
        
    # 5. Competitors & Tracked Products
    comp_a = Competitor(workspace_id=workspace.id, name="SoundWave Pro", website="https://soundwavepro-example.com")
    comp_b = Competitor(workspace_id=workspace.id, name="AeroAudio Labs", website="https://aeroaudio-example.com")
    db.add_all([comp_a, comp_b])
    db.flush()
    
    # Competitor Pricing: SoundWave undercut HP001 by 12.5% ($52.49 vs our $59.99)
    cp1 = CompetitorProduct(
        competitor_id=comp_a.id,
        product_id=created_prods["HP001"].id,
        competitor_product_name="SoundWave Elite Over-Ear",
        current_price=52.49
    )
    cp2 = CompetitorProduct(
        competitor_id=comp_b.id,
        product_id=created_prods["HP001"].id,
        competitor_product_name="AeroAudio Horizon ANC",
        current_price=64.99
    )
    cp3 = CompetitorProduct(
        competitor_id=comp_a.id,
        product_id=created_prods["SPK002"].id,
        competitor_product_name="SoundWave AquaBoom Mini",
        current_price=34.99
    )
    db.add_all([cp1, cp2, cp3])
    db.flush()
    
    # Price History
    h1 = CompetitorPriceHistory(competitor_product_id=cp1.id, price=58.00, source="demo")
    h2 = CompetitorPriceHistory(competitor_product_id=cp1.id, price=52.49, source="demo")
    db.add_all([h1, h2])
    
    db.commit()
    db.close()
    print("Database successfully seeded with realistic demonstration e-commerce records.")

if __name__ == "__main__":
    seed_database()
