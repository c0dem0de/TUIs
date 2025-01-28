#!/bin/bash

# Function to detect shell and corresponding rc file
get_shell_rc() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        echo "$HOME/.bashrc"
    elif [ -n "$KSH_VERSION" ]; then
        echo "$HOME/.kshrc"
    else
        # Default to bashrc if unable to detect
        echo "$HOME/.bashrc"
    fi
}

# The alias/function to add
PYAPP_FUNCTION='function _pyapp(){ python3 =(curl -H "Cache-Control: no-cache" -s "$1"); }; _pyapp'
ALIAS_LINE="alias pyapp='$PYAPP_FUNCTION'"

# Get the appropriate rc file
RC_FILE=$(get_shell_rc)

# Check if the alias already exists
if grep -q "alias pyapp=" "$RC_FILE" 2>/dev/null; then
    echo "pyapp alias already exists in $RC_FILE"
    exit 0
fi

# Add the alias to the rc file
echo "" >> "$RC_FILE"
echo "# Python app execution alias" >> "$RC_FILE"
echo "$ALIAS_LINE" >> "$RC_FILE"

source $RC_FILE
