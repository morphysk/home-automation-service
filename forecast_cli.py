#!/usr/bin/env python3
"""
Command-line interface for weather forecasts using Open-Meteo API.
"""

import argparse
import json
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, sys.path[0])

from home_automation_service.services.forecast import WeatherForecastService


def format_temperature(temp):
    if temp is not None:
        return f"{temp}°C"
    return "N/A"


def format_humidity(humidity):
    if humidity is not None:
        return f"{humidity}%"
    return "N/A"


def format_wind_speed(wind_speed):
    if wind_speed is not None:
        return f"{wind_speed} km/h"
    return "N/A"


def format_pressure(pressure):
    if pressure is not None:
        return f"{pressure} hPa"
    return "N/A"


def format_rain(rain):
    if rain is not None:
        return f"{rain} mm"
    return "N/A"


def format_time(time_str):
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except:
        return time_str


def display_current_forecast(data, verbose=False):
    current = data.get("current", {})
    if current:
        print(f"\n🌤️  Current Forecast Conditions")
        print("=" * 60)
        print(f"   Time: {format_time(current.get('time', 'N/A'))}")
        print(f"   Temperature: {format_temperature(current.get('temperature'))}")
        print(f"   Feels Like: {format_temperature(current.get('apparent_temperature'))}")
        print(f"   Humidity: {format_humidity(current.get('humidity'))}")
        print(f"   Weather: {current.get('weather_description', 'N/A')}")
        print(f"   Wind: {format_wind_speed(current.get('wind_speed'))} at {current.get('wind_direction', 'N/A')}°")
        print(f"   Pressure: {format_pressure(current.get('pressure'))}")
        print(f"   Cloud Cover: {current.get('cloud_cover', 'N/A')}%")


def display_hourly_forecast(data, verbose=False):
    hourly = data.get("hourly", [])
    if not hourly:
        print("No hourly forecast data available")
        return
    
    print(f"\n🕐 Hourly Forecast (Next 24 hours)")
    print("=" * 60)
    
    # Show next 24 hours
    for i, hour_data in enumerate(hourly[:24]):
        time = format_time(hour_data.get("time", "N/A"))
        temp = format_temperature(hour_data.get("temperature"))
        weather = hour_data.get("weather_description", "N/A")
        wind = format_wind_speed(hour_data.get("wind_speed"))
        rain = format_rain(hour_data.get("rain"))
        
        print(f"   {time}: {temp} | {weather} | Wind: {wind} | Rain: {rain}")
        
        if verbose:
            humidity = format_humidity(hour_data.get("humidity"))
            pressure = format_pressure(hour_data.get("pressure"))
            cloud = f"{hour_data.get('cloud_cover', 'N/A')}%"
            print(f"        Humidity: {humidity} | Pressure: {pressure} | Clouds: {cloud}")


def display_daily_forecast(data, verbose=False):
    daily = data.get("daily", [])
    if not daily:
        print("No daily forecast data available")
        return
    
    print(f"\n📅 Daily Forecast")
    print("=" * 60)
    
    for day_data in daily:
        date_str = day_data.get("date", "N/A")
        sunrise = format_time(day_data.get("sunrise", "N/A"))
        sunset = format_time(day_data.get("sunset", "N/A"))
        
        print(f"   {date_str}:")
        print(f"     Sunrise: {sunrise} | Sunset: {sunset}")


def display_forecast_summary(data, verbose=False):
    daily_summaries = data.get("daily_summaries", [])
    if not daily_summaries:
        print("No forecast summary available")
        return
    
    print(f"\n📊 Forecast Summary")
    print("=" * 60)
    
    for summary in daily_summaries:
        date_str = summary.get("date", "N/A")
        min_temp = format_temperature(summary.get("min_temp"))
        max_temp = format_temperature(summary.get("max_temp"))
        avg_humidity = format_humidity(summary.get("avg_humidity"))
        total_rain = format_rain(summary.get("total_rain"))
        
        print(f"   {date_str}:")
        print(f"     Temperature: {min_temp} to {max_temp}")
        print(f"     Humidity: {avg_humidity}")
        print(f"     Rain: {total_rain}")


def display_location_info(data):
    location = data.get("location", {})
    if location:
        print(f"\n📍 Location Information")
        print("=" * 60)
        print(f"   Coordinates: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
        print(f"   Elevation: {location.get('elevation', 'N/A')} m")
        print(f"   Timezone: {location.get('timezone', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Weather Forecast CLI using Open-Meteo API")
    parser.add_argument("--today", action="store_true", help="Show today's detailed forecast")
    parser.add_argument("--week", action="store_true", help="Show weekly forecast")
    parser.add_argument("--summary", action="store_true", help="Show forecast summary")
    parser.add_argument("--days", type=int, default=7, help="Number of days (1-7, default: 7)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # If no specific option is selected, show default forecast
    if not any([args.today, args.week, args.summary]):
        args.days = args.days
    
    # Validate days parameter
    if args.days < 1 or args.days > 7:
        print("Days parameter must be between 1 and 7")
        sys.exit(1)
    
    # Initialize forecast service
    try:
        forecast_service = WeatherForecastService()
    except Exception as e:
        print(f"Failed to initialize forecast service: {e}")
        sys.exit(1)
    
    # Get forecast data based on requested type
    try:
        if args.today:
            data = forecast_service.get_today_forecast()
        elif args.week:
            data = forecast_service.get_week_forecast()
        elif args.summary:
            data = forecast_service.get_forecast_summary()
        else:
            data = forecast_service.get_forecast(days=args.days)
        
        if not data:
            print("Failed to retrieve forecast data")
            sys.exit(1)
        
        if data.get("error"):
            print(f"Error: {data['error']}")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error retrieving forecast: {e}")
        sys.exit(1)
    
    # Output data
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        # Display location info
        display_location_info(data)
        
        # Display current conditions
        display_current_forecast(data, args.verbose)
        
        # Display forecast based on type
        if args.today:
            display_hourly_forecast(data, args.verbose)
            display_daily_forecast(data, args.verbose)
        elif args.week:
            display_hourly_forecast(data, args.verbose)
            display_daily_forecast(data, args.verbose)
        elif args.summary:
            display_forecast_summary(data, args.verbose)
        else:
            display_hourly_forecast(data, args.verbose)
            display_daily_forecast(data, args.verbose)
        
        # Show generation time
        if data.get("generated_at"):
            generated_time = datetime.fromisoformat(data["generated_at"])
            print(f"\n🕐 Generated at: {generated_time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
