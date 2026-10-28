import json
import os
import sys
import time
import difflib

# =====================================================================
# BAGIAN 1: PENGATURAN AWAL
# =====================================================================

# Lokasi books.json = satu folder dengan file program ini.
# Jadi tidak masalah program dijalankan dari folder mana pun.
FOLDER = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(FOLDER, "books.json")

# Supaya warna (ANSI) dan simbol seperti █ ★ tampil benar di Windows.
if os.name == "nt":
    os.system("")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# =====================================================================
# BAGIAN 2: WARNA
# Warna di terminal dibuat dengan kode khusus "\033[...m".
# Kita simpan di satu tempat supaya mudah dipakai dan diganti.
# =====================================================================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def warna(teks, *kode):
    """Bungkus teks dengan warna, lalu kembalikan ke normal di akhir."""
    return "".join(kode) + str(teks) + C.RESET


# =====================================================================
# BAGIAN 3: ANIMASI DAN TAMPILAN
# =====================================================================

def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def ketik(teks, jeda=0.03):
    """Efek mengetik: huruf muncul satu per satu."""
    for huruf in teks:
        sys.stdout.write(huruf)
        sys.stdout.flush()      # paksa huruf langsung tampil
        time.sleep(jeda)
    print()


def loading(pesan, durasi=1.2):
    """Animasi spinner berputar selama beberapa detik."""
    putar = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    selesai = time.time() + durasi
    i = 0
    while time.time() < selesai:
        sys.stdout.write("\r" + warna(putar[i % len(putar)], C.CYAN) + " " + pesan)
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    # \r kembali ke awal baris, spasi menghapus tulisan spinner tadi
    sys.stdout.write("\r" + " " * (len(pesan) + 4) + "\r")
    sys.stdout.flush()


def bar_animasi(pesan, lebar=30):
    """Progress bar yang terisi pelan-pelan."""
    for i in range(lebar + 1):
        isi = "█" * i + "░" * (lebar - i)
        persen = int(i / lebar * 100)
        sys.stdout.write(f"\r{pesan} " + warna(isi, C.GREEN) + f" {persen}%")
        sys.stdout.flush()
        time.sleep(0.02)
    print()


def garis(panjang=64, simbol="─"):
    print(warna(simbol * panjang, C.DIM))


def banner():
    """Judul besar berwarna yang muncul baris demi baris."""
    kotak = [
        "╔══════════════════════════════════════════════════════════╗",
        "║                                                          ║",
        "║              📚  B O O K   T R A C K E R  📚             ║",
        "║                                                          ║",
        "╚══════════════════════════════════════════════════════════╝",
    ]
    # Setiap baris diberi warna berbeda supaya terlihat seperti gradasi
    gradasi = [C.MAGENTA, C.BLUE, C.CYAN, C.GREEN, C.YELLOW]
    for baris, w in zip(kotak, gradasi):
        print(warna(baris, w, C.BOLD))
        time.sleep(0.12)


def layar_sambutan():
    bersihkan_layar()
    print()
    banner()
    print()
    ketik(warna("  Selamat datang, Pembaca! ✨", C.YELLOW, C.BOLD), 0.04)
    ketik(warna("  Catat, cari, dan kenali buku-bukumu di sini.", C.WHITE), 0.02)
    print()
    loading("Menyiapkan rak buku...", 1.3)


# =====================================================================
# BAGIAN 4: BACA DAN SIMPAN DATA
# =====================================================================

def load():
    """Baca books.json. Kalau file belum ada / rusak, mulai dari daftar kosong."""
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(warna("⚠ books.json rusak (cek koma / kurung). Mulai dari kosong.", C.RED))
        return []


def save(books):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)


# =====================================================================
# BAGIAN 5: PENCARIAN
# =====================================================================

