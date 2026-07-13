from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import User, VerificationCode
from app.schemas import (
    ForgotPasswordRequest,
    MessageOut,
    RegisterPendingOut,
    ResetPasswordRequest,
    RoleUpdateRequest,
    TokenOut,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
    VerifyRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_CODE = "123456"
CODE_TTL_MINUTES = 10
ALLOWED_ROLES = {"farmer", "agronomist", "cooperative", "consultant"}


def _issue_token(user: User) -> TokenOut:
    token = create_access_token(user.email)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


def _validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Şifre en az 8 karakter olmalıdır.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Şifrede en az 1 büyük harf olmalıdır.")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Şifrede en az 1 küçük harf olmalıdır.")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Şifrede en az 1 rakam olmalıdır.")


def _normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    return digits or None


def _find_user_by_login(db: Session, login: str) -> User | None:
    value = login.strip().lower()
    user = db.query(User).filter(User.email == value).first()
    if user:
        return user
    phone = _normalize_phone(login)
    if phone:
        return db.query(User).filter(User.phone == phone).first()
    return None


def _create_code(db: Session, email: str, purpose: str) -> str:
    db.query(VerificationCode).filter(
        VerificationCode.email == email.lower(),
        VerificationCode.purpose == purpose,
        VerificationCode.used.is_(False),
    ).update({"used": True})
    code = DEMO_CODE
    row = VerificationCode(
        email=email.lower(),
        code=code,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES),
        used=False,
    )
    db.add(row)
    db.commit()
    return code


def _consume_code(db: Session, email: str, purpose: str, code: str) -> None:
    row = (
        db.query(VerificationCode)
        .filter(
            VerificationCode.email == email.lower(),
            VerificationCode.purpose == purpose,
            VerificationCode.used.is_(False),
        )
        .order_by(VerificationCode.id.desc())
        .first()
    )
    if not row or row.code != code.strip():
        raise HTTPException(status_code=400, detail="Doğrulama kodu hatalı.")
    if row.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Doğrulama kodunun süresi dolmuş.")
    row.used = True
    db.commit()


@router.post("/register", response_model=RegisterPendingOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    _validate_password_strength(payload.password)
    email = payload.email.lower()
    phone = _normalize_phone(payload.phone)
    existing = db.query(User).filter(User.email == email).first()
    if existing and existing.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta ile kayıtlı bir hesap zaten var.",
        )
    if phone:
        phone_owner = db.query(User).filter(User.phone == phone).first()
        if phone_owner and (not existing or phone_owner.id != existing.id) and phone_owner.email_verified:
            raise HTTPException(status_code=400, detail="Bu telefon numarası zaten kayıtlı.")

    if existing and not existing.email_verified:
        existing.name = payload.name
        existing.phone = phone
        existing.password_hash = hash_password(payload.password)
        existing.role = payload.role if payload.role in ALLOWED_ROLES else "farmer"
        db.commit()
    else:
        user = User(
            name=payload.name,
            email=email,
            phone=phone,
            password_hash=hash_password(payload.password),
            role=payload.role if payload.role in ALLOWED_ROLES else "farmer",
            email_verified=False,
        )
        db.add(user)
        db.commit()

    demo_code = _create_code(db, email, "register")
    return RegisterPendingOut(
        email=email,
        message="Doğrulama kodu e-posta adresinize gönderildi (MVP: demo kodu yanıtta).",
        demo_code=demo_code,
        expires_in_seconds=CODE_TTL_MINUTES * 60,
    )


@router.post("/verify", response_model=TokenOut)
def verify_email(payload: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Hesap bulunamadı.")
    _consume_code(db, payload.email, "register", payload.code)
    user.email_verified = True
    db.commit()
    db.refresh(user)
    return _issue_token(user)


@router.post("/resend-code", response_model=MessageOut)
def resend_code(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = _find_user_by_login(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="Hesap bulunamadı.")
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Hesap zaten doğrulanmış.")
    code = _create_code(db, user.email, "register")
    return MessageOut(message="Yeni doğrulama kodu gönderildi.", demo_code=code)


@router.patch("/me/role", response_model=UserOut)
def update_role(
    payload: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.role = payload.role
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)


@router.post("/forgot-password", response_model=MessageOut)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = _find_user_by_login(db, payload.email)
    generic = "Eğer hesap varsa doğrulama kodu gönderildi."
    if not user:
        return MessageOut(message=generic, demo_code=None)
    code = _create_code(db, user.email, "reset")
    return MessageOut(message=generic, demo_code=code, email=user.email)


@router.post("/reset-password", response_model=MessageOut)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    _validate_password_strength(payload.new_password)
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Hesap bulunamadı.")
    _consume_code(db, payload.email, "reset", payload.code)
    user.password_hash = hash_password(payload.new_password)
    user.email_verified = True
    db.commit()
    return MessageOut(message="Şifreniz güncellendi. Giriş yapabilirsiniz.")


@router.post("/login", response_model=TokenOut)
def login_json(payload: UserLogin, db: Session = Depends(get_db)):
    user = _find_user_by_login(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta/telefon veya şifre hatalı.",
        )
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız doğrulanmamış. Lütfen e-posta doğrulamasını tamamlayın.",
        )
    if getattr(user, "is_active", True) is False:
        raise HTTPException(status_code=403, detail="Hesap pasif.")
    user.last_login_at = datetime.utcnow()
    db.commit()
    return _issue_token(user)


@router.post("/token", response_model=TokenOut)
def login_form(
    payload: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = _find_user_by_login(db, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta/telefon veya şifre hatalı.",
        )
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız doğrulanmamış.",
        )
    if getattr(user, "is_active", True) is False:
        raise HTTPException(status_code=403, detail="Hesap pasif.")
    user.last_login_at = datetime.utcnow()
    db.commit()
    return _issue_token(user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Güncellenecek alan yok.")

    if "name" in data and data["name"] is not None:
        name = data["name"].strip()
        if len(name) < 2:
            raise HTTPException(status_code=400, detail="Ad en az 2 karakter olmalıdır.")
        current_user.name = name

    if "phone" in data:
        phone = _normalize_phone(data["phone"])
        if phone:
            phone_owner = (
                db.query(User)
                .filter(User.phone == phone, User.id != current_user.id)
                .first()
            )
            if phone_owner and phone_owner.email_verified:
                raise HTTPException(status_code=400, detail="Bu telefon numarası zaten kayıtlı.")
        current_user.phone = phone

    new_password = data.get("new_password")
    if new_password is not None:
        current_password = data.get("current_password")
        if not current_password:
            raise HTTPException(
                status_code=400,
                detail="Şifre değiştirmek için mevcut şifrenizi girin.",
            )
        if not verify_password(current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Mevcut şifre hatalı.")
        _validate_password_strength(new_password)
        current_user.password_hash = hash_password(new_password)

    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)
