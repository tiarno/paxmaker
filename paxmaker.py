from PyPDF2 import PdfFileReader
from string import Template
from datetime import datetime
import base64
import os

header = '\\[{pax}{0.1l}\\\\\n'
t_file = Template('''\\[{file}{\\<$name\\>}{
  Date={$date},
  Size={$size},
  }\\\\
\\[{pagenum}{$pages}\\\\
''')
t_page = Template('''\\[{page}{$page}{$x1 $y1 $x2 $y2}{}\\\\
''')
t_link = Template('''\\[{annot}{$page}{Link}{$x1 $y1 $x2 $y2}{GoTo}{
  DestLabel={$label},
  Border={[0 0 1]},
  C={[1 0 0]},
  H={/I},
}\\\\
''')
t_anchor = Template('''\\[{dest}{$page}{$label}{XYZ}{
  DestY={$y},
  DestX={$x},
}\\\\
''')
class PaxMaker(object):
    def __init__(self, name):
        self.name = name
        self.pdf = PdfFileReader(name)
        self.anchors = dict()
        self.links = dict()
        self.pages = {'links': list(), 'anchors': list()}

    def filedata(self):
        now = datetime.now()
        d = {
            'name': base64.b16encode(os.path.basename(self.name)),
            'date': now.strftime('D:%Y%m%d%H%M%S%z'),
            'size': os.path.getsize(self.name),
            'pages': self.pdf.numPages
        }
        return t_file.substitute(d)

    def get_anchors(self):
        dests = self.pdf.trailer['/Root']['/Dests']
        for dest in dests:
            self.anchors[dest] = {
                'page': dests[dest][0] + 1,
                'x': '%.3f' % dests[dest][2],
                'y': '%.3f' % dests[dest][3]
                }

    def get_links(self):
        dest_label = 1
        for i, page in enumerate(self.pdf.pages):
            annots = list()
            obj = page.getObject()
            if obj.get('/Annots'):
                annots = obj.get('/Annots').getObject()
            for annot in annots:
                data = annot.getObject()
                if data.get('/Subtype') == '/Link':
                    dest = data.get('/Dest')
                    if dest:
                        rect = data.get('/Rect')
                        self.links[dest] = {
                            'label': dest_label,
                            'x1': '%.3f' % rect[0], 'y1': '%.3f' % rect[1],
                            'x2': '%.3f' % rect[2], 'y2': '%.3f' % rect[3],
                            'page': i + 1,
                            }
                        dest_label += 1

    def merge(self):
        for i in range(self.pdf.numPages):
            for dest, data in self.links.items():
                if data['page'] == i + 1:
                    self.pages['links'].append(data)
            for dest, data in self.links.items():
                anchor = self.anchors[dest]
                if anchor['page'] == i + 1:
                    anchor['label'] = data['label']
                    self.pages['anchors'].append(anchor)

    def write(self):
        root = os.path.dirname(self.name)
        stem = os.path.splitext(os.path.basename(self.name))[0]
        paxfile = os.path.join(root, '%s.pax' % stem)
        with open(paxfile, 'w') as f:
            f.write(header)
            f.write(self.filedata())
            for i, page in enumerate(self.pdf.pages):
                size = page['/MediaBox']
                data = {
                    'page': i + 1,
                    'x1': size[0], 'y1': size[1],
                    'x2': size[2], 'y2': size[3],
                    }
                f.write(t_page.substitute(data))
                pagelinks = [x for x in self.pages['links'] if x['page'] == i + 1]
                for link in sorted(pagelinks, key=lambda x: x.get('label')):
                    d = {
                        'page': link['page'],
                        'label': link['label'],
                        'x1': link['x1'], 'y1': link['y1'],
                        'x2': link['x2'], 'y2': link['y2'],
                    }
                    f.write(t_link.substitute(d))
            for i, page in enumerate(self.pdf.pages):
                pageanchors = [x for x in self.pages['anchors'] if x['page'] == i + 1]
                for anchor in sorted(pageanchors, key=lambda x: x.get('label')):
                    d = {
                        'page': anchor['page'],
                        'label': anchor['label'],
                        'x': anchor['x'],
                        'y': anchor['y']
                    }
                    f.write(t_anchor.substitute(d))

if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    p = PaxMaker(fname)
    p.get_anchors()
    p.get_links()
    p.merge()
    p.write()
