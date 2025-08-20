#!/usr/bin/env python3
"""
Command-line interface for Netatmo weather station data.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from home_automation_service.services.netatmo import NetatmoService


def format_temperature(temp):
    """Format temperature with proper unit"""
    if temp is not None:
        return f"{temp}°C"
    return "N/A"


def format_humidity(humidity):
    """Format humidity with proper unit"""
    if humidity is not None:
        return f"{humidity}%"
    return "N/A"


def format_pressure(pressure):
    """Format pressure with proper unit"""
    if pressure is not None:
        return f"{pressure} hPa"
    return "N/A"


def format_co2(co2):
    """Format CO2 with proper unit"""
    if co2 is not None:
        return f"{co2} ppm"
    return "N/A"


def format_noise(noise):
    """Format noise with proper unit"""
    if noise is not None:
        return f"{noise} dB"
    return "N/A"


def format_wind_strength(wind_strength):
    """Format wind strength with proper unit"""
    if wind_strength is not None:
        return f"{wind_strength} km/h"
    return "N/A"


def format_wind_angle(wind_angle):
    """Format wind angle with direction"""
    if wind_angle is not None:
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(wind_angle / 22.5) % 16
        return f"{wind_angle}° ({directions[index]})"
    return "N/A"


def format_rain(rain):
    """Format rain with proper unit"""
    if rain is not None:
        return f"{rain} mm"
    return "N/A"


def display_outdoor_weather(data, verbose=False):
    """Display outdoor weather data including wind, rain, temperature, and pressure"""
    print(f"\n🌤️  Outdoor Weather Data")
    print("=" * 60)
    
    # Outdoor temperature and humidity
    outdoor = data.get("outdoor", {})
    if outdoor:
        print(f"🌡️  Outdoor Module: {outdoor.get('module_name', 'Unknown')}")
        print(f"   Temperature: {format_temperature(outdoor.get('temperature'))}")
        print(f"   Humidity: {format_humidity(outdoor.get('humidity'))}")
        if outdoor.get('pressure'):
            print(f"   Pressure: {format_pressure(outdoor.get('pressure'))}")
            if outdoor.get('pressure_trend'):
                trend = outdoor.get('pressure_trend')
                trend_symbol = "↗️" if trend == "up" else "↘️" if trend == "down" else "→"
                print(f"   Pressure Trend: {trend_symbol} {trend}")
        
        if outdoor.get('last_update'):
            timestamp = datetime.fromtimestamp(outdoor['last_update'])
            print(f"   Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wind data
    wind = data.get("wind", {})
    if wind:
        print(f"\n💨 Wind Module: {wind.get('module_name', 'Unknown')}")
        print(f"   Wind Strength: {format_wind_strength(wind.get('wind_strength'))}")
        print(f"   Wind Direction: {format_wind_angle(wind.get('wind_angle'))}")
        print(f"   Gust Strength: {format_wind_strength(wind.get('gust_strength'))}")
        print(f"   Gust Direction: {format_wind_angle(wind.get('gust_angle'))}")
        
        if wind.get('last_update'):
            timestamp = datetime.fromtimestamp(wind['last_update'])
            print(f"   Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Rain data
    rain = data.get("rain", {})
    if rain:
        print(f"\n🌧️  Rain Module: {rain.get('module_name', 'Unknown')}")
        print(f"   Current Rain: {format_rain(rain.get('rain'))}")
        print(f"   Rain (1h): {format_rain(rain.get('rain_1h'))}")
        print(f"   Rain (24h): {format_rain(rain.get('rain_24h'))}")
        
        if rain.get('last_update'):
            timestamp = datetime.fromtimestamp(rain['last_update'])
            print(f"   Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if any outdoor data is missing
    if not any([outdoor, wind, rain]):
        print("⚠️  No outdoor weather modules detected")
        print("   Make sure you have outdoor, wind, and/or rain modules connected")


def display_current_weather(data, verbose=False):
    """Display current weather data in a formatted way"""
    if not data.get("current"):
        print("❌ No current weather data available")
        return
    
    current = data["current"]
    dashboard = current.get("dashboard_data", {})
    
    print(f"\n🌤️  Current Weather - {current.get('device_name', 'Unknown Station')}")
    print("=" * 60)
    
    # Main station data
    if dashboard:
        print(f"📍 Location: {current.get('location', {}).get('latitude', 'N/A')}, "
              f"{current.get('location', {}).get('longitude', 'N/A')}")
        print(f"📊 Main Station Readings:")
        print(f"   Temperature: {format_temperature(dashboard.get('Temperature'))}")
        print(f"   Humidity: {format_humidity(dashboard.get('Humidity'))}")
        print(f"   Pressure: {format_pressure(dashboard.get('Pressure'))}")
        print(f"   CO2: {format_co2(dashboard.get('CO2'))}")
        print(f"   Noise: {format_noise(dashboard.get('Noise'))}")
        
        if dashboard.get('time_utc'):
            timestamp = datetime.fromtimestamp(dashboard['time_utc'])
            print(f"   Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Module data
    modules = current.get("modules", [])
    if modules:
        print(f"\n📡 Additional Modules ({len(modules)}):")
        for i, module in enumerate(modules, 1):
            module_dashboard = module.get("dashboard_data", {})
            print(f"\n   {i}. {module.get('module_name', 'Unknown')} ({module.get('module_type', 'Unknown Type')})")
            
            if module_dashboard:
                if module_dashboard.get('Temperature') is not None:
                    print(f"      Temperature: {format_temperature(module_dashboard.get('Temperature'))}")
                if module_dashboard.get('Humidity') is not None:
                    print(f"      Humidity: {format_humidity(module_dashboard.get('Humidity'))}")
                if module_dashboard.get('Rain') is not None:
                    print(f"      Rain: {format_rain(module_dashboard.get('Rain'))}")
                if module_dashboard.get('WindStrength') is not None:
                    print(f"      Wind: {format_wind_strength(module_dashboard.get('WindStrength'))}")
                if module_dashboard.get('time_utc'):
                    timestamp = datetime.fromtimestamp(module_dashboard['time_utc'])
                    print(f"      Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


def display_historical_data(data, verbose=False):
    """Display historical weather data"""
    if not data.get("historical"):
        print("❌ No historical data available")
        return
    
    historical = data["historical"]
    body = historical.get("body", [])
    
    if not body:
        print("❌ No historical measurements found")
        return
    
    print(f"\n📈 Historical Data for Today")
    print("=" * 60)
    
    for measurement in body:
        beg_time = measurement.get("beg_time")
        step_time = measurement.get("step_time")
        values = measurement.get("value", [])
        
        if beg_time:
            timestamp = datetime.fromtimestamp(beg_time)
            print(f"\n🕐 {timestamp.strftime('%H:%M')} - "
                  f"Step: {step_time//60 if step_time else 'N/A'} min")
            
            for value_set in values:
                if len(value_set) >= 5:
                    print(f"   Temperature: {format_temperature(value_set[0])}")
                    print(f"   Humidity: {format_humidity(value_set[1])}")
                    print(f"   Pressure: {format_pressure(value_set[2])}")
                    print(f"   CO2: {format_co2(value_set[3])}")
                    print(f"   Noise: {format_noise(value_set[4])}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Netatmo Weather Station CLI")
    parser.add_argument("--current", action="store_true", help="Show current weather data")
    parser.add_argument("--historical", action="store_true", help="Show historical data for today")
    parser.add_argument("--summary", action="store_true", help="Show both current and historical data")
    parser.add_argument("--outdoor", action="store_true", help="Show outdoor weather data (wind, rain, temp, pressure)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # If no specific option is selected, show current weather
    if not any([args.current, args.historical, args.summary, args.outdoor]):
        args.current = True
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        "NETATMO_CLIENT_ID",
        "NETATMO_CLIENT_SECRET", 
        "NETATMO_USERNAME",
        "NETATMO_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with your Netatmo credentials.")
        print("See config.env.example for reference.")
        sys.exit(1)
    
    # Initialize service
    try:
        netatmo = NetatmoService()
    except Exception as e:
        print(f"❌ Failed to initialize NetatmoService: {e}")
        sys.exit(1)
    
    # Authenticate
    if not netatmo.authenticate():
        print("❌ Authentication failed. Please check your Netatmo credentials.")
        sys.exit(1)
    
    # Get data based on requested type
    if args.outdoor:
        try:
            data = netatmo.get_outdoor_weather_data()
            if data.get("error"):
                print(f"❌ Error retrieving outdoor data: {data['error']}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error retrieving outdoor data: {e}")
            sys.exit(1)
    else:
        try:
            data = netatmo.get_current_day_data()
            if data.get("error"):
                print(f"❌ Error retrieving data: {data['error']}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error retrieving data: {e}")
            sys.exit(1)
    
    # Output data
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        if args.outdoor:
            display_outdoor_weather(data, args.verbose)
        else:
            if args.current or args.summary:
                display_current_weather(data, args.verbose)
            
            if args.historical or args.summary:
                display_historical_data(data, args.verbose)


if __name__ == "__main__":
    main()
