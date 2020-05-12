import typing
import copy
import textwrap
import Levenshtein as lev
import itertools
# from wand.color import Color
# from wand.image import Image
# from wand.drawing import Drawing
# from wand.compat import nested
import datetime
import os
import shutil
import pdf2image
import subprocess


class Alphanumeric:
    pass


class Globals:
    policy_id = 0

global_ = Globals()
global_.latex_render_dict = {"branch": {}, "section": {}, "policy": {}}


class RevisionUnchangeableError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "Revision Object is not editable to preserve revision state, cache edits instead."


# def diff_image(text_1: str, text_2: str):
#     with Drawing() as draw:
#         with Image(width=1000, height=1000, background=Color('hsla(0, 0, 100, 50)')) as img:
#             draw.font_family = 'Helvetica'
#             draw.font_size = 30.0
#             draw.push()
#             draw.fill_color = Color("hsl(0%, 0%, 0%)")
#             draw.gravity = "north_west"
#             draw.text_under_color = Color("hsl(0%, 100%, 50%)")
#             draw.text(10,10, "\n".join(textwrap.wrap("Blah. The result is a list of tuples (operation, startpos, destpos), where operation is one of 'equal', 'replace', 'insert', or 'delete'; startpos and destpos are position of characters in the first (source) and the second (destination) strings. The returned list doesn't contain the 'equal', but all the related functions accept both lists with and without 'equal's. These are operations on single characters.", 75)))
#             text_1 = "\u10F6" + text_1  # otherwise edits without matching preceding text are not shown
#             text_2 = "\u10F6" + text_2
#             out = []
#             matched_blocks = lev.matching_blocks(lev.editops(text_1, text_2), text_1, text_2)
#             for i, matching in enumerate(zip(matched_blocks, matched_blocks[1:] + [0])):
#                 if matching[0][2] == 0:
#                     continue
#                 if matching[0][0] > 0 and i == 0:
#                     out.append("[--[")
#                     for n in range(matching[0][0]):
#                         out.append(text_1[n])
#                     out.append("], ++[")
#                     for n in range(matching[0][0]):
#                         out.append(text_2[n])
#                     out.append("]]")
#                 for n in range(matching[0][2]):
#                     out.append(text_1[n+matching[0][0]])
#                 has_remove = (matching[0][0] + matching[0][2]) - matching[1][0] < 0
#                 has_add    = (matching[0][1] + matching[0][2]) - matching[1][1] < 0
#                 if has_add or has_remove:
#                     out.append("[")
#                     if has_remove:
#                         out.append("--[")
#                         for n in range(matching[0][0] + matching[0][2], matching[1][0]):
#                             out.append(text_1[n])
#                         out.append("], ")
#                     if has_add:
#                         out.append("++[")
#                         for n in range(matching[0][1] + matching[0][2], matching[1][1]):
#                             out.append(text_2[n])
#                         out.append("]")
#                     out.append("]")
#             draw.pop()
#             draw(img)
#             img.save(filename='image.png')
#             return "".join(out).replace("\u10F6", "")

def diff(text_1: str, text_2: str):
    text_1 = "\u10F6" + text_1  # otherwise edits without matching preceding text are not shown
    text_2 = "\u10F6" + text_2
    out = []
    matched_blocks = lev.matching_blocks(lev.editops(text_1, text_2), text_1, text_2)
    for i, matching in enumerate(zip(matched_blocks, matched_blocks[1:] + [0])):
        if matching[0][2] == 0:
            continue
        if matching[0][0] > 0 and i == 0:
            out.append("[--[")
            for n in range(matching[0][0]):
                out.append(text_1[n])
            out.append("], ++[")
            for n in range(matching[0][0]):
                out.append(text_2[n])
            out.append("]]")
        for n in range(matching[0][2]):
            out.append(text_1[n+matching[0][0]])
        has_remove = (matching[0][0] + matching[0][2]) - matching[1][0] < 0
        has_add    = (matching[0][1] + matching[0][2]) - matching[1][1] < 0
        if has_add or has_remove:
            out.append("[")
            if has_remove:
                out.append("--[")
                for n in range(matching[0][0] + matching[0][2], matching[1][0]):
                    out.append(text_1[n])
                out.append("], ")
            if has_add:
                out.append("++[")
                for n in range(matching[0][1] + matching[0][2], matching[1][1]):
                    out.append(text_2[n])
                out.append("]")
            out.append("]")
    return "".join(out).replace("\u10F6", "")


