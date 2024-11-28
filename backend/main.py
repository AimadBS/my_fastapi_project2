from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configuration de l'application FastAPI
app = FastAPI()

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Assurez-vous que MongoDB est en cours d'exécution
db = client.my_database
users_collection = db.users

# Initialisation du cryptage du mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modèle pour l'utilisateur
class User(BaseModel):
    username: str
    password: str

# Fonction pour hasher un mot de passe
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Fonction pour vérifier un mot de passe
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Fonction pour obtenir un utilisateur par son nom d'utilisateur
def get_user_from_db(username: str):
    return users_collection.find_one({"username": username})

# Route pour l'inscription
@app.post("/register")
async def register_user(user: User):
    # Vérifier si l'utilisateur existe déjà
    if get_user_from_db(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash du mot de passe
    hashed_password = get_password_hash(user.password)

    # Enregistrer l'utilisateur dans la base de données MongoDB
    users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": "User created successfully"}

# Configuration de l'authentification OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration du secret pour signer les tokens JWT
SECRET_KEY = "5c92a82452e1cfd0719a420dfb720b75"  # Garde-le secret en sécurité
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fonction pour créer un token JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Route pour générer un token (login)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_from_db(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )
    # Génération du token JWT
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Route protégée qui nécessite un token valide
@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"message": "Voici les items sécurisés"}
