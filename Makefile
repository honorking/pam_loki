LIB_SRC_PATH=pam-python-1.0.4

.PHONY:	all
all:    lib

.PHONY: lib
lib:
	$(MAKE) --directory $(LIB_SRC_PATH) $@

.PHONY: install
install:
	$(MAKE) --directory $(LIB_SRC_PATH) install-lib

.PHONY: clean
clean:
	$(MAKE) --directory $(LIB_SRC_PATH) $@
