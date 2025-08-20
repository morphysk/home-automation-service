import os
from aiohttp import web
from dotenv import load_dotenv
from aiohttp_cache import setup_cache

from .routes import setup_routes

# Load environment variables from .env file
load_dotenv()


async def swagger_json(request: web.Request) -> web.Response:
    """Serve the custom swagger.json file"""
    try:
        # Use current working directory to find swagger.json
        swagger_path = "swagger.json"
        with open(swagger_path, "r") as f:
            content = f.read()
        return web.Response(
            text=content,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except FileNotFoundError:
        return web.Response(
            text='{"error": "swagger.json not found"}',
            status=404,
            content_type="application/json"
        )


async def swagger_ui(request: web.Request) -> web.Response:
    """Serve a simple Swagger UI that uses our custom swagger.json"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Home Weather Service - API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/swagger.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>
"""
    return web.Response(text=html_content, content_type="text/html")


def create_app() -> web.Application:
    app = web.Application()
    
    # Set up routes first
    setup_routes(app)

    # Initialize aiohttp-cache (defaults to in-memory backend)
    setup_cache(app)
    
    # Add custom Swagger endpoints
    app.router.add_get("/api/swagger.json", swagger_json)
    app.router.add_get("/api/docs", swagger_ui)
    
    return app


def main() -> None:
    host = os.getenv("HWS_HOST", "0.0.0.0")
    port = int(os.getenv("HWS_PORT", "8080"))
    web.run_app(create_app(), host=host, port=port)


if __name__ == "__main__":
    main()


