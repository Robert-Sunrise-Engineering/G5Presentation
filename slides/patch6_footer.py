"""Remove the tool-stack footer/credential line from every page of the combined deck.

Removes the standalone text "gemma4:12b · Ollama · ArcGIS Pro 3.7 · UGRC parcels
(CC BY 4.0)" (the right-hand footer on content slides and the right-hand
credential line on the title slide). Leaves "TRUST BUT VERIFY" (footer left) and
the presenter name (title left) untouched. Content references to ArcGIS / Ollama
elsewhere in the slides are kept.

Run:  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" slides\\patch6_footer.py
"""
from pptx import Presentation

prs = Presentation(r"slides/deck_g5_full.pptx")

SIG = "Ollama · ArcGIS Pro"   # signature of the footer/credential line only

removed = 0
for slide in prs.slides:
    for sh in list(slide.shapes):
        if sh.has_text_frame and SIG in sh.text_frame.text:
            sh._element.getparent().remove(sh._element)
            removed += 1

prs.save(r"slides/deck_g5_full.pptx")
print(f"removed footer/credential line from {removed} shapes")
