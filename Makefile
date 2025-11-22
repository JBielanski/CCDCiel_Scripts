# Makefile for compiling and installing CCDCiel Python scripts
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# Usage:
#   make                # Compile and install the main script (focuser_position_per_filter)
#   make all            # Compile and install all scripts
#   make additional     # Compile and install additional scripts
#   make additional_indi # Compile and install additional scripts with INDI dependency
#   make clean          # Clean up generated files
#

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

# --- MAIN TARGETS ---
main: focuser_position_per_filter.pyc install_focuser_position_per_filter

# Build all main targets
all: main additional additional_indi

# Compile Python 'focuser_position_per_filter.py' script to bytecode
focuser_position_per_filter.pyc: focuser_position_per_filter.py
	$(PYTHON) -m compileall $<

# Create a focuser_position_per_filter.script
focuser_position_per_filter.script: __pycache__/focuser_position_per_filter.cpython-$(PYTHON_VERSION).pyc focuser_position_per_filter.py
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy $< $@; \
		copy $(word 2,$^) $@; \
		echo "No chmod on Windows"; \
	else \
		#cp $< $@; \
		cp $(word 2,$^) $@; \
		chmod +x $@; \
	fi

# Install script to ccdciel scripts directory
install_focuser_position_per_filter: focuser_position_per_filter.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy $< $(CCDCIEL_DIR)\\$<; \
		dir $(CCDCIEL_DIR)\\$<; \
	else \
		cp $< $(CCDCIEL_DIR)/$<; \
		ls -la $(CCDCIEL_DIR)/$<; \
	fi

# --- ADDITIONAL TARGETS ---

additional: camera_warm_up.pyc install_camera_warm_up log_focuser_position.pyc install_log_focuser_position log_filters_wheel_position.pyc install_log_filters_wheel_position

# Compile Python 'camera_warm_up.py' script to bytecode
camera_warm_up.pyc: camera_warm_up.py
	$(PYTHON) -m compileall $<

# Create a camera_warm_up.script
camera_warm_up.script: __pycache__/camera_warm_up.cpython-$(PYTHON_VERSION).pyc camera_warm_up.py
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy $< $@; \
		copy $(word 2,$^) $@; \
		echo "No chmod on Windows"; \
	else \
		#cp $< $@; \
		cp $(word 2,$^) $@; \
		chmod +x $@; \
	fi

# Install script to ccdciel scripts directory
install_camera_warm_up: camera_warm_up.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy $< $(CCDCIEL_DIR)\\$<; \
		dir $(CCDCIEL_DIR)\\$<; \
	else \
		cp $< $(CCDCIEL_DIR)/$<; \
		ls -la $(CCDCIEL_DIR)/$<; \
	fi

# Compile Python 'log_focuser_position.py' script to bytecode
log_focuser_position.pyc: log_focuser_position.py
	$(PYTHON) -m compileall $<

# Create a log_focuser_position.script
log_focuser_position.script: __pycache__/log_focuser_position.cpython-$(PYTHON_VERSION).pyc log_focuser_position.py
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy $< $@; \
		copy $(word 2,$^) $@; \
		echo "No chmod on Windows"; \
	else \
		#cp $< $@; \
		cp $(word 2,$^) $@; \
		chmod +x $@; \
	fi

# Install script to ccdciel scripts directory
install_log_focuser_position: log_focuser_position.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy $< $(CCDCIEL_DIR)\\$<; \
		dir $(CCDCIEL_DIR)\\$<; \
	else \
		cp $< $(CCDCIEL_DIR)/$<; \
		ls -la $(CCDCIEL_DIR)/$<; \
	fi

# Compile Python 'log_filters_wheel_position.py' script to bytecode
log_filters_wheel_position.pyc: log_filters_wheel_position.py
	$(PYTHON) -m compileall $<

# Create a log_filters_wheel_position.script
log_filters_wheel_position.script: __pycache__/log_filters_wheel_position.cpython-$(PYTHON_VERSION).pyc log_filters_wheel_position.py
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy $< $@; \
		copy $(word 2,$^) $@; \
		echo "No chmod on Windows"; \
	else \
		#cp $< $@; \
		cp $(word 2,$^) $@; \
		chmod +x $@; \
	fi

# Install script to ccdciel scripts directory
install_log_filters_wheel_position: log_filters_wheel_position.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy $< $(CCDCIEL_DIR)\\$<; \
		dir $(CCDCIEL_DIR)\\$<; \
	else \
		cp $< $(CCDCIEL_DIR)/$<; \
		ls -la $(CCDCIEL_DIR)/$<; \
	fi

# --- ADDITIONAL WITH INDI DEPENDENCY TARGETS ---

