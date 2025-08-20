from aiohttp import web

from .handlers.health import health
from .handlers.weather import get_current_weather, get_historical_weather, get_weather_summary, get_outdoor_weather
from .handlers.forecast import get_forecast, get_today_forecast, get_week_forecast, get_forecast_summary
# from .handlers.loxone import get_loxone_weather


def setup_routes(app: web.Application) -> None:
    app.router.add_get("/health", health)
    
    # Weather endpoints
    app.router.add_get("/weather/current", get_current_weather)
    app.router.add_get("/weather/historical", get_historical_weather)
    app.router.add_get("/weather/summary", get_weather_summary)
    app.router.add_get("/weather/outdoor", get_outdoor_weather)
    
    # Forecast endpoints
    app.router.add_get("/forecast", get_forecast)
    app.router.add_get("/forecast/today", get_today_forecast)
    app.router.add_get("/forecast/week", get_week_forecast)
    app.router.add_get("/forecast/summary", get_forecast_summary)
    
    # Loxone weather endpoint (temporarily disabled)
    # app.router.add_get("/forecast/", get_loxone_weather)


