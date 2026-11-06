install:
	pip install -r requirements.txt

test:
	python3 -m pytest -q project/tests

# The evaluation set: k link-bearing sentences injected into candidate-free
# filler, padded to a constant length. Requires the screened item bank.
# The committed evaluation set was built with 60 per level. Rebuilding overwrites
# cardinality_docs.json with different documents under the same doc_ids, so the
# cached responses would be scored against the wrong gold. Refuse unless forced.
docs:
	@test "$(FORCE)" = 1 || { echo "refusing: would overwrite the committed evaluation set (make docs FORCE=1)"; exit 1; }
	cd project && python3 scripts/build_cardinality_docs.py --per-level 60

# Both decoding arms. Needs ollama with qwen3:14b pulled.
arms:
	cd project && ./run_decoding_14b.sh

score:
	cd project && python3 scripts/score_decoding.py

.PHONY: install test docs arms score
