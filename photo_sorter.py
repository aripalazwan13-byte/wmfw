from __future__ import annotations

import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont

APP_DIR = Path(__file__).resolve().parent
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
WATERMARK_TEXT = "@humassmkn1stabat"
WATERMARK_OPACITY = 102  # 40% dari 255
LOGO_WIDTH_RATIO = 0.08
BOTTOM_MARGIN_RATIO = 0.05
TEXT_SIZE_RATIO = 0.012
GAP_RATIO = 0.008


def load_font(size: int):
    candidates = [
        APP_DIR / "Anton-Regular.ttf",
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(str(candidate), max(8, size))
        except OSError:
            pass
    return ImageFont.load_default()


def apply_watermark(source_path: Path, output_path: Path, logo_path: Path | None):
    with Image.open(source_path) as original:
        photo = ImageOps.exif_transpose(original).convert("RGBA")

    width, height = photo.size
    short_side = min(width, height)
    layer = Image.new("RGBA", photo.size, (0, 0, 0, 0))
    logo = None

    if logo_path and logo_path.is_file():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            bbox = logo.getchannel("A").getbbox()
            if bbox:
                logo = logo.crop(bbox)
            target_w = max(1, int(width * LOGO_WIDTH_RATIO))
            scale = target_w / max(1, logo.width)
            target_h = max(1, int(logo.height * scale))
            max_h = max(1, int(height * 0.15))
            if target_h > max_h:
                scale = max_h / max(1, logo.height)
                target_w = max(1, int(logo.width * scale))
                target_h = max_h
            logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
            alpha = logo.getchannel("A").point(lambda a: int(a * WATERMARK_OPACITY / 255))
            logo.putalpha(alpha)
        except Exception:
            logo = None

    font = load_font(max(8, int(short_side * TEXT_SIZE_RATIO)))
    text_bbox = font.getbbox(WATERMARK_TEXT)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    logo_w, logo_h = logo.size if logo else (0, 0)
    gap = max(1, int(short_side * GAP_RATIO)) if logo else 0
    group_h = logo_h + gap + text_h if logo else text_h
    start_y = height - group_h - int(height * BOTTOM_MARGIN_RATIO)

    if logo:
        layer.alpha_composite(logo, ((width - logo_w) // 2, start_y))
        text_y = start_y + logo_h + gap - text_bbox[1]
    else:
        text_y = start_y - text_bbox[1]

    draw = ImageDraw.Draw(layer)
    text_x = (width - text_w) // 2 - text_bbox[0]
    draw.text((text_x, text_y), WATERMARK_TEXT, font=font,
              fill=(255, 255, 255, WATERMARK_OPACITY))

    result = Image.alpha_composite(photo, layer)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ext = output_path.suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        result.convert("RGB").save(output_path, quality=95, optimize=True)
    elif ext == ".webp":
        result.convert("RGB").save(output_path, quality=95, method=6)
    elif ext == ".png":
        result.save(output_path, optimize=True)
    else:
        result.convert("RGB").save(output_path, quality=95)


class PhotoSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Sorter • Humas SMKN 1 Stabat")
        self.root.geometry("1120x720")
        self.root.minsize(900, 600)

        self.source_dir = tk.StringVar(value="")
        self.output_dir = tk.StringVar(value=str(APP_DIR / "foto_tersortir"))
        self.logo_path = tk.StringVar(value=str(APP_DIR / "logo.png"))
        self.use_watermark = tk.BooleanVar(value=False)
        self.dark_mode = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Pilih folder foto untuk mulai menyortir.")
        self.files: list[Path] = []
        self.current_index = 0
        self.folder_slots: dict[int, str] = {1: "Acara", 2: "Fotbar"}
        self.photo_ref = None

        self._setup_style()
        self._build_ui()
        self._bind_keys()
        self._apply_theme()

    def _setup_style(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

    def _build_ui(self):
        self.top = ttk.Frame(self.root, padding=(14, 12))
        self.top.pack(fill="x")
        ttk.Label(self.top, text="PHOTO SORTER", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Label(self.top, text="HUMAS SMKN 1 STABAT", font=("Segoe UI", 9)).pack(side="left", padx=(12, 0))
        self.theme_button = ttk.Button(self.top, text="☀ / ☾ Mode", command=self.toggle_theme)
        self.theme_button.pack(side="right")

        paths = ttk.Frame(self.root, padding=(14, 0, 14, 10))
        paths.pack(fill="x")
        ttk.Label(paths, text="Folder foto:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(paths, textvariable=self.source_dir).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Button(paths, text="Pilih…", command=self.choose_source).grid(row=0, column=2, padx=(8, 16), pady=4)
        ttk.Label(paths, text="Folder hasil:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(paths, textvariable=self.output_dir).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(paths, text="Pilih…", command=self.choose_output).grid(row=1, column=2, padx=(8, 16), pady=4)
        paths.columnconfigure(1, weight=1)

        options = ttk.Frame(self.root, padding=(14, 0, 14, 10))
        options.pack(fill="x")
        ttk.Checkbutton(options, text="Tambahkan watermark saat menyortir", variable=self.use_watermark).pack(side="left")
        ttk.Label(options, text="Logo:").pack(side="left", padx=(16, 6))
        ttk.Entry(options, textvariable=self.logo_path, width=32).pack(side="left")
        ttk.Button(options, text="Pilih logo…", command=self.choose_logo).pack(side="left", padx=6)
        ttk.Button(options, text="＋ Tambah folder / tombol", command=self.add_folder).pack(side="right")

        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        left = ttk.Frame(body, padding=8)
        right = ttk.Frame(body, padding=8)
        body.add(left, weight=1)
        body.add(right, weight=3)

        ttk.Label(left, text="Daftar foto", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True)
        self.photo_list = tk.Listbox(list_frame, activestyle="dotbox", exportselection=False,
                                     font=("Segoe UI", 10), borderwidth=0, highlightthickness=1)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.photo_list.yview)
        self.photo_list.configure(yscrollcommand=scroll.set)
        self.photo_list.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.photo_list.bind("<<ListboxSelect>>", self.on_select)

        ttk.Label(right, text="Pratinjau foto", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.preview = tk.Label(right, text="Pilih folder foto untuk melihat pratinjau",
                                font=("Segoe UI", 12), anchor="center", relief="flat")
        self.preview.pack(fill="both", expand=True, pady=8)
        self.file_label = ttk.Label(right, text="Belum ada foto dipilih")
        self.file_label.pack(anchor="w")

        self.shortcut_frame = ttk.LabelFrame(self.root, text="Tombol sortir cepat  •  tekan angka 1–9", padding=10)
        self.shortcut_frame.pack(fill="x", padx=14, pady=(0, 8))
        self.shortcut_buttons = {}
        self._refresh_shortcuts()

        bottom = ttk.Frame(self.root, padding=(14, 0, 14, 12))
        bottom.pack(fill="x")
        ttk.Button(bottom, text="← Sebelumnya", command=self.previous_photo).pack(side="left")
        ttk.Button(bottom, text="Berikutnya →", command=self.next_photo).pack(side="left", padx=8)
        ttk.Button(bottom, text="Buka folder hasil", command=self.open_output).pack(side="left", padx=8)
        ttk.Label(bottom, textvariable=self.status).pack(side="right")

    def _bind_keys(self):
        self.root.bind("<KeyPress>", self.on_key)
        self.root.bind("<Left>", lambda e: self.previous_photo())
        self.root.bind("<Right>", lambda e: self.next_photo())

    def _apply_theme(self):
        dark = self.dark_mode.get()
        bg = "#171923" if dark else "#f2f4f8"
        panel = "#222634" if dark else "#ffffff"
        fg = "#f4f6fb" if dark else "#202533"
        field = "#11141d" if dark else "#ffffff"
        self.root.configure(bg=bg)
        self.style.configure(".", background=bg, foreground=fg, fieldbackground=field, bordercolor=panel)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", padding=(9, 6), background=panel, foreground=fg)
        self.style.map("TButton", background=[("active", "#3b82f6" if dark else "#dbeafe")])
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.configure("TLabelframe", background=bg, foreground=fg)
        self.style.configure("TLabelframe.Label", background=bg, foreground=fg)
        self.style.configure("TEntry", fieldbackground=field, foreground=fg)
        self.photo_list.configure(bg=panel, fg=fg, selectbackground="#2563eb",
                                  selectforeground="#ffffff", highlightbackground=bg)
        self.preview.configure(bg=panel, fg=fg)

    def toggle_theme(self):
        self.dark_mode.set(not self.dark_mode.get())
        self._apply_theme()

    def choose_source(self):
        folder = filedialog.askdirectory(title="Pilih folder berisi foto")
        if folder:
            self.source_dir.set(folder)
            self.load_photos()

    def choose_output(self):
        folder = filedialog.askdirectory(title="Pilih folder penyimpanan hasil")
        if folder:
            self.output_dir.set(folder)

    def choose_logo(self):
        filename = filedialog.askopenfilename(title="Pilih logo watermark",
            filetypes=[("File gambar", "*.png *.jpg *.jpeg *.webp"), ("Semua file", "*.*")])
        if filename:
            self.logo_path.set(filename)

    def load_photos(self):
        folder = Path(self.source_dir.get())
        if not folder.is_dir():
            messagebox.showwarning("Folder belum dipilih", "Pilih folder yang berisi foto terlebih dahulu.")
            return
        self.files = sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS),
                            key=lambda p: p.name.lower())
        self.photo_list.delete(0, tk.END)
        for path in self.files:
            self.photo_list.insert(tk.END, path.name)
        self.current_index = 0
        if self.files:
            self.photo_list.selection_set(0)
            self.show_photo(0)
            self.status.set(f"{len(self.files)} foto dimuat.")
        else:
            self.preview.configure(image="", text="Tidak ada foto yang didukung di folder ini.")
            self.file_label.configure(text="Tidak ada foto")
            self.status.set("Tidak ada foto ditemukan.")

    def on_select(self, _event=None):
        selection = self.photo_list.curselection()
        if selection:
            self.current_index = selection[0]
            self.show_photo(self.current_index)

    def show_photo(self, index):
        if not self.files or not (0 <= index < len(self.files)):
            return
        path = self.files[index]
        try:
            with Image.open(path) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((780, 470), Image.Resampling.LANCZOS)
                self.photo_ref = ImageTk.PhotoImage(im)
            self.preview.configure(image=self.photo_ref, text="")
            self.file_label.configure(text=f"{index + 1}/{len(self.files)}  •  {path.name}")
            self.photo_list.selection_clear(0, tk.END)
            self.photo_list.selection_set(index)
            self.photo_list.activate(index)
            self.photo_list.see(index)
        except Exception as exc:
            self.preview.configure(image="", text=f"Gagal membuka foto:\n{exc}")
        self.status.set("Pilih folder tujuan dengan tombol 1–9.")

    def on_key(self, event):
        if event.char in "123456789" and len(event.char) == 1:
            slot = int(event.char)
            if slot in self.folder_slots:
                self.sort_current(slot)
        elif event.keysym == "Right":
            self.next_photo()
        elif event.keysym == "Left":
            self.previous_photo()

    def _refresh_shortcuts(self):
        for child in self.shortcut_frame.winfo_children():
            child.destroy()
        self.shortcut_buttons = {}
        for slot in range(1, 10):
            name = self.folder_slots.get(slot)
            label = f"{slot}  •  {name}" if name else f"{slot}  •  (kosong)"
            btn = ttk.Button(self.shortcut_frame, text=label,
                             command=lambda s=slot: self.sort_current(s),
                             state=("normal" if name else "disabled"))
            btn.pack(side="left", fill="x", expand=True, padx=3)
            self.shortcut_buttons[slot] = btn

    def add_folder(self):
        used = set(self.folder_slots)
        available = [n for n in range(3, 10) if n not in used]
        if not available:
            messagebox.showinfo("Slot penuh", "Semua tombol 1–9 sudah digunakan. Hapus atau ubah folder terlebih dahulu.")
            return
        name = simpledialog.askstring("Tambah folder", "Nama folder baru:", parent=self.root)
        if not name or not name.strip():
            return
        slot = simpledialog.askinteger("Pilih tombol", f"Pilih tombol untuk folder ini: {', '.join(map(str, available))}",
                                       parent=self.root, minvalue=3, maxvalue=9)
        if slot is None:
            return
        if slot not in available:
            messagebox.showwarning("Tombol sudah digunakan", "Tombol tersebut sudah terpakai. Pilih tombol kosong.")
            return
        self.folder_slots[slot] = name.strip()
        self._refresh_shortcuts()
        self.status.set(f"Folder '{name.strip()}' ditambahkan pada tombol {slot}.")

    def sort_current(self, slot):
        if not self.files:
            messagebox.showinfo("Belum ada foto", "Pilih folder foto terlebih dahulu.")
            return
        if slot not in self.folder_slots:
            return
        source = self.files[self.current_index]
        destination_root = Path(self.output_dir.get()).expanduser()
        if not str(destination_root).strip():
            messagebox.showwarning("Folder hasil", "Pilih folder hasil terlebih dahulu.")
            return
        category = self.folder_slots[slot]
        target_dir = destination_root / category
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        if target.exists():
            stem, suffix, n = source.stem, source.suffix, 2
            while (target_dir / f"{stem}_{n}{suffix}").exists():
                n += 1
            target = target_dir / f"{stem}_{n}{suffix}"
        try:
            if self.use_watermark.get():
                logo = Path(self.logo_path.get()).expanduser() if self.logo_path.get().strip() else None
                apply_watermark(source, target, logo)
            else:
                shutil.copy2(source, target)
            self.status.set(f"Tersimpan: {category}/{target.name}")
            self.next_photo()
        except Exception as exc:
            messagebox.showerror("Gagal menyortir", f"Foto tidak dapat disimpan.\n\n{exc}")

    def next_photo(self):
        if self.files and self.current_index < len(self.files) - 1:
            self.current_index += 1
            self.show_photo(self.current_index)

    def previous_photo(self):
        if self.files and self.current_index > 0:
            self.current_index -= 1
            self.show_photo(self.current_index)

    def open_output(self):
        folder = Path(self.output_dir.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        try:
            import os
            os.startfile(str(folder))
        except Exception:
            messagebox.showinfo("Folder hasil", str(folder))


def main():
    root = tk.Tk()
    PhotoSorterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
