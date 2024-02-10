# EVH Utils

EVH Utils is a collection of modules designed for ingame use, but can be used in other scenarios as well.

## Current list of modules

* `bytestring_parser`: an automatic bytestring class with versioning support. Example: see `ToonDNA_with_parser`.
* `layout_element`: a node that automatically repositions nodes inside of it. Example: see `LayoutSystem`.

## Information on use

### Bytestring Parser

The Bytestring Parser is used to convert structured data into bytestrings and vice versa.
Since the structured data may change over time, Bytestring Parser provides an optional streamlined way
to automatically upgrade bytestrings to the newest version, implemented through migrations.
For example, we can consider a simple class that stores one color as a uint8 index:

```python
from evh_utils.BytestringParser import BytestringParser, Packers

class ColorData(BytestringParser, version=1):
    color = Packers.uint8

color = ColorData(1)
bytestring = color.bytestring
```

Let's say at some point the color has to be changed to the 3-byte RGB version, but the old
bytestrings must still function. For that, a migration can be created along with a version bump:

```python
from evh_utils.BytestringParser import BytestringParser, Packers, migration

class ColorData(BytestringParser, version=2):
    color = Packers.tuple(Packers.uint8, Packers.uint8, Packers.uint8)

    @migration(fromVersion=1, convertedField="color")
    def colorToTuple(self, oldColor=Packers.uint8):
        # In a real application this would be a lookup in a dict/list of colors
        if oldColor == 0:
            return 0, 0, 0
        return 255, 255, 255

new_color = ColorData((255, 0, 0))
new_bytestring = new_color.bytestring
```

Any number of migrations can be added during the same version bump. Each migration can either add,
modify, or remove fields, although it's currently not possible to add a migration that depends
on other fields, or add fields at the beginning of the datagram.

Now, bytestrings of both
version 1 and version 2 can be loaded, and any new bytestring will be automatically converted to version 2:

```python
color = ColorData.from_bytestring(bytestring)
new_color = ColorData.from_bytestring(new_bytestring)
```

Note: Bytestring Parser acts like a blackbox. It might be non-trivial to add compatibility for the bytestrings
created with other methods.

### Layout Element

Layout Element is used to align multiple Panda3D nodes (including NodePaths, DirectGUIWidgets, etc.) along an axis.

The Layout Element must be initialized with an axis and the alignment point:

```python
from evh_utils.LayoutElement import LayoutElement, AlignVector, Alignment, Direction

layout = LayoutElement(
    AlignVector.from_2d(Alignment.CENTER, Alignment.UP),  # can also be a 3D align vector
    direction=Direction.DOWN,
    padding=0.02  # default 0
)
```

These attributes also can be changed at the runtime, although it requires that `layout.redraw()` is called after.

For each node the size has to be provided, then the item can be added to the element:

```python
from direct.gui.DirectFrame import DirectFrame
from evh_utils.LayoutElement import ArrangedElement

node = DirectFrame(
    text="Some node",
    scale=0.1,
)
item = ArrangedElement.from_size(node, 0.5, 0.12)
layout.add(item)  # by default redraws automatically, this can be disabled by adding `redraw=False`
                  # if multiple items should be added in a row
# If the item no longer should be in the layout...
layout.remove(item)
```

In many cases the size can be derived from the node using a method such as `calcTightBounds`, although
the DirectGUI system doesn't really give the correct results with that in the majority of cases.

Warning: The Layout Element expects that it only stores a handful of items inside each one.
If you try to align a hundred items in the same axis, expect performance dropoffs.
