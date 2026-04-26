"""Internationalization (i18n) support for MCGG.

Provides translations for UI strings in multiple languages.
Currently supports: English (en), Indonesian (id).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class Language(Enum):
    """Supported languages."""

    EN = "en"
    ID = "id"


DEFAULT_LANGUAGE = Language.EN


# Translation dictionary type
Translations = dict[str, str]


@dataclass
class TranslationSet:
    """A set of translations for one language."""

    code: Language
    name: str
    translations: Translations


# English translations
EN_TRANSLATIONS: Translations = {
    # App
    "app.title": "Magic Chess Go Go - Opponent Predictor",
    "app.welcome": "Welcome to MCGG Opponent Predictor",
    "app.start_session": "Start New Session",
    "app.resume_session": "Resume Session",
    "app.exit": "Exit",

    # Player
    "player.title": "Player",
    "player.name": "Name",
    "player.position": "Position",
    "player.active": "Active",
    "player.eliminated": "Eliminated",
    "player.local": "(You)",
    "player.add": "Add Player",
    "player.remove": "Remove Player",
    "player.set_local": "Set as Local Player",

    # Session
    "session.title": "Game Session",
    "session.phase": "Phase",
    "session.round": "Round",
    "session.current": "Current Round",
    "session.total_rounds": "Total Rounds Played",
    "session.active_players": "Active Players",
    "session.history": "Round History",
    "session.no_history": "No rounds played yet",
    "session.end": "End Session",
    "session.started": "Started at",
    "session.ended": "Ended at",

    # Round
    "round.title": "Round",
    "round.opponent": "Opponent",
    "round.monster": "Monster",
    "round.user": "Player",
    "round.predictable": "Predictable",
    "round.random": "Random",
    "round.record": "Record Round",
    "round.skip": "Skip Round",
    "round.advance": "Advance to Next Round",

    # Prediction
    "prediction.title": "Opponent Prediction",
    "prediction.current": "Prediction for Current Round",
    "prediction.none": "No prediction available for this round",
    "prediction.confidence": "Confidence",
    "prediction.based_on": "Based on",
    "prediction.method": "Method",
    "prediction.valid": "Valid Prediction",
    "prediction.invalid": "Cannot Predict (Random Round)",
    "prediction.result": "Predicted Opponent",

    # Round Types
    "roundtype.monster": "Monster Battle",
    "roundtype.user": "Player Battle",

    # Phase Info
    "phase.info": "Phase {phase}, Round {round}",
    "phase.phase": "Phase {number}",
    "phase.current": "Current Phase",

    # Rules
    "rules.title": "Prediction Rules",
    "rules.i4": "Round i-4: Your opponent = opponent of your 'first ex' at round i-3",
    "rules.ii2": "Round ii-2: Your opponent = opponent of your 'first ex' at round ii-1",
    "rules.ii4": "Round ii-4: Your opponent = opponent of your ii-2 opponent at round i-4",
    "rules.ii5": "Round ii-5: Your opponent = opponent of your ii-4 opponent at round ii-2",
    "rules.ii6": "Round ii-6: Your opponent = opponent of your ii-5 opponent at round ii-3",
    "rules.random": "Random rounds (cannot predict): i-2, i-3, ii-1, ii-3",
    "rules.note": "Note: Predictions only valid when all players are active",

    # Errors
    "error.no_session": "No active session. Please start a new session.",
    "error.no_local_player": "Please set a local player first.",
    "error.invalid_round": "Invalid round data.",
    "error.no_prediction": "Cannot make prediction for this round.",

    # Confirmations
    "confirm.end_session": "Are you sure you want to end the current session?",
    "confirm.yes": "Yes",
    "confirm.no": "No",
    "confirm.cancel": "Cancel",

    # Status
    "status.playing": "Playing",
    "status.waiting": "Waiting for input",
    "status.complete": "Complete",
    "status.abandoned": "Abandoned",
}


# Indonesian translations
ID_TRANSLATIONS: Translations = {
    # App
    "app.title": "Magic Chess Go Go - Prediksi Lawan",
    "app.welcome": "Selamat datang di Prediksi Lawan MCGG",
    "app.start_session": "Mulai Sesi Baru",
    "app.resume_session": "Lanjutkan Sesi",
    "app.exit": "Keluar",

    # Player
    "player.title": "Pemain",
    "player.name": "Nama",
    "player.position": "Posisi",
    "player.active": "Aktif",
    "player.eliminated": "Tereliminasi",
    "player.local": "(Anda)",
    "player.add": "Tambah Pemain",
    "player.remove": "Hapus Pemain",
    "player.set_local": "Jadikan Pemain Lokal",

    # Session
    "session.title": "Sesi Permainan",
    "session.phase": "Fase",
    "session.round": "Ronde",
    "session.current": "Ronde Saat Ini",
    "session.total_rounds": "Total Ronde Dimainkan",
    "session.active_players": "Pemain Aktif",
    "session.history": "Riwayat Ronde",
    "session.no_history": "Belum ada ronde yang dimainkan",
    "session.end": "Akhiri Sesi",
    "session.started": "Dimulai pada",
    "session.ended": "Berakhir pada",

    # Round
    "round.title": "Ronde",
    "round.opponent": "Lawan",
    "round.monster": "Monster",
    "round.user": "Pemain",
    "round.predictable": "Dapat Diprediksi",
    "round.random": "Acak",
    "round.record": "Rekam Ronde",
    "round.skip": "Lewati Ronde",
    "round.advance": "Lanjut ke Ronde Berikutnya",

    # Prediction
    "prediction.title": "Prediksi Lawan",
    "prediction.current": "Prediksi untuk Ronde Saat Ini",
    "prediction.none": "Tidak ada prediksi untuk ronde ini",
    "prediction.confidence": "Tingkat Kepercayaan",
    "prediction.based_on": "Berdasarkan",
    "prediction.method": "Metode",
    "prediction.valid": "Prediksi Valid",
    "prediction.invalid": "Tidak Dapat Diprediksi (Ronde Acak)",
    "prediction.result": "Lawan yang Diprediksi",

    # Round Types
    "roundtype.monster": "Pertarungan Monster",
    "roundtype.user": "Pertarungan Pemain",

    # Phase Info
    "phase.info": "Fase {phase}, Ronde {round}",
    "phase.phase": "Fase {number}",
    "phase.current": "Fase Saat Ini",

    # Rules
    "rules.title": "Aturan Prediksi",
    "rules.i4": "Ronde i-4: Lawanmu = lawan dari 'mantan pertama' di ronde i-3",
    "rules.ii2": "Ronde ii-2: Lawanmu = lawan dari 'mantan pertama' di ronde ii-1",
    "rules.ii4": "Ronde ii-4: Lawanmu = lawan dari lawanmu di ronde ii-2 di ronde i-4",
    "rules.ii5": "Ronde ii-5: Lawanmu = lawan dari lawanmu di ronde ii-4 di ronde ii-2",
    "rules.ii6": "Ronde ii-6: Lawanmu = lawan dari lawanmu di ronde ii-5 di ronde ii-3",
    "rules.random": "Ronde acak (tidak dapat diprediksi): i-2, i-3, ii-1, ii-3",
    "rules.note": "Catatan: Prediksi hanya berlaku jika semua pemain masih aktif",

    # Errors
    "error.no_session": "Tidak ada sesi aktif. Silakan mulai sesi baru.",
    "error.no_local_player": "Silakan tentukan pemain lokal terlebih dahulu.",
    "error.invalid_round": "Data ronde tidak valid.",
    "error.no_prediction": "Tidak dapat membuat prediksi untuk ronde ini.",

    # Confirmations
    "confirm.end_session": "Apakah Anda yakin ingin mengakhiri sesi saat ini?",
    "confirm.yes": "Ya",
    "confirm.no": "Tidak",
    "confirm.cancel": "Batal",

    # Status
    "status.playing": "Bermain",
    "status.waiting": "Menunggu input",
    "status.complete": "Selesai",
    "status.abandoned": "Ditinggalkan",
}


# Language registry
LANGUAGES: dict[Language, TranslationSet] = {
    Language.EN: TranslationSet(Language.EN, "English", EN_TRANSLATIONS),
    Language.ID: TranslationSet(Language.ID, "Bahasa Indonesia", ID_TRANSLATIONS),
}


class I18n:
    """Internationalization helper class."""

    def __init__(self, language: Language = DEFAULT_LANGUAGE):
        self._language = language
        self._cache: dict[str, str] = {}
        self._translations = LANGUAGES[language].translations

    @property
    def language(self) -> Language:
        """Get current language."""
        return self._language

    def set_language(self, language: Language) -> None:
        """Change the current language."""
        self._language = language
        self._translations = LANGUAGES[language].translations
        self._cache.clear()

    def t(self, key: str, **kwargs: str | int) -> str:
        """Translate a key with optional format arguments.

        Args:
            key: Translation key (e.g., "app.title")
            **kwargs: Format arguments for the translation string

        Returns:
            Translated string with placeholders replaced

        Example:
            i18n.t("phase.info", phase=2, round=3) -> "Phase 2, Round 3"
        """
        if key not in self._cache:
            self._cache[key] = self._translations.get(key, key)

        result = self._cache[key]

        if kwargs:
            try:
                result = result.format(**kwargs)
            except (KeyError, ValueError):
                pass

        return result

    def get_available_languages(self) -> list[tuple[Language, str]]:
        """Get list of available languages as (Language, display_name) tuples."""
        return [(lang.code, lang_set.name) for lang, lang_set in LANGUAGES.items()]


# Global i18n instance
_i18n: I18n | None = None


def get_i18n() -> I18n:
    """Get the global i18n instance, creating it if necessary."""
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n


def set_i18n_language(language: Language) -> None:
    """Set the global i18n language."""
    get_i18n().set_language(language)


def t(key: str, **kwargs: str | int) -> str:
    """Translate a key using the global i18n instance."""
    return get_i18n().t(key, **kwargs)
