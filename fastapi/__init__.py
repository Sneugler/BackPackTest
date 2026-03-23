class FastAPI:
    def __init__(self, *args, **kwargs):
        self.routes = {}
    def get(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
