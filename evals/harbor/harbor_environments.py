"""Evaluation-only Harbor environment adapters."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess

from harbor.environments.docker.docker import DockerEnvironment


class PinnedImageDockerEnvironment(DockerEnvironment):
    """Use an audited local image while preserving the immutable task package."""

    def __init__(
        self,
        *args,
        task_env_config,
        environment_dir: Path,
        pinned_image: str,
        source_dockerfile_sha256: str,
        npm_version: str,
        **kwargs,
    ) -> None:
        dockerfile = environment_dir / "Dockerfile"
        actual_source_hash = hashlib.sha256(dockerfile.read_bytes()).hexdigest()
        if actual_source_hash != source_dockerfile_sha256:
            raise RuntimeError(
                "immutable task Dockerfile hash mismatch: "
                f"expected {source_dockerfile_sha256}, got {actual_source_hash}"
            )

        result = subprocess.run(
            [
                "docker",
                "image",
                "inspect",
                pinned_image,
                "--format",
                "{{json .Config.Labels}}",
            ],
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"required evaluation image is unavailable: {pinned_image}"
            )
        labels = result.stdout
        required_markers = (
            f'"harbor.evaluation.source-dockerfile-sha256":"{source_dockerfile_sha256}"',
            f'"harbor.evaluation.npm-version":"{npm_version}"',
            '"harbor.evaluation.codex-nvm-bridge":"home-to-usr-local"',
        )
        missing_markers = [marker for marker in required_markers if marker not in labels]
        if missing_markers:
            raise RuntimeError(
                "evaluation image provenance labels are missing: "
                + ", ".join(missing_markers)
            )

        pinned_task_config = task_env_config.model_copy(
            update={"docker_image": pinned_image}
        )
        super().__init__(
            *args,
            task_env_config=pinned_task_config,
            environment_dir=environment_dir,
            **kwargs,
        )
