from typing import Optional

from app.config import settings


try:
    from google import genai
except ImportError:
    genai = None


client = None

if settings.GOOGLE_API_KEY and genai is not None:
    try:
        client = genai.Client(
            api_key=settings.GOOGLE_API_KEY
        )
    except Exception:
        client = None


def call_gemini(prompt: str) -> Optional[str]:
    """
    Send a prompt to Gemini.

    Returns None if Gemini is unavailable.
    """

    if client is None:
        return None

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()

    except Exception:
        return None

    return None


def generate_workout_gemini(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
    experience: str
) -> str:

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized 7-day workout plan.

User information:
Name: {name}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Workout intensity: {intensity}
Experience level: {experience}

Requirements:

1. Create exactly 7 days.
2. Each day must contain:
   - Day and focus
   - Warm-up
   - Main workout
   - Sets/repetitions or duration
   - Rest guidance
   - Cool-down/recovery
3. Include at least one recovery/rest day.
4. Adapt the difficulty to the selected intensity.
5. Adapt the plan to the fitness goal.
6. Keep the format simple and readable.
7. Do not make medical diagnoses.
8. Add a short safety note at the end.

Format:

DAY 1 - ...
Warm-up:
Main Workout:
- Exercise:
- Sets:
- Reps/Duration:
- Rest:
Cool-down:

DAY 2 - ...

Continue through DAY 7.
"""

    result = call_gemini(prompt)

    if result:
        return result

    return demo_workout(
        name,
        age,
        weight,
        goal,
        intensity,
        experience
    )


def generate_nutrition_tip_with_flash(goal: str) -> str:

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Fitness goal:
{goal}

Give one concise and practical nutrition or recovery tip.

The response should:
- Be easy to understand.
- Be 3 to 5 sentences.
- Support the fitness goal.
- Avoid extreme dieting.
- Avoid medical claims.
- Encourage hydration and balanced nutrition when relevant.
"""

    result = call_gemini(prompt)

    if result:
        return result

    return demo_nutrition_tip(goal)


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
) -> str:

    prompt = f"""
You are FitBuddy's workout plan revision assistant.

Fitness goal:
{goal}

Intensity:
{intensity}

Original workout plan:

{original_plan}

User feedback:

{feedback}

Create an updated 7-day workout plan.

Requirements:
1. Preserve useful parts of the original plan.
2. Apply the user's feedback.
3. Maintain exactly 7 days.
4. Include warm-up, main workout and cool-down/recovery.
5. Include at least one recovery/rest day.
6. Keep the selected intensity in mind.
7. Make the result easy to follow.
8. Add a short safety note.

Return only the updated plan.
"""

    result = call_gemini(prompt)

    if result:
        return result

    return demo_updated_plan(
        original_plan,
        feedback,
        goal,
        intensity
    )


