import xml.etree.ElementTree as ET
import regex
import numpy as np
from molgenerator import MolFile
from molgenerator import ORIGIN

# Returns a list of commands and coordinates from a path string.
def parsepath(path:str):
    commands = []
    for command, str in regex.findall(r"([a-zA-Z]) *((?:(?:-?\d*(?:\.\d+)?(?: *|,?)))*)", path):
        str = str.strip()
        # There are no coords
        if str == "":
            commands.append({"command":command})
            continue
        
        # This is the dumb way of getting the coords. Does not necessarily handle all edge cases.
        coords = str.split()
        for i, n in enumerate(coords):
            coords[i] = int(n)
        
        coords = np.array(coords)
        if command.lower() == "c":
            coords = coords.reshape(len(coords) // 6, 3, 2)
        else:
            coords = coords.reshape(len(coords) // 2, 2)

        commands.append({
            "command":command,
            "coords":coords
        })
    return commands
    
def getsvgpaths(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    group = root.find("./{http://www.w3.org/2000/svg}g")

    paths = []
    for path in group.findall("./{http://www.w3.org/2000/svg}path"):
        paths.append(parsepath(path.attrib["d"]))
    return paths

def svgtomol(filename):
    mol = MolFile()
    for path in getsvgpaths(filename):
        for command in path:
            char = command["command"]
            if char == "M":
                for point in command["coords"]:
                    mol.absoluteanchor(point)
            elif char == "m":
                for offset in command["coords"]:
                    mol.relativeanchor(offset)
            elif char.lower() == "z":
                mol.close()
            elif char == "l":
                for offset in command["coords"]:
                    mol.relativechain(offset)
            elif char == "c":
                for offsets in command["coords"]:
                    point = cubicbezier(ORIGIN, offsets[0], offsets[1], offsets[2], 0.5)
                    mol.relativechain(point)
                    mol.relativechain(offsets[2] - point)
            else:
                raise Exception("Unknown path command.")
    return mol

def cubicbezier(P0, P1, P2, P3, t):
    u = 1 - t
    return u * u * u * P0 + 3 * u * u * t * P1 + 3 * u * t * t * P2 + t * t * t * P3
