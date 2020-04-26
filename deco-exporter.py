from Crypto.Cipher import Blowfish
from Crypto.Cipher import AES
from struct import unpack
from tkinter import Tk, Label, Button, Text, filedialog
from webbrowser import open as op
from pathlib import Path
from shutil import copyfile, rmtree
import ast
import pickle
import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

with open(resource_path("decos.txt"), "r") as decos:
    contents = decos.read()
decoDict = ast.literal_eval(contents)

with open(resource_path("floats.pickle"), "rb") as fp:
    FLOAT_CONSTANTS = pickle.load(fp)
with open(resource_path("ints.pickle"), "rb") as fp:
    INTEGER_CONSTANTS = pickle.load(fp)

minJewelId = 727

maxJewelId = 2272

numDecos = maxJewelId - minJewelId + 1

decoInventorySize = 50 * 10

numBytesPerDeco = 8

saveSlotDecosOffsets = [4302696, 6439464, 8576232]


def decryptSave(save):
    key = b"xieZjoe#P2134-3zmaghgpqoe0z8$3azeq"
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    save[0::4], save[1::4], save[2::4], save[3::4] = (
        save[3::4],
        save[2::4],
        save[1::4],
        save[0::4],
    )
    save = bytearray(cipher.decrypt(save))
    save[0::4], save[1::4], save[2::4], save[3::4] = (
        save[3::4],
        save[2::4],
        save[1::4],
        save[0::4],
    )
    return save


def decryptRegion(save, offset, length):
    salt = [0] * 0x200
    keys = [[0 for x in range(0x10)] for y in range(0x20)]
    keyLength = [0] * 0x20
    keySalt = crc32(0xA37A55D7, save, offset + length, 0x200)
    saveOffset = offset
    saltOffset = 0

    generateSalt(salt, keySalt)
    generateKeys(keys, keySalt, salt)
    generateKeyLength(keyLength, keySalt, length)

    for i in range(32):
        saltOffset = 0

        cipher = AES.new(bytes(keys[i]), AES.MODE_ECB)

        while saveOffset < keyLength[i] + offset:
            branch = 4 if (salt[saltOffset & 0x1FF] & 1) == 0 else 0

            save[saveOffset - branch + 4] ^= salt[saltOffset + 8 & 0x1FF]
            save[saveOffset - branch + 5] ^= salt[saltOffset + 9 & 0x1FF]
            save[saveOffset - branch + 6] ^= salt[saltOffset + 10 & 0x1FF]
            save[saveOffset - branch + 7] ^= salt[saltOffset + 11 & 0x1FF]

            save[saveOffset - branch + 12] ^= salt[saltOffset + 12 & 0x1FF]
            save[saveOffset - branch + 13] ^= salt[saltOffset + 13 & 0x1FF]
            save[saveOffset - branch + 14] ^= salt[saltOffset + 14 & 0x1FF]
            save[saveOffset - branch + 15] ^= salt[saltOffset + 15 & 0x1FF]

            save[saveOffset : saveOffset + 16] = cipher.decrypt(
                save[saveOffset : saveOffset + 16]
            )

            save[saveOffset + branch + 0] ^= salt[saltOffset + 0 & 0x1FF]
            save[saveOffset + branch + 1] ^= salt[saltOffset + 1 & 0x1FF]
            save[saveOffset + branch + 2] ^= salt[saltOffset + 2 & 0x1FF]
            save[saveOffset + branch + 3] ^= salt[saltOffset + 3 & 0x1FF]

            save[saveOffset + branch + 8] ^= salt[saltOffset + 4 & 0x1FF]
            save[saveOffset + branch + 9] ^= salt[saltOffset + 5 & 0x1FF]
            save[saveOffset + branch + 10] ^= salt[saltOffset + 6 & 0x1FF]
            save[saveOffset + branch + 11] ^= salt[saltOffset + 7 & 0x1FF]

            saltOffset += 4
            saveOffset += 16


def rshift(val, n):
    return val >> n if val >= 0 else (val + 0x100000000) >> n