def edit_ratio(text_1: str, text_2: str):
    matched_blocks = lev.matching_blocks(lev.editops(text_1, text_2), text_1, text_2)
    return len(matched_blocks) / (len(text_1.split(" ")) + len(text_2.split(" "))) / 2


# def diff_latex(text_1: str, text_2: str):
#     text_1 = "\u10F6" + text_1  # otherwise edits without matching preceding text are not shown
#     text_2 = "\u10F6" + text_2
#     initial = ["\\documentclass[12pt]{article}\n\\usepackage[scaled]{helvet}\n\\usepackage[text={8.5in,200in}]{geometry}\n\\renewcommand\\familydefault{\sfdefault}\n\\usepackage[T1]{fontenc}\n\\usepackage{xspace}\n\\usepackage{xcolor}\n\\usepackage[hidelinks]{hyperref}\n\\usepackage{soul}\n\n\\definecolor{added}{RGB}{176, 195, 79}\n\\definecolor{removed}{RGB}{221, 96, 120}\n\n\\newcommand{\\rcadded}[1]{\\sethlcolor{added}\\hl{\\textbf{#1}}}\n\n\\newcommand{\\rcremoved}[1]{\\sethlcolor{removed}\\hl{\\textbf{#1}}}\n\n\\topmargin=-1.1in\n\\oddsidemargin=-0.5in\n\\textwidth=7.5in\n\\footskip=0.3in\n\n\\begin{document}\n\\raggedright\n\\Large\n\\newdimen\\height\n\n\\setbox0=\\vbox{"]
#     out = []
#     matched_blocks = lev.matching_blocks(lev.editops(text_1, text_2), text_1, text_2)
#     for i, matching in enumerate(zip(matched_blocks, matched_blocks[1:] + [0])):
#         if matching[0][2] == 0:
#             continue
#         if matching[0][0] > 0 and i == 0:
#             out.append("\\rcremoved{-{}-")
#             for n in range(matching[0][0]):
#                 out.append(text_1[n])
#             out.append("}, \\rcadded{++")
#             for n in range(matching[0][0]):
#                 out.append(text_2[n])
#             out.append("}")
#         for n in range(matching[0][2]):
#             out.append(text_1[n+matching[0][0]])
#         has_remove = (matching[0][0] + matching[0][2]) - matching[1][0] < 0
#         has_add    = (matching[0][1] + matching[0][2]) - matching[1][1] < 0
#         # if has_add or has_remove:
#         # out.append("[")
#         if has_remove:
#             out.append("\\rcremoved{-{}-")
#             for n in range(matching[0][0] + matching[0][2], matching[1][0]):
#                 out.append(text_1[n])
#             out.append("}")
#         if has_add:
#             out.append("\\rcadded{++")
#             for n in range(matching[0][1] + matching[0][2], matching[1][1]):
#                 out.append(text_2[n])
#             out.append("}")
#         # out.append("]")
#     out = initial + out + ["}"] + out
#     out.append("\n\\height=\\ht0 \\advance\\height by \\dp0\n\\newlength\\finallength\\setlength{\\finallength}{\\height plus 200pt minus 100pt}\n\\addtolength{\\finallength}{0.9in}\n\\pdfpageheight=\\finallength\n\\end{document}")
#     current_datetime = str(datetime.datetime.now())
#     current_datetime = current_datetime.replace("-", "")
#     current_datetime = current_datetime.replace(":", "")
#     current_datetime = current_datetime.replace(".", "")
#     current_datetime = current_datetime.replace(" ", "_")
#     filename = f"/Users/macbookpro/rcbot/tex_files/{current_datetime}/"
#     os.mkdir(filename)
#     with open(f"{filename}{current_datetime}.tex", "w+") as f:
#         f.write("".join(out).replace("\u10F6", ""))
#     os.chdir(filename)
#     os.system(f"pdflatex {filename}{current_datetime}.tex")
#     shutil.copy2(f"{filename}{current_datetime}.pdf", os.path.realpath("/Users/macbookpro/rcbot/text_images/"))
#     images = pdf2image.convert_from_path(f"/Users/macbookpro/rcbot/text_images/{current_datetime}.pdf", output_folder="/Users/macbookpro/rcbot/text_images/", fmt='png', output_file=current_datetime, single_file=True)
#     shutil.rmtree("/Users/macbookpro/rcbot/tex_files/")
#     os.mkdir("/Users/macbookpro/rcbot/tex_files/")
#     return filename


