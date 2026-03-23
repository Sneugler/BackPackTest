class Typer:
    def __init__(self, *args, **kwargs):
        self.commands = {}
    def command(self, name=None):
        def decorator(func):
            self.commands[name or func.__name__] = func
            return func
        return decorator
    def add_typer(self, typer, name=None):
        self.commands[name or 'sub'] = typer
    def __call__(self, *args, **kwargs):
        return None

def echo(message):
    print(message)
