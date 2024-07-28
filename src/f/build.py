from fontTools.ttLib import TTFont
from loguru import logger


class FClient:
    def __init__(self, basedir: str = ""):
        self.basedir = basedir
        self.sub_fonts = []
        self.main_font = None

        self.__fix_basedir()

    def __fix_basedir(self):
        if self.basedir == "":
            return

        if not self.basedir.endswith("/"):
            self.basedir = f"{self.basedir}/"

    def openFont(self, path: str):
        font = TTFont(self.basedir + path)

        font["OS/2"].achVendID = "SRSU"
        font["head"].unitsPerEm = 1000

        logger.info(f"Opened file: {path}")
        logger.info(f"numGlyphs: {font['maxp'].numGlyphs}")
        logger.info(f"achVendID: {font['OS/2'].achVendID}")
        logger.info(f"unitsPerEm: {font['head'].unitsPerEm}")

        path = f"dist/{path.rsplit('.')[0]}.ttx"
        font.saveXML(path)

        if self.main_font is None:
            self.main_font = font
        else:
            self.sub_fonts.append(font)

    def merge(self):
        self.main_font.glyphOrder
        for child in self.sub_fonts:
            for glyph in child["glyf"].glyphs:
                if glyph not in self.main_font["glyf"].glyphs:
                    self.main_font["glyf"].glyphs[glyph] = child["glyf"].glyphs[glyph]

        self.main_font["maxp"].numGlyphs = len(self.main_font["glyf"].glyphs.keys())

    def saveXML(self):
        self.main_font.saveXML("dist/merged.ttx")

    def exportTTF(self):
        self.main_font.save("dist/merged.ttf")


if __name__ == "__main__":
    f = FClient("resource")

    f.openFont("F-Extended.ttf")
    f.openFont("BIZUDGothic-Regular.ttf")

    f.merge()
    f.saveXML()
    f.exportTTF()

    TTFont().importXML("dist/merged.ttx")
