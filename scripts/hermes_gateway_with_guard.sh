#!/bin/bash
# Hermes Gateway Wrapper — runs guard cleanup, then starts the gateway
# ~/.hermes/hermes-agent/scripts/hermes_gateway_with_guard.sh

# Run guard first
bash "$HOME/.hermes/scripts/hermes_gateway_startup_guard.sh"

# Then start the gateway
cd "$HOME/.hermes/hermes-agent" || exit 1

# Source .env if it exists
if [ -f "$HOME/.hermes/hermes-agent/.env" ]; then
    set -a
    source "$HOME/.hermes/hermes-agent/.env"
    set +a
fi

# Also source profile env for API keys
if [ -f "$HOME/.hermes/.env" ]; then
    set -a
    source "$HOME/.hermes/.env"
    set +a
fi

exec "$HOME/.hermes/hermes-agent/venv/bin/python" -m gateway.run
