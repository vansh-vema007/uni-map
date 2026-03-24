from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET_KEY')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 168))
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ============= MODELS =============

class UserCreate(BaseModel):
    roll_number: str
    email: EmailStr
    password: str
    name: str
    year: int
    department: str

class UserLogin(BaseModel):
    roll_number: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    roll_number: str
    email: str
    name: str
    year: int
    department: str
    created_at: str

class TimetableEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    day: str
    start_time: str
    end_time: str
    subject: str
    room: str
    building: str
    faculty: str
    lat: float
    lng: float

class TimetableCreate(BaseModel):
    day: str
    start_time: str
    end_time: str
    subject: str
    room: str
    building: str
    faculty: str
    lat: float
    lng: float

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class Location(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    building_name: str
    lat: float
    lng: float
    type: str
    floor_count: int
    description: str

class AttendanceRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    subject: str
    date: str
    status: str
    percentage: float

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    type: str
    title: str
    message: str
    read: bool
    created_at: str

class RouteRequest(BaseModel):
    from_building: str
    to_building: str
    mode: str = "walking"

class RouteResponse(BaseModel):
    from_location: dict
    to_location: dict
    distance: float
    estimated_time: int
    path: List[dict]

# ============= UTILITY FUNCTIONS =============

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ============= AUTHENTICATION ROUTES =============

@api_router.post("/auth/signup")
async def signup(user_data: UserCreate):
    existing_user = await db.users.find_one(
        {"$or": [{"roll_number": user_data.roll_number}, {"email": user_data.email}]},
        {"_id": 0}
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this roll number or email already exists")
    
    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(user_data.password)
    
    user_doc = {
        "id": user_id,
        "roll_number": user_data.roll_number,
        "email": user_data.email,
        "password_hash": hashed_pwd,
        "name": user_data.name,
        "year": user_data.year,
        "department": user_data.department,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_access_token({"user_id": user_id})
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "roll_number": user_data.roll_number,
            "email": user_data.email,
            "name": user_data.name,
            "year": user_data.year,
            "department": user_data.department
        }
    }

@api_router.post("/auth/login")
async def login(login_data: UserLogin):
    user = await db.users.find_one({"roll_number": login_data.roll_number}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user["id"]})
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "roll_number": user["roll_number"],
            "email": user["email"],
            "name": user["name"],
            "year": user["year"],
            "department": user["department"]
        }
    }

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    return User(
        id=current_user["id"],
        roll_number=current_user["roll_number"],
        email=current_user["email"],
        name=current_user["name"],
        year=current_user["year"],
        department=current_user["department"],
        created_at=current_user["created_at"]
    )

# ============= TIMETABLE ROUTES =============

@api_router.get("/timetable", response_model=List[TimetableEntry])
async def get_timetable(current_user: dict = Depends(get_current_user)):
    entries = await db.timetable.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
    return entries

@api_router.post("/timetable")
async def add_timetable_entry(entry: TimetableCreate, current_user: dict = Depends(get_current_user)):
    entry_id = str(uuid.uuid4())
    entry_doc = {
        "id": entry_id,
        "user_id": current_user["id"],
        **entry.model_dump()
    }
    await db.timetable.insert_one(entry_doc)
    return {"message": "Timetable entry added", "id": entry_id}

@api_router.get("/timetable/today", response_model=List[TimetableEntry])
async def get_today_schedule(current_user: dict = Depends(get_current_user)):
    today = datetime.now().strftime("%A")
    entries = await db.timetable.find(
        {"user_id": current_user["id"], "day": today},
        {"_id": 0}
    ).to_list(100)
    return entries

@api_router.get("/timetable/next")
async def get_next_class(current_user: dict = Depends(get_current_user)):
    today = datetime.now().strftime("%A")
    current_time = datetime.now().strftime("%H:%M")
    
    entries = await db.timetable.find(
        {"user_id": current_user["id"], "day": today},
        {"_id": 0}
    ).to_list(100)
    
    upcoming = [e for e in entries if e["start_time"] > current_time]
    if upcoming:
        next_class = min(upcoming, key=lambda x: x["start_time"])
        return next_class
    return None

# ============= ATTENDANCE ROUTES =============

@api_router.get("/attendance", response_model=List[AttendanceRecord])
async def get_attendance(current_user: dict = Depends(get_current_user)):
    records = await db.attendance.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
    return records

