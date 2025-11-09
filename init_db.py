import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = 'database.db'

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# 1. Hapus tabel lama jika ada
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS mahasiswa")


# 2. Buat tabel 'users' (HANYA UNTUK LOGIN ADMIN)
print("Membuat tabel 'users' untuk admin...")
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE, 
    password TEXT NOT NULL,
    nama_lengkap TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin'
)
""")

# 3. Buat tabel 'mahasiswa' (UNTUK DATA CRUD)
print("Membuat tabel 'mahasiswa'...")
cursor.execute("""
CREATE TABLE mahasiswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_lengkap TEXT NOT NULL,
    nim TEXT NOT NULL UNIQUE,
    jurusan TEXT NOT NULL,
    email TEXT
)
""")

# 4. Masukkan data admin default
print("Memasukkan data admin default (admin/admin123)...")
admin_pass_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
cursor.execute("""
INSERT INTO users (username, password, nama_lengkap, role) 
VALUES (?, ?, ?, 'admin')
""", ('admin', admin_pass_hash, 'Administrator'))

# 5. Masukkan data contoh mahasiswa
print("Memasukkan data contoh mahasiswa...")
contoh_mahasiswa = [
    ('Andy Aldyansyah', '10123001', 'Teknik Informatika', 'andy@kampus.com'),
    ('Angel Threesilia', '10123002', 'Farmasi', 'angel@kampus.com'),
    ('Citra Lestari', '10223001', 'Desain Grafis', 'citra@kampus.com')
]
cursor.executemany("""
INSERT INTO mahasiswa (nama_lengkap, nim, jurusan, email) 
VALUES (?, ?, ?, ?)
""", contoh_mahasiswa)


conn.commit()
conn.close()

print(f"Database '{DB_NAME}' berhasil dibuat ulang untuk Sistem Manajemen Mahasiswa.")
print("Silakan jalankan 'app.py'.")