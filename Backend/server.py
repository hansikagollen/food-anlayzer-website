from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from PIL import Image
import io

app = FastAPI()

# CORS (important for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = load_model("model/food_freshness_model.h5")

# Class labels (same as training)
classes = ["fresh", "semi_rotten", "stale"]

# Preprocessing
def preprocess(image):
    image = image.resize((224, 224))
    image = np.array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)
    return image

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    img = preprocess(image)

    pred = model.predict(img)[0]   # get array like [0.2, 0.5, 0.3]
    idx = np.argmax(pred)

    confidence = float(pred[idx])

    # 🔥 THRESHOLD LOGIC
    # If semi_rotten probability is reasonably high, prefer it
    if pred[1] > 0.35:   # semi_rotten index = 1
        result = "semi_rotten"
        confidence = float(pred[1])
    else:
        result = classes[idx]

    return {
        "freshness_class": result,
        "confidence": confidence
    }

@app.get("/")
def home():
    return {"message": "Food Freshness API is running 🚀"}