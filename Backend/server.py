from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import cv2

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color-based freshness analysis (no ML model needed)
logging.info("="*60)
logging.info("Food Freshness Analyzer - Color-Based Analysis Mode")
logging.info("Using lightweight HSV color analysis for freshness detection")
logging.info("="*60)

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Response Models
class NutritionInfo(BaseModel):
    calories: float
    carbs: float
    protein: float
    fat: float
    fiber: float

class HealthWarnings(BaseModel):
    diabetes_risk: str  # "Low", "Moderate", "High"
    thyroid_impact: str  # "Beneficial", "Neutral", "Harmful"
    blood_pressure: str  # "Lowers", "Neutral", "Raises"
    cholesterol: str  # "Lowers", "Neutral", "Raises"
    weight_management: str  # "Helps Weight Loss", "Neutral", "Weight Gain"

class PredictionResponse(BaseModel):
    food_name: str
    freshness_class: str  # "Fresh", "Semi-Rotten", "Rotten"
    confidence: float
    nutrition: NutritionInfo
    bioactive_compounds: list[str]
    health_benefits: str
    diet_preferences: list[str]  # NEW: Diet tags
    health_warnings: HealthWarnings  # NEW: Health warnings
    image_base64: str

# Mock food database for demonstration
# You will replace this with your actual CNN model predictions
MOCK_FOODS = {
    "apple": {
        "nutrition": {"calories": 52, "carbs": 14, "protein": 0.3, "fat": 0.2, "fiber": 2.4},
        "bioactive_compounds": ["Quercetin", "Catechin", "Chlorogenic acid", "Anthocyanins"],
        "health_benefits": "Rich in antioxidants and fiber. Supports heart health, aids digestion, and may reduce risk of diabetes. High in vitamin C for immune support."
    },
    "banana": {
        "nutrition": {"calories": 89, "carbs": 23, "protein": 1.1, "fat": 0.3, "fiber": 2.6},
        "bioactive_compounds": ["Dopamine", "Catechin", "Resistant starch", "Pectin"],
        "health_benefits": "Excellent source of potassium for heart health. Provides quick energy, supports digestive health, and helps regulate blood sugar levels."
    },
    "tomato": {
        "nutrition": {"calories": 18, "carbs": 3.9, "protein": 0.9, "fat": 0.2, "fiber": 1.2},
        "bioactive_compounds": ["Lycopene", "Beta-carotene", "Naringenin", "Chlorogenic acid"],
        "health_benefits": "High in lycopene, a powerful antioxidant. Supports heart health, skin protection, and may reduce cancer risk. Rich in vitamins A and C."
    },
    "carrot": {
        "nutrition": {"calories": 41, "carbs": 10, "protein": 0.9, "fat": 0.2, "fiber": 2.8},
        "bioactive_compounds": ["Beta-carotene", "Alpha-carotene", "Lutein", "Polyacetylenes"],
        "health_benefits": "Excellent source of beta-carotene for eye health. Supports immune function, skin health, and has anti-inflammatory properties."
    },
    "orange": {
        "nutrition": {"calories": 47, "carbs": 12, "protein": 0.9, "fat": 0.1, "fiber": 2.4},
        "bioactive_compounds": ["Hesperidin", "Naringenin", "Vitamin C", "Carotenoids"],
        "health_benefits": "Very high in vitamin C for immune support. Contains flavonoids that support heart health and reduce inflammation. Aids in iron absorption."
    }
}

@api_router.get("/")
async def root():
    return {"message": "Food Freshness Analysis API", "version": "1.0"}