@api_router.get("/attendance/summary")
async def get_attendance_summary(current_user: dict = Depends(get_current_user)):
    records = await db.attendance.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    
    if not records:
        return {"overall_percentage": 0, "subjects": []}
    
    subject_stats = {}
    for record in records:
        subject = record["subject"]
        if subject not in subject_stats:
            subject_stats[subject] = {"present": 0, "total": 0}
        subject_stats[subject]["total"] += 1
        if record["status"] == "present":
            subject_stats[subject]["present"] += 1
    
    subjects = []
    for subject, stats in subject_stats.items():
        percentage = (stats["present"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        subjects.append({
            "subject": subject,
            "percentage": round(percentage, 2),
            "present": stats["present"],
            "total": stats["total"]
        })
    
    overall = sum(s["percentage"] for s in subjects) / len(subjects) if subjects else 0
    
    return {
        "overall_percentage": round(overall, 2),
        "subjects": subjects
    }

# ============= LOCATIONS ROUTES =============

@api_router.get("/locations", response_model=List[Location])
async def get_locations():
    locations = await db.locations.find({}, {"_id": 0}).to_list(100)
    return locations

@api_router.get("/locations/{building_name}")
async def get_location_by_name(building_name: str):
    location = await db.locations.find_one({"building_name": building_name}, {"_id": 0})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

# ============= NAVIGATION ROUTES =============

@api_router.post("/navigate", response_model=RouteResponse)
async def calculate_route(route_req: RouteRequest):
    from_loc = await db.locations.find_one({"building_name": route_req.from_building}, {"_id": 0})
    to_loc = await db.locations.find_one({"building_name": route_req.to_building}, {"_id": 0})
    
    if not from_loc or not to_loc:
        raise HTTPException(status_code=404, detail="One or both locations not found")
    
    from math import radians, sin, cos, sqrt, atan2
    
    lat1, lon1 = radians(from_loc["lat"]), radians(from_loc["lng"])
    lat2, lon2 = radians(to_loc["lat"]), radians(to_loc["lng"])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371 * c * 1000
    
    speed = 1.4 if route_req.mode == "walking" else 4.0
    estimated_time = int(distance / speed)
    
    path = [
        {"lat": from_loc["lat"], "lng": from_loc["lng"]},
        {"lat": to_loc["lat"], "lng": to_loc["lng"]}
    ]
    
    return RouteResponse(
        from_location={"name": from_loc["building_name"], "lat": from_loc["lat"], "lng": from_loc["lng"]},
        to_location={"name": to_loc["building_name"], "lat": to_loc["lat"], "lng": to_loc["lng"]},
        distance=round(distance, 2),
        estimated_time=estimated_time,
        path=path
    )

# ============= AI ASSISTANT ROUTES =============

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_msg: ChatMessage, current_user: dict = Depends(get_current_user)):
    session_id = chat_msg.session_id or str(uuid.uuid4())
    
    system_message = f"""You are CampusAI, an intelligent assistant for Chandigarh University students. You help with:
    - Campus navigation and directions
    - Class schedules and timetables
    - Faculty information
    - Exam schedules and academic queries
    - Study tips and recommendations
    
    Current student: {current_user['name']} (Roll: {current_user['roll_number']})
    Department: {current_user['department']}, Year: {current_user['year']}
    
    Be helpful, concise, and friendly. If asked about navigation, provide clear directions.
    """
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=chat_msg.message)
        response = await chat.send_message(user_message)
        
        chat_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "session_id": session_id,
            "user_message": chat_msg.message,
            "ai_response": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.chat_history.insert_one(chat_doc)
        
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")

@api_router.get("/chat/history")
async def get_chat_history(current_user: dict = Depends(get_current_user), limit: int = 50):
    history = await db.chat_history.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return history

# ============= NOTIFICATIONS ROUTES =============

@api_router.get("/notifications", response_model=List[Notification])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    return notifications

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

# ============= SEED DATA ROUTE =============

