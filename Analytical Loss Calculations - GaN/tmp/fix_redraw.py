from pathlib import Path
p=Path('waveform_plotter.py'); s=p.read_text(encoding='utf-8').replace('    for artist in list(figure.texts):\n        artist.remove()', '    for artist in list(figure.texts):\n        if artist is not getattr(figure, "_suptitle", None):\n            artist.remove()')
p.write_text(s,encoding='utf-8')
