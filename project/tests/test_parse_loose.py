"""The tolerant parser for the unconstrained arm. A parse failure here scores
as a recall failure, so it is tested on the exact shapes the model emits."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_decoding_arm import parse_loose, repair_quotes, json_valid

GOOD = '{"links": [{"counterparty": "Acme", "relation": "customer", "evidence": "Acme buys."}]}'


def test_valid_json_is_unchanged():
    assert parse_loose(GOOD)[0]["counterparty"] == "Acme"
    assert json_valid(GOOD)


def test_reasoning_block_is_stripped():
    assert len(parse_loose("<think>{not json}</think>\n" + GOOD)) == 1


def test_interior_quotes_are_repaired():
    bad = ('{"links": [{"counterparty": "Express Scripts, Inc. ("Express Scripts")", '
           '"relation": "customer", "evidence": "sales to Express Scripts ("ESI") rose."}]}')
    assert not json_valid(bad)
    links = parse_loose(bad)
    assert len(links) == 1
    assert links[0]["counterparty"] == 'Express Scripts, Inc. ("Express Scripts")'
    assert links[0]["evidence"] == 'sales to Express Scripts ("ESI") rose.'


def test_already_escaped_quotes_survive():
    ok = '{"links": [{"counterparty": "A \\"B\\" C", "relation": "x", "evidence": "e"}]}'
    assert parse_loose(ok)[0]["counterparty"] == 'A "B" C'


def test_repair_fails_closed():
    assert repair_quotes('{"links": [{"counterparty": "A", ') is None
    assert parse_loose("no json here at all") == []
    assert parse_loose("") == []


def test_empty_list_is_empty_not_failure():
    assert parse_loose('{"links": []}') == []
    assert json_valid('{"links": []}')