@api_router.post("/seed")
async def seed_data(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    campus_locations = [
        {"id": str(uuid.uuid4()), "building_name": "Block A", "lat": 30.7683, "lng": 76.5756, "type": "academic", "floor_count": 4, "description": "Main Academic Block"},
        {"id": str(uuid.uuid4()), "building_name": "Block B", "lat": 30.7690, "lng": 76.5760, "type": "academic", "floor_count": 3, "description": "Engineering Block"},
        {"id": str(uuid.uuid4()), "building_name": "Block C", "lat": 30.7675, "lng": 76.5750, "type": "academic", "floor_count": 5, "description": "Science & Technology Block"},
        {"id": str(uuid.uuid4()), "building_name": "Library", "lat": 30.7688, "lng": 76.5745, "type": "facility", "floor_count": 6, "description": "Central Library"},
        {"id": str(uuid.uuid4()), "building_name": "Hostel 1", "lat": 30.7670, "lng": 76.5765, "type": "hostel", "floor_count": 8, "description": "Boys Hostel"},
        {"id": str(uuid.uuid4()), "building_name": "Hostel 2", "lat": 30.7665, "lng": 76.5770, "type": "hostel", "floor_count": 8, "description": "Girls Hostel"},
        {"id": str(uuid.uuid4()), "building_name": "Sports Complex", "lat": 30.7695, "lng": 76.5740, "type": "facility", "floor_count": 2, "description": "Sports & Recreation Center"},
        {"id": str(uuid.uuid4()), "building_name": "Cafeteria", "lat": 30.7680, "lng": 76.5755, "type": "facility", "floor_count": 2, "description": "Main Cafeteria"},
        {"id": str(uuid.uuid4()), "building_name": "Admin Block", "lat": 30.7685, "lng": 76.5748, "type": "admin", "floor_count": 3, "description": "Administration Building"},
    ]
    
    existing_locations = await db.locations.count_documents({})
    if existing_locations == 0:
        await db.locations.insert_many(campus_locations)
    
    timetable_entries = [
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Monday", "start_time": "09:00", "end_time": "10:30", "subject": "Data Structures", "room": "A-301", "building": "Block A", "faculty": "Dr. Sharma", "lat": 30.7683, "lng": 76.5756},
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Monday", "start_time": "11:00", "end_time": "12:30", "subject": "Database Systems", "room": "B-205", "building": "Block B", "faculty": "Prof. Kumar", "lat": 30.7690, "lng": 76.5760},
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Monday", "start_time": "14:00", "end_time": "15:30", "subject": "AI & ML", "room": "C-401", "building": "Block C", "faculty": "Dr. Singh", "lat": 30.7675, "lng": 76.5750},
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Tuesday", "start_time": "09:00", "end_time": "10:30", "subject": "Operating Systems", "room": "A-205", "building": "Block A", "faculty": "Dr. Gupta", "lat": 30.7683, "lng": 76.5756},
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Tuesday", "start_time": "11:00", "end_time": "12:30", "subject": "Computer Networks", "room": "B-301", "building": "Block B", "faculty": "Prof. Patel", "lat": 30.7690, "lng": 76.5760},
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Wednesday", "start_time": "09:00", "end_time": "10:30", "subject": "Data Structures Lab", "room": "C-Lab1", "building": "Block C", "faculty": "Dr. Sharma", "lat": 30.7675, "lng": 76.5750},
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Thursday", "start_time": "09:00", "end_time": "10:30", "subject": "Software Engineering", "room": "A-401", "building": "Block A", "faculty": "Prof. Reddy", "lat": 30.7683, "lng": 76.5756},
        {"id": str(uuid.uuid4()), "user_id": user_id, "day": "Friday", "start_time": "09:00", "end_time": "10:30", "subject": "Web Technologies", "room": "B-101", "building": "Block B", "faculty": "Dr. Verma", "lat": 30.7690, "lng": 76.5760},
    ]
    
    existing_timetable = await db.timetable.count_documents({"user_id": user_id})
    if existing_timetable == 0:
        await db.timetable.insert_many(timetable_entries)
    
    attendance_records = [
        {"id": str(uuid.uuid4()), "user_id": user_id, "subject": "Data Structures", "date": "2026-01-15", "status": "present", "percentage": 85.5},
        {"id": str(uuid.uuid4()), "user_id": user_id, "subject": "Database Systems", "date": "2026-01-15", "status": "present", "percentage": 92.0},
        {"id": str(uuid.uuid4()), "user_id": user_id, "subject": "AI & ML", "date": "2026-01-15", "status": "absent", "percentage": 78.0},
        {"id": str(uuid.uuid4()), "user_id": user_id, "subject": "Operating Systems", "date": "2026-01-16", "status": "present", "percentage": 88.5},
        {"id": str(uuid.uuid4()), "user_id": user_id, "subject": "Computer Networks", "date": "2026-01-16", "status": "present", "percentage": 95.0},
    ]
    
    existing_attendance = await db.attendance.count_documents({"user_id": user_id})
    if existing_attendance == 0:
        await db.attendance.insert_many(attendance_records)
    
    notifications = [
        {"id": str(uuid.uuid4()), "user_id": user_id, "type": "class", "title": "Class Starting Soon", "message": "Your Data Structures class starts in 30 minutes at Block A, Room 301", "read": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "user_id": user_id, "type": "assignment", "title": "Assignment Due", "message": "Database Systems assignment is due tomorrow", "read": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "user_id": user_id, "type": "event", "title": "Tech Fest 2026", "message": "Annual tech fest starting next week. Register now!", "read": False, "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    
    existing_notifications = await db.notifications.count_documents({"user_id": user_id})
    if existing_notifications == 0:
        await db.notifications.insert_many(notifications)
    
    return {"message": "Mock data seeded successfully"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
