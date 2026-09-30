from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from sqlalchemy.orm import Session

from app.database import get_db
from app.gemini_service import (
    generate_nutrition_tip_with_flash,
    generate_workout_gemini,
    update_workout_plan
)
from app.models import User
from app.schemas import (
    FeedbackRequest,
    NutritionRequest,
    UserInput
)


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "FitBuddy"
        }
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,

    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    experience: str = Form("Beginner"),

    db: Session = Depends(get_db)
):
    try:

        user_input = UserInput(
            user_id=user_id.strip(),
            name=name.strip(),
            age=age,
            weight=weight,
            goal=goal.strip(),
            intensity=intensity.strip(),
            experience=experience.strip()
        )

    except Exception as exc:

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Validation Error",
                "message": str(exc)
            },
            status_code=400
        )

    workout_plan = generate_workout_gemini(
        name=user_input.name,
        age=user_input.age,
        weight=user_input.weight,
        goal=user_input.goal,
        intensity=user_input.intensity,
        experience=user_input.experience
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        user_input.goal
    )

    existing_user = (
        db.query(User)
        .filter(User.user_id == user_input.user_id)
        .first()
    )

    if existing_user:

        existing_user.name = user_input.name
        existing_user.age = user_input.age
        existing_user.weight = user_input.weight
        existing_user.goal = user_input.goal
        existing_user.intensity = user_input.intensity
        existing_user.experience = user_input.experience
        existing_user.original_plan = workout_plan
        existing_user.updated_plan = None
        existing_user.feedback = None
        existing_user.nutrition_tip = nutrition_tip

        db.commit()
        db.refresh(existing_user)

        user = existing_user

    else:

        user = User(
            user_id=user_input.user_id,
            name=user_input.name,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
            experience=user_input.experience,
            original_plan=workout_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "Your Fitness Plan",
            "user": user,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "message": None
        }
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),
    feedback: str = Form(...),

    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id.strip())
        .first()
    )

    if not user:

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "User Not Found",
                "message": "No user was found with that User ID."
            },
            status_code=404
        )

    if not feedback.strip():

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Invalid Feedback",
                "message": "Please enter feedback."
            },
            status_code=400
        )

    new_plan = update_workout_plan(
        original_plan=user.original_plan,
        feedback=feedback.strip(),
        goal=user.goal,
        intensity=user.intensity
    )

    user.updated_plan = new_plan
    user.feedback = feedback.strip()

    user.nutrition_tip = generate_nutrition_tip_with_flash(
        user.goal
    )

    db.commit()
    db.refresh(user)

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "Updated Fitness Plan",
            "user": user,
            "workout_plan": new_plan,
            "nutrition_tip": user.nutrition_tip,
            "message": "Your workout plan has been updated successfully!"
        }
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "title": "All Users",
            "users": users
        }
    )


@router.post("/delete-user/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user:
        db.delete(user)
        db.commit()

    return RedirectResponse(
        url="/view-all-users",
        status_code=303
    )


# -------------------------------------------------------
# API ROUTES
# -------------------------------------------------------


@router.get("/api/health")
def health_check():

    return {
        "status": "ok",
        "application": "FitBuddy"
    }


@router.post("/api/generate-workout")
def api_generate_workout(
    data: UserInput,
    db: Session = Depends(get_db)
):

    workout_plan = generate_workout_gemini(
        name=data.name,
        age=data.age,
        weight=data.weight,
        goal=data.goal,
        intensity=data.intensity,
        experience=data.experience
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        data.goal
    )

    existing_user = (
        db.query(User)
        .filter(User.user_id == data.user_id)
        .first()
    )

    if existing_user:

        existing_user.name = data.name
        existing_user.age = data.age
        existing_user.weight = data.weight
        existing_user.goal = data.goal
        existing_user.intensity = data.intensity
        existing_user.experience = data.experience
        existing_user.original_plan = workout_plan
        existing_user.updated_plan = None
        existing_user.feedback = None
        existing_user.nutrition_tip = nutrition_tip

        db.commit()
        db.refresh(existing_user)

        user = existing_user

    else:

        user = User(
            user_id=data.user_id,
            name=data.name,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
            experience=data.experience,
            original_plan=workout_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "success": True,
        "user_id": user.user_id,
        "workout_plan": workout_plan,
        "nutrition_tip": nutrition_tip
    }


@router.post("/api/submit-feedback")
def api_submit_feedback(
    data: FeedbackRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == data.user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_plan = update_workout_plan(
        original_plan=user.original_plan,
        feedback=data.feedback,
        goal=user.goal,
        intensity=user.intensity
    )

    user.updated_plan = new_plan
    user.feedback = data.feedback

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "user_id": user.user_id,
        "updated_plan": new_plan
    }


@router.post("/api/nutrition-tip")
def api_nutrition_tip(
    data: NutritionRequest
):

    tip = generate_nutrition_tip_with_flash(
        data.goal
    )

    return {
        "success": True,
        "goal": data.goal,
        "nutrition_tip": tip
    }


@router.get("/api/users")
def api_get_users(
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return {
        "count": len(users),
        "users": [
            {
                "user_id": user.user_id,
                "name": user.name,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "experience": user.experience,
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                )
            }
            for user in users
        ]
    }


@router.get("/api/users/{user_id}")
def api_get_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": user.user_id,
        "name": user.name,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "experience": user.experience,
        "original_plan": user.original_plan,
        "updated_plan": user.updated_plan,
        "nutrition_tip": user.nutrition_tip,
        "feedback": user.feedback
    }


@router.delete("/api/users/{user_id}")
def api_delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "success": True,
        "message": "User deleted successfully"
    }