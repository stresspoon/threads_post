from .main import app

def handler(request, context):
    return app(request, context)