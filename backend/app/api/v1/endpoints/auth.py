from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.entities import User, Workspace, WorkspaceMember, UserRole
from app.schemas.domain import UserCreate, UserResponse, Token
from app.api.deps import get_current_user, get_current_workspace_id

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
        
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.ADMIN.value
    )
    db.add(user)
    db.flush()
    
    # Create default workspace
    slug = user_in.email.split("@")[0].lower() + "-workspace"
    workspace = Workspace(
        name=f"{user_in.full_name or 'Default'}'s Workspace",
        slug=slug
    )
    db.add(workspace)
    db.flush()
    
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role="admin"
    )
    db.add(member)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        workspace_id=workspace.id,
        created_at=user.created_at
    )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    membership = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.id).first()
    workspace_id = membership.workspace_id if membership else ""
    
    access_token = create_access_token(data={"sub": user.email, "workspace_id": workspace_id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "workspace_id": workspace_id
    }

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_current_workspace_id)
):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        workspace_id=workspace_id,
        created_at=current_user.created_at
    )
