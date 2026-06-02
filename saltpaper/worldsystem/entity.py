
from typing import TypeVar, Type

_T = TypeVar('_T')


class Entity():
    _id_counter = 0

    def __init__(self, world):
        self.id = Entity._id_counter
        Entity._id_counter += 1
        self.components = {}
        self.world = world
        self.killed = False
        world.entities[self.id] = self

    def add(self, component):
        self.components[type(component)] = component

    def add_many(self, *components):
        for component in components:
            self.add(component)

    def get(self, component_type: Type[_T]) -> _T | None:
        for comp_cls, comp in self.components.items():
            if issubclass(comp_cls, component_type):
                return comp  # type: ignore[return-value]
        return None

    def has(self, component_type: type) -> bool:
        return (self.get(component_type) is not None)

    def remove(self, component_type):
        comp = self.get(component_type)
        if comp:
            self.components.pop(type(comp), None)

    def kill(self):
        self.killed = True
        self.world.entities.pop(self.id, None)
        return self

    def __getattr__(self, name):
        for component in self.components.values():
            if hasattr(component, name):
                return getattr(component, name)
        raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

    def __setattr__(self, name, value):
        if "components" in self.__dict__:
            for component in self.components.values():
                if hasattr(component, name):
                    setattr(component, name, value)
                    return
        object.__setattr__(self, name, value)

    @staticmethod
    def _component_attrs(component):
        attrs = {}
        if hasattr(component, "__dict__"):
            attrs.update(component.__dict__)

        slots = getattr(component, "__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        for slot in slots:
            if hasattr(component, slot):
                attrs[slot] = getattr(component, slot)

        return {k: v for k, v in attrs.items() if not k.startswith("_")}

    def __str__(self):
        header = (
            f"Entity(id: {self.id}, killed: {self.killed}, "
            f"components: {len(self.components)})"
        )
        if not self.components:
            return f"{header}\n  (no components)"

        lines = [header]
        for component in sorted(self.components.values(), key=lambda c: type(c).__name__):
            comp_name = type(component).__name__
            attrs = self._component_attrs(component)
            if attrs:
                formatted = ", ".join(
                    f"{name}={value!r}" for name, value in sorted(attrs.items())
                )
                lines.append(f"  - {comp_name}({formatted})")
            else:
                lines.append(f"  - {comp_name}(no public attributes)")

        return "\n".join(lines)
