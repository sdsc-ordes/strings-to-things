# app/core/transformation_log.py
"""
Internal logger for recording transformation events.
"""


class TransformationLog:
    def __init__(self, verbose: bool = True):
        self.entries = []
        self.verbose = verbose  # control printing

    def add_entry(
        self, subject, predicate, original_value, replacement_iri, reason: str
    ):
        """
        Record a transformation decision.
        """
        entry = {
            "subject": subject,
            "predicate": predicate,
            "original": original_value,
            "replacement": replacement_iri,
            "reason": reason,
        }
        self.entries.append(entry)

        # 👇 Emit message immediately when adding entry
        if self.verbose:
            if replacement_iri:
                print(
                    f"[TRANSFORM] Replaced '{original_value}' "
                    f"→ <{replacement_iri}> (subject: <{subject}>, predicate: <{predicate}>)"
                )
            else:
                print(
                    f"[TRANSFORM] No replacement for '{original_value}' "
                    f"(subject: <{subject}>, predicate: <{predicate}>, reason: {reason})"
                )

    def get_summary(self):
        """
        Return summary statistics of transformation events.
        """
        return {
            "total": len(self.entries),
        }
