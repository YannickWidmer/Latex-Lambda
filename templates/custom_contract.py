
# convert html document to LaTeX
# import lxml.html # http://lxml.de/lxmlhtml.html
from lxml import etree
from io import StringIO, BytesIO


tag_to_command={
    'h1': 'section',
    'h2': 'subsection',
    'h3': 'subsubsection'
}

def html2latex(el): # fill in this function to catch and convert html tags
    result = []
    if el.text:
        result.append(el.text)
    for sel in el:
        if False: # get info
            print('tag',sel.tag)
            print('text',sel.text)
            print('tail',sel.tail)
            print('attrib',sel.attrib)
        if sel.tag in tag_to_command:
            result.append('\\' + tag_to_commandsection[sel.tag] + '{' + html2latex(sel) + '}')
        elif sel.tag in ["td", "table"]:
            result.append("<%s>" % sel.tag)
            result.append(html2latex(sel))
            result.append("</%s>" % sel.tag)
        elif sel.tag in ["span"]:  #
            for att in sel.attrib.keys():
                if att =='style':
                    if sel.attrib[att] == 'font-style:italic':
                        result.append(r'\textit{%s}' % (html2latex(sel)))
                    elif sel.attrib[att] == 'font-style:bold':
                        result.append(r'\textbf{%s}' % (html2latex(sel)))
        else:
            result.append(html2latex(sel))
        if sel.tail:
            result.append(sel.tail)
    return "".join(result)

html = u'''
<!DOCTYPE html>
    <html>
  <head>
    <title></title>
  </head>
<body >
  <h1 class="hmchapter" data-hmvarbodychaptertitle = "My title">My title</h1>
  text <span style="font-style:italic">in a specific context</span> and more.
</body>
</html>
'''

def convert_html(html):
    # must be unicode or lxml parse crashes
    parser = etree.HTMLParser()
    tree   = etree.parse(StringIO(html), parser) # expects a file, use StringIO for string
    root = tree.getroot()
    latex = html2latex(root)
    return latex


def render(data, to_pdf):
    if to_pdf and 'upload'  not in data and 'htlm' not in data:
        raise ValueError('A pdf or html must be specified. Upload a pdf to s3 and pass a file argument with a dict containing as key custom_upload_contract and the location in s3 as value or add a property html with html value in data.')
    if 'upload' in data and 'html' in data:
        raise ValueError('Either specify a pdf or send html not both')
    if 'html' in data:
            data['html'] = convert_html(data['html'])

    return data