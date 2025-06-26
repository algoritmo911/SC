# api/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

# --- Configuration ---
SECRET_KEY = "YOUR_VERY_SECRET_KEY_CHANGE_THIS" # TODO: Load from env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Pydantic Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    # You can add more fields to the token payload, e.g., user_id, roles

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    # Add other user fields as necessary, e.g., wallet_address

class UserInDB(User):
    hashed_password: str
    # roles: List[str] = [] # Example for role-based access control

# --- Database (Placeholder) ---
# In a real application, this would be a database (SQL, NoSQL, etc.)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secretpassword"), # Hash a default password
        "disabled": False,
    },
    "jane": {
        "username": "jane",
        "full_name": "Jane Roe",
        "email": "jane@example.com",
        "hashed_password": pwd_context.hash("anothersecret"),
        "disabled": False,
    }
}

def get_user(db, username: str) -> Optional[UserInDB]:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

# --- Password Utilities ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- JWT Token Creation ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- OAuth2 Scheme ---
# This tells FastAPI where to look for the token (in the Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # "token" is the path to your token endpoint

# --- Dependency to Get Current User ---
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # "sub" is standard claim for subject (username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return User(**user.model_dump(exclude={"hashed_password"})) # Return User model, not UserInDB

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# --- Token Endpoint (Example) ---
# This would typically be in your endpoints.py, but shown here for completeness of auth logic.
# from fastapi import APIRouter
# auth_router = APIRouter()
# @auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Provides an endpoint to get a JWT token.
    It uses OAuth2PasswordRequestForm which expects 'username' and 'password'
    in a form-data body.
    """
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Example of how to protect an endpoint (would be in endpoints.py):
# from .auth import get_current_active_user, User
# @router.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user

# Notes:
# 1. SECRET_KEY must be kept secret and should be loaded from environment variables.
# 2. This is a basic implementation. For production, consider:
#    - Refresh tokens.
#    - Token revocation.
#    - More robust user database integration.
#    - Role-based access control (RBAC).
#    - Using an Identity Provider (IdP) like Keycloak, Auth0, etc. for OAuth2.
# 3. The `/token` endpoint logic should be added to your `endpoints.py` or a dedicated auth router.
#    If you add it to `endpoints.py`, ensure the APIRouter instance is used.
#    Example: router.post("/token", response_model=Token)(login_for_access_token)

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # Create a new user and hash their password
    # new_user_password = "secure_password_123"
    # hashed = get_password_hash(new_user_password)
    # print(f"Hashed password for 'testuser': {hashed}")
    # fake_users_db["testuser"] = {
    #     "username": "testuser",
    #     "full_name": "Test User",
    #     "email": "test@example.com",
    #     "hashed_password": hashed,
    #     "disabled": False,
    # }

    # Simulate token creation
    # token_data = {"sub": "johndoe"}
    # access_token = create_access_token(data=token_data)
    # print(f"Access token for johndoe: {access_token}")

    # To make this runnable with the /token endpoint example:
    # 1. `pip install python-jose[cryptography] passlib[bcrypt] fastapi uvicorn`
    # 2. Create a main.py:
    #    from fastapi import FastAPI, Depends
    #    from api.auth import login_for_access_token #, User, get_current_active_user (for protected routes)
    #    from api.auth import Token # for response model
    #    from fastapi.security import OAuth2PasswordRequestForm

    #    app = FastAPI()

    #    @app.post("/token", response_model=Token)
    #    async def login_route(form_data: OAuth2PasswordRequestForm = Depends()):
    #        return await login_for_access_token(form_data)

    #    # Example protected route
    #    # @app.get("/users/me/", response_model=User)
    #    # async def read_users_me(current_user: User = Depends(get_current_active_user)):
    #    #     return current_user

    #    if __name__ == "__main__":
    #        import uvicorn
    #        uvicorn.run(app, host="0.0.0.0", port=8000)
    # 3. Run `python main.py`
    # 4. Use a tool like Postman or curl to POST to `http://localhost:8000/token`
    #    with form-data: username=johndoe, password=secretpassword
    pass