def cari(books, kata):
    """
    Cari buku berdasarkan kata kunci (judul ATAU penulis).
    Setiap buku diberi skor 0 sampai 1, makin mirip makin tinggi.
    """
    kata = kata.lower().strip()
    kata_kata = kata.split()
    hasil = []

    for b in books:
        judul = b.get("judul", "").lower()
        penulis = b.get("penulis", "").lower()
        gabungan = judul + " " + penulis

        if kata == judul:
            skor = 1.0                                  # persis sama
        elif kata in judul:
            skor = 0.95                                 # "dune" ada di judul
        elif kata in penulis:
            skor = 0.9                                  # "tere" ada di penulis
        elif all(k in gabungan for k in kata_kata):
            skor = 0.85                                 # "dune herbert" (judul + penulis)
        elif all(difflib.get_close_matches(k, gabungan.split(), n=1, cutoff=0.75)
                 for k in kata_kata):
            # Toleran typo per kata: "poter" dianggap mirip "potter"
            skor = 0.8
        else:
            # Cadangan: bandingkan seluruh kalimat
            skor = difflib.SequenceMatcher(None, kata, judul).ratio()

        if skor >= 0.6:                                 # di bawah 0.6 dianggap tidak cocok
            hasil.append((skor, b))

    hasil.sort(key=lambda x: x[0], reverse=True)        # skor tertinggi di atas
    return [b for skor, b in hasil[:8]]                 # ambil maksimal 8


def potong(teks, panjang):
    """Potong teks panjang dan beri '…' supaya tabel tidak berantakan."""
    return teks if len(teks) <= panjang else teks[: panjang - 1] + "…"


def tampil_hasil(hasil):
    print()
    print(warna(f"  {'No':<4}{'Judul':<34}{'Penulis':<22}{'Genre'}", C.BOLD, C.CYAN))
    garis(80)
    for i, b in enumerate(hasil, start=1):
        print(
            "  " + warna(f"{i:<4}", C.YELLOW)
            + warna(f"{potong(b['judul'], 32):<34}", C.WHITE, C.BOLD)
            + warna(f"{potong(b['penulis'], 20):<22}", C.GREEN)
            + warna(b.get("genre", "-"), C.MAGENTA)
        )
    garis(80)


def tampil_detail(b):
    print()
    print(warna("  ╭─────────────── DETAIL BUKU ───────────────╮", C.CYAN))
    print("   " + warna("Judul    : ", C.DIM) + warna(b["judul"], C.WHITE, C.BOLD))
    print("   " + warna("Penulis  : ", C.DIM) + warna(b["penulis"], C.GREEN))
    print("   " + warna("Genre    : ", C.DIM) + warna(b.get("genre", "-"), C.MAGENTA))
    print("   " + warna("Halaman  : ", C.DIM) + warna(b.get("halaman", "-"), C.YELLOW))
    print(warna("  ╰───────────────────────────────────────────╯", C.CYAN))


# =====================================================================
# BAGIAN 6: INPUT DENGAN VALIDASI
# =====================================================================

def tanya(pertanyaan, wajib=True):
    """Tanya teks. Kalau wajib, ulangi terus sampai tidak kosong."""
    while True:
        jawab = input(warna(pertanyaan, C.CYAN)).strip()
        if jawab or not wajib:
            return jawab
        print(warna("  ✗ Tidak boleh kosong, coba lagi.", C.RED))


def tanya_angka(pertanyaan):
    """Tanya angka positif. Ulangi terus sampai user mengetik angka yang benar."""
    while True:
        jawab = input(warna(pertanyaan, C.CYAN)).strip()
        if jawab.isdigit() and int(jawab) > 0:
            return int(jawab)
        print(warna("  ✗ Harus angka lebih dari 0 (contoh: 320).", C.RED))


# =====================================================================
# BAGIAN 7: TAMBAH BUKU
# =====================================================================

def tambah_buku(books, judul_awal=""):
    print()
    print(warna("  ➕ TAMBAH BUKU BARU", C.GREEN, C.BOLD))
    print(warna("  (data akan disimpan ke books.json)", C.DIM))
    print()

    if judul_awal:
        # Judul sudah diketik user di pencarian, jadi tinggal dikonfirmasi
        print(warna("  Judul   : ", C.CYAN) + warna(judul_awal, C.WHITE, C.BOLD))
        judul = judul_awal
    else:
        judul = tanya("  Judul   : ")

    penulis = tanya("  Penulis : ")
    genre = tanya("  Genre   : ")
    halaman = tanya_angka("  Halaman : ")

    buku_baru = {
        "judul": judul,
        "penulis": penulis,
        "genre": genre,
        "halaman": halaman,
    }

    books.append(buku_baru)
    print()
    bar_animasi("  Menyimpan")
    save(books)
    print(warna(f"  ✓ '{judul}' berhasil ditambahkan! Total: {len(books)} buku.", C.GREEN, C.BOLD))


