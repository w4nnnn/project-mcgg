"""Rich tables for MCGG Analyzer."""

from rich.table import Table
from rich.box import ROUNDED

from mcgg.models import Session, Player, RoundRecord, RoundType, RoundNumber


def create_history_table(session: Session) -> Table:
    """Create a formatted history table."""
    table = Table(
        title=f"Riwayat Ronde - Sesi {session.id}",
        box=ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Fase", justify="center", style="cyan")
    table.add_column("Ronde", justify="center", style="cyan")
    table.add_column("Tipe", style="magenta")
    table.add_column("Lawan", style="green")
    table.add_column("Hasil", style="yellow")
    
    for record in session.round_history:
        rn = record.round_number
        opp_type = "Monster" if record.opponent_type == RoundType.MONSTER else "Player"
        opp_name = record.opponent.name if record.opponent else "Monster"
        result = record.result.value if record.result else "-"
        
        table.add_row(
            str(record.phase),
            rn.value,
            opp_type,
            opp_name,
            result
        )
    
    return table


def create_player_table(session: Session) -> Table:
    """Create a formatted player table."""
    table = Table(
        title="Daftar Pemain",
        box=ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Posisi", justify="center", style="cyan")
    table.add_column("Nama", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Tipe", style="magenta")
    
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


def create_session_list_table(sessions: list) -> Table:
    """Create a formatted session list table."""
    table = Table(
        title="Sesi Tersimpan",
        box=ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("ID", style="cyan")
    table.add_column("Dimulai", style="magenta")
    table.add_column("Fase", justify="center", style="yellow")
    table.add_column("Ronde", justify="center", style="yellow")
    table.add_column("Total", justify="center", style="green")
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
    
    return table


def create_prediction_chain_table(prediction, session: Session) -> Table:
    """Create a visualization of the prediction chain."""
    table = Table(
        title="Visualisasi Chain Prediction",
        box=ROUNDED,
        show_header=False
    )
    table.add_column("Step", style="cyan")
    table.add_column("Description", style="white")
    
    if prediction.chain_description:
        parts = prediction.chain_description.split(" → ")
        for i, part in enumerate(parts, start=1):
            table.add_row(str(i), part)
    
    return table
