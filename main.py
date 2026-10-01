from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import random

import models
from database import engine, get_db

# Δημιουργία των πινακών στη βάση
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Home Simulation API")

@app.get("/")
def home():
    return {"message": "Smart Home API is running!"}

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
