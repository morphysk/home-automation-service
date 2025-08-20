import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class NetatmoService:
    """Service for interacting with Netatmo Weather Station API using token-based authentication"""
    
    def __init__(self):
        self.client_id = os.getenv("NETATMO_CLIENT_ID")
        self.client_secret = os.getenv("NETATMO_CLIENT_SECRET")
        self.access_token = os.getenv("NETATMO_ACCESS_TOKEN")
        self.refresh_token = os.getenv("NETATMO_REFRESH_TOKEN")
        
        if not all([self.client_id, self.client_secret, self.access_token, self.refresh_token]):
            logger.warning("Netatmo token credentials not fully configured. Some features may not work.")
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
            
        try:
            auth_url = "https://api.netatmo.com/oauth2/token"
            auth_data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(auth_url, data=auth_data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            
            logger.info("Successfully refreshed Netatmo access token")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed: {e}")
            return False
    
    def get_stations_data(self) -> Optional[Dict]:
        """Get current data from all weather stations"""
        if not self.access_token:
            logger.error("No access token available")
            return None
        
        try:
            url = "https://api.netatmo.com/api/getstationsdata"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                # Token expired, try to refresh
                if self.refresh_access_token():
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    response = requests.get(url, headers=headers)
                else:
                    return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get stations data: {e}")
            return None
    
    def get_measurements(self, device_id: str, module_id: str = None, 
                        scale: str = "1hour", type_list: List[str] = None) -> Optional[Dict]:
        """Get historical measurements for a specific device/module"""
        if not self.access_token:
            logger.error("No access token available")
            return None
        
        if type_list is None:
            type_list = ["Temperature", "Humidity", "Pressure", "CO2", "Noise"]
        
        try:
            url = "https://api.netatmo.com/api/getmeasure"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Calculate time range for current day
            now = datetime.now()
            start_date = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            end_date = int(now.timestamp())
            
            params = {
                "device_id": device_id,
                "scale": scale,
                "type": ",".join(type_list),
                "date_begin": start_date,
                "date_end": end_date,
                "optimize": "false"
            }
            
            if module_id:
                params["module_id"] = module_id
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 401:
                # Token expired, try to refresh
                if self.refresh_access_token():
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    response = requests.get(url, headers=headers, params=params)
                else:
                    return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get measurements: {e}")
            return None
    
    def get_outdoor_weather_data(self) -> Dict:
        """Get outdoor weather data including wind, rain, temperature, and pressure"""
        result = {
            "outdoor": None,
            "wind": None,
            "rain": None,
            "error": None
        }
        
        # Get current station data
        stations_data = self.get_stations_data()
        if not stations_data:
            result["error"] = "Failed to get current station data"
            return result
        
        try:
            devices = stations_data.get("body", {}).get("devices", [])
            if not devices:
                result["error"] = "No weather stations found"
                return result
            
            device = devices[0]  # Get first device
            device_id = device.get("_id")
            
            # Extract outdoor data from modules
            outdoor_data = {}
            wind_data = {}
            rain_data = {}
            
            for module in device.get("modules", []):
                module_type = module.get("type")
                module_name = module.get("module_name", "Unknown")
                dashboard_data = module.get("dashboard_data", {})
                
                if module_type == "NAModule1":  # Outdoor module
                    outdoor_data = {
                        "module_id": module.get("_id"),
                        "module_name": module_name,
                        "module_type": module_type,
                        "temperature": dashboard_data.get("Temperature"),
                        "humidity": dashboard_data.get("Humidity"),
                        "last_update": dashboard_data.get("time_utc"),
                        "dashboard_data": dashboard_data
                    }
                
                elif module_type == "NAModule2":  # Wind module
                    wind_data = {
                        "module_id": module.get("_id"),
                        "module_name": module_name,
                        "module_type": module_type,
                        "wind_strength": dashboard_data.get("WindStrength"),
                        "wind_angle": dashboard_data.get("WindAngle"),
                        "gust_strength": dashboard_data.get("GustStrength"),
                        "gust_angle": dashboard_data.get("GustAngle"),
                        "last_update": dashboard_data.get("time_utc"),
                        "dashboard_data": dashboard_data
                    }
                
                elif module_type == "NAModule3":  # Rain module
                    rain_data = {
                        "module_id": module.get("_id"),
                        "module_name": module_name,
                        "module_type": module_type,
                        "rain": dashboard_data.get("Rain"),
                        "rain_1h": dashboard_data.get("sum_rain_1h"),
                        "rain_24h": dashboard_data.get("sum_rain_24h"),
                        "last_update": dashboard_data.get("time_utc"),
                        "dashboard_data": dashboard_data
                    }
            
            # Get main station pressure data
            main_dashboard = device.get("dashboard_data", {})
            if main_dashboard.get("Pressure"):
                outdoor_data["pressure"] = main_dashboard.get("Pressure")
                outdoor_data["pressure_trend"] = main_dashboard.get("pressure_trend")
            
            result["outdoor"] = outdoor_data
            result["wind"] = wind_data
            result["rain"] = rain_data
            
        except Exception as e:
            logger.error(f"Error processing outdoor weather data: {e}")
            result["error"] = f"Error processing data: {str(e)}"
        
        return result
    
    def get_current_day_data(self) -> Dict:
        """Get current and historical data for the current day"""
        result = {
            "current": None,
            "historical": None,
            "outdoor": None,
            "error": None
        }
        
        # Get current station data
        stations_data = self.get_stations_data()
        if not stations_data:
            result["error"] = "Failed to get current station data"
            return result
        
        try:
            # Extract current data
            devices = stations_data.get("body", {}).get("devices", [])
            if devices:
                device = devices[0]  # Get first device
                device_id = device.get("_id")
                
                # Current data from main device
                current_data = {
                    "device_id": device_id,
                    "device_name": device.get("station_name", "Unknown"),
                    "location": {
                        "latitude": device.get("place", {}).get("location", [0, 0])[0],
                        "longitude": device.get("place", {}).get("location", [0, 0])[1],
                        "altitude": device.get("place", {}).get("altitude", 0)
                    },
                    "dashboard_data": device.get("dashboard_data", {}),
                    "modules": []
                }
                
                # Add module data
                for module in device.get("modules", []):
                    module_data = {
                        "module_id": module.get("_id"),
                        "module_name": module.get("module_name", "Unknown"),
                        "module_type": module.get("type"),
                        "dashboard_data": module.get("dashboard_data", {})
                    }
                    current_data["modules"].append(module_data)
                
                result["current"] = current_data
                
                # Get outdoor weather data
                outdoor_result = self.get_outdoor_weather_data()
                if not outdoor_result.get("error"):
                    result["outdoor"] = {
                        "outdoor": outdoor_result.get("outdoor"),
                        "wind": outdoor_result.get("wind"),
                        "rain": outdoor_result.get("rain")
                    }
                
                # Get historical data for the main device
                if device_id:
                    historical_data = self.get_measurements(device_id)
                    if historical_data:
                        result["historical"] = historical_data
                    
                    # Get historical data for modules
                    for module in device.get("modules", []):
                        module_id = module.get("_id")
                        if module_id:
                            module_history = self.get_measurements(device_id, module_id)
                            if module_history and result["historical"]:
                                # Ensure historical body is a list
                                if "body" not in result["historical"]:
                                    result["historical"]["body"] = []
                                elif not isinstance(result["historical"]["body"], list):
                                    # Convert to list if it's not already
                                    result["historical"]["body"] = [result["historical"]["body"]]
                                
                                # Handle module history data
                                module_body = module_history.get("body")
                                if isinstance(module_body, list):
                                    result["historical"]["body"].extend(module_body)
                                elif isinstance(module_body, dict):
                                    result["historical"]["body"].append(module_body)
            
        except Exception as e:
            logger.error(f"Error processing station data: {e}")
            result["error"] = f"Error processing data: {str(e)}"
        
        return result
