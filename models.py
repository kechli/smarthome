from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from datetime import datetime
from database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)          # π.χ. "Φως Σαλονιού"
    device_type = Column(String)               # π.χ. "switch", "light"
    pin_gpio = Column(Integer, nullable=True)  # Ακίδα Raspberry Pi (π.χ. 17)
    is_active = Column(Boolean, default=False) # True = Ανοιχτό, False = Κλειστό
    location = Column(String, default="Home")  # π.χ. "Σαλόνι"


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, index=True)   # π.χ. "DHT22_LivingRoom"
    sensor_type = Column(String)               # π.χ. "temperature", "humidity"
    value = Column(Float, nullable=False)      # π.χ. 23.5
    unit = Column(String, default="°C")        # π.χ. "°C"
    timestamp = Column(DateTime, default=datetime.utcnow) # Ώρα καταγραφής

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # 👈 ΕΔΩ προσθέτεις τη νέα γραμμή:
    is_admin = Column(Boolean, default=False)