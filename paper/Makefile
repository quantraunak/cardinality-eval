all: cardinality.pdf

figures/cardinality.pdf: make_figures.py
	python3 make_figures.py

cardinality.pdf: cardinality.tex figures/cardinality.pdf
	pdflatex -interaction=nonstopmode cardinality.tex >/dev/null
	pdflatex -interaction=nonstopmode cardinality.tex >/dev/null

arxiv: cardinality.pdf
	rm -rf arxiv && mkdir -p arxiv/figures
	cp cardinality.tex arxiv/ && cp figures/cardinality.pdf arxiv/figures/
	cd arxiv && tar czf ../cardinality-arxiv.tar.gz .
	@echo "arXiv submission tarball: cardinality-arxiv.tar.gz"

clean:
	rm -f *.aux *.log *.out *.bbl *.blg

.PHONY: all arxiv clean
