from fastapi import Header, HTTPException, status
from config import settings

async def verify_token(x_token: str = Header(..., alias=settings.API_TOKEN_NAME)):
    """
    验证请求头中的 API Token
    默认 Header key: x-token
    """
    if x_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Token",
        )
    return x_token
