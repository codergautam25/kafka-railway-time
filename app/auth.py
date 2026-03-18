
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()
SECRET="enterprise_secret"

def verify_token(token: str = Depends(security)):
    try:
        decoded = jwt.decode(token.credentials, SECRET, algorithms=["HS256"])
        print(f"Token verified: {decoded}")
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=403, detail=f"invalid token: {str(e)}")
