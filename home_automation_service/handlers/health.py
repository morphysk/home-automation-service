from aiohttp import web


async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


