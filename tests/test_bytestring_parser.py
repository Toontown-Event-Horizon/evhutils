from bytestring_parser import BytestringParser, Packers, migration


class UnversionedParser(BytestringParser):
    fieldId: int = Packers.uint8
    fieldData: int = Packers.int16
    extraArgs = Packers.tuple(Packers.int32, Packers.int32, Packers.int32)


class VersionedParserOld(BytestringParser, version=1):
    safeColor: int = Packers.uint8
    unusedField: int = Packers.uint8


class VersionedParserIntermediate(BytestringParser, version=2):
    safeColor: int = Packers.uint8
    bodyIndex: int = Packers.uint8
    unusedField: int = Packers.uint8

    @migration(fromVersion=1, convertedField="bodyIndex", added=True)
    def bodyIndexAdded(self):
        return 0


class VersionedParserNew(BytestringParser, version=3):
    colorTuple = Packers.tuple(Packers.uint8, Packers.uint8, Packers.uint8)
    bodyIndex: int = Packers.uint8

    @migration(fromVersion=1, convertedField="bodyIndex", added=True)
    def bodyIndexAdded(self):
        return 0

    @migration(fromVersion=2, convertedField="colorTuple")
    def tupleBasedColors(self, oldColor: int = Packers.uint8):
        # example where 0 = black and everything else = white
        if oldColor == 0:
            return 0, 0, 0
        return 255, 255, 255

    @migration(fromVersion=2, convertedField="unusedField", removed=True, locatedAfter="bodyIndex")
    def removeUnusedField(self, unusedField: int = Packers.uint8):
        pass


class SameFieldChangeA(BytestringParser, version=1):
    myField: int = Packers.uint8


class SameFieldChangeB(BytestringParser, version=2):
    myField: int = Packers.uint16

    @migration(fromVersion=1, convertedField="myField")
    def rangeIncrease(self, oldValue: int = Packers.uint8):
        # Shift upwards, all new values are < 255
        return oldValue + 1000


class SameFieldChangeC(BytestringParser, version=3):
    myField: int = Packers.uint32

    @migration(fromVersion=1, convertedField="myField")
    def rangeIncrease(self, oldValue: int = Packers.uint8):
        # Shift upwards, all new values are < 255
        return oldValue + 1000

    @migration(fromVersion=2, convertedField="myField")
    def rangeIncreaseAgain(self, oldValue: int = Packers.uint16):
        # Shift upwards, but multiplicatively so we can check commutativity properly
        return oldValue * 50


def test_unversioned():
    item1 = UnversionedParser(1, 2, (3, 4, 5))
    item2 = UnversionedParser(3, 4, (5, 6, 7))
    assert item1 != item2
    item1Copy = UnversionedParser.fromBytestring(item1.bytestring)
    assert item1Copy == item1
    assert item1Copy != item2


def test_version_upgrade():
    oldVersion = VersionedParserOld(3, 5)
    upgradedVersion = VersionedParserIntermediate.fromBytestring(oldVersion.bytestring)
    assert upgradedVersion == VersionedParserIntermediate(3, 0, 5)

    doubleUpgradedVersion = VersionedParserNew.fromBytestring(upgradedVersion.bytestring)
    assert doubleUpgradedVersion == VersionedParserNew((255, 255, 255), 0)

    twiceUpgradedVersion = VersionedParserNew.fromBytestring(oldVersion.bytestring)
    assert doubleUpgradedVersion == twiceUpgradedVersion

    keptVersion = VersionedParserNew.fromBytestring(doubleUpgradedVersion.bytestring)
    assert keptVersion == doubleUpgradedVersion


def test_same_field_upgrade():
    oldItem = SameFieldChangeA(10)
    midItem = SameFieldChangeB.fromBytestring(oldItem.bytestring)
    newItem = SameFieldChangeC.fromBytestring(oldItem.bytestring)
    assert len(oldItem.bytestring) == 2
    assert len(midItem.bytestring) == 3
    assert len(newItem.bytestring) == 5

    assert oldItem.myField == 10
    assert midItem.myField == 1010
    assert newItem.myField == 50 * 1010
    assert newItem == SameFieldChangeC.fromBytestring(midItem.bytestring)
