import azure.functions as func

from main import app

_func_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@_func_app.route(route="{*route}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def a2a_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await func.AsgiMiddleware(app).handle_async(req, context)
