.PHONY: dashboard public snapshot test release

dashboard:
	./scripts/run_dashboard.sh

public:
	./scripts/run_public_dashboard.sh --port 8766

snapshot:
	python3 scripts/build_public_snapshot.py

test:
	python3 -m unittest discover -s tests
	node --check dashboard/static/app.js
	bash -n scripts/run_dashboard.sh scripts/run_public_dashboard.sh scripts/share_public_dashboard.sh

release: snapshot test