def crc32(initialValue, data, offset, length):
    for i in range(offset, offset + length):
        temp = (initialValue ^ data[i]) & 0xFF
        for j in range(0, 8):
            if (temp & 1) == 1:
                temp = rshift(temp, 1)
                temp ^= 0xEDB88320
            else:
                temp = rshift(temp, 1)
        initialValue = rshift(initialValue, 8)
        initialValue ^= temp
    return initialValue


def generateSalt(salt, keySalt):
    c = keySalt ^ 0x4BF0CF23
    s = 0
    offset = 0x5D7
    offsetChange = (
        rshift(keySalt, 0x18)
        + (rshift(keySalt, 0x10) & 0xFF)
        + (rshift(keySalt, 0x8) & 0xFF)
        + (keySalt & 0xFF)
        + 1
    )
    for i in range(0, 0x200, 4):
        s = INTEGER_CONSTANTS[offset & 0xFFF] ^ c
        if ((-(s & 0x7)) + 1) == 0:
            s ^= 0xBD75F29
        salt[i] = s & 0xFF
        salt[i + 1] = rshift(s, 0x8) & 0xFF
        salt[i + 2] = rshift(s, 0x10) & 0xFF
        salt[i + 3] = rshift(s, 0x18) & 0xFF

        offset += offsetChange


def generateKeys(keys, keySalt, salt):
    c1 = 0x5A8B79A9 ^ keySalt
    c2 = 0x34616F90 ^ keySalt
    c3 = 0xC4C638DF ^ keySalt
    c4 = 0x94FB64E8 ^ keySalt

    k = 0
    encodedKeyIndex = 0

    for i in range(32):
        encodedKeyIndex = readInt(salt, i << 2)
        k = encodedKeyIndex ^ c1
        keys[i][0] = k & 0xFF
        keys[i][1] = rshift(k, 0x8) & 0xFF
        keys[i][2] = rshift(k, 0x10) & 0xFF
        keys[i][3] = rshift(k, 0x18) & 0xFF

        k = encodedKeyIndex ^ c2
        keys[i][4] = k & 0xFF
        keys[i][5] = rshift(k, 0x8) & 0xFF
        keys[i][6] = rshift(k, 0x10) & 0xFF
        keys[i][7] = rshift(k, 0x18) & 0xFF

        k = encodedKeyIndex ^ c3
        keys[i][8] = k & 0xFF
        keys[i][9] = rshift(k, 0x8) & 0xFF
        keys[i][10] = rshift(k, 0x10) & 0xFF
        keys[i][11] = rshift(k, 0x18) & 0xFF

        k = encodedKeyIndex ^ c4
        keys[i][12] = k & 0xFF
        keys[i][13] = rshift(k, 0x8) & 0xFF
        keys[i][14] = rshift(k, 0x10) & 0xFF
        keys[i][15] = rshift(k, 0x18) & 0xFF


def generateKeyLength(keyLength, keySalt, length):
    averageLengthInt = rshift(length, 5)
    averageLengthFloat = float(averageLengthInt)
    expectedLength = averageLengthInt

    for i in range(31):
        keyLength[i] = (int)(
            (
                FLOAT_CONSTANTS[
                    INTEGER_CONSTANTS[(keySalt + i) & 0xFFF ^ 0x5D7] & 0xFFF ^ 0x885
                ]
                - 0.5
            )
            * averageLengthFloat
        ) + expectedLength + 0xF & 0xFFFFFFF0
        expectedLength += averageLengthInt
    keyLength[31] = length


def readInt(arr, ptr):
    return (
        (arr[ptr] & 0xFF)
        | ((arr[ptr + 1] & 0xFF) << 8)
        | ((arr[ptr + 2] & 0xFF) << 16)
        | ((arr[ptr + 3] & 0xFF) << 24)
    )


def mainDecrypt():
    savedata = open("temp_for_deco/SAVEDATA1000", "rb")
    save = bytearray(savedata.read())
    savedata.close()

    save = decryptSave(save)
    decryptRegion(save, 0x70, 0xDA50)
    decryptRegion(save, 0x3010D8, 0x2098C0)
    decryptRegion(save, 0x50AB98, 0x2098C0)
    decryptRegion(save, 0x714658, 0x2098C0)

    newFile = open("temp_for_deco/SAVEDATA1000.dec", "wb")
    newFile.write(save)
    newFile.close()


