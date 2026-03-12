"""Core constants shared across the entire application.

Centralising these values prevents magic strings from being scattered
across forms and templates, and makes it trivial to update the design
system (e.g. swap Tailwind classes) in a single place.
"""

# Shared TailwindCSS utility classes applied to every ``<input>`` element.
# Provides a consistent look-and-feel across all forms without requiring
# per-form CSS overrides.
INPUT_CSS: str = (
    "w-full px-4 py-3 rounded-lg border border-gray-300 "
    "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
    "transition duration-200"
)