additional_indi: end_session_indi.pyc install_end_session_indi iEQ_scope_go_home_indi.pyc install_iEQ_scope_go_home_indi pegasus_SPB_set_dews_AB_to_zero_indi.pyc install_pegasus_SPB_set_dews_AB_to_zero_indi

# Compile Python 'end_session_indi.py' script to bytecode
end_session_indi.pyc: end_session_indi.py
	$(PYTHON) -m compileall  $<

# Create a end_session_indi.script
end_session_indi.script: __pycache__/end_session_indi.cpython-$(PYTHON_VERSION).pyc end_session_indi.py
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy $< $@; \
		copy $(word 2,$^) $@; \
		echo "No chmod on Windows"; \
	else \
		#cp $< $@; \
		cp $(word 2,$^) $@; \
		chmod +x $@; \
	fi

# Install script to ccdciel scripts directory
install_end_session_indi: end_session_indi.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy $< $(CCDCIEL_DIR)\\$<; \
		dir $(CCDCIEL_DIR)\\$<; \
	else \
		cp $< $(CCDCIEL_DIR)/$<; \
		ls -la $(CCDCIEL_DIR)/$<; \
	fi

# Compile Python 'iEQ_scope_go_home_indi.py' script to bytecode
iEQ_scope_go_home_indi.pyc: iEQ_scope_go_home_indi.py
	$(PYTHON) -m compileall $<

# Create a iEQ_scope_go_home_indi.script
iEQ_scope_go_home_indi.script: __pycache__/iEQ_scope_go_home_indi.cpython-$(PYTHON_VERSION).pyc iEQ_scope_go_home_indi.py
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy $< $@; \
		copy $(word 2,$^) $@; \
		echo "No chmod on Windows"; \
	else \
		#cp $< $@; \
		cp $(word 2,$^) $@; \
		chmod +x $@; \
	fi

# Install script to ccdciel scripts directory
install_iEQ_scope_go_home_indi: iEQ_scope_go_home_indi.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy $< $(CCDCIEL_DIR)\\$<; \
		dir $(CCDCIEL_DIR)\\$<; \
	else \
		cp $< $(CCDCIEL_DIR)/$<; \
		ls -la $(CCDCIEL_DIR)/$<; \
	fi

# Compile Python 'pegasus_SPB_set_dews_AB_to_zero_indi.py' script to bytecode
pegasus_SPB_set_dews_AB_to_zero_indi.pyc: pegasus_SPB_set_dews_AB_to_zero_indi.py
	$(PYTHON) -m compileall $<

# Create a pegasus_SPB_set_dews_AB_to_zero_indi.script
pegasus_SPB_set_dews_AB_to_zero_indi.script: __pycache__/pegasus_SPB_set_dews_AB_to_zero_indi.cpython-$(PYTHON_VERSION).pyc pegasus_SPB_set_dews_AB_to_zero_indi.py
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy $< $@; \
		copy $(word 2,$^) $@; \
		echo "No chmod on Windows"; \
	else \
		#cp $< $@; \
		cp $(word 2,$^) $@; \
		chmod +x $@; \
	fi

# Install script to ccdciel scripts directory
install_pegasus_SPB_set_dews_AB_to_zero_indi: pegasus_SPB_set_dews_AB_to_zero_indi.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy $< $(CCDCIEL_DIR)\\$<; \
		dir $(CCDCIEL_DIR)\\$<; \
	else \
		cp $< $(CCDCIEL_DIR)/$<; \
		ls -la $(CCDCIEL_DIR)/$<; \
	fi

# Clean up generated files
clean:
	@if [ -d "__pycache__" ]; then \
		rm -rf __pycache__; \
	fi
	@if [ -f "focuser_position_per_filter.script" ]; then \
		rm -f focuser_position_per_filter.script; \
	fi
	@if [ -f "camera_warm_up.script" ]; then \
		rm -f camera_warm_up.script; \
	fi
	@if [ -f "log_focuser_position.script" ]; then \
		rm -f log_focuser_position.script; \
	fi
	@if [ -f "log_filters_wheel_position.script" ]; then \
		rm -f log_filters_wheel_position.script; \
	fi
	@if [ -f "end_session_indi.script" ]; then \
		rm -f end_session_indi.script; \
	fi
	@if [ -f "iEQ_scope_go_home_indi.script" ]; then \
		rm -f iEQ_scope_go_home_indi.script; \
	fi
	@if [ -f "pegasus_SPB_set_dews_AB_to_zero_indi.script" ]; then \
		rm -f pegasus_SPB_set_dews_AB_to_zero_indi.script; \
	fi


