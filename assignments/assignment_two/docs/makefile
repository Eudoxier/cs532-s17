PROJECT=assignment_two
BIBTEX=bibtex
OUTDIR = ../../../pelican/pdfs/
TEXDIR = .

# Pygment files
PFILE = $(PROJECT).pyg
OFILE = $(PROJECT).out.pyg

# The compiler and the -output-directory flag
TCC = pdflatex

# Mode options = nonstopmode, batchmode, scrollmode, errorstopmode
MODE = nonstopmode
TEXFLAGS = -interaction $(MODE) -halt-on-error -file-line-error -shell-escape

all: documentation clean

documentation:
	$(TCC) $(TEXFLAGS) $(TEXDIR)/$(PROJECT).tex 
	$(TCC) $(TEXFLAGS) $(TEXDIR)/$(PROJECT).tex 
	$(TCC) $(TEXFLAGS) $(TEXDIR)/$(PROJECT).tex 


clean:
	touch $(PROJECT).pdf
	cp $(PROJECT).pdf $(OUTDIR)
	rm -f $(PROJECT).aux
	rm -f $(PROJECT).bcf
	rm -f $(PROJECT).log
	rm -f $(PROJECT).out
	rm -f $(PROJECT).run.xml
	rm -f $(PROJECT).pyg
