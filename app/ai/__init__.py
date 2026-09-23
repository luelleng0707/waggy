"""Conversational explanation layer. Not a second Waggy engine."""

# Do not eagerly import agent/conversation here. `app.state.store` imports
# `app.ai.models`; loading this package must not re-enter the store.
