from database import SessionLocal
import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_initial_admin():
    db = SessionLocal()
    
    # Στοιχεία του Admin
    admin_username = "admin"
    admin_password = "admin123"  # Αλλάξτε το με έναν ισχυρό κωδικό
    
    # Έλεγχος αν υπάρχει ήδη
    existing_user = db.query(models.User).filter(models.User.username == admin_username).first()
    if existing_user:
        print(f"⚠️ Ο χρήστης '{admin_username}' υπάρχει ήδη!")
        db.close()
        return

    # Δημιουργία Admin
    hashed_pwd = pwd_context.hash(admin_password)
    admin_user = models.User(
        username=admin_username,
        hashed_password=hashed_pwd,
        is_admin=True  # 👈 Ορίζεται ως Admin
    )
    
    db.add(admin_user)
    db.commit()
    print(f"✅ Ο Admin χρήστης '{admin_username}' δημιουργήθηκε με επιτυχία!")
    db.close()

if __name__ == "__main__":
    create_initial_admin()