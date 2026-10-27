.PHONY: score-results help

help:
	@echo "Targets:"
	@echo "  make score-results RESULTS=<path> PROFILE=<prof>   Score a results.xml with this role's exception list"

score-results:
	@test -n "$(RESULTS)" || (echo "RESULTS= path to OpenSCAP results.xml required" && exit 1)
	@test -n "$(PROFILE)" || (echo "PROFILE= required (e.g. stig, cis-l1)" && exit 1)
	@python3 scripts/score-results.py --results "$(RESULTS)" --profile "$(PROFILE)" --verify-json compliance/verify.json
