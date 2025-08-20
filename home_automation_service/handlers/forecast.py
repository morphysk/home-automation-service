from aiohttp import web
from ..services.forecast import WeatherForecastService
import logging
from aiohttp_cache import cache

logger = logging.getLogger(__name__)

# Create a single service instance to reuse across requests
_forecast_service = WeatherForecastService()


def _create_error_response(error_msg: str, status: int = 500) -> web.Response:
    return web.json_response(
        {"error": error_msg, "status": "error"}, 
        status=status
    )


def _create_success_response(data: dict) -> web.Response:
    return web.json_response({
        "status": "success",
        "data": data
    })


def _validate_days_parameter(days_str: str) -> tuple[int, str]:
    try:
        days = int(days_str)
        if days < 1 or days > 7:
            return 7, f"Days parameter {days} out of range (1-7), using default: 7"
        return days, ""
    except ValueError:
        return 7, f"Invalid days parameter '{days_str}', using default: 7"


def _parse_coordinates(coord_str: str) -> tuple[float, float, str]:
    try:
        if not coord_str or ',' not in coord_str:
            return 14.446, 49.922, "Invalid coordinates format, using default: 14.446,49.922"
        
        parts = coord_str.split(',')
        if len(parts) != 2:
            return 14.446, 49.922, "Invalid coordinates format, using default: 14.446,49.922"
        
        longitude = float(parts[0].strip())
        latitude = float(parts[1].strip())
        
        # Validate coordinate ranges
        if not (-180 <= longitude <= 180):
            return 14.446, 49.922, f"Longitude {longitude} out of range (-180 to 180), using default: 14.446"
        if not (-90 <= latitude <= 90):
            return 49.922, 49.922, f"Latitude {latitude} out of range (-90 to 90), using default: 49.922"
        
        return longitude, latitude, ""
    except ValueError:
        return 14.446, 49.922, f"Invalid coordinate values in '{coord_str}', using default: 14.446,49.922"


@cache(expires=1800)
async def get_forecast(request: web.Request) -> web.Response:
    try:
        # Check if this is a Loxone-style request
        user = request.query.get("user")
        coord = request.query.get("coord")
        asl = request.query.get("asl")
        format_type = request.query.get("format", "1")
        new_api = request.query.get("new_api", "0")
        
        # If Loxone-style parameters are present, handle them
        if user and coord:
            return await _handle_loxone_forecast(request, user, coord, asl, format_type, new_api)
        
        # Standard forecast request
        days_str = request.query.get("days", "7")
        days, warning = _validate_days_parameter(days_str)
        
        # Use default coordinates for standard requests
        forecast_data = _forecast_service.get_forecast(days=days)
        
        if not forecast_data:
            return _create_error_response("Failed to fetch forecast data", 500)
        
        response_data = {"forecast": forecast_data}
        if warning:
            response_data["warning"] = warning
            
        return _create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_forecast: {e}")
        return _create_error_response(f"Internal server error: {str(e)}", 500)


async def _handle_loxone_forecast(request: web.Request, user: str, coord: str, asl: str, format_type: str, new_api: str) -> web.Response:
    #Handle Loxone-style forecast requests with coordinate-specific data
    try:
        # Parse coordinates
        longitude, latitude, coord_warning = _parse_coordinates(coord)
        
        # Parse altitude
        altitude = 351  # default
        if asl:
            try:
                altitude = int(asl)
                if altitude < 0 or altitude > 10000:
                    altitude = 351
                    coord_warning += f" Altitude {asl} out of range (0-10000), using default: 351"
            except ValueError:
                coord_warning += f" Invalid altitude '{asl}', using default: 351"
        
        # Create a new forecast service with the specified coordinates
        from ..services.forecast import WeatherForecastService
        location_service = WeatherForecastService(latitude=latitude, longitude=longitude)
        
        # Get forecast data for the specified location
        forecast_data = location_service.get_forecast(days=7)
        
        if not forecast_data:
            return _create_error_response("Failed to fetch forecast data for specified location", 500)
        
        # Create Loxone-style response
        response_data = {
            "user": user,
            "coordinates": {
                "longitude": longitude,
                "latitude": latitude,
                "altitude": altitude
            },
            "format": format_type,
            "new_api": new_api,
            "forecast": forecast_data
        }
        
        if coord_warning:
            response_data["warning"] = coord_warning
            
        return _create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in _handle_loxone_forecast: {e}")
        return _create_error_response(f"Internal server error: {str(e)}", 500)


@cache(expires=900)  # 15 minutes for today's forecast
async def get_today_forecast(request: web.Request) -> web.Response:
    try:
        forecast_data = _forecast_service.get_today_forecast()
        
        if not forecast_data:
            return _create_error_response("No data available for today", 404)
            
        return _create_success_response({"today_forecast": forecast_data})
        
    except Exception as e:
        logger.error(f"Error in get_today_forecast: {e}")
        return _create_error_response(f"Internal server error: {str(e)}", 500)


@cache(expires=1800)  # 30 minutes for week forecast
async def get_week_forecast(request: web.Request) -> web.Response:
    try:
        forecast_data = _forecast_service.get_week_forecast()
        
        if not forecast_data:
            return _create_error_response("No data available for week forecast", 404)
            
        return _create_success_response({"week_forecast": forecast_data})
        
    except Exception as e:
        logger.error(f"Error in get_week_forecast: {e}")
        return _create_error_response(f"Internal server error: {str(e)}", 500)


@cache(expires=1800)  # 30 minutes for forecast summary
async def get_forecast_summary(request: web.Request) -> web.Response:
    try:
        forecast_data = _forecast_service.get_forecast_summary()
        
        if not forecast_data:
            return _create_error_response("No data available for forecast summary", 404)
            
        return _create_success_response({"forecast_summary": forecast_data})
        
    except Exception as e:
        logger.error(f"Error in get_forecast_summary: {e}")
        return _create_error_response(f"Internal server error: {str(e)}", 500)