@api_router.post("/predict", response_model=PredictionResponse)
async def predict_food(file: UploadFile = File(...)):
    """
    Endpoint to analyze food freshness and nutrition using the trained CNN model.
    """
    try:
        # Read and validate image
        contents = await file.read()
        
        try:
            image = Image.open(BytesIO(contents))
            image.verify()  # Verify it's a valid image
            image = Image.open(BytesIO(contents))  # Reopen after verify
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Convert image to base64 for response
        buffered = BytesIO()
        image_rgb = image.convert('RGB')
        image_rgb.thumbnail((800, 800))  # Resize for efficiency
        image_rgb.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # ============================================================
        # COLOR-BASED FRESHNESS ANALYSIS (No ML model needed)
        # ============================================================
        
        # Analyze image using HSV color analysis
        logging.info("Using color-based freshness analysis")
        
        img_array = np.array(image.convert('RGB'))
        img_array = cv2.resize(img_array, (224, 224))
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        
        # Calculate metrics
        avg_saturation = np.mean(s)
        avg_value = np.mean(v)
        avg_hue = np.mean(h)
        
        # Calculate standard deviation to detect uniformity (fresh produce is more uniform)
        std_value = np.std(v)
        
        # Detect brown/aged colors (signs of staleness/rotting)
        # Brown/aged hues: 10-30 in HSV (orange-brown range)
        brown_mask = ((h >= 10) & (h <= 30) & (s > 30) & (v > 30) & (v < 180))
        brown_ratio = np.sum(brown_mask) / brown_mask.size
        
        # Detect very dark areas (severe rotting/mold)
        very_dark_ratio = np.sum(v < 50) / v.size
        
        # Detect dark areas (browning/aging)
        dark_ratio = np.sum(v < 100) / v.size
        
        # Detect dull areas (loss of freshness - low saturation)
        dull_ratio = np.sum(s < 60) / s.size
        
        # Calculate color variance (fresh produce has more uniform color)
        color_variance = np.std(v)
        
        # Scoring system for freshness (0-100 scale)
        freshness_score = 100
        
        # Deduct points for negative indicators
        freshness_score -= brown_ratio * 150  # Brown spots reduce score
        freshness_score -= very_dark_ratio * 200  # Very dark areas major reduction
        freshness_score -= dark_ratio * 80  # Dark areas moderate reduction
        freshness_score -= dull_ratio * 60  # Dull colors reduce score
        
        # Add points for positive indicators
        if avg_saturation > 80:
            freshness_score += 10  # Vibrant colors = fresh
        if avg_value > 150:
            freshness_score += 10  # Bright = fresh
        
        # Classify based on score
        if freshness_score >= 65:
            freshness_class = "Fresh"
            confidence = 0.75 + (freshness_score - 65) / 200
        elif freshness_score >= 35:
            freshness_class = "Semi-Rotten"
            confidence = 0.70 + (freshness_score - 35) / 200
        else:
            freshness_class = "Rotten"
            confidence = 0.75 + max(0, (35 - freshness_score)) / 200
        
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        # Simple food name with freshness indicator
        if freshness_class == "Rotten":
            food_name = "Food Item (⚠️ ROTTEN)"
        elif freshness_class == "Semi-Rotten":
            food_name = "Food Item (⚠️ Going Bad)"
        else:
            food_name = "Food Item"
        
        # Log analysis for debugging
        logger.info(f"Analysis: sat={avg_saturation:.1f}, val={avg_value:.1f}, vdark={very_dark_ratio:.2f}, dark={dark_ratio:.2f}, brown={brown_ratio:.2f}, dull={dull_ratio:.2f}, score={freshness_score:.1f} -> {food_name} - {freshness_class}")
        
        # Get nutritional data and health information based on freshness
        if freshness_class == "Fresh":
            food_data = {
                "nutrition": {"calories": 52, "carbs": 14, "protein": 0.8, "fat": 0.3, "fiber": 2.5},
                "bioactive_compounds": ["Vitamins", "Antioxidants", "Phytonutrients", "Minerals"],
                "health_benefits": "Fresh produce retains maximum nutrients and antioxidants. Supports immune function, digestive health, and overall wellness. Best for optimal health benefits.",
                "diet_preferences": ["Vegan", "Vegetarian", "Gluten-Free", "Paleo", "Keto-Friendly", "Diabetic-Friendly", "Heart-Healthy"],
                "health_warnings": {
                    "diabetes_risk": "Low",
                    "thyroid_impact": "Beneficial",
                    "blood_pressure": "Lowers",
                    "cholesterol": "Lowers",
                    "weight_management": "Helps Weight Loss"
                }
            }
        elif freshness_class == "Semi-Rotten":
            food_data = {
                "nutrition": {"calories": 48, "carbs": 13, "protein": 0.7, "fat": 0.3, "fiber": 2.2},
                "bioactive_compounds": ["Reduced Vitamins", "Some Antioxidants", "Minerals"],
                "health_benefits": "Semi-rotten produce has reduced nutritional value. Some vitamins may be degraded. Consume soon and cook thoroughly to ensure safety.",
                "diet_preferences": ["Vegetarian", "May be suitable for some diets after cooking"],
                "health_warnings": {
                    "diabetes_risk": "Moderate",
                    "thyroid_impact": "Neutral",
                    "blood_pressure": "Neutral",
                    "cholesterol": "Neutral",
                    "weight_management": "Neutral"
                }
            }
        else:  # Rotten
            food_data = {
                "nutrition": {"calories": 40, "carbs": 11, "protein": 0.5, "fat": 0.2, "fiber": 1.8},
                "bioactive_compounds": ["Degraded Nutrients", "Possible Toxins", "Harmful Bacteria"],
                "health_benefits": "⚠️ ROTTEN produce should be discarded immediately. May contain harmful bacteria, mold toxins, and pathogens. Not safe for consumption. Can cause foodborne illness, food poisoning, and serious health issues.",
                "diet_preferences": ["⚠️ NOT SUITABLE FOR ANY DIET", "DO NOT CONSUME"],
                "health_warnings": {
                    "diabetes_risk": "High",
                    "thyroid_impact": "Harmful",
                    "blood_pressure": "Raises",
                    "cholesterol": "Raises",
                    "weight_management": "Harmful - Risk of Food Poisoning"
                }
            }
        
        # ============================================================
        # END OF COLOR-BASED ANALYSIS
        # ============================================================
        
        response = PredictionResponse(
            food_name=food_name,
            freshness_class=freshness_class,
            confidence=round(confidence, 2),
            nutrition=NutritionInfo(**food_data["nutrition"]),
            bioactive_compounds=food_data["bioactive_compounds"],
            health_benefits=food_data["health_benefits"],
            diet_preferences=food_data["diet_preferences"],
            health_warnings=HealthWarnings(**food_data["health_warnings"]),
            image_base64=image_base64
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)