import enum


@enum.unique
class PandocFormat(enum.Enum):
    commonmark = 'commonmark'
    commonmark_x = 'commonmark_x'
    docx = 'docx'
    gfm = 'gfm'
    html = 'html'
    html4 = 'html4'
    html5 = 'html5'
    ipynb = 'ipynb'
    json = 'json'
    latex = 'latex'
    markdown = 'markdown'
    markdown_github = 'markdown_github'
    markdown_mmd = 'markdown_mmd'
    markdown_phpextra = 'markdown_phpextra'
    markdown_strict = 'markdown_strict'
    pdf = 'pdf'
    plain = 'plain'

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'


@enum.unique
class PandocInputFormat(enum.Enum):
    commonmark = PandocFormat.commonmark.value
    commonmark_x = PandocFormat.commonmark_x.value
    docx = PandocFormat.docx.value
    gfm = PandocFormat.gfm.value
    html = PandocFormat.html.value
    ipynb = PandocFormat.ipynb.value
    json = PandocFormat.json.value
    latex = PandocFormat.latex.value
    markdown = PandocFormat.markdown.value
    markdown_github = PandocFormat.markdown_github.value
    markdown_mmd = PandocFormat.markdown_mmd.value
    markdown_phpextra = PandocFormat.markdown_phpextra.value
    markdown_strict = PandocFormat.markdown_strict.value

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'

@enum.unique
class PandocOutputFormat(enum.Enum):
    commonmark = PandocFormat.commonmark.value
    commonmark_x = PandocFormat.commonmark_x.value
    docx = PandocFormat.docx.value
    gfm = PandocFormat.gfm.value
    html = PandocFormat.html.value
    html4 = PandocFormat.html4.value
    html5 = PandocFormat.html5.value
    ipynb = PandocFormat.ipynb.value
    json = PandocFormat.json.value
    latex = PandocFormat.latex.value
    markdown = PandocFormat.markdown.value
    markdown_github = PandocFormat.markdown_github.value
    markdown_mmd = PandocFormat.markdown_mmd.value
    markdown_phpextra = PandocFormat.markdown_phpextra.value
    markdown_strict = PandocFormat.markdown_strict.value
    pdf = PandocFormat.pdf.value
    plain = PandocFormat.plain.value

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'
