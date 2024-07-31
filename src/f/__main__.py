from f.builder import TTFontBuilder


if __name__ == "__main__":
    loader = TTFontBuilder("resource/")
    loader.open_main_font("F-Extended.ttf")
    loader.open_sub_font("BIZUDGothic-Regular.ttf")
    loader.open_sub_font("SymbolsNerdFontMono-Regular.ttf")
    loader.open_sub_font("NotoColorEmoji-Regular.ttf")

    loader.merge()
    loader.export_xml()
    loader.export_ttf()  # failed
