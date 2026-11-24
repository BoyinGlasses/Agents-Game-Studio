"""Harness adapters for Agents Game Studio v2."""

from __future__ import annotations

ENGINE_CHOICES: tuple[str, ...] = ("godot", "unity", "unreal", "none")
HARNESS_CHOICES: tuple[str, ...] = ("codex", "antigravity", "opencode", "claude", "universal")

__all__ = ["ENGINE_CHOICES", "HARNESS_CHOICES"]
