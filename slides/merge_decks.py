"""Combine deck_g5.pptx (slides 1–7) + deck_g5_beats2.pptx (slides 8–15)
into a single 15-slide deck.

Run:  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" slides\\merge_decks.py
Output: slides\\deck_g5_full.pptx
"""
import copy
from pptx import Presentation
from pptx.dml.color import RGBColor

BG = RGBColor(0x12, 0x15, 0x1A)

base = Presentation(r"slides/deck_g5.pptx")        # slides 1–7 (user-edited)
beats2 = Presentation(r"slides/deck_g5_beats2.pptx")  # slides 8–15

blank = base.slide_layouts[6]  # same blank layout used by both builders

def append_slide(src_slide):
    dst = base.slides.add_slide(blank)
    # match the shared dark background
    dst.background.fill.solid()
    dst.background.fill.fore_color.rgb = BG
    # deep-copy every shape (no images/media in this deck)
    spTree = dst.shapes._spTree
    for sh in src_slide.shapes:
        spTree.append(copy.deepcopy(sh._element))
    # carry the speaker notes
    if src_slide.has_notes_slide:
        dst.notes_slide.notes_text_frame.text = src_slide.notes_slide.notes_text_frame.text
    return dst

for slide in beats2.slides:
    append_slide(slide)

base.save(r"slides/deck_g5_full.pptx")
print("saved slides/deck_g5_full.pptx —", len(base.slides._sldIdLst), "slides")
