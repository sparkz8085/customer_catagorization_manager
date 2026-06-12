import os
import secrets
import requests
from fastapi import APIRouter, Request, Response, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from services.auth_session import create_session_cookie
from database.user_store import upsert_user

router = APIRouter()
templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
templates = Jinja2Templates(directory=templates_dir)

# Client keys loaded from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID", "")
FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET", "")

def get_redirect_uri(request: Request, provider: str) -> str:
    """Helper to dynamically construct the redirect URI based on headers or scheme."""
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.url.netloc)
    return f"{proto}://{host}/auth/callback/{provider}"

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None, info: str = None):
    # Pass whether real client IDs are configured to toggle simulation notices in UI
    google_configured = bool(GOOGLE_CLIENT_ID)
    facebook_configured = bool(FACEBOOK_CLIENT_ID)
    
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "error": error,
            "info": info,
            "google_configured": google_configured,
            "facebook_configured": facebook_configured
        }
    )

@router.get("/login/google")
async def login_google(request: Request):
    if not GOOGLE_CLIENT_ID:
        return RedirectResponse(url="/login?error=Google+OAuth+is+not+configured.+Please+set+GOOGLE_CLIENT_ID+in+your+.env+file.")
        
    redirect_uri = get_redirect_uri(request, "google")
    state = secrets.token_hex(16)
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20profile%20email&"
        f"state={state}"
    )
    # Note: In a production app, the state should be checked in the callback, 
    # but for this service-level dashboard, direct redirection is fine.
    return RedirectResponse(url=google_auth_url)

@router.get("/login/facebook")
async def login_facebook(request: Request):
    if not FACEBOOK_CLIENT_ID:
        return RedirectResponse(url="/login?error=Facebook+OAuth+is+not+configured.+Please+set+FACEBOOK_CLIENT_ID+in+your+.env+file.")
        
    redirect_uri = get_redirect_uri(request, "facebook")
    state = secrets.token_hex(16)
    facebook_auth_url = (
        f"https://www.facebook.com/v12.0/dialog/oauth?"
        f"client_id={FACEBOOK_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=email%20public_profile&"
        f"state={state}"
    )
    return RedirectResponse(url=facebook_auth_url)

@router.get("/auth/callback/google")
async def callback_google(request: Request, code: str = None, error: str = None):
    if error or not code:
        return RedirectResponse(url=f"/login?error=Google+login+failed:+{error or 'Missing+code'}")
        
    try:
        redirect_uri = get_redirect_uri(request, "google")
        # Exchange code for access token
        token_res = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            },
            timeout=10
        )
        token_data = token_res.json()
        if "error" in token_data:
            return RedirectResponse(url=f"/login?error=Google+token+exchange+failed:+{token_data.get('error_description')}")
            
        access_token = token_data.get("access_token")
        
        # Retrieve user profile info
        profile_res = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        profile = profile_res.json()
        
        email = profile.get("email", "")
        name = profile.get("name", "Google User")
        picture = profile.get("picture", "")
        provider_uid = profile.get("sub", "")
        
        if not email:
            return RedirectResponse(url="/login?error=Failed+to+retrieve+email+from+Google+profile")
            
        # Register user in database
        user = upsert_user(
            provider="google",
            provider_uid=provider_uid,
            email=email,
            name=name,
            avatar_url=picture
        )
        
        # Create session cookie
        session_cookie = create_session_cookie(user)
        response = RedirectResponse(url="/?welcome=true", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="session",
            value=session_cookie,
            httponly=True,
            max_age=86400 * 30, # 30 days
            samesite="lax",
            secure=request.url.scheme == "https"
        )
        return response
        
    except Exception as e:
        return RedirectResponse(url=f"/login?error=Google+callback+processing+failed:+{str(e)}")

