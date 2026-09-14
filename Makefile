install:
	pip install -r requirements.txt

test:
	python3 -m pytest -q project/tests

# The evaluation set: k link-bearing sentences injected into candidate-free
# filler, padded to a constant length. Requires the screened item bank.
docs:
	cd project && python3 scripts/build_cardinality_docs.py --per-level 25

# Both decoding arms. Needs ollama with qwen3:14b pulled.
arms:
	cd project && ./run_decoding_14b.sh

score:
	cd project && python3 scripts/score_decoding.py

.PHONY: install test docs arms score
