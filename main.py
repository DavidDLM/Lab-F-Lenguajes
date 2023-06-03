# Main.py

from processor import *

filename = "yap1.yalp"
yaparFilename = 'YAPar/' + filename
generate = 'compiler.py'
yapar = Processor(yaparFilename, generate)
yapar.compiler()