def getJewelCounts(save, offset):
    jewels = []
    buff = save[offset : offset + (decoInventorySize * numBytesPerDeco)]
    anyNonZero = False
    for i in range(decoInventorySize):
        e = i * 8
        jewelId = unpack("<i", buff[e : e + 4])[0]
        jewelCount = unpack("<i", buff[e + 4 : e + 8])[0]

        if jewelId == 0:
            continue
        if jewelId < minJewelId or jewelId > maxJewelId:
            output_text.delete("1.0", "end")
            output_text.insert(
                "end",
                f"Error parsing decorations. Index={i} ID={jewelId} Count={jewelCount}\n",
            )
            root.update()
            return None
        if jewelCount > 0:
            anyNonZero = True
        jewels.append((jewelId, jewelCount))
    if anyNonZero:
        return jewels
    return None


def outputHoneyHunter(jewels):
    hhoutput = []
    for x in jewels:
        saveslot = []
        for i in decoDict:
            found = False
            for j in x:
                if j[0] == i:
                    saveslot.append(min(decoDict[i][1], j[1]))
                    found = True
            if not found:
                saveslot.append(0)
        hhoutput.append(saveslot)
    for i, x in enumerate(hhoutput):
        hhoutput[i] = ",".join(str(j) for j in hhoutput[i])
    with open("export.txt", "w") as text_file:
        if len(hhoutput) > 1:
            for i, x in enumerate(hhoutput):
                print(f"Save {i+1}:\n{x}", end="\n\n", file=text_file)
        else:
            print(hhoutput[0], file=text_file)


def mainConvert():
    savedata = open("temp_for_deco/SAVEDATA1000.dec", "rb")
    save = bytearray(savedata.read())
    savedata.close()

    jewels = []
    for i in range(3):
        temp = getJewelCounts(save, saveSlotDecosOffsets[i])
        if temp != None:
            jewels.append(temp)
    if jewels != None:
        outputHoneyHunter(jewels)


def openPages():
    op(r"https://steamid.io/")
    op(r"http://steamcommunity.com/my/profile")


def getDir():
    found = False

    directory = filedialog.askdirectory(
        initialdir=r"C:\Program Files (x86)\Steam\userdata",
        parent=root,
        title="Select userdata\<your ID>",
    )
    datafile = Path(f"{directory}/582010/remote/SAVEDATA1000")
    Path("temp_for_deco").mkdir(parents=True, exist_ok=True)
    tempfolder = Path("temp_for_deco")
    dest = Path("temp_for_deco/SAVEDATA1000")

    if datafile.is_file():
        found = True
        output_text.delete("1.0", "end")
    else:
        output_text.delete("1.0", "end")
        output_text.insert(
            "end", "Save file not found:\n  Try selecting directory again.\n"
        )
        root.update()
    if found:
        copyfile(str(datafile), str(dest))
        output_text.insert("end", "Starting Decryption\n")
        root.update()
        mainDecrypt()
        mainConvert()
        output_text.insert("end", "Done! -> export.txt created")
        root.update()
    rmtree(tempfolder)


root = Tk()
root.title("Deco Exporter!")
label = Label(
    root,
    text="Get Steam ID by pasting your url link into https://steamid.io\nIt will be steamID3 [U:1:<YOUR ID HERE>]",
)
label.grid(column=0, row=0)
id_button = Button(root, text="Open Web Pages to get ID", command=openPages)
id_button.grid(column=1, row=0, sticky="ew")
label = Label(root, text="Select the userdata\<your ID> folder")
label.grid(column=0, row=1)
export_button = Button(root, text="Select Directory", command=getDir)
export_button.grid(column=1, row=1, sticky="ew")
output_text = Text(root, height=3, width=0)
output_text.grid(column=0, row=2, sticky="ew")
close_button = Button(root, text="Close", command=root.quit)
close_button.grid(column=1, row=2)
root.mainloop()
