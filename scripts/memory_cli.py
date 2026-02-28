import argparse
import asyncio
import json
import sys
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Add project root to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import init_db, close_db, get_recent_sessions, get_messages_for_session, add_pinned_memory, get_pinned_memories, remove_pinned_memory, clear_unpinned_memories

load_dotenv()
console = Console()

async def list_sessions():
    sessions = await get_recent_sessions(5)
    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return
        
    table = Table(title="Last 5 Sessions")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Summary", style="green")
    table.add_column("Ended At", style="magenta")

    for s in sessions:
        ended_at = s['ended_at'].strftime("%Y-%m-%d %H:%M:%S") if s['ended_at'] else "Ongoing"
        table.add_row(str(s['id']), s['summary'] or "No summary", ended_at)

    console.print(table)

async def show_session(session_id: int):
    messages = await get_messages_for_session(session_id)
    if not messages:
        console.print(f"[yellow]No messages found for session {session_id}.[/yellow]")
        return
    
    for m in messages:
        if m['role'] == 'user':
            console.print(f"[blue]User:[/blue] {m['content']}")
        else:
            console.print(f"[green]Chuks:[/green] {m['content']}\n")

async def pin_memory(content: str):
    await add_pinned_memory(content)
    console.print(f"[green]Successfully pinned memory:[/green] {content}")

async def list_pins():
    pins = await get_pinned_memories()
    if not pins:
        console.print("[yellow]No pinned memories found.[/yellow]")
        return
        
    table = Table(title="Pinned Memories")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Category", style="magenta")
    table.add_column("Content", style="green")

    for p in pins:
        table.add_row(str(p['id']), p['category'], p['content'])

    console.print(table)

async def unpin_memory(memory_id: int):
    await remove_pinned_memory(memory_id)
    console.print(f"[green]Successfully unpinned memory ID: {memory_id}[/green]")

async def clear_memories():
    confirm = input("Are you sure you want to clear all non-pinned memories? (y/N): ")
    if confirm.lower() == 'y':
        await clear_unpinned_memories()
        console.print("[red]All non-pinned memories cleared.[/red]")
    else:
        console.print("[yellow]Aborted.[/yellow]")

async def export_session(session_id: int):
    messages = await get_messages_for_session(session_id)
    if not messages:
        console.print(f"[yellow]No messages found for session {session_id}.[/yellow]")
        return
    
    filename = f"session_{session_id}_export.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    console.print(f"[green]Exported session {session_id} to {filename}[/green]")

async def main():
    parser = argparse.ArgumentParser(description="Chuks Memory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="Show last 5 sessions with summaries")
    
    show_parser = subparsers.add_parser("show", help="Show all messages from a session")
    show_parser.add_argument("session_id", type=int)

    pin_parser = subparsers.add_parser("pin", help="Pin a memory")
    pin_parser.add_argument("content", type=str)

    subparsers.add_parser("pins", help="List all pinned memories")

    unpin_parser = subparsers.add_parser("unpin", help="Remove a pinned memory")
    unpin_parser.add_argument("memory_id", type=int)

    subparsers.add_parser("clear", help="Clear all non-pinned memories")

    export_parser = subparsers.add_parser("export", help="Export session as JSON")
    export_parser.add_argument("session_id", type=int)

    args = parser.parse_args()

    await init_db()

    try:
        if args.command == "list":
            await list_sessions()
        elif args.command == "show":
            await show_session(args.session_id)
        elif args.command == "pin":
            await pin_memory(args.content)
        elif args.command == "pins":
            await list_pins()
        elif args.command == "unpin":
            await unpin_memory(args.memory_id)
        elif args.command == "clear":
            await clear_memories()
        elif args.command == "export":
            await export_session(args.session_id)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