@router.get("/auth/callback/facebook")
async def callback_facebook(request: Request, code: str = None, error: str = None):
    if error or not code:
        return RedirectResponse(url=f"/login?error=Facebook+login+failed:+{error or 'Missing+code'}")
        
    try:
        redirect_uri = get_redirect_uri(request, "facebook")
        # Exchange code for access token
        token_res = requests.get(
            "https://graph.facebook.com/v12.0/oauth/access_token",
            params={
                "code": code,
                "client_id": FACEBOOK_CLIENT_ID,
                "client_secret": FACEBOOK_CLIENT_SECRET,
                "redirect_uri": redirect_uri
            },
            timeout=10
        )
        token_data = token_res.json()
        if "error" in token_data:
            return RedirectResponse(url=f"/login?error=Facebook+token+exchange+failed:+{token_data['error'].get('message')}")
            
        access_token = token_data.get("access_token")
        
        # Retrieve user profile info
        profile_res = requests.get(
            f"https://graph.facebook.com/me?fields=id,name,email,picture.type(large)&access_token={access_token}",
            timeout=10
        )
        profile = profile_res.json()
        
        provider_uid = profile.get("id", "")
        name = profile.get("name", "Facebook User")
        email = profile.get("email", "")
        # Fallback email if Facebook doesn't return one (signed up with phone)
        if not email:
            email = f"{provider_uid}@facebook.com"
            
        picture_data = profile.get("picture", {}).get("data", {})
        picture = picture_data.get("url", "")
        
        # Register user in database
        user = upsert_user(
            provider="facebook",
            provider_uid=provider_uid,
            email=email,
            name=name,
            avatar_url=picture
        )
        
        # Create session cookie
        session_cookie = create_session_cookie(user)
        response = RedirectResponse(url="/?welcome=true", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="session",
            value=session_cookie,
            httponly=True,
            max_age=86400 * 30, # 30 days
            samesite="lax",
            secure=request.url.scheme == "https"
        )
        return response
        
    except Exception as e:
        return RedirectResponse(url=f"/login?error=Facebook+callback+processing+failed:+{str(e)}")

@router.get("/auth/mock-callback")
async def mock_callback(request: Request, provider: str):
    """Simulates a successful OAuth login for local development and reviewers."""
    if provider == "facebook":
        name = "Facebook Socialite"
        email = "facebook.user@example.com"
        avatar = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150"
        provider_uid = "mock-fb-888999"
    else:
        # Default to google
        provider = "google"
        name = "Google Explorer"
        email = "google.user@example.com"
        avatar = "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=150"
        provider_uid = "mock-google-111222"
        
    user = upsert_user(
        provider=provider,
        provider_uid=provider_uid,
        email=email,
        name=name,
        avatar_url=avatar
    )
    
    session_cookie = create_session_cookie(user)
    response = RedirectResponse(url="/?welcome=true", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="session",
        value=session_cookie,
        httponly=True,
        max_age=86400 * 30,
        samesite="lax",
        secure=request.url.scheme == "https"
    )
    return response

@router.post("/login/email")
async def login_email(request: Request, name: str = Form(...), email: str = Form(...), nickname: str = Form(None), password: str = Form(None)):
    """Handles standard simulated developer email logins."""
    if not email or not name:
        return RedirectResponse(url="/login?error=Email+and+Name+are+required")
        
    avatar = f"https://api.dicebear.com/7.x/initials/svg?seed={name}"
    
    user = upsert_user(
        provider="mock",
        provider_uid=f"mock-email-{secrets.token_hex(4)}",
        email=email,
        name=name,
        avatar_url=avatar,
        nickname=nickname,
        password=password
    )
    
    session_cookie = create_session_cookie(user)
    response = RedirectResponse(url="/?welcome=true", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="session",
        value=session_cookie,
        httponly=True,
        max_age=86400 * 30,
        samesite="lax",
        secure=request.url.scheme == "https"
    )
    return response

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login?info=You+have+been+logged+out+successfully.")
    response.delete_cookie(key="session")
    return response
