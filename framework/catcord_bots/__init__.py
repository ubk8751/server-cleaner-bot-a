"""Catcord bots framework - shared runtime for Matrix bots"""
__version__ = "0.1.0"

from catcord_bots.formatting import storage_status_label, format_retention_stats, format_pressure_stats

__all__ = ["storage_status_label", "format_retention_stats", "format_pressure_stats"]
