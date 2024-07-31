from loguru import logger
from fontTools.ttLib import TTFont


class TTFontBuilder:
    def __init__(self, base_dir: str = ""):
        self.__set_base_dir(base_dir)
        self.main_font = None
        self.sub_fonts = []

    def __set_base_dir(self, base_dir: str):
        if not base_dir.endswith("/"):
            base_dir += "/"
            logger.info("`/` appended to path that is a directory.")

        self.__base_dir = base_dir

    def __open_font(self, file_name: str) -> TTFont:
        path = self.__base_dir + file_name
        logger.info(f"* Opened: {path}")

        font = TTFont(path)
        logger.debug(f"numGlyphs: {font['maxp'].numGlyphs}")
        logger.debug(f"achVendID: {font['OS/2'].achVendID}")
        logger.debug(f"unitsPerEm: {font['head'].unitsPerEm}")

        return font

    def __set_main_font(self, font: TTFont):
        self.main_font = font

    def __add_sub_font(self, font: TTFont):
        self.sub_fonts.append(font)

    def __merge_sub_font(self, index: int):
        sub_font = self.sub_fonts[index]
        order = sub_font.getGlyphOrder()

        for glyph in list(sub_font["glyf"].glyphs):
            # Removes an invalid glyph
            if glyph not in order:
                del sub_font["glyf"].glyphs[glyph]
                continue

            if glyph in self.main_font["glyf"].glyphs:
                continue

            # Copying a glyph
            self.main_font["glyf"].glyphs[glyph] = sub_font["glyf"].glyphs[glyph]

            # Copying metrics
            if glyph in sub_font["hmtx"].metrics:
                self.main_font["hmtx"].metrics[glyph] = sub_font["hmtx"].metrics[glyph]

    def open_main_font(self, file_name: str):
        """
        Open a new font file and set as main font.
        """
        main_font = self.__open_font(file_name)
        logger.info(f"Set as main font: {file_name}")

        self.__set_main_font(main_font)

    def open_sub_font(self, file_name: str):
        """
        Open a new font file and add as sub font to list.
        """
        sub_font = self.__open_font(file_name)
        logger.info(f"Added as sub font: {file_name}")

        self.__add_sub_font(sub_font)

    def merge(self):
        oldNumGlyphs = self.main_font["maxp"].numGlyphs
        for i in range(len(self.sub_fonts)):
            self.__merge_sub_font(i)
        newNumGlyphs = len(self.main_font["glyf"].glyphs.keys())

        self.main_font.setGlyphOrder(list(self.main_font["glyf"].glyphs.keys()))

        self.main_font["maxp"].numGlyphs = newNumGlyphs
        logger.info(f"glyphs: {oldNumGlyphs} -> {newNumGlyphs}")

    def export_xml(self):
        self.main_font.saveXML("dist/merged.ttx")

    def export_ttf(self):
        self.main_font.save("dist/merged.ttf")