def demo_workout(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
    experience: str
) -> str:

    intensity_data = {
        "Low": {
            "sets": "2 sets",
            "rest": "60-90 seconds"
        },
        "Medium": {
            "sets": "3 sets",
            "rest": "60 seconds"
        },
        "High": {
            "sets": "3-4 sets",
            "rest": "30-60 seconds"
        }
    }

    data = intensity_data.get(
        intensity,
        intensity_data["Medium"]
    )

    return f"""
FITBUDDY - 7 DAY WORKOUT PLAN

User: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}
Experience: {experience}

DAY 1 - FULL BODY
Warm-up:
5-10 minutes of light walking and mobility.

Main Workout:
- Bodyweight Squats - {data["sets"]} x 12 reps
- Push-ups - {data["sets"]} x 8-12 reps
- Glute Bridges - {data["sets"]} x 12 reps
- Plank - {data["sets"]} x 30 seconds

Rest:
{data["rest"]}

Cool-down:
5 minutes of stretching.

DAY 2 - CARDIO
Warm-up:
5 minutes easy walking.

Main Workout:
- Brisk Walking/Jogging - 20-30 minutes
- High Knees - {data["sets"]} x 20 seconds
- Step-ups - {data["sets"]} x 10 each leg

Rest:
{data["rest"]}

Cool-down:
Light walking and stretching.

DAY 3 - UPPER BODY
Warm-up:
Arm circles and shoulder mobility for 5 minutes.

Main Workout:
- Push-ups - {data["sets"]} x 8-12
- Incline Push-ups - {data["sets"]} x 10
- Chair Triceps Dips - {data["sets"]} x 8-10
- Plank Shoulder Taps - {data["sets"]} x 10 each side

Rest:
{data["rest"]}

Cool-down:
Upper-body stretching.

DAY 4 - RECOVERY
Activity:
- Easy walking - 15-20 minutes
- Light stretching
- Breathing exercises

Focus:
Recovery and mobility.

DAY 5 - LOWER BODY
Warm-up:
5-10 minutes of walking and mobility.

Main Workout:
- Squats - {data["sets"]} x 12
- Reverse Lunges - {data["sets"]} x 10 each leg
- Glute Bridges - {data["sets"]} x 15
- Calf Raises - {data["sets"]} x 15

Rest:
{data["rest"]}

Cool-down:
Lower-body stretching.

DAY 6 - CORE + CARDIO
Warm-up:
5 minutes of light activity.

Main Workout:
- Plank - {data["sets"]} x 30 seconds
- Mountain Climbers - {data["sets"]} x 20 seconds
- Bicycle Crunches - {data["sets"]} x 12
- Brisk Walking - 20 minutes

Rest:
{data["rest"]}

Cool-down:
Gentle stretching.

DAY 7 - FLEXIBILITY & RECOVERY
Activities:
- Easy walk - 15 minutes
- Full-body stretching - 15 minutes
- Deep breathing - 5 minutes

Recovery:
Focus on hydration, sleep and recovery.

SAFETY NOTE:
Start at a comfortable level, maintain proper form and stop if you experience unusual pain, dizziness or difficulty breathing. Consult a qualified professional for personalized medical or exercise advice.
"""


def demo_nutrition_tip(goal: str) -> str:

    goal_lower = goal.lower()

    if "muscle" in goal_lower:
        return (
            "For muscle gain, include a good protein source in your meals "
            "such as eggs, chicken, fish, beans, milk or yogurt. "
            "Combine protein with balanced carbohydrates and vegetables. "
            "Stay hydrated and give your body enough recovery time."
        )

    if "loss" in goal_lower or "fat" in goal_lower:
        return (
            "For weight management, focus on balanced meals with vegetables, "
            "protein, whole grains and appropriate portions. "
            "Limit highly processed foods and sugary drinks. "
            "Drink enough water and maintain regular sleep."
        )

    return (
        "For general wellness, focus on balanced meals containing protein, "
        "vegetables, fruits and whole grains. Stay hydrated throughout the day. "
        "Regular sleep and recovery are also important parts of a healthy routine."
    )


def demo_updated_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
) -> str:

    return f"""
FITBUDDY - UPDATED 7 DAY PLAN

The plan has been updated based on your feedback:

"{feedback}"

GOAL: {goal}
INTENSITY: {intensity}

DAY 1 - CARDIO + FULL BODY
- 5-10 min warm-up
- Brisk walking/jogging - 20 min
- Squats - 3 x 12
- Push-ups - 3 x 10
- Plank - 3 x 30 sec
- 5 min cool-down

DAY 2 - UPPER BODY
- 5-10 min warm-up
- Push-ups - 3 x 10
- Incline push-ups - 3 x 12
- Shoulder taps - 3 x 10
- Light stretching

DAY 3 - CARDIO
- 5 min warm-up
- Brisk walk/jog - 25-30 min
- Step-ups - 3 x 10
- Light stretching

DAY 4 - REST + YOGA
- 15-20 min gentle yoga
- Breathing exercises
- Light mobility work

DAY 5 - LOWER BODY
- Squats - 3 x 12
- Lunges - 3 x 10 each leg
- Glute bridges - 3 x 15
- Calf raises - 3 x 15
- Cool-down

DAY 6 - CORE + CARDIO
- Plank - 3 x 30 sec
- Mountain climbers - 3 x 20 sec
- Bicycle crunches - 3 x 12
- Brisk walking - 20 min

DAY 7 - ACTIVE RECOVERY
- Easy walking - 15-20 min
- Full-body stretching
- Recovery and hydration

SAFETY NOTE:
Perform exercises at a comfortable level and stop if you experience unusual pain, dizziness or difficulty breathing.
"""