class ViewMode(str):
    def __new__(cls, entity, mode, scope=None):
        if scope:
            value = f"{entity}:{mode}:{scope}"
        else:
            value = f"{entity}:{mode}"

        obj = str.__new__(cls, value)
        obj.entity = entity
        obj.mode = mode
        obj.scope = scope
        return obj

    def is_entity(self, entity):
        return self.entity == entity

    def is_mode(self, mode):
        return self.mode == mode

    def is_scope(self, scope):
        return self.scope == scope


def vm(entity, mode, scope=None):
    return ViewMode(entity, mode, scope)