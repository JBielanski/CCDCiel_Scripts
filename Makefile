# Detect the operating system and set the PYTHON variable accordingly
ifeq ($(OS),Windows_NT)
	PYTHON = python
	CCDCIEL_DIR = %APPDATA%\\ccdciel
else
	PYTHON = /usr/bin/python
	ifeq ("$(wildcard $(PYTHON))","")
		PYTHON = /usr/bin/python3
		ifeq ("$(wildcard $(PYTHON))","")
			@echo "Python not found!!!";
			exit 0;
		endif
	endif
	CCDCIEL_DIR = ~/.config/ccdciel
endif
PYTHON_VERSION = $(shell $(PYTHON) -c 'import sys; print("{0[0]}{0[1]}".format(sys.version_info));')

all: focuser_position_per_filter.pyc install

# Compile Python 'focuser_position_per_filter.py' script to bytecode
focuser_position_per_filter.pyc: focuser_position_per_filter.py
	$(PYTHON) -m compileall focuser_position_per_filter.py

# Create a focuser_position_per_filter.script
focuser_position_per_filter.script: __pycache__/focuser_position_per_filter.cpython-$(PYTHON_VERSION).pyc
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy __pycache__\focuser_position_per_filter.cpython-$(PYTHON_VERSION).pyc focuser_position_per_filter.script; \
		copy focuser_position_per_filter.py focuser_position_per_filter.script; \
		echo "No chmod on Windows"; \
	else \
		#cp __pycache__/focuser_position_per_filter.cpython-$(PYTHON_VERSION).pyc focuser_position_per_filter.script; \
		cp focuser_position_per_filter.py focuser_position_per_filter.script; \
		chmod +x focuser_position_per_filter.script; \
	fi

# Install script to ccdciel scripts directory
install: focuser_position_per_filter.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy focuser_position_per_filter.script $(CCDCIEL_DIR)\\focuser_position_per_filter.script; \
		dir $(CCDCIEL_DIR)\\focuser_position_per_filter.script; \
	else \
		cp focuser_position_per_filter.script $(CCDCIEL_DIR)/focuser_position_per_filter.script; \
		ls -la $(CCDCIEL_DIR)/focuser_position_per_filter.script; \
	fi

# Clean up generated files
clean:
	@if [ -d "__pycache__" ]; then \
		rm -rf __pycache__; \
	fi
	@if [ -f "focuser_position_per_filter.script" ]; then \
		rm -f focuser_position_per_filter.script; \
	fi

