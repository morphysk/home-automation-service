# Home Automation Weather Service

A Python-based service for retrieving current and historical weather data from Netatmo weather stations.

## Features

- **Current Weather Data**: Real-time temperature, humidity, pressure, CO2, and noise readings
- **Historical Data**: Hourly measurements for the current day
- **Outdoor Weather Data**: Dedicated endpoints for wind, rain, outdoor temperature, and pressure
- **Multi-module Support**: Handles main station and additional modules (indoor, outdoor, rain gauge, wind gauge, etc.)
- **Automatic Authentication**: Handles Netatmo API token refresh automatically
- **RESTful API**: Clean HTTP endpoints with JSON responses
- **Swagger Documentation**: Interactive API documentation at `/api/docs`

## Prerequisites

- Python 3.11+
- Netatmo weather station
- Netatmo developer account

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Netatmo API

1. Go to [Netatmo Developer Portal](https://dev.netatmo.com/)
2. Create a new application
3. Note your `Client ID` and `Client Secret`
4. Copy `config.env.example` to `.env`:
   ```bash
   cp config.env.example .env
   ```
5. Edit `.env` with your credentials:
   ```
   NETATMO_CLIENT_ID=your_client_id_here
   NETATMO_CLIENT_SECRET=your_client_secret_here
   NETATMO_USERNAME=your_netatmo_email@example.com
   NETATMO_PASSWORD=your_netatmo_password
   ```

### 3. Run the Service

```bash
python -m home_automation_service.app
```

The service will start on `http://localhost:8080` by default.

## API Endpoints

### Current Weather
```
GET /weather/current
```
Returns current weather data from all modules.

### Historical Weather
```
GET /weather/historical
```
Returns historical measurements for the current day.

### Weather Summary
```
GET /weather/summary
```
Returns both current and historical data in a single response.

### Outdoor Weather
```
GET /weather/outdoor
```
Returns outdoor weather data including:
- **Wind**: Wind strength, direction, gust strength, gust direction
- **Rain**: Current rain, 1-hour accumulation, 24-hour accumulation
- **Outdoor Temperature**: Temperature and humidity from outdoor module
- **Pressure**: Atmospheric pressure and trend from main station

### Health Check
```
GET /health
```
Service health status.

## API Documentation

Interactive API documentation is available at `/api/docs` when the service is running.

## Data Structure

### Current Weather Response
```json
{
  "status": "success",
  "data": {
    "current": {
      "device_id": "device_id",
      "device_name": "Station Name",
      "location": {
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0
      },
      "dashboard_data": {
        "time_utc": 1234567890,
        "Temperature": 22.5,
        "Humidity": 45,
        "Pressure": 1013.2,
        "CO2": 450,
        "Noise": 35
      },
      "modules": [
        {
          "module_id": "module_id",
          "module_name": "Module Name",
          "module_type": "NAModule1",
          "dashboard_data": {
            "time_utc": 1234567890,
            "Temperature": 18.2,
            "Humidity": 60
          }
        }
      ]
    },
    "timestamp": 1234567890
  }
}
```

### Outdoor Weather Response
```json
{
  "status": "success",
  "data": {
    "outdoor": {
      "module_id": "outdoor_module_id",
      "module_name": "Outdoor Module",
      "module_type": "NAModule1",
      "temperature": 18.5,
      "humidity": 65,
      "pressure": 1013.2,
      "pressure_trend": "up",
      "last_update": 1234567890
    },
    "wind": {
      "module_id": "wind_module_id",
      "module_name": "Wind Module",
      "module_type": "NAModule2",
      "wind_strength": 15.2,
      "wind_angle": 180,
      "gust_strength": 25.8,
      "gust_angle": 175,
      "last_update": 1234567890
    },
    "rain": {
      "module_id": "rain_module_id",
      "module_name": "Rain Module",
      "module_type": "NAModule3",
      "rain": 0.0,
      "rain_1h": 0.0,
      "rain_24h": 2.5,
      "last_update": 1234567890
    }
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Historical Weather Response
```json
{
  "status": "success",
  "data": {
    "historical": {
      "body": [
        {
          "beg_time": 1234567890,
          "step_time": 3600,
          "value": [
            [22.5, 45, 1013.2, 450, 35]
          ]
        }
      ]
    },
    "date": 1234567890
  }
}
```

## Command Line Interface

The service includes a comprehensive CLI for easy access to weather data:

```bash
# Show current weather
python weather_cli.py --current

# Show historical data
python weather_cli.py --historical

# Show both current and historical
python weather_cli.py --summary

# Show outdoor weather (wind, rain, temp, pressure)
python weather_cli.py --outdoor

# Output in JSON format
python weather_cli.py --outdoor --json
```

### CLI Features

- **Wind Data**: Wind strength (km/h), direction (degrees + compass), gust information
- **Rain Data**: Current rain, 1-hour and 24-hour accumulation (mm)
- **Outdoor Temperature**: Temperature (°C) and humidity (%) from outdoor module
- **Pressure Data**: Atmospheric pressure (hPa) with trend indicators
- **Formatted Output**: Easy-to-read display with emojis and proper units
- **JSON Output**: Machine-readable format for scripting and automation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NETATMO_CLIENT_ID` | Netatmo API client ID | Required |
| `NETATMO_CLIENT_SECRET` | Netatmo API client secret | Required |
| `NETATMO_USERNAME` | Netatmo account email | Required |
| `NETATMO_PASSWORD` | Netatmo account password | Required |
| `HWS_HOST` | Server host | `0.0.0.0` |
| `HWS_PORT` | Server port | `8080` |

## Development

### Running Tests
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Test Netatmo integration
python test_netatmo.py
```

### Code Formatting
```bash
# Format code with black
black home_automation_service/

# Sort imports with isort
isort home_automation_service/
```

## Makefile Commands

```bash
make install              # Install dependencies
make run                 # Run the web service
make test                # Test Netatmo integration
make weather             # Show current weather
make weather-current     # Current weather only
make weather-historical  # Historical data only
make weather-summary     # Both current and historical
make weather-outdoor     # Outdoor weather (wind, rain, temp, pressure)
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Verify your Netatmo credentials in `.env`
2. **No Data Returned**: Check if your weather station is online and has recent data
3. **Missing Outdoor Data**: Ensure you have outdoor, wind, and/or rain modules connected
4. **Rate Limiting**: Netatmo API has rate limits; the service handles this automatically

### Module Types

The service automatically detects and handles different Netatmo module types:
- **NAModule1**: Outdoor module (temperature, humidity)
- **NAModule2**: Wind module (wind strength, direction, gusts)
- **NAModule3**: Rain module (rainfall measurements)
- **Main Station**: Indoor module (temperature, humidity, pressure, CO2, noise)

### Logs

Check the console output for detailed error messages and API responses.

## Security Notes

- Never commit your `.env` file to version control
- Keep your Netatmo credentials secure
- The service only requests read access to weather data

## License

This project is open source and available under the MIT License.
