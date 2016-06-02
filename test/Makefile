check : utils_verify segments_verify
	@echo "All Tests Passed"

define printpassfail
	{ echo "Pass" ; true ; } || { echo "Fail" ; false ; }
endef

utils_verify :
	@echo "=== start utils_verify ===>"
	python utils_verify.py && $(printpassfail)
	@echo "<=== end utils_verify ==="

segments_verify :
	@echo "=== start segments_verify ===>"
	python segments_verify.py && $(printpassfail)
	@echo "<=== end segments_verify ==="
