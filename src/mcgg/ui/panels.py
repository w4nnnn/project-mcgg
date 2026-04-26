"""Rich UI panels for MCGG Analyzer."""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED

from mcgg.models import Session, Player, Prediction, RoundType, RoundNumber
from mcgg.i18n import get_i18n, Language


def get_i18n_instance(lang: Language = Language.ID):
    """Get i18n instance for given language."""
    i18n = get_i18n()
    if i18n.language != lang:
        i18n.set_language(lang)
    return i18n


def phase_indicator_panel(session: Session, lang: Language = Language.ID) -> Panel:
    """Show current phase and round indicator."""
    i18n = get_i18n_instance(lang)
    rn = session.current_round_number
    
    # Build content
    phase_text = Text()
    phase_text.append(f"Fase: ", style="bold cyan")
    phase_text.append(f"{session.current_phase}", style="bold white")
    phase_text.append(f"\nRonde: ", style="bold cyan")
    phase_text.append(f"{session.current_round} ({rn.value})", style="bold white")
    phase_text.append(f"\nTipe: ", style="bold cyan")
    
    if rn.is_predictable:
        phase_text.append("Dapat Diprediksi", style="bold green")
    else:
        phase_text.append("Acak (Random)", style="bold yellow")
    
    phase_text.append(f"\nPemain Aktif: ", style="bold cyan")
    phase_text.append(f"{len(session.active_players)}/8", style="bold white")
    
    return Panel(
        phase_text,
        title=f"[bold]Status Permainan[/bold]",
        box=ROUNDED,
        style="blue"
    )


def prediction_panel(prediction: Prediction, session: Session, lang: Language = Language.ID) -> Panel:
    """Show prediction result panel."""
    i18n = get_i18n_instance(lang)
    rn = session.current_round_number
    
    if prediction.is_valid and prediction.predicted_opponent:
        # Success prediction
        content = Text()
        content.append(f"[bold green]Lawan Diprediksi:[/bold green] ", style="bold")
        content.append(f"{prediction.predicted_opponent.name}", style="bold white")
        content.append(f"\n[bold yellow]Confidence:[/bold yellow] ")
        content.append(f"{prediction.confidence:.0%}", style="bold white")
        
        if prediction.chain_description:
            content.append(f"\n[bold cyan]Chain:[/bold cyan] ")
            content.append(f"{prediction.chain_description}", style="italic")
        
        if prediction.warnings:
            content.append(f"\n[bold red]Warnings:[/bold red]")
            for w in prediction.warnings:
                content.append(f"\n  - {w}", style="yellow")
        
        style = "green"
    else:
        # Cannot predict
        content = Text()
        content.append(f"[bold red]Tidak Dapat Diprediksi[/bold red]")
        content.append(f"\n[bold]Ronde:[/bold] {rn.value}")
        content.append(f"\n[bold]Alasan:[/bold] {prediction.prediction_method}")
        
        if prediction.warnings:
            for w in prediction.warnings:
                content.append(f"\n  - {w}", style="yellow")
        
        style = "red"
    
    return Panel(
        content,
        title=f"[bold]Prediksi - {rn.value}[/bold]",
        box=ROUNDED,
        style=style
    )


def session_info_panel(session: Session, lang: Language = Language.ID) -> Panel:
    """Show session information panel."""
    i18n = get_i18n_instance(lang)
    
    content = Text()
    content.append(f"ID: ", style="cyan")
    content.append(f"{session.id}\n")
    content.append(f"Fase: ", style="cyan")
    content.append(f"{session.current_phase}\n")
    content.append(f"Ronde: ", style="cyan")
    content.append(f"{session.current_round}\n")
    content.append(f"Total Ronde Dimainkan: ", style="cyan")
    content.append(f"{len(session.round_history)}\n")
    content.append(f"Pemain: ", style="cyan")
    content.append(f"{len(session.players)}\n")
    content.append(f"Pemain Aktif: ", style="cyan")
    content.append(f"{len(session.active_players)}/8\n")
    
    status = "[green]Aktif[/green]" if session.is_active else "[red]Berakhir[/red]"
    content.append(f"Status: ", style="cyan")
    content.append(f"{status}\n")
    
    # Show local player
    local = session.local_player
    if local:
        content.append(f"\nPemain Lokal: [bold]{local.name}[/bold]")
    
    return Panel(
        content,
        title=f"[bold]Info Sesi[/bold]",
        box=ROUNDED,
        style="blue"
    )


def player_list_panel(session: Session, lang: Language = Language.ID) -> Table:
    """Show player list as a table."""
    i18n = get_i18n_instance(lang)
    
    table = Table(box=ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Posisi", justify="center")
    table.add_column("Nama", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Tipe")
    
    for p in session.players:
        status = "[green]Aktif[/green]" if p.is_active else "[red]Tereliminasi[/red]"
        ptype = "[bold]Anda[/bold]" if p.is_local_player else "Player"
        table.add_row(
            str(p.position),
            p.name,
            status,
            ptype
        )
    
    return table


def round_history_panel(session: Session, lang: Language = Language.ID) -> Table:
    """Show round history as a table."""
    i18n = get_i18n_instance(lang)
    
    if not session.round_history:
        return Panel(
            Text("[yellow]Belum ada ronde yang dimainkan.[/yellow]"),
            title="[bold]Riwayat Ronde[/bold]",
            box=ROUNDED
        )
    
    table = Table(box=ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Fase", justify="center")
    table.add_column("Ronde", justify="center")
    table.add_column("Tipe", style="magenta")
    table.add_column("Lawan", style="green")
    
    for record in session.round_history:
        rn = record.round_number
        opp_type = "Monster" if record.opponent_type == RoundType.MONSTER else "Player"
        opp_name = record.opponent.name if record.opponent else "Monster"
        table.add_row(
            str(record.phase),
            rn.value,
            opp_type,
            opp_name
        )
    
    return table
