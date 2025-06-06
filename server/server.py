# server.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from model import Model
import os
from collections import defaultdict

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация rate limiting
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))  # Макс. запросов в минуту
RATE_LIMIT_WINDOW = 60  # Окно времени в секундах (1 минута)
BAN_TIME = 3600  # Время бана в секундах (1 час)

# Инициализация модели
MODEL_PATH = os.getenv("MODEL_PATH", "improved_discount_model.joblib")
model = Model(model_path=MODEL_PATH)
model.load()

# Хранилище для rate limiting
request_counts = defaultdict(int)
ban_list = {}
last_reset = datetime.now()

# Модели данных


class PriceEntry(BaseModel):
    x: str  # Дата в формате 'YYYY-MM-DD'
    y: float  # Цена со скидкой
    d: float  # Процент скидки
    is_sale: int  # Флаг распродажи


class PredictionRequest(BaseModel):
    price_history: List[PriceEntry]


class PredictionResponse(BaseModel):
    request_id: str
    prediction: str
    probability: str
    is_fake: bool
    features: Dict[str, float]


class RateLimitResponse(BaseModel):
    detail: str
    retry_after: int


# Инициализация FastAPI
app = FastAPI(
    title="Fake Discount Detection API",
    description="API для определения фейковых скидок на основе истории цен",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def check_rate_limit(request: Request):
    global last_reset, request_counts, ban_list

    client_ip = request.client.host

    # Сброс счетчиков раз в минуту
    if (datetime.now() - last_reset).total_seconds() > RATE_LIMIT_WINDOW:
        request_counts.clear()
        last_reset = datetime.now()

    # Проверка бана
    if client_ip in ban_list:
        if (datetime.now() - ban_list[client_ip]).total_seconds() < BAN_TIME:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Try again after {BAN_TIME} seconds",
                headers={"Retry-After": str(BAN_TIME)}
            )
        else:
            del ban_list[client_ip]

    # Увеличение счетчика запросов
    request_counts[client_ip] += 1

    # Проверка превышения лимита
    if request_counts[client_ip] > RATE_LIMIT:
        ban_list[client_ip] = datetime.now()
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. You are banned for {BAN_TIME} seconds",
            headers={"Retry-After": str(BAN_TIME)}
        )


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Fake Discount Detection API")
    if not model.loaded:
        logger.error("Model failed to load on startup")
        raise RuntimeError("Model failed to load")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model.loaded}


@app.post("/predict",
          response_model=PredictionResponse,
          responses={
              429: {
                  "model": RateLimitResponse,
                  "description": "Rate limit exceeded"
              }
          })
async def predict(
    request: PredictionRequest,
    request_info: Request
):
    request_id = str(uuid.uuid4())
    client_ip = request_info.client.host

    # Проверка rate limit
    await check_rate_limit(request_info)

    logger.info(f"Request {request_id} from IP {client_ip} started processing")

    try:
        # Преобразуем входные данные
        price_history = [
            {
                'x': entry.x,
                'y': entry.y,
                'd': entry.d,
                'is_sale': entry.is_sale
            }
            for entry in request.price_history
        ]

        # Выполняем предсказание
        result = model.predict(price_history)

        # Формируем ответ
        response = {
            "request_id": request_id,
            "prediction": result['prediction'],
            "probability": result['probability'],
            "is_fake": result['is_fake'],
            "features": result['features']
        }

        logger.info(f"Request {request_id} completed successfully")
        return response

    except Exception as e:
        logger.error(f"Request {request_id} failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Prediction failed: {str(e)}"
        )

# Эндпоинт для тестирования rate limit


@app.get("/rate_limit_test")
async def rate_limit_test(request: Request):
    await check_rate_limit(request)
    return {"message": "OK", "your_ip": request.client.host}


# uvicorn server:app --host 0.0.0.0 --port 7123 --workers 4
