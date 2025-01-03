
import json
from fastapi import FastAPI,  HTTPException, status 
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import database
from auth import create_access_token, create_refresh_token , SECRET_KEY , ALGORITHM
from jose import JWTError, jwt
from models import *




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # List of allowed origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)





# FastAPI Routes
@app.post("/user/login", response_model=LoginToken)
def login(user: User):
    # Authenticate the user
    db_user = database.check_user(user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    # Generate tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "user_info": user_info(**db_user),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

# @app.post("/auth/refresh", response_model=Token)
# def refresh_token(refresh_token: str):
#     try:
#         # Decode and validate the refresh token
#         payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid refresh token",
#             )
#         # Generate new tokens
#         access_token = create_access_token(data={"sub": username})
#         new_refresh_token = create_refresh_token(data={"sub": username})
#         return {
#             "access_token": access_token,
#             "refresh_token": new_refresh_token,
#         }
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token",
#         )
    

# a function to check if the token is valid
@app.post("/user/auth")
def check_token(request: token):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return JSONResponse(content={"isValid": False, "error": "Invalid token"})

        if database.authenticate_user(username):
            return JSONResponse(content={"isValid": True})
        return JSONResponse(content={"isValid": False, "error": "Invalid username or password"})
    except JWTError:
        return JSONResponse(content={"isValid": False, "error": "Signature has expired"})
    except Exception as e:
        print(e)
    
@app.get("/menu-items")
def get_menu_items():
    with open("./Lectures.json") as file:
        data = json.load(file)  
    return JSONResponse(content=[data])

class Subject(BaseModel):
    label: str

@app.post("/subjects/add")
async def add_subject(subject: Subject):
    try:
        with open("./Lectures.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            data['items'].append({"label": subject.label, "items": []})
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
        return JSONResponse(content=[data])
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in Lectures.json"}, 400
    except Exception as e:
        return {"error": str(e)}, 500
    

@app.post("/lectures/add")
async def add_lecture(lecture: Lecture):
    try:
        with open("./Lectures.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            for item in data['items']:
                if item['label'] == lecture.subject:
                    break
            item['items'].append({"label": lecture.label, "icon": "pi pi-fw pi-bookmark" , 'to': f"/lectures/{lecture.subject}/{lecture.label}"})
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
        return JSONResponse(content=[data])
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in Lectures.json"}, 400
    except Exception as e:
        return {"error": str(e)}, 500
    
    
    
    


@app.post("/lectures/data/add")
async def add_lecture_data(data: Data) -> JSONResponse:
    """
    Add or update a lecture data in the database.

    Args:
        data (Data): The data to add or update.

    Returns:
        JSONResponse: A JSON response with a message indicating success or failure.
    """
    database.add_or_update_lecture_data("lectures.db", data)
    return JSONResponse(content={"message": "Successfully added data to the database"})
# a function to get the lectures from the database
@app.post("/lectures/data/get")
def get_lectures(data: GetData) -> JSONResponse:
    lecture_data = database.get_lecture_data("lectures.db", data.subject, data.lecture)
    if lecture_data is None:
        return JSONResponse(content={"error": "Lecture data not found"})
    return JSONResponse(content=lecture_data)