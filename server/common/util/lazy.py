
class Lazy:
    def __init__(self, getter):
        self.getter = getter

    def __call__(self, *args, **kwargs):
        if self.value is None:
            self.value = self.getter(*args, **kwargs)
        return self.value
