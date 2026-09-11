"""STT interface and stubs — PTT-oriented; no real Mac audio required on Linux."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Transcript:
    text: str
    confidence: float
    backend: str
    meta: dict[str, Any] | None = None


class STTBackend(ABC):
    name: str

    @abstractmethod
    def transcribe_text(self, text: str) -> Transcript:
        """Passthrough / normalize text as if PTT produced it (demo / tests)."""

    @abstractmethod
    def transcribe_wav(self, path: str | Path) -> Transcript:
        """Transcribe a wav file. Stubs may return placeholder text."""


class PassthroughSTT(STTBackend):
    """CLI / demo backend: treat provided text as the transcript."""

    name = "passthrough"

    def transcribe_text(self, text: str) -> Transcript:
        return Transcript(text=text.strip(), confidence=1.0, backend=self.name)

    def transcribe_wav(self, path: str | Path) -> Transcript:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        # No audio decode on Linux Phase 0 — return filename stem as hint.
        return Transcript(
            text="",
            confidence=0.0,
            backend=self.name,
            meta={"wav": str(p), "note": "passthrough does not decode audio"},
        )


class AppleSpeechStub(STTBackend):
    name = "apple_speech"

    def transcribe_text(self, text: str) -> Transcript:
        return Transcript(text=text.strip(), confidence=0.9, backend=self.name)

    def transcribe_wav(self, path: str | Path) -> Transcript:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        return Transcript(
            text="[apple_speech stub — run on macOS]",
            confidence=0.0,
            backend=self.name,
            meta={"wav": str(p)},
        )


class WhisperStub(STTBackend):
    name = "whisper"

    def transcribe_text(self, text: str) -> Transcript:
        return Transcript(text=text.strip(), confidence=0.92, backend=self.name)

    def transcribe_wav(self, path: str | Path) -> Transcript:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        return Transcript(
            text="[whisper stub — install whisper.cpp / openai-whisper on Mac]",
            confidence=0.0,
            backend=self.name,
            meta={"wav": str(p)},
        )


class CloudSTTStub(STTBackend):
    name = "cloud"

    def transcribe_text(self, text: str) -> Transcript:
        return Transcript(text=text.strip(), confidence=0.95, backend=self.name)

    def transcribe_wav(self, path: str | Path) -> Transcript:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        return Transcript(
            text="[cloud STT stub — set API key; privacy tradeoff]",
            confidence=0.0,
            backend=self.name,
            meta={"wav": str(p)},
        )


_REGISTRY: dict[str, type[STTBackend]] = {
    PassthroughSTT.name: PassthroughSTT,
    AppleSpeechStub.name: AppleSpeechStub,
    WhisperStub.name: WhisperStub,
    CloudSTTStub.name: CloudSTTStub,
}


def list_backends() -> list[str]:
    return sorted(_REGISTRY)


def get_backend(name: str = "passthrough") -> STTBackend:
    try:
        return _REGISTRY[name]()
    except KeyError as exc:
        raise KeyError(f"unknown STT backend: {name}; have {list_backends()}") from exc
