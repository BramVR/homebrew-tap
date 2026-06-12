#!/usr/bin/env python3
"""Render the gohealthcli Homebrew formula from GitHub release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import sys
import urllib.request


TARGETS = ("darwin_arm64", "darwin_amd64", "linux_arm64", "linux_amd64")
USER_AGENT = "bramvr-homebrew-tap-updater"


def sha256(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://github.com/"):
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    digest = hashlib.sha256()
    with urllib.request.urlopen(request) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_url(repository: str, tag: str, formula: str, version: str, template: str, target: str) -> str:
    artifact = template.format(
        formula=formula,
        version=version,
        tag=tag,
        target=target,
    )
    return f"https://github.com/{repository}/releases/download/{tag}/{artifact}"


def render_formula(
    formula: str,
    repository: str,
    version: str,
    description: str,
    checksums: dict[str, tuple[str, str]],
) -> str:
    return f'''class Gohealthcli < Formula
  desc "{description}"
  homepage "https://github.com/{repository}"
  version "{version}"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "{checksums["darwin_arm64"][0]}"
      sha256 "{checksums["darwin_arm64"][1]}"
    else
      url "{checksums["darwin_amd64"][0]}"
      sha256 "{checksums["darwin_amd64"][1]}"
    end
  end

  on_linux do
    if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
      url "{checksums["linux_arm64"][0]}"
      sha256 "{checksums["linux_arm64"][1]}"
    end

    if Hardware::CPU.intel? && Hardware::CPU.is_64_bit?
      url "{checksums["linux_amd64"][0]}"
      sha256 "{checksums["linux_amd64"][1]}"
    end
  end

  def install
    bin.install "{formula}"
  end

  def caveats
    <<~EOS
      Quick start:
        gohealthcli init
        gohealthcli doctor --plain

      Default local paths after init:
        ~/.config/gohealthcli/config.toml
        ~/.local/share/gohealthcli/gohealthcli.sqlite
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{{bin}}/gohealthcli --version")
    assert_match "Initialise a fresh", shell_output("#{{bin}}/gohealthcli help init 2>&1")
  end
end
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formula", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--artifact-template", required=True)
    args = parser.parse_args()

    if args.formula != "gohealthcli":
        raise SystemExit("this tap updater only supports gohealthcli")
    if not args.tag.startswith("v"):
        raise SystemExit("release tag must start with v")

    version = args.tag[1:]
    checksums: dict[str, tuple[str, str]] = {}
    for target in TARGETS:
        url = artifact_url(args.repository, args.tag, args.formula, version, args.artifact_template, target)
        digest = sha256(url)
        checksums[target] = (url, digest)
        print(f"{target}: {digest}  {url}")

    path = pathlib.Path("Formula") / f"{args.formula}.rb"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_formula(args.formula, args.repository, version, args.description, checksums),
        encoding="utf-8",
    )
    print(f"updated {path} to {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
