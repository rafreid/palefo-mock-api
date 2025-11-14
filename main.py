"""
FastAPI Mock Server for Palefò API
Based on api-service.js endpoints
"""

from fastapi import FastAPI, HTTPException, Query, File, UploadFile, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import random
import uuid

app = FastAPI(title="Palefò Mock API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Pydantic Models
# ============================================================================

class Sentence(BaseModel):
    id: int
    kreyolText: str
    englishTranslation: str
    category: Optional[str] = None
    difficultyLevel: int
    audioUrl: Optional[str] = None


class Statistics(BaseModel):
    totalContributions: int
    uniqueContributors: int
    totalAudioHours: float


class Contributor(BaseModel):
    email: str
    contributionCount: int
    rank: int
    gender: Optional[str] = None
    region: Optional[str] = None


class Contribution(BaseModel):
    id: int
    kreyolText: str
    audioUrl: str
    email: Optional[str] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    isApproved: bool
    rejectionReason: Optional[str] = None
    createdAt: str
    updatedAt: str


class ContributionList(BaseModel):
    items: List[Contribution]
    page: int
    pageSize: int
    totalItems: int
    totalPages: int


class ModerationRequest(BaseModel):
    approved: bool
    rejectionReason: Optional[str] = None


class AIPhrase(BaseModel):
    phrase: str
    englishTranslation: str
    category: Optional[str] = None
    difficultyLevel: Optional[int] = None
    wordCount: int


# ============================================================================
# Mock Data
# ============================================================================

MOCK_SENTENCES = [
    {
        "id": 1,
        "kreyolText": "Bonjou, kijan ou ye?",
        "englishTranslation": "Hello, how are you?",
        "category": "greetings",
        "difficultyLevel": 1,
        "audioUrl": "https://example.blob.core.windows.net/audio/1.mp3"
    },
    {
        "id": 2,
        "kreyolText": "Mwen byen, mèsi.",
        "englishTranslation": "I'm fine, thank you.",
        "category": "greetings",
        "difficultyLevel": 1,
        "audioUrl": "https://example.blob.core.windows.net/audio/2.mp3"
    },
    {
        "id": 3,
        "kreyolText": "Kisa ou renmen manje?",
        "englishTranslation": "What do you like to eat?",
        "category": "food",
        "difficultyLevel": 2,
        "audioUrl": "https://example.blob.core.windows.net/audio/3.mp3"
    },
    {
        "id": 4,
        "kreyolText": "M ap aprann pale kreyòl.",
        "englishTranslation": "I am learning to speak Creole.",
        "category": "education",
        "difficultyLevel": 2,
        "audioUrl": "https://example.blob.core.windows.net/audio/4.mp3"
    },
    {
        "id": 5,
        "kreyolText": "Solèy la cho jodi a.",
        "englishTranslation": "The sun is hot today.",
        "category": "weather",
        "difficultyLevel": 1,
        "audioUrl": "https://example.blob.core.windows.net/audio/5.mp3"
    },
    {
        "id": 6,
        "kreyolText": "Nou bezwen travay ansanm pou bati yon pi bon demen.",
        "englishTranslation": "We need to work together to build a better tomorrow.",
        "category": "society",
        "difficultyLevel": 4,
        "audioUrl": "https://example.blob.core.windows.net/audio/6.mp3"
    },
    {
        "id": 7,
        "kreyolText": "Timoun yo ap jwe nan lakou a.",
        "englishTranslation": "The children are playing in the yard.",
        "category": "family",
        "difficultyLevel": 2,
        "audioUrl": "https://example.blob.core.windows.net/audio/7.mp3"
    },
    {
        "id": 8,
        "kreyolText": "Pwogrè teknolojik la enpòtan pou devlopman peyi a.",
        "englishTranslation": "Technological progress is important for the country's development.",
        "category": "technology",
        "difficultyLevel": 5,
        "audioUrl": "https://example.blob.core.windows.net/audio/8.mp3"
    },
]

MOCK_CONTRIBUTIONS = [
    {
        "id": i,
        "kreyolText": sentence["kreyolText"],
        "audioUrl": sentence["audioUrl"],
        "email": f"user{i}@example.com",
        "gender": random.choice(["male", "female", "other"]),
        "region": random.choice(["Port-au-Prince", "Cap-Haïtien", "Les Cayes", "Gonaïves"]),
        "isApproved": random.choice([True, False]),
        "rejectionReason": None if random.choice([True, False]) else "Audio quality issue",
        "createdAt": "2025-01-01T10:00:00Z",
        "updatedAt": "2025-01-01T10:00:00Z"
    }
    for i, sentence in enumerate(MOCK_SENTENCES, start=1)
]

MOCK_CONTRIBUTORS = [
    {"email": "contributor1@example.com", "contributionCount": 15000, "rank": 1, "gender": "female", "region": "Port-au-Prince"},
    {"email": "contributor2@example.com", "contributionCount": 12000, "rank": 2, "gender": "male", "region": "Cap-Haïtien"},
    {"email": "contributor3@example.com", "contributionCount": 8500, "rank": 3, "gender": "female", "region": "Les Cayes"},
    {"email": "contributor4@example.com", "contributionCount": 6200, "rank": 4, "gender": "male", "region": "Gonaïves"},
    {"email": "contributor5@example.com", "contributionCount": 4500, "rank": 5, "gender": "other", "region": "Port-au-Prince"},
    {"email": "contributor6@example.com", "contributionCount": 3100, "rank": 6, "gender": "female", "region": "Jacmel"},
    {"email": "contributor7@example.com", "contributionCount": 2800, "rank": 7, "gender": "male", "region": "Saint-Marc"},
    {"email": "contributor8@example.com", "contributionCount": 2200, "rank": 8, "gender": "female", "region": "Jérémie"},
    {"email": "contributor9@example.com", "contributionCount": 1900, "rank": 9, "gender": "male", "region": "Hinche"},
    {"email": "contributor10@example.com", "contributionCount": 1500, "rank": 10, "gender": "female", "region": "Port-de-Paix"},
]


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Palefò Mock API",
        "version": "1.0.0",
        "endpoints": {
            "sentences": "/api/sentences/*",
            "contributions": "/api/contributions",
            "statistics": "/api/statistics",
            "contributors": "/api/contributors/top",
            "ai": "/api/ai/*"
        }
    }


