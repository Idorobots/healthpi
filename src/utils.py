class with_state(dict):
    def __init__(self, **kwargs):
        for arg in kwargs:
            self[arg] = kwargs[arg]

    def __getattr__(self, name):
        return self[name]

    def __call__(self, fun):
        def wrapped(*args):
            return fun(self, *args)
        return wrapped

def fix_path(path):
    if path.endswith("/"):
        return path

    else:
        return path + "/"
