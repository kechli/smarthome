from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import random
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import models
from database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import bcrypt
SECRET_KEY = "supersecretkey"  # Άλλαξέ το αν έχεις ορίσει άλλο key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Δημιουργία των πινακών στη βάση
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Home Simulation API")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

from fastapi.responses import RedirectResponse

@app.get("/")
def home():
    return RedirectResponse(url="/static/login.html")

# --- ENDPOINTS ΣΥΣΚΕΥΩΝ (DEVICES) ---

@app.post("/devices/")
def create_device(name: str, device_type: str, pin_gpio: int = None, location: str = "Home", db: Session = Depends(get_db)):
    """Δημιουργία νέας έξυπνης συσκευής"""
    new_device = models.Device(
        name=name,
        device_type=device_type,
        pin_gpio=pin_gpio,
        location=location
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@app.get("/devices/")
def list_devices(db: Session = Depends(get_db)):
    """Επιστρέφει όλες τις συσκευές"""
    return db.query(models.Device).all()

@app.post("/devices/{device_id}/toggle")
def toggle_device(device_id: int, db: Session = Depends(get_db)):
    """Αλλαγή κατάστασης συσκευής (ON <-> OFF)"""
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Η συσκευή δεν βρέθηκε")
    
    device.is_active = not device.is_active
    db.commit()
    db.refresh(device)
    
    status_str = "ON" if device.is_active else "OFF"
    return {"message": f"Η συσκευή '{device.name}' είναι τώρα {status_str}", "is_active": device.is_active}

# --- ENDPOINTS ΑΙΣΘΗΤΗΡΩΝ (SIMULATED SENSORS) ---

@app.post("/sensors/simulate-read")
def simulate_sensor_read(sensor_name: str = "DHT22_LivingRoom", sensor_type: str = "temperature", db: Session = Depends(get_db)):
    """Προσομοίωση λήψης μέτρησης από αισθητήρα"""
    if sensor_type == "temperature":
        val = round(random.uniform(18.0, 28.0), 1)
        unit = "°C"
    elif sensor_type == "humidity":
        val = round(random.uniform(40.0, 70.0), 1)
        unit = "%"
    else:
        val = round(random.uniform(0.0, 100.0), 1)
        unit = "units"

    new_reading = models.SensorReading(
        sensor_name=sensor_name,
        sensor_type=sensor_type,
        value=val,
        unit=unit
    )
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)
    return new_reading

@app.get("/sensors/history")
def get_sensor_history(db: Session = Depends(get_db)):
    """Επιστρέφει το ιστορικό μετρήσεων"""
    return db.query(models.SensorReading).order_by(models.SensorReading.timestamp.desc()).all()

app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/users/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin
    }

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # Έλεγχος αν υπάρχει ο χρήστης και ταυτοποίηση του κωδικού
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}