# ============================================================================
# Sentences Endpoints
# ============================================================================

@app.get("/api/sentences/random")
def get_random_sentences(
    count: int = Query(1, ge=1, le=50),
    excludeIds: Optional[str] = Query(None)
):
    """
    Get random sentences
    Query params:
    - count: Number of sentences to retrieve (default: 1, max: 50)
    - excludeIds: Comma-separated list of sentence IDs to exclude
    """
    exclude_list = []
    if excludeIds:
        try:
            exclude_list = [int(id.strip()) for id in excludeIds.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid excludeIds format")

    available_sentences = [s for s in MOCK_SENTENCES if s["id"] not in exclude_list]

    if not available_sentences:
        return []

    selected_count = min(count, len(available_sentences))
    return random.sample(available_sentences, selected_count)


@app.get("/api/sentences/category/{category}")
def get_sentences_by_category(
    category: str = Path(...),
    count: int = Query(1, ge=1, le=50)
):
    """
    Get sentences by category
    Path params:
    - category: Category name
    Query params:
    - count: Number of sentences to retrieve
    """
    filtered_sentences = [s for s in MOCK_SENTENCES if s.get("category") == category]

    if not filtered_sentences:
        return []

    selected_count = min(count, len(filtered_sentences))
    return random.sample(filtered_sentences, selected_count)


@app.get("/api/sentences/category-simple/{category}")
def get_sentences_by_category_simple(
    category: str = Path(...),
    count: int = Query(1, ge=1, le=50)
):
    """
    Get sentences by category (simple query, no stored procedure)
    Path params:
    - category: Category name
    Query params:
    - count: Number of sentences to retrieve
    """
    # Same implementation as category endpoint for mock purposes
    return get_sentences_by_category(category, count)


@app.get("/api/sentences/difficulty/{level}")
def get_sentences_by_difficulty(
    level: int = Path(..., ge=1, le=5),
    count: int = Query(1, ge=1, le=50)
):
    """
    Get sentences by difficulty level
    Path params:
    - level: Difficulty level (1-5)
    Query params:
    - count: Number of sentences to retrieve
    """
    filtered_sentences = [s for s in MOCK_SENTENCES if s["difficultyLevel"] == level]

    if not filtered_sentences:
        return []

    selected_count = min(count, len(filtered_sentences))
    return random.sample(filtered_sentences, selected_count)


# ============================================================================
# Statistics Endpoint
# ============================================================================

@app.get("/api/statistics", response_model=Statistics)
def get_statistics():
    """
    Get platform statistics
    Returns:
    - totalContributions: Total number of contributions
    - uniqueContributors: Number of unique contributors
    - totalAudioHours: Total hours of audio recorded
    """
    total_contributions = sum(c["contributionCount"] for c in MOCK_CONTRIBUTORS)
    unique_contributors = len(MOCK_CONTRIBUTORS)
    # Assume average contribution is 3 seconds
    total_audio_hours = round((total_contributions * 3) / 3600, 2)

    return {
        "totalContributions": total_contributions,
        "uniqueContributors": unique_contributors,
        "totalAudioHours": total_audio_hours
    }


# ============================================================================
# Contributors Endpoint
# ============================================================================

@app.get("/api/contributors/top", response_model=List[Contributor])
def get_top_contributors(limit: int = Query(10, ge=1, le=100)):
    """
    Get top contributors
    Query params:
    - limit: Number of top contributors to retrieve (default: 10, max: 100)
    """
    return MOCK_CONTRIBUTORS[:limit]


# ============================================================================
# Contributions Endpoints
# ============================================================================

@app.post("/api/contributions")
async def submit_contribution(
    KreyòlText: str = Form(...),
    AudioFile: UploadFile = File(...),
    Email: Optional[str] = Form(None),
    Gender: Optional[str] = Form(None),
    Region: Optional[str] = Form(None)
):
    """
    Submit a new contribution
    Form data:
    - KreyòlText: The Haitian Kreyòl text (required)
    - AudioFile: Audio recording file (required)
    - Email: Contributor email (optional)
    - Gender: Gender selection (optional)
    - Region: Region selection (optional)
    """
    # Validate audio file
    if not AudioFile.filename:
        raise HTTPException(status_code=400, detail="Audio file is required")

    # Validate file type
    allowed_extensions = [".mp3", ".wav", ".webm", ".m4a"]
    file_extension = "." + AudioFile.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create mock contribution
    new_id = len(MOCK_CONTRIBUTIONS) + 1
    mock_audio_url = f"https://example.blob.core.windows.net/audio/{uuid.uuid4()}.{file_extension[1:]}"

    new_contribution = {
        "id": new_id,
        "kreyolText": KreyòlText,
        "audioUrl": mock_audio_url,
        "email": Email,
        "gender": Gender,
        "region": Region,
        "isApproved": False,  # Pending approval by default
        "rejectionReason": None,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    }

    MOCK_CONTRIBUTIONS.append(new_contribution)

    return new_contribution


@app.get("/api/contributions", response_model=ContributionList)
def get_contributions(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    includeUnapproved: bool = Query(False)
):
    """
    Get list of contributions with pagination
    Query params:
    - page: Page number (default: 1)
    - pageSize: Items per page (default: 20, max: 100)
    - includeUnapproved: Include unapproved contributions (default: false)
    """
    # Filter contributions based on approval status
    if includeUnapproved:
        filtered_contributions = MOCK_CONTRIBUTIONS
    else:
        filtered_contributions = [c for c in MOCK_CONTRIBUTIONS if c["isApproved"]]

    total_items = len(filtered_contributions)
    total_pages = (total_items + pageSize - 1) // pageSize

    # Calculate pagination
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize

    items = filtered_contributions[start_idx:end_idx]

    return {
        "items": items,
        "page": page,
        "pageSize": pageSize,
        "totalItems": total_items,
        "totalPages": total_pages
    }


@app.get("/api/contributions/{id}", response_model=Contribution)
def get_contribution_by_id(id: int = Path(..., ge=1)):
    """
    Get a specific contribution by ID
    Path params:
    - id: Contribution ID
    """
    contribution = next((c for c in MOCK_CONTRIBUTIONS if c["id"] == id), None)

    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    return contribution


@app.patch("/api/contributions/{id}/approval")
def moderate_contribution(
    id: int = Path(..., ge=1),
    moderation: ModerationRequest = None
):
    """
    Approve or reject a contribution (Admin only)
    Path params:
    - id: Contribution ID
    Body:
    - approved: Boolean indicating approval status
    - rejectionReason: Reason for rejection (required if approved=false)
    """
    contribution = next((c for c in MOCK_CONTRIBUTIONS if c["id"] == id), None)

    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    if not moderation.approved and not moderation.rejectionReason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required when rejecting a contribution"
        )

    # Update contribution
    contribution["isApproved"] = moderation.approved
    contribution["rejectionReason"] = moderation.rejectionReason if not moderation.approved else None
    contribution["updatedAt"] = datetime.utcnow().isoformat() + "Z"

    return contribution


