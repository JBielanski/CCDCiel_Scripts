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

all: focuser_position_per_filter.pyc install_focuser_position_per_filter

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
install_focuser_position_per_filter: focuser_position_per_filter.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy focuser_position_per_filter.script $(CCDCIEL_DIR)\\focuser_position_per_filter.script; \
		dir $(CCDCIEL_DIR)\\focuser_position_per_filter.script; \
	else \
		cp focuser_position_per_filter.script $(CCDCIEL_DIR)/focuser_position_per_filter.script; \
		ls -la $(CCDCIEL_DIR)/focuser_position_per_filter.script; \
	fi

# --- ADDITIONAL TARGETS ---

additional: camera_warm_up.pyc install_camera_warm_up log_focuser_position.pyc install_log_focuser_position log_filters_wheel_position.pyc install_log_filters_wheel_position

# Compile Python 'camera_warm_up.py' script to bytecode
camera_warm_up.pyc: camera_warm_up.py
	$(PYTHON) -m compileall camera_warm_up.py

# Create a camera_warm_up.script
camera_warm_up.script: __pycache__/camera_warm_up.cpython-$(PYTHON_VERSION).pyc
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy __pycache__\camera_warm_up.cpython-$(PYTHON_VERSION).pyc camera_warm_up.script; \
		copy camera_warm_up.py camera_warm_up.script; \
		echo "No chmod on Windows"; \
	else \
		#cp __pycache__/camera_warm_up.cpython-$(PYTHON_VERSION).pyc camera_warm_up.script; \
		cp camera_warm_up.py camera_warm_up.script; \
		chmod +x camera_warm_up.script; \
	fi

# Install script to ccdciel scripts directory
install_camera_warm_up: camera_warm_up.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy camera_warm_up.script $(CCDCIEL_DIR)\\camera_warm_up.script; \
		dir $(CCDCIEL_DIR)\\camera_warm_up.script; \
	else \
		cp camera_warm_up.script $(CCDCIEL_DIR)/camera_warm_up.script; \
		ls -la $(CCDCIEL_DIR)/camera_warm_up.script; \
	fi

# Compile Python 'log_focuser_position.py' script to bytecode
log_focuser_position.pyc: log_focuser_position.py
	$(PYTHON) -m compileall log_focuser_position.py

# Create a log_focuser_position.script
log_focuser_position.script: __pycache__/log_focuser_position.cpython-$(PYTHON_VERSION).pyc
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy __pycache__\log_focuser_position.cpython-$(PYTHON_VERSION).pyc log_focuser_position.script; \
		copy log_focuser_position.py log_focuser_position.script; \
		echo "No chmod on Windows"; \
	else \
		#cp __pycache__/log_focuser_position.cpython-$(PYTHON_VERSION).pyc log_focuser_position.script; \
		cp log_focuser_position.py log_focuser_position.script; \
		chmod +x log_focuser_position.script; \
	fi

# Install script to ccdciel scripts directory
install_log_focuser_position: log_focuser_position.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy log_focuser_position.script $(CCDCIEL_DIR)\\log_focuser_position.script; \
		dir $(CCDCIEL_DIR)\\log_focuser_position.script; \
	else \
		cp log_focuser_position.script $(CCDCIEL_DIR)/log_focuser_position.script; \
		ls -la $(CCDCIEL_DIR)/log_focuser_position.script; \
	fi

# Compile Python 'log_filters_wheel_position.py' script to bytecode
log_filters_wheel_position.pyc: log_filters_wheel_position.py
	$(PYTHON) -m compileall log_filters_wheel_position.py

# Create a log_filters_wheel_position.script
log_filters_wheel_position.script: __pycache__/log_filters_wheel_position.cpython-$(PYTHON_VERSION).pyc
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy __pycache__\log_filters_wheel_position.cpython-$(PYTHON_VERSION).pyc log_filters_wheel_position.script; \
		copy log_filters_wheel_position.py log_filters_wheel_position.script; \
		echo "No chmod on Windows"; \
	else \
		#cp __pycache__/log_filters_wheel_position.cpython-$(PYTHON_VERSION).pyc log_filters_wheel_position.script; \
		cp log_filters_wheel_position.py log_filters_wheel_position.script; \
		chmod +x log_filters_wheel_position.script; \
	fi

# Install script to ccdciel scripts directory
install_log_filters_wheel_position: log_filters_wheel_position.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy log_filters_wheel_position.script $(CCDCIEL_DIR)\\log_filters_wheel_position.script; \
		dir $(CCDCIEL_DIR)\\log_filters_wheel_position.script; \
	else \
		cp log_filters_wheel_position.script $(CCDCIEL_DIR)/log_filters_wheel_position.script; \
		ls -la $(CCDCIEL_DIR)/log_filters_wheel_position.script; \
	fi

# --- ADDITIONAL WITH INDI DEPENDENCY TARGETS ---

additional_indi: end_session_indi.pyc install_end_session_indi iEQ_scope_go_home_indi.pyc install_iEQ_scope_go_home_indi pegasus_SPB_set_dews_AB_to_zero_indi.pyc install_pegasus_SPB_set_dews_AB_to_zero_indi