# =====================================================================
# BAGIAN 8: MENU CARI BUKU
# =====================================================================

def menu_cari(books):
    print()
    print(warna("  🔎 CARI BUKU", C.YELLOW, C.BOLD))
    kata = tanya("  Ketik judul atau penulis: ")

    loading("Mencari di rak...", 0.9)
    hasil = cari(books, kata)

    # ----- Kasus 1: buku TIDAK ketemu -----
    if not hasil:
        print(warna(f"  ✗ Buku '{kata}' belum ada di database.", C.RED, C.BOLD))
        print()
        jawab = input(warna("  Mau memasukkan data bukunya sekarang? (y/n): ", C.YELLOW)).strip().lower()
        if jawab == "y":
            tambah_buku(books, judul_awal=kata)
        return

    # ----- Kasus 2: buku ketemu -----
    print(warna(f"  ✓ Ditemukan {len(hasil)} buku:", C.GREEN, C.BOLD))
    tampil_hasil(hasil)

    pilih = input(warna("  Ketik nomor untuk lihat detail (Enter untuk kembali): ", C.CYAN)).strip()
    if pilih.isdigit() and 1 <= int(pilih) <= len(hasil):
        tampil_detail(hasil[int(pilih) - 1])
    elif pilih == "":
        return

    # Kalau yang dicari ternyata tidak ada di daftar, tawarkan menambah
    print()
    jawab = input(warna("  Bukan yang kamu cari? Tambah buku baru? (y/n): ", C.YELLOW)).strip().lower()
    if jawab == "y":
        tambah_buku(books, judul_awal=kata)


# =====================================================================
# BAGIAN 9: LIHAT SEMUA BUKU
# =====================================================================

def lihat_semua(books):
    print()
    print(warna(f"  📖 SEMUA BUKU ({len(books)})", C.YELLOW, C.BOLD))
    if not books:
        print(warna("  (belum ada buku)", C.DIM))
        return
    tampil_hasil(books)


# =====================================================================
# BAGIAN 10: MENU UTAMA
# =====================================================================

def tampil_menu(jumlah):
    print()
    print(warna("  ┌──────────────── MENU ────────────────┐", C.MAGENTA))
    print("  " + warna("│", C.MAGENTA) + warna("  1 ", C.YELLOW, C.BOLD) + "🔎 Cari buku                      " + warna("│", C.MAGENTA))
    print("  " + warna("│", C.MAGENTA) + warna("  2 ", C.YELLOW, C.BOLD) + "➕ Tambah buku                    " + warna("│", C.MAGENTA))
    print("  " + warna("│", C.MAGENTA) + warna("  3 ", C.YELLOW, C.BOLD) + "📖 Lihat semua buku               " + warna("│", C.MAGENTA))
    print("  " + warna("│", C.MAGENTA) + warna("  0 ", C.YELLOW, C.BOLD) + "👋 Keluar                         " + warna("│", C.MAGENTA))
    print(warna("  └──────────────────────────────────────┘", C.MAGENTA))
    print(warna(f"   Koleksi saat ini: {jumlah} buku", C.DIM))


def main():
    layar_sambutan()
    books = load()
    print(warna(f"  ✓ {len(books)} buku berhasil dimuat.", C.GREEN))

    while True:
        tampil_menu(len(books))
        pilihan = input(warna("\n  Pilih menu: ", C.CYAN, C.BOLD)).strip()

        if pilihan == "1":
            menu_cari(books)
        elif pilihan == "2":
            tambah_buku(books)
        elif pilihan == "3":
            lihat_semua(books)
        elif pilihan == "0":
            print()
            ketik(warna("  Terima kasih sudah membaca! Sampai jumpa 📚", C.YELLOW, C.BOLD), 0.04)
            break
        else:
            print(warna("  ✗ Pilihan tidak dikenal, ketik 1, 2, 3, atau 0.", C.RED))


# Baris ini artinya: "jalankan main() hanya kalau file ini dijalankan langsung"
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:       # kalau user tekan Ctrl+C
        print(warna("\n\n  Program dihentikan. Sampai jumpa!", C.YELLOW))