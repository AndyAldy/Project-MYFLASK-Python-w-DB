import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = 'database.db'

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# 1. Hapus tabel lama jika ada
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS mahasiswa")


# 2. Buat tabel 'users' (Admin) - Tetap sama
print("Membuat tabel 'users' untuk admin...")
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE, 
    password TEXT NOT NULL,
    nama_lengkap TEXT NOT NULL,
    email TEXT, 
    role TEXT NOT NULL DEFAULT 'admin'
)
""")

# 3. Buat tabel 'mahasiswa' (DENGAN TAMBAHAN PASSWORD)
print("Membuat tabel 'mahasiswa'...")
cursor.execute("""
CREATE TABLE mahasiswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_lengkap TEXT NOT NULL,
    nim TEXT NOT NULL UNIQUE,
    jurusan TEXT NOT NULL,
    email TEXT,
    password TEXT NOT NULL 
)
""")

# 4. Masukkan data admin default - Tetap sama
print("Memasukkan data admin default (admin/admin123)...")
admin_pass_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
cursor.execute("""
INSERT INTO users (username, password, nama_lengkap, email, role) 
VALUES (?, ?, ?, ?, 'admin')
""", ('admin', admin_pass_hash, 'Administrator', 'admin@sistem.com'))

# 5. Masukkan data contoh mahasiswa (DENGAN TAMBAHAN PASSWORD)
print("Memasukkan data contoh mahasiswa (pass: mahasiswa123)...")
# Buat hash password default untuk mahasiswa
mhs_pass_hash = generate_password_hash('mahasiswa123', method='pbkdf2:sha256')

contoh_mahasiswa = [
    ('Andy Aldyansyah', '10123001', 'Teknik Informatika', 'andy@kampus.com', mhs_pass_hash),
    ('Angel Threesilia', '10123002', 'Farmasi', 'angel@kampus.com', mhs_pass_hash),
    ('Citra Lestari', '10223001', 'Desain Grafis', 'citra@kampus.com', mhs_pass_hash)
]
cursor.executemany("""
INSERT INTO mahasiswa (nama_lengkap, nim, jurusan, email, password) 
VALUES (?, ?, ?, ?, ?)
""", contoh_mahasiswa)


conn.commit()
conn.close()

print(f"Database '{DB_NAME}' berhasil dibuat ulang.")
print("Mahasiswa sekarang memiliki password.")
print("Silakan jalankan 'app.py'.")