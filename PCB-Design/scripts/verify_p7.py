from pathlib import Path
source=(Path(__file__).resolve().parent/'verify_p6.py').read_text()
exec(compile(source.replace('from p6_data import *','from p7_data import *'),__file__,'exec'))
