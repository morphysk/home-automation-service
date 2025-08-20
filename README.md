# Home Automation Weather Service

A Python-based service for retrieving current and historical weather data from Netatmo weather stations.

## Features

- **Current Weather Data**: Real-time temperature, humidity, pressure, CO2, and noise readings
- **Historical Data**: Hourly measurements for the current day
- **Outdoor Weather Data**: Dedicated endpoints for wind, rain, outdoor temperature, and pressure
- **Multi-module Support**: Handles main station and additional modules (indoor, outdoor, rain gauge, wind gauge, etc.)
- **Automatic Authentication**: Handles Netatmo API token refresh automatically
- **RESTful API**: Clean HTTP endpoints with JSON responses

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

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NETATMO_CLIENT_ID` | Netatmo API client ID | Required |
| `NETATMO_CLIENT_SECRET` | Netatmo API client secret | Required |
| `NETATMO_USERNAME` | Netatmo account email | Required |
| `NETATMO_PASSWORD` | Netatmo account password | Required |
| `HWS_HOST` | Server host | `0.0.0.0` |
| `HWS_PORT` | Server port | `8080` |


## Module Types

The service automatically detects and handles different Netatmo module types:
- **NAModule1**: Outdoor module (temperature, humidity)
- **NAModule2**: Wind module (wind strength, direction, gusts)
- **NAModule3**: Rain module (rainfall measurements)
- **Main Station**: Indoor module (temperature, humidity, pressure, CO2, noise)

