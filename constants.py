"""
Global constants shared across the project — exam labels, hidden vault
command names/limits, mock-test wizard step count, etc. Centralized here so
they're easy to find and change in one place instead of hunting through
feature modules for a magic number or string.
"""

# --- Onboarding ---
EXAM_LABELS = {"ssc_cgl": "SSC CGL", "jee_mains": "JEE Mains", "custom": "Custom / Other"}

# --- Personal vault (hidden feature) ---
# Deliberately not mentioned in /help, BotFather's command menu, or the
# persistent keyboard — see vault.py for the feature itself.
VAULT_VIEW_COMMAND = "admin"
VAULT_SAVE_COMMAND = "admins"
VAULT_MAX_ATTEMPTS = 5
VAULT_LOCKOUT_MINUTES = 15

# --- Mock test logging wizard ---
MOCKTEST_TOTAL_STEPS = 16
MOCKTEST_SKIP_WORDS = ("skip", "none", "na", "n/a", "-")