def diff_latex__no_render__no_header(text_1: str, text_2: str):
    text_1 = "\u10F6" + text_1  # otherwise edits without matching preceding text are not shown
    text_2 = "\u10F6" + text_2
    out = []
    matched_blocks = lev.matching_blocks(lev.editops(text_1, text_2), text_1, text_2)
    for i, matching in enumerate(zip(matched_blocks, matched_blocks[1:] + [0])):
        if matching[0][2] == 0:
            continue
        if matching[0][0] > 0 and i == 0:
            out.append("\\rcremoved{-{}-")
            for n in range(matching[0][0]):
                out.append(text_1[n])
            out.append("}, \\rcadded{++")
            for n in range(matching[0][0]):
                out.append(text_2[n])
            out.append("}")
        for n in range(matching[0][2]):
            out.append(text_1[n+matching[0][0]])
        has_remove = (matching[0][0] + matching[0][2]) - matching[1][0] < 0
        has_add    = (matching[0][1] + matching[0][2]) - matching[1][1] < 0
        if has_remove:
            out.append("\\rcremoved{-{}-")
            for n in range(matching[0][0] + matching[0][2], matching[1][0]):
                out.append(text_1[n])
            out.append("}")
        if has_add:
            out.append("\\rcadded{++")
            for n in range(matching[0][1] + matching[0][2], matching[1][1]):
                out.append(text_2[n])
            out.append("}")
    if out[len(out) - 1] == "\\vspace{5pt}\\hrule\\vspace{5pt}":
        del out[len(out) - 1]
    return "".join(out).replace("\u10F6", "")


def diff_latex__bulk_diff__no_render__no_header(text_1: str, text_2: str):
    text_1 = "\u10F6" + text_1  # otherwise edits without matching preceding text are not shown
    text_2 = "\u10F6" + text_2
    out = []
    text_1_split = text_1.split("\\vspace{5pt}\\hrule\\vspace{5pt}")
    text_2_split = text_2.split("\\vspace{5pt}\\hrule\\vspace{5pt}")
    for t1, t2 in itertools.zip_longest(text_1_split, text_2_split):
        removed_temp = []
        for x in t1.split("\n"):
            if x != "":
                if x != "\\vspace{5pt}\\hrule\\vspace{5pt}":
                    removed_temp.append("\\rcremoved{-{}-")
                    removed_temp.append(x)
                    removed_temp.append("}")
                else:
                    removed_temp.append(x)
            removed_temp.append("\n\n")
        out.append("".join(removed_temp))
        added_temp = []
        for x in t2.split("\n"):
            if x != "":
                if x != "\\vspace{5pt}\\hrule\\vspace{5pt}":
                    added_temp.append("\\rcadded{++")
                    added_temp.append(x)
                    added_temp.append("}")
                else:
                    added_temp.append(x)
            added_temp.append("\n\n")
        out.append("".join(added_temp))
        if len(t1) > 1 or len(t2) > 1:
            out.append("\\vspace{5pt}\\hrule\\vspace{5pt}")
    if out[len(out) - 1] == "\\vspace{5pt}\\hrule\\vspace{5pt}":
        del out[len(out) - 1]
    return "".join(out).replace("\u10F6", "")


def diff_latex__add_header_footer(text):
    initial = ["\\documentclass[12pt]{article}\n\\usepackage[scaled]{helvet}\n\\usepackage[text={8.5in,200in}]{geometry}\n\\renewcommand\\familydefault{\sfdefault}\n\\usepackage[T1]{fontenc}\n\\usepackage{xspace}\n\\usepackage{xcolor}\n\\usepackage[hidelinks]{hyperref}\n\\usepackage{soul}\n\n\\definecolor{added}{RGB}{176, 195, 79}\n\\definecolor{removed}{RGB}{221, 96, 120}\n\n\\newcommand{\\rcadded}[1]{\\sethlcolor{added}\\hl{\\textbf{#1}}}\n\n\\newcommand{\\rcremoved}[1]{\\sethlcolor{removed}\\hl{\\textbf{#1}}}\n\n\\topmargin=-1.1in\n\\oddsidemargin=-0.5in\n\\textwidth=7.5in\n\\footskip=0.3in\n\n\\begin{document}\n\\raggedright\n\\Large\n\\newdimen\\height\n\n\\setbox0=\\vbox{"]
    out = [text]
    out = initial + out + ["}"] + out
    out.append("\n\\height=\\ht0 \\advance\\height by \\dp0\n\\newlength\\finallength\\setlength{\\finallength}{\\height plus 200pt minus 100pt}\n\\addtolength{\\finallength}{0.9in}\n\\pdfpageheight=\\finallength\n\\end{document}")
    return "".join(out).replace("\u10F6", "")


