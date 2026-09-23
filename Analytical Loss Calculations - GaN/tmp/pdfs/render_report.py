import pymupdf
from pathlib import Path
d=pymupdf.open('LOSS_MODELING.pdf')
text=''.join(p.get_text() for p in d)
assert len(d)==4
assert 'Contents' not in text and 'parallel' not in text.lower()
for n,p in enumerate(d,1):
    p.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save(f'tmp/pdfs/report-{n}.png')
print('Four pages rendered; no contents or paralleling sections.')
