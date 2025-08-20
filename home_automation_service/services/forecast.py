import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class WeatherForecastService:
    
    def __init__(self, latitude: float = 49.922, longitude: float = 14.446, timezone: str = "Europe/Berlin"):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.df = None  # Main pandas DataFrame
        
        # Weather code descriptions
        self.weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
    
    def get_forecast(self, days: int = 7) -> Optional[Dict]:
        try:
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "daily": "sunrise,sunset",
                "hourly": "temperature_2m,relative_humidity_2m,weather_code,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,wind_gusts_10m,wind_direction_10m,rain,showers,snowfall,precipitation,precipitation_probability,surface_pressure,cloud_cover,apparent_temperature",
                "timezone": self.timezone
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            forecast_data = response.json()
            return self._process_forecast_data(forecast_data, days)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch forecast: {e}")
            return None
    
    def _process_forecast_data(self, raw_data: Dict, days: int) -> Dict:
        try:
            # Create pandas DataFrame from hourly data
            self.df = self._create_dataframe(raw_data.get("hourly", {}))
            
            # Process daily data
            daily_data = self._process_daily_data(raw_data.get("daily", {}), days)
            
            # Get current conditions
            current_conditions = self._get_current_conditions()
            
            # Get processed hourly data
            processed_hourly = self._get_hourly_data(days)
            
            return {
                "location": {
                    "latitude": raw_data.get("latitude"),
                    "longitude": raw_data.get("longitude"),
                    "elevation": raw_data.get("elevation"),
                    "timezone": raw_data.get("timezone")
                },
                "current": current_conditions,
                "hourly": processed_hourly,
                "daily": daily_data,
                "units": raw_data.get("hourly_units", {}),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
            return {"error": f"Error processing forecast data: {str(e)}"}
    
    def _create_dataframe(self, hourly_data: Dict) -> pd.DataFrame:
        try:
            if not hourly_data or not hourly_data.get("time"):
                return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(hourly_data)
            
            # Convert time to datetime and set as index
            df['datetime'] = pd.to_datetime(df['time'])
            df.set_index('datetime', inplace=True)
            
            # Add derived columns
            df['date'] = df.index.date
            df['hour'] = df.index.hour
            df['weekday'] = df.index.strftime('%a')
            
            # Add weather description
            df['weather_description'] = df['weather_code'].map(self.weather_codes).fillna('Unknown')
            
            # Clean up any missing values
            df = df.fillna(0)
            
            logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error creating DataFrame: {e}")
            return pd.DataFrame()
    
    def _get_hourly_data(self, days: int = 7) -> List[Dict]:
        if self.df is None or self.df.empty:
            return []
        
        try:
            # Filter data for the specified number of days
            end_date = datetime.now().date() + timedelta(days=days)
            filtered_df = self.df[self.df.index.date <= end_date]
            
            # Convert to list of dictionaries
            result = []
            for idx, row in filtered_df.iterrows():
                result.append({
                    "time": idx.isoformat(),
                    "temperature": float(row.get('temperature_2m', 0)),
                    "apparent_temperature": float(row.get('apparent_temperature', row.get('temperature_2m', 0))),
                    "humidity": float(row.get('relative_humidity_2m', 0)),
                    "weather_code": int(row.get('weather_code', 0)),
                    "weather_description": row.get('weather_description', 'Unknown'),
                    "wind_speed": float(row.get('wind_speed_10m', 0)),
                    "wind_direction": float(row.get('wind_direction_10m', 0)),
                    "wind_gusts": float(row.get('wind_gusts_10m', row.get('wind_speed_10m', 0))),
                    "rain": float(row.get('rain', 0)),
                    "pressure": float(row.get('surface_pressure', 1013)),
                    "cloud_cover": float(row.get('cloud_cover', 0)),
                    "cloud_cover_low": float(row.get('cloud_cover_low', 0)),
                    "cloud_cover_mid": float(row.get('cloud_cover_mid', 0)),
                    "cloud_cover_high": float(row.get('cloud_cover_high', 0)),
                    "precipitation_probability": float(row.get('precipitation_probability', 0))
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting hourly data: {e}")
            return []
    
    def _process_daily_data(self, daily_data: Dict, days: int) -> List[Dict]:
        processed = []
        
        times = daily_data.get("time", [])
        sunrises = daily_data.get("sunrise", [])
        sunsets = daily_data.get("sunset", [])
        
        for i in range(min(len(times), days)):
            if i < len(times):
                processed.append({
                    "date": times[i],
                    "sunrise": sunrises[i] if i < len(sunrises) else None,
                    "sunset": sunsets[i] if i < len(sunsets) else None
                })
        
        return processed
    
    def _get_current_conditions(self) -> Dict:
        try:
            if self.df is None or self.df.empty:
                return {}
            
            # Get current time
            now = datetime.now()
            current_hour = now.hour
            current_date = now.date()
            
            # Find the closest available data point
            if current_date in self.df['date'].values:
                # Get data for current date and hour
                today_data = self.df[self.df['date'] == current_date]
                
                if not today_data.empty:
                    # Find the closest hour
                    hour_diff = abs(today_data['hour'] - current_hour)
                    closest_idx = hour_diff.idxmin()
                    row = today_data.loc[closest_idx]
                    
                    return {
                        "time": closest_idx.isoformat(),
                        "temperature": float(row.get('temperature_2m', 0)),
                        "apparent_temperature": float(row.get('apparent_temperature', row.get('temperature_2m', 0))),
                        "humidity": float(row.get('relative_humidity_2m', 0)),
                        "weather_code": int(row.get('weather_code', 0)),
                        "weather_description": row.get('weather_description', 'Unknown'),
                        "wind_speed": float(row.get('wind_speed_10m', 0)),
                        "wind_direction": float(row.get('wind_direction_10m', 0)),
                        "pressure": float(row.get('surface_pressure', 1013)),
                        "cloud_cover": float(row.get('cloud_cover', 0))
                    }
            
            # Fallback: return first available data point
            if not self.df.empty:
                first_row = self.df.iloc[0]
                return {
                    "time": self.df.index[0].isoformat(),
                    "temperature": float(first_row.get('temperature_2m', 0)),
                    "apparent_temperature": float(first_row.get('apparent_temperature', first_row.get('temperature_2m', 0))),
                    "humidity": float(first_row.get('relative_humidity_2m', 0)),
                    "weather_code": int(first_row.get('weather_code', 0)),
                    "weather_description": first_row.get('weather_description', 'Unknown'),
                    "wind_speed": float(first_row.get('wind_speed_10m', 0)),
                    "wind_direction": float(first_row.get('wind_direction_10m', 0)),
                    "pressure": float(first_row.get('surface_pressure', 1013)),
                    "cloud_cover": float(first_row.get('cloud_cover', 0))
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting current conditions: {e}")
            return {}
    
    def get_today_forecast(self) -> Optional[Dict]:
        try:
            if self.df is None or self.df.empty:
                # Fetch fresh data if needed
                forecast_data = self.get_forecast(days=1)
                if not forecast_data or 'error' in forecast_data:
                    return None
            
            # Get today's data
            today = datetime.now().date()
            today_data = self.df[self.df['date'] == today]
            
            if today_data.empty:
                return {"error": "No data available for today"}
            
            # Calculate daily statistics
            daily_stats = {
                "date": today.isoformat(),
                "temperature": {
                    "current": float(today_data['temperature_2m'].iloc[-1]) if not today_data.empty else 0,
                    "min": float(today_data['temperature_2m'].min()),
                    "max": float(today_data['temperature_2m'].max()),
                    "average": float(today_data['temperature_2m'].mean())
                },
                "humidity": {
                    "current": float(today_data['relative_humidity_2m'].iloc[-1]) if not today_data.empty else 0,
                    "average": float(today_data['relative_humidity_2m'].mean())
                },
                "wind": {
                    "current_speed": float(today_data['wind_speed_10m'].iloc[-1]) if not today_data.empty else 0,
                    "average_speed": float(today_data['wind_speed_10m'].mean()),
                    "max_gust": float(today_data['wind_gusts_10m'].max())
                },
                "precipitation": {
                    "total_rain": float(today_data['rain'].sum()),
                    "probability": float(today_data['precipitation_probability'].mean())
                },
                "pressure": {
                    "current": float(today_data['surface_pressure'].iloc[-1]) if not today_data.empty else 1013,
                    "average": float(today_data['surface_pressure'].mean())
                },
                "clouds": {
                    "average_cover": float(today_data['cloud_cover'].mean())
                },
                "hourly_data": self._get_hourly_data(1)
            }
            
            return daily_stats
            
        except Exception as e:
            logger.error(f"Error getting today's forecast: {e}")
            return {"error": f"Error getting today's forecast: {str(e)}"}
    
    def get_week_forecast(self) -> Optional[Dict]:
        try:
            if self.df is None or self.df.empty:
                # Fetch fresh data if needed
                forecast_data = self.get_forecast(days=7)
                if not forecast_data or 'error' in forecast_data:
                    return None
            
            # Group by date and calculate daily summaries
            daily_summaries = []
            
            for i in range(7):
                target_date = datetime.now().date() + timedelta(days=i)
                day_data = self.df[self.df['date'] == target_date]
                
                if not day_data.empty:
                    summary = {
                        "date": target_date.isoformat(),
                        "weekday": target_date.strftime('%A'),
                        "temperature": {
                            "min": float(day_data['temperature_2m'].min()),
                            "max": float(day_data['temperature_2m'].max()),
                            "average": float(day_data['temperature_2m'].mean())
                        },
                        "humidity": float(day_data['relative_humidity_2m'].mean()),
                        "wind_speed": float(day_data['wind_speed_10m'].mean()),
                        "rain": float(day_data['rain'].sum()),
                        "pressure": float(day_data['surface_pressure'].mean()),
                        "weather_code": int(day_data['weather_code'].mode().iloc[0]) if not day_data['weather_code'].mode().empty else 0,
                        "weather_description": day_data['weather_description'].mode().iloc[0] if not day_data['weather_description'].mode().empty else 'Unknown'
                    }
                    daily_summaries.append(summary)
                else:
                    # Add placeholder for missing data
                    daily_summaries.append({
                        "date": target_date.isoformat(),
                        "weekday": target_date.strftime('%A'),
                        "temperature": {"min": 0, "max": 0, "average": 0},
                        "humidity": 0,
                        "wind_speed": 0,
                        "rain": 0,
                        "pressure": 1013,
                        "weather_code": 0,
                        "weather_description": "No data"
                    })
            
            return {
                "location": {
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "timezone": self.timezone
                },
                "daily_summaries": daily_summaries,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting week forecast: {e}")
            return {"error": f"Error getting week forecast: {str(e)}"}
    
    def get_forecast_summary(self) -> Optional[Dict]:
        try:
            if self.df is None or self.df.empty:
                # Fetch fresh data if needed
                forecast_data = self.get_forecast(days=7)
                if not forecast_data or 'error' in forecast_data:
                    return None
            
            # Calculate overall statistics
            overall_stats = {
                "temperature": {
                    "min": float(self.df['temperature_2m'].min()),
                    "max": float(self.df['temperature_2m'].max()),
                    "average": float(self.df['temperature_2m'].mean())
                },
                "humidity": {
                    "min": float(self.df['relative_humidity_2m'].min()),
                    "max": float(self.df['relative_humidity_2m'].max()),
                    "average": float(self.df['relative_humidity_2m'].mean())
                },
                "wind": {
                    "average_speed": float(self.df['wind_speed_10m'].mean()),
                    "max_gust": float(self.df['wind_gusts_10m'].max())
                },
                "precipitation": {
                    "total_rain": float(self.df['rain'].sum()),
                    "rainy_hours": int((self.df['rain'] > 0).sum())
                },
                "pressure": {
                    "min": float(self.df['surface_pressure'].min()),
                    "max": float(self.df['surface_pressure'].max()),
                    "average": float(self.df['surface_pressure'].mean())
                },
                "data_points": len(self.df),
                "date_range": {
                    "start": self.df.index.min().isoformat(),
                    "end": self.df.index.max().isoformat()
                }
            }
            
            return {
                "summary": overall_stats,
                "current_conditions": self._get_current_conditions(),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting forecast summary: {e}")
            return {"error": f"Error getting forecast summary: {str(e)}"}
    
    def get_data_for_date(self, target_date: Union[str, datetime, pd.Timestamp]) -> Optional[pd.DataFrame]:
        try:
            if self.df is None or self.df.empty:
                return None
            
            # Convert target_date to datetime.date
            if isinstance(target_date, str):
                target_date = pd.to_datetime(target_date).date()
            elif isinstance(target_date, datetime):
                target_date = target_date.date()
            elif isinstance(target_date, pd.Timestamp):
                target_date = target_date.date()
            
            # Filter data for the target date
            date_data = self.df[self.df['date'] == target_date]
            return date_data if not date_data.empty else None
            
        except Exception as e:
            logger.error(f"Error getting data for date {target_date}: {e}")
            return None
    
    def get_data_for_hour(self, target_hour: int) -> Optional[pd.DataFrame]:
        try:
            if self.df is None or self.df.empty:
                return None
            
            # Filter data for the target hour
            hour_data = self.df[self.df['hour'] == target_hour]
            return hour_data if not hour_data.empty else None
            
        except Exception as e:
            logger.error(f"Error getting data for hour {target_hour}: {e}")
            return None
