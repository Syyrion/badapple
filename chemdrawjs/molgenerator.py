from more_itertools import minmax
import numpy as np

MAX_LINE_LENGTH = 50
ORIGIN = np.array([0, 0])

MOLECULE = "X"

class MolFile:
    def __init__(self):
        self.atoms = []
        self.headix = 0
        self.head = np.array([0, 0])
        self.anchorix = 0
        self.anchor = np.array([0, 0])
        self.bonds = []

    def getstring(self, scale):
        atomlist = ""
        for i, (x, y) in enumerate(self.getcentered(scale), 1):
            atomlist += f"M  V30 {i:d} {MOLECULE} {x:.6f} {y:.6f} {0:.6f} 0\n"
        
        bondlist = ""
        for i, (a, b) in enumerate(self.bonds, 1):
            bondlist += f"M  V30 {i:d} 1 {a:d} {b:d}\n"

        return f"""
  ChemDraw10162216512D

  0  0  0     0  0              0 V3000
M  V30 BEGIN CTAB
M  V30 COUNTS {len(self.atoms):d} {len(self.bonds):d} 0 0 0
M  V30 BEGIN ATOM
{atomlist}M  V30 END ATOM
M  V30 BEGIN BOND
{bondlist}M  V30 END BOND
M  V30 END CTAB
M  END
"""

    def getcentered(self, scale):
        coords = np.transpose(self.atoms)
        xcoords = coords[0]
        ycoords = coords[1]
        xmin, xmax = minmax(xcoords)
        ymin, ymax = minmax(ycoords)
        xcoords -= (xmin + xmax) * 0.5
        ycoords -= (ymin + ymax) * 0.5
        return zip(xcoords * scale[0], ycoords * scale[1])


    # Creates an atom and sets the anchor at that atom.
    def absoluteanchor(self, P):
        self.atoms.append(P)
        self.headix = len(self.atoms)
        self.anchorix = self.headix
        self.head = P
        self.anchor = P
        return self
    
    # Same as above but relative
    def relativeanchor(self, P):
        self.absoluteanchor(self.head + P)


    # Creates an atom and bonds it to the previous.
    def absolutechain(self, P):
        self.atoms.append(P)
        self.head = P
        self.bonds.append((self.headix, n := len(self.atoms)))
        self.headix = n
        return self

    # Same as above but relative
    def relativechain(self, P):
        self.absolutechain(self.head + P)


    def absolutesegmentedchain(self, P1):
        P0 = self.head
        divisions = int(np.linalg.norm(P1 - self.head) / MAX_LINE_LENGTH) + 1
        for i in range(divisions):
            point = lerp(P0, P1, (i + 1) / divisions)
            self.absolutechain(point)
        pass
    
    # Connects the head to the anchor point.
    def close(self):
        self.bonds.append((self.headix, self.anchorix))
        self.head = self.anchor
        return self

    def createframe(self, size):
        self.absoluteanchor(np.array([size[0], 0]))
        self.absolutesegmentedchain(ORIGIN)
        self.absolutesegmentedchain(np.array([0, size[1]]))

def lerp(P0, P1, t):
    return (1 - t) * P0 + t * P1
