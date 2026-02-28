import pytest
from catcord_bots.formatting import storage_status_label, format_retention_stats, format_pressure_stats


class TestFormatting:
    def test_storage_status_label(self):
        assert storage_status_label(30.0, 85.0, 92.0) == "healthy"
        assert storage_status_label(60.0, 85.0, 92.0) == "OK"
        assert storage_status_label(80.0, 85.0, 92.0) == "tight"
        assert storage_status_label(87.0, 85.0, 92.0) == "pressure"
        assert storage_status_label(95.0, 85.0, 92.0) == "critical"

    def test_format_retention_stats(self):
        payload = {
            "disk": {"percent_before": 45.2, "pressure_threshold": 85.0, "emergency_threshold": 92.0},
            "actions": {"deleted_count": 10, "freed_gb": 1.5, "deleted_by_type": {"images": 3, "non_images": 7}},
            "candidates_count": 50,
            "total_files_count": 1000,
            "timing": {"duration_seconds": 5}
        }
        result = format_retention_stats(payload)
        assert "Disk: 45.2%" in result
        assert "Storage: healthy" in result
        assert "Retention candidates: 50" in result
        assert "Deleted: 10" in result
        assert "Freed: 1.50 GB" in result
        assert "Files on disk: 1000" in result
        assert "Duration: 5s" in result

    def test_format_pressure_stats(self):
        payload = {
            "disk": {"percent_before": 87.0, "percent_after": 82.0, "pressure_threshold": 85.0, "emergency_threshold": 92.0},
            "actions": {"deleted_count": 5, "freed_gb": 0.8, "deleted_by_type": {"images": 2, "non_images": 3}},
            "timing": {"duration_seconds": 3}
        }
        result = format_pressure_stats(payload)
        assert "Disk: 87.0% → 82.0%" in result
        assert "Storage: pressure" in result
        assert "Deleted: 5" in result
        assert "Freed: 0.80 GB" in result
        assert "Duration: 3s" in result
