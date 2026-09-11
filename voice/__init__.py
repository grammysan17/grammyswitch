"""Pluggable STT backends (stubs for Phase 0)."""

from voice.stt import STTBackend, get_backend, list_backends

__all__ = ["STTBackend", "get_backend", "list_backends"]
