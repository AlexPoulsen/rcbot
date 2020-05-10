from wand.color import Color
from wand.image import Image
from wand.drawing import Drawing
from wand.compat import nested
import textwrap

with Drawing() as draw:
    with Image(width=1000, height=400, background=Color('hsla(0, 0, 100, 50)')) as img:
        draw.font_family = 'Helvetica'
        draw.font_size = 30.0
        draw.push()
        draw.fill_color = Color("hsl(0%, 0%, 0%)")
        draw.gravity = "north_west"
        draw.text_under_color = Color("hsl(0%, 100%, 50%)")
        draw.text(10,10, "\n".join(textwrap.wrap("Blah. The result is a list of tuples (operation, startpos, destpos), where operation is one of 'equal', 'replace', 'insert', or 'delete'; startpos and destpos are position of characters in the first (source) and the second (destination) strings. The returned list doesn't contain the 'equal', but all the related functions accept both lists with and without 'equal's. These are operations on single characters.", 75)))
        draw.pop()
        draw(img)
        img.save(filename='text_image/image.png')

string = "[++[Blah. ]]The result is a list of t[--[ri], ++[u]]ples (operation, s[++[tart]]pos, d[++[est]]pos), where operation is one of 'equal', 'replace', 'insert', or 'delete'; s[++[tart]]pos and d[++[est]]pos are position of characters in the first (source) and the second (destination) strings. T[--[hese are operations on signle characters. In fact t], ]he returned list doesn't contain the 'equal', but all the related functions accept both lists with and without 'equal'[++[s. These are operations on single character]]s."
