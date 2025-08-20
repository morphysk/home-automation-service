from aiohttp import web
from ..services.netatmo import NetatmoService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def get_current_weather(request: web.Request) -> web.Response:
    try:
        netatmo = NetatmoService()
        data = netatmo.get_current_day_data()
        
        if data.get("error"):
            return web.json_response(
                {"error": data["error"]}, 
                status=500
            )
        
        return web.json_response({
            "status": "success",
            "data": {
                "current": data["current"],
                "timestamp": data["current"]["dashboard_data"].get("time_utc") if data["current"] else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        return web.json_response(
            {"error": f"Internal server error: {str(e)}"}, 
            status=500
        )


async def get_historical_weather(request: web.Request) -> web.Response:
    try:
        netatmo = NetatmoService()
        data = netatmo.get_current_day_data()
        
        if data.get("error"):
            return web.json_response(
                {"error": data["error"]}, 
                status=500
            )
        
        return web.json_response({
            "status": "success",
            "data": {
                "historical": data["historical"],
                "timestamp": data["current"]["dashboard_data"].get("time_utc") if data["current"] else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting historical weather: {e}")
        return web.json_response(
            {"error": f"Internal server error: {str(e)}"}, 
            status=500
        )


async def get_weather_summary(request: web.Request) -> web.Response:
    try:
        netatmo = NetatmoService()
        data = netatmo.get_current_day_data()
        
        if data.get("error"):
            return web.json_response(
                {"error": data["error"]}, 
                status=500
            )
        
        return web.json_response({
            "status": "success",
            "data": {
                "current": data["current"],
                "historical": data["historical"],
                "timestamp": data["current"]["dashboard_data"].get("time_utc") if data["current"] else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting weather summary: {e}")
        return web.json_response(
            {"error": f"Internal server error: {str(e)}"}, 
            status=500
        )


async def get_outdoor_weather(request: web.Request) -> web.Response:
    try:
        netatmo = NetatmoService()
        outdoor_data = netatmo.get_outdoor_weather_data()
        
        if outdoor_data.get("error"):
            return web.json_response(
                {"error": outdoor_data["error"]}, 
                status=500
            )
        
        return web.json_response({
            "status": "success",
            "data": {
                "outdoor": outdoor_data["outdoor"],
                "wind": outdoor_data["wind"],
                "rain": outdoor_data["rain"]
            },
            "timestamp": datetime.now().timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error getting outdoor weather: {e}")
        return web.json_response(
            {"error": f"Internal server error: {str(e)}"}, 
            status=500
        )
