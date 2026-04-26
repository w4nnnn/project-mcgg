"""Rich input forms for MCGG Analyzer."""

from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table

from mcgg.models import Player, MatchResult, RoundType
from mcgg.i18n import Language, get_i18n


def get_i18n(lang: Language):
    """Get i18n instance with language set."""
    i18n = get_i18n()
    if i18n.language != lang:
        i18n.set_language(lang)
    return i18n


def prompt_player_names(lang: Language = Language.ID) -> tuple[list[str], str]:
    """Prompt for player names.
    
    Returns:
        tuple of (list of player names, name of local player)
    """
    i18n = get_i18n(lang)
    console = Console()
    
    console.print("[bold cyan]Masukkan nama-nama pemain:[/bold cyan]")
    console.print("(Minimal 2 pemain, maksimal 8 pemain)")
    console.print("(Ketik 'done' jika sudah selesai)\n")
    
    players = []
    
    while True:
        name = Prompt.ask("[yellow]Nama pemain[/yellow]")
        
        if name.lower() in ('done', 'selesai', 's'):
            break
        
        if not name.strip():
            continue
        
        if name in players:
            console.print(f"[red]Nama '{name}' sudah ada![/red]")
            continue
        
        players.append(name)
        
        if len(players) >= 8:
            console.print("[yellow]Maksimal 8 pemain tercapai.[/yellow]")
            break
        
        console.print(f"[green]Ditambahkan:[/green] {name} (total: {len(players)})")
    
    if len(players) < 2:
        console.print("[red]Minimal 2 pemain diperlukan![/red]")
        return prompt_player_names(lang)
    
    # Select local player
    console.print(f"\n[bold cyan]Pilih pemain lokal (Anda):[/bold cyan]")
    for i, p in enumerate(players, start=1):
        marker = " *" if i == 1 else ""
        console.print(f"  {i}. {p}{marker}")
    
    while True:
        choice = IntPrompt.ask(
            f"[yellow]Pilihan[/yellow] (1-{len(players)})",
            default=1
        )
        if 1 <= choice <= len(players):
            break
        console.print("[red]Pilihan tidak valid![/red]")
    
    local_name = players[choice - 1]
    
    return players, local_name


def prompt_opponent(
    player_names: list[str],
    lang: Language = Language.ID
) -> tuple[str, bool]:
    """Prompt for opponent name.
    
    Returns:
        tuple of (opponent_name, is_monster)
    """
    console = Console()
    
    console.print("\n[bold cyan]Pilih Lawan:[/bold cyan]")
    console.print("  0. Monster")
    for i, p in enumerate(player_names, start=1):
        console.print(f"  {i}. {p}")
    
    while True:
        choice = IntPrompt.ask("[yellow]Pilihan[/yellow]", default=0)
        
        if choice == 0:
            return ("Monster", True)
        if 1 <= choice <= len(player_names):
            return (player_names[choice - 1], False)
        console.print("[red]Pilihan tidak valid![/red]")


def prompt_match_result(lang: Language = Language.ID) -> MatchResult:
    """Prompt for match result."""
    console = Console()
    
    console.print("\n[bold cyan]Pilih Hasil:[/bold cyan]")
    console.print("  1. Win (Menang)")
    console.print("  2. Lose (Kalah)")
    console.print("  3. Draw (Seri)")
    
    while True:
        choice = IntPrompt.ask("[yellow]Pilihan[/yellow]", default=1)
        
        if choice == 1:
            return MatchResult.WIN
        if choice == 2:
            return MatchResult.LOSE
        if choice == 3:
            return MatchResult.DRAW
        console.print("[red]Pilihan tidak valid![/red]")


def prompt_yes_no(message: str, default: bool = False, lang: Language = Language.ID) -> bool:
    """Prompt for yes/no confirmation."""
    return Confirm.ask(f"[yellow]{message}[/yellow]", default=default)


def display_round_summary(
    round_num: str,
    opponent: str,
    result: MatchResult,
    next_phase: int,
    next_round: int,
    lang: Language = Language.ID
):
    """Display a summary after recording a round."""
    console = Console()
    
    console.print(f"\n[green]Ronde {round_num} berhasil direkam![/green]")
    console.print(f"  Lawan: {opponent}")
    console.print(f"  Hasil: [bold]{result.value.upper()}[/bold]")
    console.print(f"\n[cyan]Selanjutnya:[/cyan]")
    console.print(f"  Fase {next_phase}, Ronde {next_round}")
