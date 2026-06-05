from zipfile import ZipFile
from xml.etree import ElementTree as ET
from pathlib import Path
p = Path(r'C:\Users\user\Desktop\ATUL SARASWAT_Technical Director.docx')
with ZipFile(p, 'r') as z:
    xml = z.read('word/document.xml')
root = ET.fromstring(xml)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
text = []
for node in root.iterfind('.//w:t', ns):
    if node.text:
        text.append(node.text)
print('\n'.join(text))
