import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import bcrypt
from datetime import datetime, timedelta
import random

from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.models.user import User
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.audit import AuditLog, SecurityIncident
from app.models.exposure import SessionExposure
from app.crypto.aes_cipher import vault_cipher

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def seed_database():
    """Seeds the database with default users and 20 realistic encrypted customer profiles."""
    print("Initializing SQLite tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already contains data. Skipping re-seed.")
            return

        print("Seeding default employee users...")
        users_data = [
            {
                "username": "support_alice",
                "email": "alice@vault.bank",
                "full_name": "Alice Jenkins",
                "role": "SUPPORT",
                "department": "Customer Operations",
                "password": "Password123!"
            },
            {
                "username": "loan_bob",
                "email": "bob@vault.bank",
                "full_name": "Bob Martinez",
                "role": "LOAN_OFFICER",
                "department": "Retail Lending",
                "password": "Password123!"
            },
            {
                "username": "auditor_clara",
                "email": "clara@vault.bank",
                "full_name": "Clara Oswald",
                "role": "COMPLIANCE_AUDITOR",
                "department": "Risk & Compliance",
                "password": "Password123!"
            },
            {
                "username": "admin_david",
                "email": "david@vault.bank",
                "full_name": "David Miller",
                "role": "ADMIN",
                "department": "Information Security",
                "password": "Password123!"
            }
        ]
        
        for u in users_data:
            user = User(
                username=u["username"],
                email=u["email"],
                full_name=u["full_name"],
                role=u["role"],
                department=u["department"],
                hashed_password=hash_password(u["password"])
            )
            db.add(user)

        print("Encrypting and seeding 20 synthetic customer records with AES-256-GCM...")
        
        synthetic_customers = [
            ("Rahul Sharma", "rahul.sharma@example.com", "+91 98201 12345", "501002348912", "ABCPS1234E", "284500.50", 780, "LOW"),
            ("Priya Patel", "priya.patel@example.com", "+91 98202 23456", "501003459023", "BKLPP5678K", "1450000.00", 810, "LOW"),
            ("Amit Verma", "amit.verma@example.com", "+91 98203 34567", "501004560134", "CFRPV9012M", "12500.00", 640, "HIGH"),
            ("Sneha Iyer", "sneha.iyer@example.com", "+91 98204 45678", "501005671245", "DGQPI3456N", "67000.25", 720, "MEDIUM"),
            ("Vikram Singh", "vikram.singh@example.com", "+91 98205 56789", "501006782356", "EHRPS7890P", "520000.00", 790, "LOW"),
            ("Ananya Rao", "ananya.rao@example.com", "+91 98206 67890", "501007893467", "FJSPR1234Q", "95000.00", 750, "LOW"),
            ("Rohan Das", "rohan.das@example.com", "+91 98207 78901", "501008904578", "GKTPD5678R", "4200.00", 590, "HIGH"),
            ("Kavita Nair", "kavita.nair@example.com", "+91 98208 89012", "501009015689", "HLUPN9012S", "310000.00", 770, "LOW"),
            ("Siddharth Roy", "siddharth.roy@example.com", "+91 98209 90123", "501010126790", "IMVPN3456T", "88000.50", 735, "MEDIUM"),
            ("Meera Joshi", "meera.joshi@example.com", "+91 98210 01234", "501011237801", "JNWPM7890U", "1250000.75", 825, "LOW"),
            ("Arjun Mehta", "arjun.mehta@example.com", "+91 98211 12345", "501012348912", "KOXPA1234V", "18000.00", 660, "MEDIUM"),
            ("Deepa Sundaram", "deepa.s@example.com", "+91 98212 23456", "501013459023", "LPYPD5678W", "490000.00", 800, "LOW"),
            ("Karan Kapoor", "karan.k@example.com", "+91 98213 34567", "501014560134", "MQZPK9012X", "7500.00", 610, "HIGH"),
            ("Divya Menon", "divya.menon@example.com", "+91 98214 45678", "501015671245", "NRAPM3456Y", "640000.00", 795, "LOW"),
            ("Naveen Reddy", "naveen.reddy@example.com", "+91 98215 56789", "501016782356", "OSBPN7890Z", "112000.00", 740, "LOW"),
            ("Pooja Choudhury", "pooja.c@example.com", "+91 98216 67890", "501017893467", "PTCPA1234A", "38000.00", 710, "MEDIUM"),
            ("Harish Kulkarni", "harish.k@example.com", "+91 98217 78901", "501018904578", "QUDPK5678B", "840000.00", 815, "LOW"),
            ("Tanvi Bhatt", "tanvi.b@example.com", "+91 98218 89012", "501019015689", "RVEPB9012C", "23000.00", 675, "MEDIUM"),
            ("Gaurav Ghosh", "gaurav.g@example.com", "+91 98219 90123", "501020126790", "SWFPG3456D", "980000.00", 830, "LOW"),
            ("Ritu Sen", "ritu.sen@example.com", "+91 98220 01234", "501021237801", "TXGPR7890E", "150000.00", 760, "LOW"),
        ]

        merchants = ["Amazon India", "Flipkart", "Swiggy", "Starbucks", "Croma Electronics", "IndiGo Airlines", "Uber", "Tata Power"]
        categories = ["SHOPPING", "FOOD", "ELECTRONICS", "TRAVEL", "UTILITY"]

        for idx, item in enumerate(synthetic_customers, start=1001):
            name, email, phone, raw_acc, raw_pan, raw_bal, credit_score, risk_tier = item
            code = f"CUST-{idx}"

            # AES-256-GCM Authenticated Encryption with Customer Code as Associated Data
            acc_enc, acc_nonce = vault_cipher.encrypt(raw_acc, associated_data=code)
            pan_enc, pan_nonce = vault_cipher.encrypt(raw_pan, associated_data=code)
            bal_enc, bal_nonce = vault_cipher.encrypt(raw_bal, associated_data=code)

            cust = Customer(
                customer_code=code,
                full_name=name,
                email=email,
                phone=phone,
                credit_score=credit_score,
                risk_tier=risk_tier,
                kyc_status="VERIFIED",
                account_number_enc=acc_enc,
                account_number_nonce=acc_nonce,
                pan_enc=pan_enc,
                pan_nonce=pan_nonce,
                balance_enc=bal_enc,
                balance_nonce=bal_nonce
            )
            db.add(cust)
            db.flush()  # populate cust.id

            # Add 2-3 synthetic transactions with encrypted amounts
            for t_idx in range(1, 4):
                raw_amt = str(round(random.uniform(250.0, 15000.0), 2))
                amt_enc, amt_nonce = vault_cipher.encrypt(raw_amt, associated_data=f"{code}-TX-{t_idx}")
                tx = Transaction(
                    customer_id=cust.id,
                    tx_code=f"TXN-{idx}-{t_idx}",
                    merchant=random.choice(merchants),
                    category=random.choice(categories),
                    amount_enc=amt_enc,
                    amount_nonce=amt_nonce,
                    status=random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILED", "DISPUTED"]),
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.add(tx)

        db.commit()
        print("Database successfully seeded with 4 users and 20 encrypted customer accounts!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
