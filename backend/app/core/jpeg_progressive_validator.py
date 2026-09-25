def extract_scan_signature(features):

    scans = []

    for block_id in features:

        feature = features[block_id]

        for scan in feature["scans"]:

            components = tuple(
                sorted(
                    component["component_id"]
                    for component in scan["components"]
                )
            )

            scans.append({
                "block_id": block_id,
                "components": components,
                "spectral_start":
                    scan["spectral_start"],
                "spectral_end":
                    scan["spectral_end"],
                "Ah":
                    scan["successive_high"],
                "Al":
                    scan["successive_low"],
            })

    return scans