# ============================================================================
# AI Phrase Generation Endpoints
# ============================================================================

AI_PHRASES = [
    {"phrase": "Lanmou se pi bèl bagay nan lavi.", "translation": "Love is the most beautiful thing in life.", "category": "emotions", "difficulty": 3},
    {"phrase": "Edikasyon se kle siksè.", "translation": "Education is the key to success.", "category": "education", "difficulty": 2},
    {"phrase": "Fanmi se richès ki pi enpòtan.", "translation": "Family is the most important wealth.", "category": "family", "difficulty": 2},
    {"phrase": "Travay di fè moun rich.", "translation": "Hard work makes people rich.", "category": "work", "difficulty": 2},
    {"phrase": "Respè se baz tout bon relasyon.", "translation": "Respect is the basis of all good relationships.", "category": "society", "difficulty": 3},
]


@app.get("/api/ai/random-phrase", response_model=AIPhrase)
def get_ai_generated_phrase(
    category: Optional[str] = Query(None),
    difficultyLevel: Optional[int] = Query(None, ge=1, le=5),
    minWords: Optional[int] = Query(None, ge=1),
    maxWords: Optional[int] = Query(None, ge=1)
):
    """
    Get AI-generated random Haitian Kreyòl phrase
    Query params:
    - category: Optional category for the phrase
    - difficultyLevel: Optional difficulty level (1-5)
    - minWords: Optional minimum word count
    - maxWords: Optional maximum word count
    """
    filtered_phrases = AI_PHRASES.copy()

    # Filter by category
    if category:
        filtered_phrases = [p for p in filtered_phrases if p["category"] == category]

    # Filter by difficulty
    if difficultyLevel:
        filtered_phrases = [p for p in filtered_phrases if p["difficulty"] == difficultyLevel]

    # Filter by word count
    if minWords or maxWords:
        filtered_phrases = [
            p for p in filtered_phrases
            if (not minWords or len(p["phrase"].split()) >= minWords) and
               (not maxWords or len(p["phrase"].split()) <= maxWords)
        ]

    if not filtered_phrases:
        # Generate a random phrase if no matches
        phrase_data = random.choice(AI_PHRASES)
    else:
        phrase_data = random.choice(filtered_phrases)

    return {
        "phrase": phrase_data["phrase"],
        "englishTranslation": phrase_data["translation"],
        "category": phrase_data["category"],
        "difficultyLevel": phrase_data["difficulty"],
        "wordCount": len(phrase_data["phrase"].split())
    }


@app.get("/api/ai/gemini-phrase", response_model=AIPhrase)
def get_gemini_phrase(
    category: Optional[str] = Query(None),
    difficultyLevel: Optional[int] = Query(None, ge=1, le=5),
    minWords: Optional[int] = Query(None, ge=1),
    maxWords: Optional[int] = Query(None, ge=1)
):
    """
    Get Google Gemini-generated random Haitian Kreyòl phrase
    Query params:
    - category: Optional category for the phrase
    - difficultyLevel: Optional difficulty level (1-5)
    - minWords: Optional minimum word count
    - maxWords: Optional maximum word count
    """
    # For mock purposes, use the same implementation as random-phrase
    return get_ai_generated_phrase(category, difficultyLevel, minWords, maxWords)


# ============================================================================
# Proxy Endpoint
# ============================================================================

@app.get("/api/proxy-audio")
def proxy_audio(url: str = Query(...)):
    """
    Proxy audio files from Azure blob storage to handle CORS
    Query params:
    - url: The URL to proxy
    """
    # In a real implementation, this would fetch and stream the audio file
    # For mock purposes, return the original URL
    return {
        "message": "Audio proxy endpoint",
        "originalUrl": url,
        "note": "In production, this would stream the audio file"
    }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
