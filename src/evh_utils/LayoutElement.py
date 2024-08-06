import dataclasses
from enum import Enum, auto

from direct.actor.Actor import Actor
from direct.gui.DirectGuiBase import DirectGuiWidget
from panda3d.core import NodePath, Vec3


class Alignment(Enum):
    BEGINNING = auto()
    CENTER = auto()
    END = auto()

    LEFT = BEGINNING
    RIGHT = END
    DOWN = BEGINNING
    UP = END
    BACKWARD = BEGINNING
    FORWARD = END

    @property
    def shiftMultiplier(self):
        if self is Alignment.END:
            return -1
        if self is Alignment.CENTER:
            return -0.5
        return 0


@dataclasses.dataclass
class AlignVector:
    x_axis: Alignment
    y_axis: Alignment
    z_axis: Alignment
    shifts: Vec3 = dataclasses.field(init=False)

    def __post_init__(self):
        self.shifts = Vec3(self.x_axis.shiftMultiplier, self.y_axis.shiftMultiplier, self.z_axis.shiftMultiplier)

    @classmethod
    def from_2d(cls, x_axis: Alignment, z_axis: Alignment):
        return cls(x_axis, Alignment.CENTER, z_axis)


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()
    UP = auto()
    BACKWARD = auto()
    FORWARD = auto()

    @property
    def axis(self):
        if self in (Direction.UP, Direction.DOWN):
            return "z"
        if self in (Direction.LEFT, Direction.RIGHT):
            return "x"
        return "y"

    @property
    def is_reverse(self):
        return self in (Direction.LEFT, Direction.DOWN, Direction.BACKWARD)


@dataclasses.dataclass
class ArrangedElement:
    node: NodePath
    left: float
    right: float
    bottom: float
    top: float
    back: float = 0
    front: float = 0
    id: int = dataclasses.field(init=False)
    sizes: dict[str, float] = dataclasses.field(init=False)

    max_id = 0

    def __post_init__(self):
        self.__class__.max_id += 1
        self.id = self.max_id
        self.sizes = {"x": self.right - self.left, "y": self.front - self.back, "z": self.top - self.bottom}

    @classmethod
    def from_size(cls, node: NodePath, width: float, height: float, depth: float = 0):
        return cls(node, -width / 2, width / 2, -height / 2, height / 2, -depth / 2, depth / 2)

    def position(self, axis, totalSize, alignment: AlignVector, priorDistance):
        shifts = alignment.shifts
        pos = Vec3(
            shifts.x * self.sizes["x"] - self.left,
            shifts.y * self.sizes["y"] - self.back,
            shifts.z * self.sizes["z"] - self.bottom,
        )
        if axis == "x":
            pos.x = shifts.x * totalSize + priorDistance - self.left
        elif axis == "y":
            pos.y = shifts.y * totalSize + priorDistance - self.right
        else:
            pos.z = shifts.z * totalSize + priorDistance - self.bottom
        return pos

    def destroy(self):
        if isinstance(self.node, DirectGuiWidget):
            self.node.destroy()
        elif isinstance(self.node, Actor):
            self.node.cleanup()
        else:
            self.node.removeNode()


class LayoutElement(NodePath):
    layout_element_id = 0

    def __init__(
        self,
        parent: NodePath,
        alignment: AlignVector,
        pos: Vec3 = Vec3(0, 0, 0),
        padding: float = 0,
        direction: Direction = Direction.RIGHT,
    ):
        self.__class__.layout_element_id += 1
        super().__init__(f"layout-element-{self.layout_element_id}")
        self.reparentTo(parent)
        self.setPos(pos)
        self.padding = padding
        self.alignment = alignment
        self.direction = direction
        self.__items: dict[int, ArrangedElement] = {}

    @property
    def itemCount(self):
        return len(self.__items)

    @property
    def __lengths(self):
        return [node.sizes[self.direction.axis] for node in self.itemList]

    @property
    def itemList(self):
        if self.direction.is_reverse:
            return list(reversed(self.__items.values()))
        return list(self.__items.values())

    def add(self, *items: ArrangedElement, redraw: bool = True):
        for item in items:
            assert item.id not in self.__items
            self.__items[item.id] = item
            item.node.reparentTo(self)
        if redraw:
            self.redraw()

    def remove(self, *items: ArrangedElement, redraw: bool = True):
        for item in items:
            element = self.__items.pop(item.id, None)
            if element:
                item.node.detachNode()
        if redraw:
            self.redraw()

    def redraw(self):
        totalLength = self.getTotalLength()
        nodes = self.itemList
        lengths = self.__lengths

        priorDistance = 0
        for node, length in zip(nodes, lengths):
            pos = node.position(self.direction.axis, totalLength, self.alignment, priorDistance)
            node.node.setPos(pos)
            priorDistance += length + self.padding

    def getTotalLength(self):
        lengths = self.__lengths
        return sum(lengths) + self.padding * (len(lengths) - 1)
