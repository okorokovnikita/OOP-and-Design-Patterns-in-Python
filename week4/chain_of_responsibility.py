class EventGet:
    def __init__(self, kind):
        self.kind = kind
        self.value = None

class EventSet:
    def __init__(self, value):
        self.value = value
        self.kind = type(value)


class SomeObject:
    def __init__(self):
        self.integer_field = 0
        self.float_field = 0.0
        self.string_field = ""


class NullHandler:
    def __init__(self, successor=None):
        self._successor = successor

    def handle(self, obj, event):
        if self._successor is not None:
            return self._successor.handle(obj, event)


class IntHandler(NullHandler):
    def handle(self, obj, event):
        if isinstance(event, EventGet) and event.kind == int:
            return obj.integer_field
        elif isinstance(event, EventSet) and event.kind == int:
            obj.integer_field = event.value
        else:
            return super().handle(obj, event)


class FloatHandler(NullHandler):
    def handle(self, obj, event):
        if isinstance(event, EventGet) and event.kind == float:
            return obj.float_field
        elif isinstance(event, EventSet) and event.kind == float:
            obj.float_field = event.value
        else:
            return super().handle(obj, event)


class StrHandler(NullHandler):
    def handle(self, obj, event):
        if isinstance(event, EventGet) and event.kind == str:
            return obj.string_field
        elif isinstance(event, EventSet) and event.kind == str:
            obj.string_field = event.value
        else:
            return super().handle(obj, event)
