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

# API Metadata for Swagger Documentation
app = FastAPI(
    title="Palefò Mock API",
    description="""
## Palefò API - Haitian Kreyòl Language Learning Platform

This API provides endpoints for managing Haitian Kreyòl sentences, contributions, and statistics.

### Features

* **Sentences**: Retrieve random sentences, filter by category or difficulty
* **Contributions**: Submit and manage audio contributions
* **Statistics**: Get platform usage statistics
* **Contributors**: View top contributors leaderboard
* **AI Integration**: Generate random phrases using AI

### Authentication

Some endpoints require admin authentication for moderation purposes.

### Rate Limiting

Currently no rate limiting is applied to this mock API.
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "Palefò Support",
        "url": "https://example.com/support",
        "email": "support@palefo.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "root",
            "description": "Root endpoints and API information",
        },
        {
            "name": "sentences",
            "description": "Operations with Haitian Kreyòl sentences. Retrieve sentences by various criteria.",
        },
        {
            "name": "statistics",
            "description": "Platform statistics including total contributions and contributors.",
        },
        {
            "name": "contributors",
            "description": "Manage and retrieve contributor information and rankings.",
        },
        {
            "name": "contributions",
            "description": "Submit and manage audio contributions. Includes moderation endpoints.",
        },
        {
            "name": "ai",
            "description": "AI-powered phrase generation using various models.",
        },
        {
            "name": "proxy",
            "description": "Proxy endpoints for handling CORS and external resources.",
        },
    ],
)

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
    {
        "id": 9,
        "kreyolText": "Imilyasyon se lanfe.",
        "englishTranslation": "Humiliation is hell.",
        "category": "proverb",
        "difficultyLevel": 2,
        "audioUrl": "https://example.blob.core.windows.net/audio/8.mp3"
    },
        {
        "id": 10,
        "kreyolText": "Gwo bounda pa vle di la sante.",
        "englishTranslation": "Big buttocks do not mean health.",
        "category": "proverb",
        "difficultyLevel": 2,
        "audioUrl": "https://example.blob.core.windows.net/audio/8.mp3"
    },
        {
        "id": 11,
        "kreyolText": "Le mwen rive sou portay jendarm arete mwen",
        "englishTranslation": "When I arrive at the gate, the police officer arrested me.",
        "category": "everyday",
        "difficultyLevel": 2,
        "audioUrl": "https://example.blob.core.windows.net/audio/8.mp3"
    },
        {
        "id": 12,
        "kreyolText": "Neg filo yo fe yon bel gala pou jen yo.",
        "englishTranslation": "The 12th graders threw a beautiful spectacle for the youth.",
        "category": "everyday",
        "difficultyLevel": 2,
        "audioUrl": "https://example.blob.core.windows.net/audio/8.mp3"
    },
    {
        "id": 13,
        "kreyolText": "Papa w se papa w, papa m pa papa w.",
        "englishTranslation": "Your father is your father, my father is not your father.",
        "category": "tongue-twister",
        "difficultyLevel": 2,
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

@app.get("/", tags=["root"])
def read_root():
    """
    # Welcome to Palefò Mock API

    Returns basic API information and available endpoint categories.

    **Access the interactive API documentation at:**
    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    """
    return {
        "message": "Welcome to Palefò Mock API",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
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

@app.get("/api/sentences/random", tags=["sentences"])
def get_random_sentences(
    count: int = Query(1, ge=1, le=50, description="Number of random sentences to retrieve"),
    excludeIds: Optional[str] = Query(None, description="Comma-separated list of sentence IDs to exclude")
):
    """
    ## Get Random Sentences

    Retrieve random Haitian Kreyòl sentences for language practice.

    **Parameters:**
    - **count**: Number of sentences to retrieve (default: 1, max: 50)
    - **excludeIds**: Optional comma-separated list of sentence IDs to exclude from results

    **Returns:** Array of sentence objects with Kreyòl text, English translation, and audio URLs
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


@app.get("/api/sentences/category/{category}", tags=["sentences"])
def get_sentences_by_category(
    category: str = Path(..., description="Category name (e.g., greetings, food, education)"),
    count: int = Query(1, ge=1, le=50, description="Number of sentences to retrieve")
):
    """
    ## Get Sentences by Category

    Retrieve sentences filtered by a specific category.

    **Available categories:** greetings, food, education, weather, society, family, technology

    **Returns:** Array of sentences matching the specified category
    """
    filtered_sentences = [s for s in MOCK_SENTENCES if s.get("category") == category]

    if not filtered_sentences:
        return []

    selected_count = min(count, len(filtered_sentences))
    return random.sample(filtered_sentences, selected_count)


@app.get("/api/sentences/category-simple/{category}", tags=["sentences"])
def get_sentences_by_category_simple(
    category: str = Path(..., description="Category name"),
    count: int = Query(1, ge=1, le=50, description="Number of sentences to retrieve")
):
    """
    ## Get Sentences by Category (Simple Query)

    Alternative endpoint using simple query instead of stored procedures.
    Provides the same functionality as the standard category endpoint.
    """
    # Same implementation as category endpoint for mock purposes
    return get_sentences_by_category(category, count)


@app.get("/api/sentences/difficulty/{level}", tags=["sentences"])
def get_sentences_by_difficulty(
    level: int = Path(..., ge=1, le=5, description="Difficulty level from 1 (easiest) to 5 (hardest)"),
    count: int = Query(1, ge=1, le=50, description="Number of sentences to retrieve")
):
    """
    ## Get Sentences by Difficulty Level

    Retrieve sentences filtered by difficulty level for progressive learning.

    **Difficulty Levels:**
    - **1**: Beginner - Basic greetings and simple phrases
    - **2**: Elementary - Common expressions
    - **3**: Intermediate - More complex sentences
    - **4**: Advanced - Complex grammar and vocabulary
    - **5**: Expert - Specialized or technical language
    """
    filtered_sentences = [s for s in MOCK_SENTENCES if s["difficultyLevel"] == level]

    if not filtered_sentences:
        return []

    selected_count = min(count, len(filtered_sentences))
    return random.sample(filtered_sentences, selected_count)


# ============================================================================
# Statistics Endpoint
# ============================================================================

@app.get("/api/statistics", response_model=Statistics, tags=["statistics"])
def get_statistics():
    """
    ## Get Platform Statistics

    Retrieve overall platform usage statistics.

    **Returns:**
    - **totalContributions**: Total number of audio contributions submitted
    - **uniqueContributors**: Number of unique contributors to the platform
    - **totalAudioHours**: Total hours of audio recordings collected

    These statistics help track the platform's growth and community engagement.
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

@app.get("/api/contributors/top", response_model=List[Contributor], tags=["contributors"])
def get_top_contributors(
    limit: int = Query(10, ge=1, le=100, description="Number of top contributors to retrieve")
):
    """
    ## Get Top Contributors Leaderboard

    Retrieve the top contributors ranked by contribution count.

    This endpoint is useful for displaying leaderboards and recognizing
    active community members who have contributed the most audio recordings.

    **Parameters:**
    - **limit**: Maximum number of contributors to return (default: 10, max: 100)

    **Returns:** List of contributors with their rank, email, and contribution count
    """
    return MOCK_CONTRIBUTORS[:limit]


# ============================================================================
# Contributions Endpoints
# ============================================================================

@app.post("/api/contributions", tags=["contributions"])
async def submit_contribution(
    KreyòlText: str = Form(..., description="The Haitian Kreyòl text to be recorded"),
    AudioFile: UploadFile = File(..., description="Audio recording file (mp3, wav, webm, or m4a)"),
    Email: Optional[str] = Form(None, description="Contributor's email address (optional)"),
    Gender: Optional[str] = Form(None, description="Gender (optional): male, female, or other"),
    Region: Optional[str] = Form(None, description="Region in Haiti (optional)")
):
    """
    ## Submit New Audio Contribution

    Upload a new audio contribution with the corresponding Kreyòl text.

    **Form Data:**
    - **KreyòlText** *(required)*: The Haitian Kreyòl text being recorded
    - **AudioFile** *(required)*: Audio file in mp3, wav, webm, or m4a format
    - **Email** *(optional)*: Contributor's email for tracking and prizes
    - **Gender** *(optional)*: Gender selection for demographic data
    - **Region** *(optional)*: Region in Haiti for accent diversity

    **Returns:** The created contribution object with a unique ID

    **Note:** Contributions are pending approval by default and require moderation.
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


@app.get("/api/contributions", response_model=ContributionList, tags=["contributions"])
def get_contributions(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    pageSize: int = Query(20, ge=1, le=100, description="Number of items per page"),
    includeUnapproved: bool = Query(False, description="Include unapproved contributions (admin only)")
):
    """
    ## Get Contributions List

    Retrieve a paginated list of audio contributions.

    **Query Parameters:**
    - **page**: Page number, starting at 1
    - **pageSize**: Number of items per page (max: 100)
    - **includeUnapproved**: Set to true to include pending/rejected contributions (requires admin access)

    **Returns:** Paginated list with contribution items and pagination metadata

    By default, only approved contributions are returned to public users.
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


@app.get("/api/contributions/{id}", response_model=Contribution, tags=["contributions"])
def get_contribution_by_id(
    id: int = Path(..., ge=1, description="Unique contribution ID")
):
    """
    ## Get Contribution by ID

    Retrieve a specific contribution by its unique identifier.

    **Path Parameters:**
    - **id**: The unique ID of the contribution

    **Returns:** Contribution object with all details including audio URL and text
    """
    contribution = next((c for c in MOCK_CONTRIBUTIONS if c["id"] == id), None)

    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    return contribution


@app.patch("/api/contributions/{id}/approval", tags=["contributions"])
def moderate_contribution(
    id: int = Path(..., ge=1, description="Contribution ID to moderate"),
    moderation: ModerationRequest = None
):
    """
    ## Moderate Contribution (Admin Only)

    Approve or reject a pending contribution.

    **Path Parameters:**
    - **id**: The unique ID of the contribution to moderate

    **Request Body:**
    - **approved**: Boolean - true to approve, false to reject
    - **rejectionReason**: String - Required when rejecting, explains why the contribution was rejected

    **Common rejection reasons:**
    - Poor audio quality
    - Background noise
    - Incorrect pronunciation
    - Text doesn't match audio
    - Inappropriate content

    **Returns:** Updated contribution object with new approval status
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


@app.get("/api/ai/random-phrase", response_model=AIPhrase, tags=["ai"])
def get_ai_generated_phrase(
    category: Optional[str] = Query(None, description="Filter by category (e.g., emotions, education, family)"),
    difficultyLevel: Optional[int] = Query(None, ge=1, le=5, description="Difficulty level (1-5)"),
    minWords: Optional[int] = Query(None, ge=1, description="Minimum number of words"),
    maxWords: Optional[int] = Query(None, ge=1, description="Maximum number of words")
):
    """
    ## Generate AI Random Phrase

    Get an AI-generated random Haitian Kreyòl phrase with English translation.

    **Query Parameters (all optional):**
    - **category**: Filter by category (emotions, education, family, work, society)
    - **difficultyLevel**: Difficulty level from 1 (easiest) to 5 (hardest)
    - **minWords**: Minimum number of words in the phrase
    - **maxWords**: Maximum number of words in the phrase

    **Returns:** Generated phrase with translation, category, difficulty level, and word count

    Useful for generating practice content and expanding the learning material.
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


@app.get("/api/ai/gemini-phrase", response_model=AIPhrase, tags=["ai"])
def get_gemini_phrase(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficultyLevel: Optional[int] = Query(None, ge=1, le=5, description="Difficulty level (1-5)"),
    minWords: Optional[int] = Query(None, ge=1, description="Minimum number of words"),
    maxWords: Optional[int] = Query(None, ge=1, description="Maximum number of words")
):
    """
    ## Generate Gemini AI Phrase

    Get a Google Gemini-generated Haitian Kreyòl phrase with English translation.

    This endpoint specifically uses Google's Gemini AI model for phrase generation.
    Parameters and functionality are the same as the standard AI phrase endpoint.

    **Query Parameters (all optional):**
    - **category**: Filter by category
    - **difficultyLevel**: Difficulty level (1-5)
    - **minWords**: Minimum word count
    - **maxWords**: Maximum word count
    """
    # For mock purposes, use the same implementation as random-phrase
    return get_ai_generated_phrase(category, difficultyLevel, minWords, maxWords)


# ============================================================================
# Proxy Endpoint
# ============================================================================

@app.get("/api/proxy-audio", tags=["proxy"])
def proxy_audio(
    url: str = Query(..., description="URL of the audio file to proxy")
):
    """
    ## Proxy Audio Files

    Proxy audio files from Azure blob storage to handle CORS restrictions.

    **Query Parameters:**
    - **url**: The full URL of the audio file to proxy

    **Purpose:**
    This endpoint helps bypass CORS (Cross-Origin Resource Sharing) restrictions
    when accessing audio files stored in Azure blob storage or other external services.

    **Note:** In production, this endpoint would fetch and stream the actual audio file.
    In this mock version, it returns information about the proxy request.
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
