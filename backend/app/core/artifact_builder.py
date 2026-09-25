from .artifact import Artifact


def confidence_to_score(confidence):
    """
    Convert detector confidence labels into numeric scores.
    """

    mapping = {
        "low": 0.30,
        "medium": 0.60,
        "high": 0.90,
    }

    return mapping.get(confidence, 0.0)


def build_artifacts(findings):
    """
    Convert raw format-detector findings into Artifact objects.
    """

    artifacts = []

    for index, finding in enumerate(findings, start=1):

        artifact = Artifact(
            artifact_id=f"artifact_{index:03d}",
            format=finding["format"],
            category=finding.get("category", "unknown"),
            offset=finding["offset"],
            extension=finding.get("extension"),
            mime_type=finding.get("mime_type"),
            confidence=confidence_to_score(
                finding.get("confidence", "low")
            ),
            status=finding.get("status", "candidate"),
        )

        artifacts.append(artifact)

    return artifacts