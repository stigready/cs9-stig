# Customer role repo — OpenSCAP prove + score check
.PHONY: prove score-results help

help:
	@echo "Targets:"
	@echo "  make prove RELEASE=<ver>     Docker reprove (apply role + OpenSCAP + compare to evidence)"
	@echo "  make score-results RESULTS=<path> PROFILE=<prof>   Score a results.xml using factory rules"

prove:
	@test -n "$(RELEASE)" || (echo "RELEASE= required (folder under compliance/releases/)" && exit 1)
	@./scripts/prove.sh

score-results:
	@test -n "$(RESULTS)" || (echo "RESULTS= path to OpenSCAP results.xml required" && exit 1)
	@test -n "$(PROFILE)" || (echo "PROFILE= required (e.g. stig, cis-l1)" && exit 1)
	@python3 scripts/score-results.py --results "$(RESULTS)" --profile "$(PROFILE)" --verify-json compliance/verify.json
