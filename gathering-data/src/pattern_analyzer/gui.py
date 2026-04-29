"""Tkinter GUI for gathering-data project."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
import uuid

from pattern_analyzer.models import (
    normalize_players,
    build_round_matches,
    round_key,
    upsert_round_matches,
    suggest_next_round,
)
from pattern_analyzer.storage import SessionStore


class GatheringDataApp:
    def __init__(self, root: tk.Tk, store: SessionStore) -> None:
        self.root = root
        self.store = store
        self.current_session_id: str | None = None
        self.round_rows: list[tuple[ttk.Combobox, ttk.Combobox]] = []
        self.selected_round_key: tuple[str, int, int] | None = None

        self.root.title("Gathering Data MCGG")
        self.root.geometry("1100x700")

        self._build_layout()
        self._refresh_session_list()

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="Siap. Buat sesi baru atau buka sesi.")
        header = ttk.Label(main, textvariable=self.status_var, anchor="w", font=("TkDefaultFont", 10, "bold"))
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        left = ttk.LabelFrame(main, text="Sesi")
        left.grid(row=1, column=0, sticky="ns", padx=(0, 12))

        self.session_listbox = tk.Listbox(left, width=24, height=28)
        self.session_listbox.pack(fill=tk.Y, padx=8, pady=8)

        buttons = ttk.Frame(left)
        buttons.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Button(buttons, text="Refresh", command=self._refresh_session_list).pack(fill=tk.X, pady=2)
        ttk.Button(buttons, text="Buka Sesi", command=self._open_selected_session).pack(fill=tk.X, pady=2)
        ttk.Button(buttons, text="Sesi Baru", command=self._new_session).pack(fill=tk.X, pady=2)
        ttk.Button(buttons, text="Hapus Sesi", command=self._delete_selected_session).pack(fill=tk.X, pady=2)

        right = ttk.Frame(main)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)

        session_box = ttk.LabelFrame(right, text="1) Informasi Sesi")
        session_box.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        session_box.columnconfigure(1, weight=1)

        ttk.Label(session_box, text="Session ID").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.session_id_var = tk.StringVar()
        ttk.Entry(session_box, textvariable=self.session_id_var, state="readonly").grid(
            row=0, column=1, sticky="ew", padx=8, pady=8
        )
        ttk.Button(session_box, text="Simpan Sesi", command=self._save_session).grid(row=0, column=2, padx=8, pady=8)

        players_box = ttk.LabelFrame(right, text="2) Input Pemain Aktif (2-8)")
        players_box.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.player_vars: list[tk.StringVar] = []
        for i in range(8):
            var = tk.StringVar()
            var.trace_add("write", self._on_players_changed)
            self.player_vars.append(var)
            ttk.Label(players_box, text=f"Pemain {i+1}").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=(8, 4), pady=4)
            ttk.Entry(players_box, textvariable=var).grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="ew", padx=(0, 8), pady=4)
            players_box.columnconfigure((i % 2) * 2 + 1, weight=1)

        round_box = ttk.LabelFrame(right, text="3) Setup Ronde + Pairing")
        round_box.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        round_box.columnconfigure(1, weight=1)

        top_meta = ttk.Frame(round_box)
        top_meta.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=8)

        ttk.Label(top_meta, text="Round Label").grid(row=0, column=0, sticky="w")
        self.round_label_var = tk.StringVar(value="i-2")
        ttk.Entry(top_meta, textvariable=self.round_label_var, width=18).grid(row=0, column=1, sticky="w", padx=(4, 16))

        ttk.Label(top_meta, text="Phase").grid(row=0, column=2, sticky="w")
        self.phase_var = tk.IntVar(value=1)
        ttk.Spinbox(top_meta, from_=1, to=99, textvariable=self.phase_var, width=6).grid(row=0, column=3, padx=(4, 16))

        ttk.Label(top_meta, text="Round No").grid(row=0, column=4, sticky="w")
        self.round_no_var = tk.IntVar(value=2)
        ttk.Spinbox(top_meta, from_=1, to=99, textvariable=self.round_no_var, width=6).grid(row=0, column=5, padx=(4, 16))

        self.editing_var = tk.StringVar(value="Mode: Tambah ronde baru")
        ttk.Label(top_meta, textvariable=self.editing_var, foreground="#375a7f").grid(row=0, column=6, sticky="w")

        pair_frame = ttk.Frame(round_box)
        pair_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        pair_frame.columnconfigure(1, weight=1)
        pair_frame.columnconfigure(2, weight=1)
        for i in range(4):
            ttk.Label(pair_frame, text=f"Pair {i+1}").grid(row=i, column=0, sticky="w", pady=3)
            c1 = ttk.Combobox(pair_frame, state="readonly")
            c2 = ttk.Combobox(pair_frame, state="readonly")
            c1.grid(row=i, column=1, sticky="ew", padx=4, pady=3)
            c2.grid(row=i, column=2, sticky="ew", padx=4, pady=3)
            c1.bind("<<ComboboxSelected>>", self._on_pair_selection_changed)
            c2.bind("<<ComboboxSelected>>", self._on_pair_selection_changed)
            c1.bind("<Button-1>", self._on_dropdown_open)
            c2.bind("<Button-1>", self._on_dropdown_open)
            self.round_rows.append((c1, c2))

        action_row = ttk.Frame(round_box)
        action_row.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        ttk.Button(action_row, text="Simpan Ronde (Tambah/Update)", command=self._save_round).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_row, text="Kosongkan Pairing", command=self._clear_round_inputs).pack(side=tk.LEFT)

        saved_box = ttk.LabelFrame(right, text="4) Ronde Tersimpan (klik untuk edit)")
        saved_box.grid(row=3, column=0, sticky="nsew")
        saved_box.columnconfigure(0, weight=1)
        saved_box.rowconfigure(0, weight=1)

        columns = ("round_label", "phase", "round_no", "pairing")
        self.rounds_tree = ttk.Treeview(saved_box, columns=columns, show="headings", height=10)
        self.rounds_tree.heading("round_label", text="Round Label")
        self.rounds_tree.heading("phase", text="Phase")
        self.rounds_tree.heading("round_no", text="Round No")
        self.rounds_tree.heading("pairing", text="Pairings")
        self.rounds_tree.column("round_label", width=120, anchor="w")
        self.rounds_tree.column("phase", width=70, anchor="center")
        self.rounds_tree.column("round_no", width=80, anchor="center")
        self.rounds_tree.column("pairing", width=540, anchor="w")
        self.rounds_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.rounds_tree.bind("<<TreeviewSelect>>", self._on_round_selected)

        scrollbar = ttk.Scrollbar(saved_box, orient="vertical", command=self.rounds_tree.yview)
        self.rounds_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=8)

    def _players_from_inputs(self) -> list[str]:
        return [v.get() for v in self.player_vars]

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _refresh_dropdown_values(self) -> None:
        players = [p.strip() for p in self._players_from_inputs() if p.strip()]
        base_options = players + ["MIRROR"]
        chosen_by_row: list[set[str]] = []
        globally_used: set[str] = set()

        for c1, c2 in self.round_rows:
            row_selected = {c1.get().strip(), c2.get().strip()} - {""}
            chosen_by_row.append(row_selected)
            globally_used.update(row_selected)

        for idx, (c1, c2) in enumerate(self.round_rows):
            row_reserved = chosen_by_row[idx]
            used_elsewhere = globally_used - row_reserved
            allowed_for_row = [name for name in base_options if name not in used_elsewhere]

            current_1 = c1.get().strip()
            current_2 = c2.get().strip()

            values_1 = list(allowed_for_row)
            values_2 = list(allowed_for_row)

            if current_2:
                values_1 = [name for name in values_1 if name != current_2]
            if current_1:
                values_2 = [name for name in values_2 if name != current_1]

            c1["values"] = values_1
            c2["values"] = values_2

    def _on_pair_selection_changed(self, _event: tk.Event | None = None) -> None:
        self._refresh_dropdown_values()

    def _on_dropdown_open(self, _event: tk.Event | None = None) -> None:
        self._refresh_dropdown_values()

    def _on_players_changed(self, *_args: object) -> None:
        self._refresh_dropdown_values()

    def _clear_round_inputs(self) -> None:
        self.selected_round_key = None
        self.editing_var.set("Mode: Tambah ronde baru")
        for c1, c2 in self.round_rows:
            c1.set("")
            c2.set("")
        self._refresh_dropdown_values()

    def _new_session(self) -> None:
        sid = str(uuid.uuid4())[:8]
        self.current_session_id = sid
        self.session_id_var.set(sid)
        for v in self.player_vars:
            v.set("")
        self.round_label_var.set("i-2")
        self.phase_var.set(1)
        self.round_no_var.set(2)
        self._clear_round_inputs()
        self._reload_saved_rounds([])
        self._set_status(f"Sesi baru dibuat: {sid}")

    def _refresh_session_list(self) -> None:
        self.session_listbox.delete(0, tk.END)
        for sid in self.store.list_sessions():
            self.session_listbox.insert(tk.END, sid)

    def _selected_session_id(self) -> str | None:
        selected = self.session_listbox.curselection()
        if not selected:
            return None
        return self.session_listbox.get(selected[0])

    def _group_rounds(self, matches: list[dict]) -> dict[tuple[str, int, int], list[dict]]:
        grouped: dict[tuple[str, int, int], list[dict]] = {}
        for m in matches:
            key = round_key(m)
            grouped.setdefault(key, []).append(m)
        return grouped

    def _reload_saved_rounds(self, matches: list[dict]) -> None:
        for item in self.rounds_tree.get_children():
            self.rounds_tree.delete(item)

        grouped = self._group_rounds(matches)
        for key in sorted(grouped.keys(), key=lambda x: (x[1], x[2], x[0])):
            rows = grouped[key]
            pair_text = ", ".join([f"{r['player1']} vs {r['player2']}" for r in rows])
            self.rounds_tree.insert("", tk.END, values=(key[0], key[1], key[2], pair_text))

    def _open_selected_session(self) -> None:
        sid = self._selected_session_id()
        if not sid:
            messagebox.showwarning("Info", "Pilih sesi dulu.")
            return

        data = self.store.load(sid)
        self.current_session_id = data["id"]
        self.session_id_var.set(data["id"])

        players = data.get("players", [])
        for i, var in enumerate(self.player_vars):
            var.set(players[i] if i < len(players) else "")

        self._refresh_dropdown_values()
        self._reload_saved_rounds(data.get("matches", []))
        self._clear_round_inputs()
        self._set_status(f"Sesi {sid} dibuka. Pilih ronde tersimpan untuk edit.")

    def _delete_selected_session(self) -> None:
        sid = self._selected_session_id()
        if not sid:
            messagebox.showwarning("Info", "Pilih sesi dulu.")
            return
        if not messagebox.askyesno("Konfirmasi", f"Hapus sesi {sid}?"):
            return
        self.store.delete(sid)
        if self.current_session_id == sid:
            self._new_session()
        self._refresh_session_list()
        self._set_status(f"Sesi {sid} dihapus.")

    def _read_current_session_payload(self) -> dict:
        if not self.current_session_id:
            raise ValueError("Klik 'Sesi Baru' atau buka sesi dulu.")

        players = normalize_players(self._players_from_inputs())

        if self.store.session_path(self.current_session_id).exists():
            payload = self.store.load(self.current_session_id)
        else:
            payload = {"id": self.current_session_id, "players": players, "matches": []}

        payload["players"] = players
        return payload

    def _on_round_selected(self, _event: tk.Event | None = None) -> None:
        if not self.current_session_id:
            return

        selected = self.rounds_tree.selection()
        if not selected:
            return
        values = self.rounds_tree.item(selected[0], "values")
        key = (str(values[0]), int(values[1]), int(values[2]))

        payload = self.store.load(self.current_session_id)
        grouped = self._group_rounds(payload.get("matches", []))
        rows = grouped.get(key, [])
        if not rows:
            return

        self.round_label_var.set(key[0])
        self.phase_var.set(key[1])
        self.round_no_var.set(key[2])
        self.selected_round_key = key
        self.editing_var.set(f"Mode: Edit ronde {key[0]} / phase {key[1]} / round {key[2]}")

        for i, (c1, c2) in enumerate(self.round_rows):
            if i < len(rows):
                c1.set(rows[i]["player1"])
                c2.set(rows[i]["player2"])
            else:
                c1.set("")
                c2.set("")
        self._refresh_dropdown_values()
        self._set_status("Ronde dimuat ke editor. Perbaiki pairing lalu simpan.")

    def _save_round(self) -> None:
        try:
            self._refresh_dropdown_values()
            payload = self._read_current_session_payload()

            pairs: list[tuple[str, str]] = []
            for c1, c2 in self.round_rows:
                pairs.append((c1.get(), c2.get()))

            matches = build_round_matches(
                payload["players"],
                self.round_label_var.get(),
                self.phase_var.get(),
                self.round_no_var.get(),
                pairs,
            )

            payload["matches"] = upsert_round_matches(payload.get("matches", []), matches)
            self.store.save(payload)

            self._reload_saved_rounds(payload["matches"])
            self._refresh_session_list()

            next_label, next_no = suggest_next_round(self.round_label_var.get(), self.round_no_var.get())
            self.round_label_var.set(next_label)
            self.round_no_var.set(next_no)
            self.selected_round_key = None
            self.editing_var.set("Mode: Tambah ronde baru")
            for c1, c2 in self.round_rows:
                c1.set("")
                c2.set("")
            self._refresh_dropdown_values()

            messagebox.showinfo("Sukses", "Ronde tersimpan. Editor pindah ke ronde berikutnya.")
            self._set_status(f"Ronde tersimpan. Lanjut input ronde {next_label} (round {next_no}).")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _save_session(self) -> None:
        try:
            payload = self._read_current_session_payload()
            self.store.save(payload)
            self._refresh_session_list()
            self._reload_saved_rounds(payload.get("matches", []))
            messagebox.showinfo("Sukses", "Sesi tersimpan.")
            self._set_status("Sesi tersimpan.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


def run_gui() -> None:
    root = tk.Tk()
    app = GatheringDataApp(root, SessionStore())
    app._new_session()
    root.mainloop()
