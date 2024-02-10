from direct.gui import DirectGuiGlobals
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.ShowBase import ShowBase

from evh_utils.LayoutElement import LayoutElement, AlignVector, Alignment, Direction, ArrangedElement

layout = LayoutElement(AlignVector.from_2d(Alignment.CENTER, Alignment.UP), direction=Direction.DOWN, padding=0.02)


def addSmallNode():
    node = DirectFrame(
        relief=DirectGuiGlobals.SUNKEN,
        text="Small node",
        scale=0.1,
    )
    layout.add(ArrangedElement.from_size(node, 0.5, 0.12))


def addLargeNode():
    node = DirectFrame(
        relief=DirectGuiGlobals.RAISED,
        text="Large node",
        scale=0.3,
    )
    layout.add(ArrangedElement.from_size(node, 0.5, 0.37))


addShortButton = DirectButton(text="+Small", command=addSmallNode, scale=0.08)
addLongButton = DirectButton(text="BIG BIG BIG", command=addLargeNode, scale=0.1)
layout.add(ArrangedElement.from_size(addShortButton, 0.5, 0.1))
layout.add(ArrangedElement.from_size(addLongButton, 0.5, 0.125))
layout.setPos(0, 0, 1)


ShowBase()
layout.reparentTo(aspect2d)
base.run()