def latex_render(text: str):
    current_datetime = str(datetime.datetime.now())
    current_datetime = current_datetime.replace("-", "")
    current_datetime = current_datetime.replace(":", "")
    current_datetime = current_datetime.replace(".", "")
    current_datetime = current_datetime.replace(" ", "_")
    filename = f"/Users/macbookpro/rcbot/tex_files/{current_datetime}/"
    os.mkdir(filename)
    with open(f"{filename}{current_datetime}.tex", "w+") as f:
        f.write(text)
    os.chdir(filename)
    subprocess.check_call(["pdflatex", f"{filename}{current_datetime}.tex"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    shutil.copy2(f"{filename}{current_datetime}.pdf", os.path.realpath("/Users/macbookpro/rcbot/text_images/"))
    images = pdf2image.convert_from_path(f"/Users/macbookpro/rcbot/text_images/{current_datetime}.pdf", output_folder="/Users/macbookpro/rcbot/text_images/", fmt='png', output_file=current_datetime, single_file=True)
    shutil.rmtree("/Users/macbookpro/rcbot/tex_files/")
    os.mkdir("/Users/macbookpro/rcbot/tex_files/")
    return current_datetime


def diff_latex(text_1: str, text_2: str):
    # print(edit_ratio(text_1, text_2))
    if edit_ratio(text_1, text_2) > 0.15:
        return latex_render(diff_latex__add_header_footer(diff_latex__bulk_diff__no_render__no_header(text_1, text_2)))
        # print(diff_latex__add_header_footer(text_1, text_2).replace("\n", "\\n\n"))
    else:
        return latex_render(diff_latex__add_header_footer(diff_latex__no_render__no_header(text_1, text_2)))


class Revision:
    __text: str = ""
    parent_id: int = 0
    __initialized: bool = False

    def __init__(self, text, parent_id: int = 0):
        self.__text = text
        self.parent_id = parent_id
        self.__initialized = True

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        if not self.__initialized:
            self.__text = text
        else:
            raise RevisionUnchangeableError()
        # return Revision(text, rev_id + 1)

    @property
    def initialized(self):
        return self.__initialized

    @initialized.setter
    def initialized(self, initialized):
        if not self.initialized:
            self.__initialized = initialized
        else:
            raise RevisionUnchangeableError()

    def __hash__(self):
        return hash((self.__text, self.parent_id, self.__initialized, id(self)))


class Policy:
    revisions: typing.List[Revision]
    policy_id: int
    selected: int
    title: str
    text: str

    def __init__(self, title, text, policy_id: int):
        self.policy_id = policy_id
        self.selected = 0
        self.title = title
        self.revisions = [Revision(text, 0)]

    def __len__(self):
        return len(self.revisions)

    def __getitem__(self, index: int):
        return self.revisions[index]

    # @property
    # def selected(self):
    #     return self.revisions[self.selected]

    # @selected.setter
    # def selected(self, selected):
    #     self.selected = selected

    @property
    def text(self):
        return self.revisions[self.selected].text

    @text.setter
    def text(self, text):
        self.revisions.append(Revision(text, self.selected))
        self.selected = len(self.revisions) - 1

    def diff(self, index_1: int, index_2: int):
        return diff(self.revisions[index_1].text, self.revisions[index_2].text)

    def diff_latex(self, index_1: int, index_2: int):
        file_id = diff_latex(self.revisions[index_1].text, self.revisions[index_2].text)
        global_.latex_render_dict["policy"][hash(self)] = file_id
        return file_id

    def __repr__(self, spacing: str = ""):
        return spacing + "policy <" + self.title + ">\n" + "\n".join([spacing*2 + "\" " + x for x in textwrap.wrap(self.text)])

    def __hash__(self):
        return hash((tuple(self.revisions), self.policy_id, self.selected, self.title, id(self)))


class Section:
    policy_order: typing.List[int]
    policies_by_id: typing.List[Policy]
    name: str
    policies: typing.List[typing.Any]

    def __init__(self, name):
        self.name = name
        self.policy_order = []
        self.policies_by_id = []

    def __len__(self):
        return len(self.policies_by_id)

    def __getitem__(self, index: int):
        return self.policies_by_id[self.policy_order[index]]

    def copy(self, index: int):
        self.sections.insert(index, self.policies_by_id[self.policy_order[index]])
        return index + 1

    def delete(self, index: int):
        del self.policies_by_id[self.policy_order[index]]
        del self.policy_order[index]

    def __delitem__(self, index: int):
        del self.policies_by_id[self.policy_order[index]]
        del self.policy_order[index]

    def swap(self, index_1: int, index_2: int):
        temp = self.policy_order[index_1]
        self.policy_order[index_1] = self.policy_order[index_2]
        self.policy_order[index_2] = temp

    def add(self, title: str, name: str, index: int = -1):
        global_.policy_id += 1
        if index == -1:
            self.policies_by_id.append(Policy(title, name, global_.policy_id))
            self.policy_order.append(len(self.policies_by_id)-1)
            return len(self.policy_order) - 1
        else:
            self.policies_by_id.append(Policy(title, name, global_.policy_id))
            self.policy_order.insert(index, len(self.policies_by_id)-1)
            return index + 1

    def diff(self, index_1: int, index_2: int):
        return diff(self.policies_by_id[self.policy_order[index_1]].text, self.policies_by_id[self.policy_order[index_2]].text)

    def diff_latex(self, index_1: int, index_2: int):
        file_id = diff_latex(self.policies_by_id[self.policy_order[index_1]].text, self.policies_by_id[self.policy_order[index_2]].text)
        global_.latex_render_dict["section"][hash(self)] = file_id
        return file_id

    def get_with_policies(self, policy_start: int, policy_length: int, section_number: int = -1):
        out = [[]]
        if section_number < 0:
            out[0].append(f"Section {section_number} {self.name}\n\n")
        else:
            out[0].append(f"Section {self.name}\n\n")
        out[0].append("\\vspace{5pt}\\hrule\\vspace{5pt}")
        out[0].append("\n\n")
        out[0] = "".join(out[0])
        for i in range(policy_start, policy_start + policy_length):
            if i > len(self.policy_order) - 1:
                # if (out[i][len(out[i]) - 1] == "\n\n\\vspace{5pt}\\hrule\\vspace{5pt}\n\n"):
                #     del out[i][len(out[i]) - 1]
                #     out[i].append("\n\n")
                #     out[i] = "".join(out[i])
                break
            p = self.policies_by_id[self.policy_order[i]]
            out.append([])
            out[i+1].append(p.title)
            out[i+1].append("\n\n\\vspace{5pt}\\hrule\\vspace{5pt}\n\n")
            out[i+1].append(p.text)
            out[i+1].append("\n\n\\vspace{5pt}\\hrule\\vspace{5pt}\n\n")
            out[i+1] = "".join(out[i+1])
        return out

    def __repr__(self, spacing: str = ""):
        return spacing + "section <" + str(self.name) + "> {\n" + spacing + ("\n" + spacing).join([self.policies_by_id[x].__repr__(spacing + "\t") for x in self.policy_order]) + f"\n{spacing}\t}}"

    def __hash__(self):
        return hash((tuple(self.policy_order), tuple(self.policies_by_id), self.name, id(self)))


class Branch:
    sections: typing.List[Section]
    name: str

    def __init__(self, name):
        self.name = name
        self.sections = []

    def __len__(self):
        return len(self.sections)

    def __getitem__(self, index: int):
        return self.sections[index]

    def copy(self, index: int):
        self.sections.insert(index, self.sections[index])
        return index + 1

    def delete(self, index: int):
        del self.sections[index]

    def __delitem__(self, index: int):
        del self.sections[index]

    def swap(self, index_1: int, index_2: int):
        temp = self.sections[index_1]
        self.sections[index_1] = self.sections[index_2]
        self.sections[index_2] = temp

    def add(self, name: str, index: int = -1):
        if index == -1:
            self.sections.append(Section(name))
            return len(self.sections) - 1
        else:
            self.sections.insert(index, Section(name))
            return index

    def diff(self, index_1: int, index_2: int, policy_start: int = 0, policy_range: int = 1):
        return diff(self.sections[index_1].get_with_policies(policy_start, policy_range, index_1), self.sections[index_2].get_with_policies(policy_start, policy_range, index_2))

    def diff_latex(self, index_1: int, index_2: int, policy_start: int = 0, policy_range: int = 1):
        # diff_latex()
        text_1 = self.sections[index_1].get_with_policies(policy_start, policy_range, index_1)
        text_2 = self.sections[index_2].get_with_policies(policy_start, policy_range, index_2)
        text_out = []
        for i, text in enumerate(itertools.zip_longest(text_1, text_2)):
            if edit_ratio(text[0], text[1]) > 0.15:
                text_out.append(diff_latex__bulk_diff__no_render__no_header(text[0], text[1]))
            else:
                text_out.append(diff_latex__no_render__no_header(text[0], text[1]))
            # if i == max(len(text_1), len(text_2)) - 1:  # trying to remove the last \hrule but i can't seem to
            #     "".join(text_out[len(text_out)-1].rsplit("\\vspace{5pt}\\hrule\\vspace{5pt}", 1))
        file_id = latex_render(diff_latex__add_header_footer("".join(text_out)))
        global_.latex_render_dict["branch"][hash(self)] = file_id
        return file_id

    def __repr__(self, spacing: str = ""):
        return spacing + "branch <" + str(self.name) + "> {\n" + spacing + ("\n" + spacing).join([x.__repr__(spacing) for x in self.sections]) + f"\n{spacing}}}"

    def __hash__(self):
        return hash((tuple(self.sections), self.name, id(self)))


class Platform:
    branches: typing.List[Branch]

    def __init__(self):
        self.branches = [Branch("platform master branch"), Branch("master change buffer")]

    # @property
    # def branches(self) -> None:
    #     raise PermissionError()

    # @branches.setter
    # def branches(self, branches) -> None:
    #     raise PermissionError()

    def __len__(self) -> int:
        return len(self.branches)

    def __getitem__(self, index: int) -> Branch:
        return self.branches[index]

    def fork(self, branch: int, name: str = "") -> int:
        self.branches.append(copy.deepcopy(self.branches[branch]))
        if name != "":
            self.branches[len(self.branches)-1].name = name
        return len(self.branches) - 1

    def delete(self, index: int):
        del self.branches[index]

    def __delitem__(self, index: int):
        del self.branches[index]

    def __repr__(self):
        return "{\n" + "\n".join([x.__repr__("\t") for x in self.branches]).replace("\t", ".  ") + "\n}"

    def __hash__(self):
        return hash((self.branches, id(self)))


p = Platform()
i = p.fork(1, "test")
p[i].add("foo")
p[i].add("bar")
p[i].add("bat", 1)
p[i][0].add("one"   , "1 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][0].add("two"   , "abc def 2 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][0].add("three" , "abc def abc def 3 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][1].add("four"  , "abc def abc def abc def 4 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][1].add("five"  , "abc def abc def abc def abc def 5 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][1].add("six"   , "abc def abc def abc def abc def abc def 6 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][2].add("seven" , "abc def abc def abc def abc def abc def abc def 7 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][2].add("eight" , "abc def abc def abc def abc def abc def abc def abc def 8 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
p[i][2].add("nine"  , "abc def abc def abc def abc def abc def abc def abc def abc def 9 abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def abc def")
# print(p)
p[i].swap(0, 2)
# print(p)
p[i][2][0].text = "The result is a list of triples (operation, spos, dpos), where operation is one of 'equal', 'replace', 'insert', or 'delete'; spos and dpos are position of characters in the first (source) and the second (destination) strings. These are operations on signle characters. In fact the returned list doesn't contain the 'equal', but all the related functions accept both lists with and without 'equal's."
p[i][2][0].text = "Blah. The result is a list of tuples (operation, startpos, destpos), where operation is one of 'equal', 'replace', 'insert', or 'delete'; startpos and destpos are position of characters in the first (source) and the second (destination) strings. The returned list doesn't contain the 'equal', but all the related functions accept both lists with and without 'equal's. These are operations on single characters."
print(p[i].diff_latex(1, 2, 0, 10))
print(p[i][2][0].diff_latex(1, 2))
print(global_.latex_render_dict)
