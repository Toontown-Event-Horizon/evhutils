from bytestring_parser import BytestringParser, Packers, migration


ColorList = [
    (0, 0, 0),
    (255, 255, 255),
    (200, 0, 0),
    (0, 0, 200),
]


class ToonDNA(BytestringParser, version=3):
    torsoIndex = Packers.uint8
    legSize = Packers.uint8
    species = Packers.uint8

    # Color used to be one number, but now it's a tuple of four colors, since ToonDNA v2
    color = Packers.tuple(Packers.uint8, Packers.uint8, Packers.uint8)

    @migration(fromVersion=1, convertedField="color")
    def colorToTuple(self, oldColor=Packers.uint8):
        return ColorList[oldColor]

    # Eyelids used to not be configurable, but now they have a shape, since ToonDNA v3
    eyelidShape = Packers.uint8

    @migration(fromVersion=2, convertedField="eyelidShape", added=True)
    def defaultEyelidShape(self):
        return 0


v1Bytestring = b"\x01\x02\x05\x04\x03"
dna = ToonDNA.fromBytestring(v1Bytestring)
print(f"Old bytestring: {v1Bytestring}")
print(f"DNA: {dna}")
print(f"New bytestring: {dna.bytestring}")
dna.eyelidShape = 2
print(f"Eyelids change: {dna.bytestring}")
