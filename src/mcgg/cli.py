"""CLI interface for MCGG Matchmaking Analyzer.

Main entry point for the command-line application.
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from mcgg.models import Session, Player, RoundType, RoundNumber, MatchResult
from mcgg.engine import PredictionEngine
from mcgg.storage import SessionStorage, Exporter
from mcgg.i18n import Language, get_i18n, t

app = typer.Typer(help="MCGG Matchmaking Analyzer - Prediksi Lawan Magic Chess Go Go")
console = Console()
storage = SessionStorage()

# Global state
current_session: Optional[Session] = None


def get_session() -> Session:
    """Get current session or raise error."""
    if current_session is None:
        typer.echo("No active session. Use 'new-session' to start.", err=True)
        raise typer.Exit(code=1)
    return current_session


def _create_session(
    player_names: List[str],
    your_name: str,
    language: Language = Language.ID,
) -> Session:
    """Create and persist a new session."""
    global current_session

    if len(player_names) < 2:
        typer.echo("Minimal 2 pemain diperlukan.", err=True)
        raise typer.Exit(code=1)
    if len(player_names) > 8:
        typer.echo("Maksimal 8 pemain.", err=True)
        raise typer.Exit(code=1)
    if your_name not in player_names:
        typer.echo(f"--you '{your_name}' harus ada dalam daftar pemain.", err=True)
        raise typer.Exit(code=1)

    get_i18n().set_language(language)

    session = Session()
    for i, name in enumerate(player_names, start=1):
        session.add_player(
            Player(
                name=name,
                position=i,
                is_local_player=(name == your_name),
            )
        )

    current_session = session
    storage.save_session(session)
    return session


def _resume_session(session_id: str, language: Language = Language.ID) -> Session:
    """Load and set the active session by ID."""
    global current_session

    get_i18n().set_language(language)
    session = storage.load_session(session_id)
    if session is None:
        typer.echo(f"Sesi '{session_id}' tidak ditemukan.", err=True)
        raise typer.Exit(code=1)

    current_session = session
    return session


def _record_round(opponent: str, result: MatchResult, notes: Optional[str] = None) -> Session:
    """Record one round and persist session."""
    session = get_session()
    _ = notes  # Reserved for future metadata.

    opponent_player = session.get_player_by_name(opponent)
    if opponent.lower() == "monster":
        opp_type = RoundType.MONSTER
        opp_player = None
    elif opponent_player:
        opp_type = RoundType.USER
        opp_player = opponent_player
    else:
        opp_player = Player(name=opponent, position=0)
        opp_type = RoundType.USER
        session.add_player(opp_player)

    record = session.add_round(opp_player or Player(name="Monster"), opp_type)
    record.result = result
    session.advance_round()
    storage.save_session(session)
    return session


def _predict_current() -> "Prediction":
    """Predict opponent for current session state."""
    session = get_session()
    engine = PredictionEngine(session)
    return engine.predict()


@app.command()
def new_session(
    player_names: List[str] = typer.Option(
        ..., 
        "--player", "-p",
        help="Nama pemain (minimal 2, maks 8). Format: --player Nama1 --player Nama2"
    ),
    your_name: str = typer.Option(
        ...,
        "--you", "-y",
        help="Nama pemain yang menggunakan aplikasi ini (anda)"
    ),
    language: Language = typer.Option(
        Language.ID,
        "--lang",
        help="Bahasa: id untuk Indonesia, en untuk English"
    ),
):
    """Mulai sesi game baru."""
    session = _create_session(player_names, your_name, language)

    console.print(f"[green]Sesi baru dibuat![/green]")
    console.print(f"Pemain lokal: [bold]{your_name}[/bold]")
    console.print(f"Total pemain: {len(player_names)}")
    console.print(f"Fase saat ini: {session.current_phase}, Ronde: {session.current_round}")
    console.print(f"ID sesi: {session.id}")
    _show_current_status()


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="ID sesi yang akan dilanjutkan"),
    language: Language = typer.Option(Language.ID, "--lang", help="Bahasa"),
):
    """Lanjutkan sesi yang sudah ada."""
    session = _resume_session(session_id, language)
    console.print(f"[green]Sesi dilanjutkan![/green]")
    _show_current_status()


@app.command()
def record(
    opponent: str = typer.Argument(..., help="Nama lawan (atau 'monster' untuk monster)"),
    result: MatchResult = typer.Option(..., "--result", "-r", help="Hasil: win/lose/draw"),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="Catatan tambahan"),
):
    """Rekam hasil ronde."""
    session = _record_round(opponent, result, notes)
    record = session.round_history[-1]

    rn = record.round_number
    console.print(f"[green]Ronde direkam:[/green] {rn.value}")
    console.print(f"  Lawan: {opponent}")
    console.print(f"  Hasil: {result.value}")
    console.print(f"  Sekarang: Fase {session.current_phase}, Ronde {session.current_round}")
    
    _show_current_status()


@app.command()
def predict():
    """Prediksi lawan untuk ronde saat ini."""
    session = get_session()
    pred = _predict_current()
    rn = session.current_round_number
    
    console.print(f"\n[bold]Prediksi untuk {rn.value}:[/bold]")
    
    if pred.is_valid and pred.predicted_opponent:
        console.print(f"  [green]Lawan diprediksi:[/green] [bold]{pred.predicted_opponent.name}[/bold]")
        console.print(f"  [yellow]Confidence:[/yellow] {pred.confidence:.0%}")
        if pred.chain_description:
            console.print(f"  [cyan]Chain:[/cyan] {pred.chain_description}")
        if pred.warnings:
            for w in pred.warnings:
                console.print(f"  [red]Warning:[/red] {w}")
    else:
        console.print(f"  [red]Tidak dapat diprediksi[/red]")
        console.print(f"  Alasan: {pred.prediction_method}")
        for w in pred.warnings:
            console.print(f"  [yellow]Note:[/yellow] {w}")


@app.command()
def tui(
    language: Language = typer.Option(Language.ID, "--lang", help="Bahasa"),
):
    """Mode semi-interaktif berbasis Rich prompt."""
    get_i18n().set_language(language)
    console.print("[bold cyan]MCGG Interactive Mode[/bold cyan]")
    console.print("Ketik nomor aksi untuk melanjutkan.")

    while True:
        console.print("\n[bold]Menu[/bold]")
        console.print("1) New Session")
        console.print("2) Resume Session")
        console.print("3) Record Round")
        console.print("4) Predict")
        console.print("5) Status")
        console.print("6) End Session")
        console.print("0) Exit TUI")

        choice = Prompt.ask(
            "Pilih aksi",
            choices=["0", "1", "2", "3", "4", "5", "6"],
            default="5",
        )

        try:
            if choice == "1":
                names_raw = Prompt.ask("Daftar pemain (pisahkan dengan koma)")
                player_names = [name.strip() for name in names_raw.split(",") if name.strip()]
                your_name = Prompt.ask("Nama kamu (harus ada di daftar pemain)")
                session = _create_session(player_names, your_name, language)
                console.print(f"[green]Sesi baru dibuat:[/green] {session.id}")
                _show_current_status()
            elif choice == "2":
                session_id = Prompt.ask("Masukkan session ID")
                session = _resume_session(session_id, language)
                console.print(f"[green]Sesi dilanjutkan:[/green] {session.id}")
                _show_current_status()
            elif choice == "3":
                session = get_session()
                default_opp = "monster" if session.current_round_number.is_monster_round else ""
                opponent = Prompt.ask("Lawan (nama pemain atau 'monster')", default=default_opp)
                result_raw = Prompt.ask("Hasil", choices=["win", "lose", "draw"], default="win")
                notes = Prompt.ask("Catatan (opsional)", default="")
                result = MatchResult(result_raw)
                updated = _record_round(opponent, result, notes or None)
                rec = updated.round_history[-1]
                console.print(f"[green]Ronde direkam:[/green] {rec.round_number.value} vs {opponent} ({result.value})")
                _show_current_status()
            elif choice == "4":
                predict()
            elif choice == "5":
                _show_current_status()
            elif choice == "6":
                end_session()
            elif choice == "0":
                console.print("[cyan]Keluar dari mode interaktif.[/cyan]")
                break
        except typer.Exit:
            console.print("[red]Aksi dibatalkan karena input/state tidak valid.[/red]")
        except Exception as exc:  # pragma: no cover - safeguard for interactive loop
            console.print(f"[red]Terjadi error:[/red] {exc}")


@app.command()
def status():
    """Tampilkan status sesi saat ini."""
    _show_current_status()


@app.command()
def history():
    """Tampilkan riwayat ronde."""
    session = get_session()
    
    if not session.round_history:
        console.print("[yellow]Belum ada ronde yang dimainkan.[/yellow]")
        return
    
    table = Table(title=f"Riwayat Ronde - Sesi {session.id}")
    table.add_column("Fase", style="cyan")
    table.add_column("Ronde", style="cyan")
    table.add_column("Tipe", style="magenta")
    table.add_column("Lawan", style="green")
    table.add_column("Hasil", style="yellow")
    
    for record in session.round_history:
        rn = record.round_number
        table.add_row(
            str(record.phase),
            rn.value,
            "Monster" if record.opponent_type == RoundType.MONSTER else "Player",
            record.opponent.name if record.opponent else "Monster",
            record.result.value if record.result else "-"
        )
    
    console.print(table)
    console.print(f"\nPemain aktif: {len(session.active_players)}/8")


@app.command()
def players():
    """Daftar semua pemain."""
    session = get_session()
    
    table = Table(title="Daftar Pemain")
    table.add_column("Posisi", style="cyan")
    table.add_column("Nama", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Tipe", style="magenta")
    
    for p in session.players:
        status = "[green]Aktif[/green]" if p.is_active else "[red]Tereliminasi[/red]"
        ptype = "[bold]Anda[/bold]" if p.is_local_player else "Player"
        table.add_row(str(p.position), p.name, status, ptype)
    
    console.print(table)


@app.command()
def end_session():
    """Akhiri sesi saat ini."""
    global current_session
    session = get_session()
    
    session.is_active = False
    session.ended_at = session.updated_at
    storage.save_session(session)
    
    console.print(f"[yellow]Sesi {session.id} diakhiri.[/yellow]")
    current_session = None


@app.command()
def list_sessions():
    """Daftar semua sesi tersimpan."""
    sessions = storage.list_sessions()
    
    if not sessions:
        console.print("[yellow]Belum ada sesi tersimpan.[/yellow]")
        return
    
    table = Table(title="Sesi Tersimpan")
    table.add_column("ID", style="cyan")
    table.add_column("Dimulai", style="magenta")
    table.add_column("Fase", style="yellow")
    table.add_column("Ronde", style="yellow")
    table.add_column("Total Ronde", style="green")
    table.add_column("Status", style="red")
    
    for s in sessions:
        status = "[green]Aktif[/green]" if s["is_active"] else "[red]Berakhir[/red]"
        started = s["started_at"][:16] if s["started_at"] else "-"
        table.add_row(
            s["id"],
            started,
            str(s["current_phase"]),
            str(s["current_round"]),
            str(s["total_rounds"]),
            status
        )
    
    console.print(table)


@app.command()
def export_csv(
    path: str = typer.Option(
        ..., "--path", "-p", help="Path file output CSV"
    )
):
    """Export riwayat ke CSV."""
    session = get_session()
    output = Exporter.export_to_csv(session, path)
    console.print(f"[green]Exported ke:[/green] {output}")


@app.command()
def export_json(
    path: str = typer.Option(
        ..., "--path", "-p", help="Path file output JSON"
    )
):
    """Export sesi lengkap ke JSON."""
    session = get_session()
    output = Exporter.export_to_json(session, path)
    console.print(f"[green]Exported ke:[/green] {output}")


@app.command()
def import_json(
    path: str = typer.Argument(..., help="Path file JSON yang akan di-import")
):
    """Import sesi dari JSON."""
    session = Exporter.import_from_json(path)
    storage.save_session(session)
    console.print(f"[green]Imported:[/green] Sesi {session.id}")
    console.print(f"Pemain: {[p.name for p in session.players]}")


def _show_current_status():
    """Show current session status."""
    session = get_session()
    rn = session.current_round_number
    
    console.print(f"\n[bold]Status Sesi {session.id}[/bold]")
    console.print(f"  Fase: {session.current_phase}")
    console.print(f"  Ronde: {session.current_round} ({rn.value})")
    console.print(f"  Tipe: {'Predictable' if rn.is_predictable else 'Random'}")
    console.print(f"  Pemain aktif: {len(session.active_players)}/8")
    
    # Show local player
    local = session.local_player
    if local:
        console.print(f"  Pemain lokal: [bold]{local.name}[/bold]")


@app.callback()
def main():
    """MCGG Matchmaking Analyzer CLI."""
    pass


if __name__ == "__main__":
    app()
