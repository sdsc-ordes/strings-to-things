# app/core/transformation_log.py
"""
Internal logger for recording transformation events.
"""

class TransformationLog:
    def __init__(self):
        self.entries = []

    def add_entry(self, subject, predicate, original_value, replacement_iri, reason: str):
        """
        Record a transformation decision.
        """
        self.entries.append({
            "subject": subject,
            "predicate": predicate,
            "original": original_value,
            "replacement": replacement_iri,
            "reason": reason
        })

    def get_summary(self):
        """
        Return summary statistics of transformation events.
        """
        return {
            "total": len(self.entries),
        }