# Compile Python 'end_session_indi.py' script to bytecode
end_session_indi.pyc: end_session_indi.py
	$(PYTHON) -m compileall end_session_indi.py

# Create a end_session_indi.script
end_session_indi.script: __pycache__/end_session_indi.cpython-$(PYTHON_VERSION).pyc
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy __pycache__\end_session_indi.cpython-$(PYTHON_VERSION).pyc end_session_indi.script; \
		copy end_session_indi.py end_session_indi.script; \
		echo "No chmod on Windows"; \
	else \
		#cp __pycache__/end_session_indi.cpython-$(PYTHON_VERSION).pyc end_session_indi.script; \
		cp end_session_indi.py end_session_indi.script; \
		chmod +x end_session_indi.script; \
	fi

# Install script to ccdciel scripts directory
install_end_session_indi: end_session_indi.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy end_session_indi.script $(CCDCIEL_DIR)\\end_session_indi.script; \
		dir $(CCDCIEL_DIR)\\end_session_indi.script; \
	else \
		cp end_session_indi.script $(CCDCIEL_DIR)/end_session_indi.script; \
		ls -la $(CCDCIEL_DIR)/end_session_indi.script; \
	fi

# Compile Python 'iEQ_scope_go_home_indi.py' script to bytecode
iEQ_scope_go_home_indi.pyc: iEQ_scope_go_home_indi.py
	$(PYTHON) -m compileall iEQ_scope_go_home_indi.py

# Create a iEQ_scope_go_home_indi.script
iEQ_scope_go_home_indi.script: __pycache__/iEQ_scope_go_home_indi.cpython-$(PYTHON_VERSION).pyc
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy __pycache__\iEQ_scope_go_home_indi.cpython-$(PYTHON_VERSION).pyc iEQ_scope_go_home_indi.script; \
		copy iEQ_scope_go_home_indi.py iEQ_scope_go_home_indi.script; \
		echo "No chmod on Windows"; \
	else \
		#cp __pycache__/iEQ_scope_go_home_indi.cpython-$(PYTHON_VERSION).pyc iEQ_scope_go_home_indi.script; \
		cp iEQ_scope_go_home_indi.py iEQ_scope_go_home_indi.script; \
		chmod +x iEQ_scope_go_home_indi.script; \
	fi

# Install script to ccdciel scripts directory
install_iEQ_scope_go_home_indi: iEQ_scope_go_home_indi.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy iEQ_scope_go_home_indi.script $(CCDCIEL_DIR)\\iEQ_scope_go_home_indi.script; \
		dir $(CCDCIEL_DIR)\\iEQ_scope_go_home_indi.script; \
	else \
		cp iEQ_scope_go_home_indi.script $(CCDCIEL_DIR)/iEQ_scope_go_home_indi.script; \
		ls -la $(CCDCIEL_DIR)/iEQ_scope_go_home_indi.script; \
	fi

# Compile Python 'pegasus_SPB_set_dews_AB_to_zero_indi.py' script to bytecode
pegasus_SPB_set_dews_AB_to_zero_indi.pyc: pegasus_SPB_set_dews_AB_to_zero_indi.py
	$(PYTHON) -m compileall pegasus_SPB_set_dews_AB_to_zero_indi.py

# Create a pegasus_SPB_set_dews_AB_to_zero_indi.script
pegasus_SPB_set_dews_AB_to_zero_indi.script: __pycache__/pegasus_SPB_set_dews_AB_to_zero_indi.cpython-$(PYTHON_VERSION).pyc
	@if [ "$(OS)" = "Windows_NT" ]; then \
		#copy __pycache__\pegasus_SPB_set_dews_AB_to_zero_indi.cpython-$(PYTHON_VERSION).pyc pegasus_SPB_set_dews_AB_to_zero_indi.script; \
		copy pegasus_SPB_set_dews_AB_to_zero_indi.py pegasus_SPB_set_dews_AB_to_zero_indi.script; \
		echo "No chmod on Windows"; \
	else \
		#cp __pycache__/pegasus_SPB_set_dews_AB_to_zero_indi.cpython-$(PYTHON_VERSION).pyc pegasus_SPB_set_dews_AB_to_zero_indi.script; \
		cp pegasus_SPB_set_dews_AB_to_zero_indi.py pegasus_SPB_set_dews_AB_to_zero_indi.script; \
		chmod +x pegasus_SPB_set_dews_AB_to_zero_indi.script; \
	fi

# Install script to ccdciel scripts directory
install_pegasus_SPB_set_dews_AB_to_zero_indi: pegasus_SPB_set_dews_AB_to_zero_indi.script
	@if [ "$(OS)" = "Windows_NT" ]; then \
		copy pegasus_SPB_set_dews_AB_to_zero_indi.script $(CCDCIEL_DIR)\\pegasus_SPB_set_dews_AB_to_zero_indi.script; \
		dir $(CCDCIEL_DIR)\\pegasus_SPB_set_dews_AB_to_zero_indi.script; \
	else \
		cp pegasus_SPB_set_dews_AB_to_zero_indi.script $(CCDCIEL_DIR)/pegasus_SPB_set_dews_AB_to_zero_indi.script; \
		ls -la $(CCDCIEL_DIR)/pegasus_SPB_set_dews_AB_to_zero_indi.script; \
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


