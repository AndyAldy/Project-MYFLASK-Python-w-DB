from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_sistem_manajemen_mahasiswa'
DB_NAME = 'database.db'

def get_db_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

# --- FUNGSI UNTUK CEK ADMIN ---
def is_admin():
    """Cek apakah user adalah admin"""
    # Di sistem baru ini, hanya admin yang bisa login
    return 'user_role' in session and session['user_role'] == 'admin'

# --- ROUTE LOGIN (HALAMAN UTAMA) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin():
        # Jika sudah login, langsung ke dashboard
        return redirect(url_for('manajemen_mahasiswa')) 

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_conn()
        # Kita cek ke tabel 'users' (tabel admin)
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password) and user['role'] == 'admin':
            session['user_username'] = user['username']
            session['user_role'] = user['role'] 
            return redirect(url_for('manajemen_mahasiswa'))
        else:
            error = "Username atau Password Admin salah."
            
    return render_template('login.html', error=error)

# --- ROUTE REGISTER (DIHAPUS) ---
# Pendaftaran publik tidak diperlukan, admin dibuat via init_db.py

# --- ROUTE BERANDA (ROUTER) ---
@app.route('/')
def show_beranda():
    if not is_admin():
        return redirect(url_for('login'))
    
    # Admin langsung diarahkan ke halaman manajemen
    return redirect(url_for('manajemen_mahasiswa'))

# --- ROUTE UTAMA MANAJEMEN MAHASISWA (CRUD) ---
@app.route('/dashboard')
def manajemen_mahasiswa():
    if not is_admin():
        return redirect(url_for('login')) # Hanya admin
        
    conn = get_db_conn()
    # Ambil data dari tabel 'mahasiswa'
    list_mahasiswa = conn.execute("SELECT id, nama_lengkap, nim, jurusan, email FROM mahasiswa").fetchall()
    conn.close()
    
    # Menampilkan halaman dashboard
    return render_template('dashboard.html', mahasiswa=list_mahasiswa, logged_in_user=session['user_username'])

# --- ROUTE CRUD (Admin Only) ---

@app.route('/add', methods=['POST'])
def add_mahasiswa():
    if not is_admin():
        return redirect(url_for('login'))
        
    # Ambil data dari form
    nama_lengkap = request.form['nama_lengkap']
    nim = request.form['nim']
    jurusan = request.form['jurusan']
    email = request.form['email']
    
    try:
        conn = get_db_conn()
        conn.execute("""
            INSERT INTO mahasiswa (nama_lengkap, nim, jurusan, email)
            VALUES (?, ?, ?, ?)
        """, (nama_lengkap, nim, jurusan, email))
        conn.commit()
        conn.close()
        flash("Data mahasiswa baru berhasil ditambahkan!", "success")
    except sqlite3.IntegrityError:
        flash(f"NIM '{nim}' sudah ada di database. Gunakan NIM lain.", "error")
        
    return redirect(url_for('manajemen_mahasiswa'))

@app.route('/edit/<int:mahasiswa_id>', methods=['GET', 'POST'])
def edit_mahasiswa(mahasiswa_id):
    if not is_admin():
        return redirect(url_for('login')) 
    
    conn = get_db_conn()
    
    if request.method == 'POST':
        # Logika update data
        nama_lengkap = request.form['nama_lengkap']
        nim = request.form['nim']
        jurusan = request.form['jurusan']
        email = request.form['email']
        
        try:
            conn.execute("""
                UPDATE mahasiswa SET nama_lengkap = ?, nim = ?, jurusan = ?, email = ?
                WHERE id = ?
            """, (nama_lengkap, nim, jurusan, email, mahasiswa_id))
            conn.commit()
            flash("Data mahasiswa berhasil diupdate.", "success")
        except sqlite3.IntegrityError:
            flash(f"NIM '{nim}' sudah digunakan oleh mahasiswa lain.", "error")
        finally:
            conn.close()
            
        return redirect(url_for('manajemen_mahasiswa'))
    
    # Logika GET (menampilkan form edit)
    mhs_data = conn.execute("SELECT * FROM mahasiswa WHERE id = ?", (mahasiswa_id,)).fetchone()
    conn.close()
    
    if not mhs_data:
        flash("Data mahasiswa tidak ditemukan.", "error")
        return redirect(url_for('manajemen_mahasiswa'))
        
    return render_template('edit_mahasiswa.html', mhs=mhs_data)

@app.route('/delete/<int:mahasiswa_id>', methods=['POST'])
def delete_mahasiswa(mahasiswa_id):
    if not is_admin():
        return redirect(url_for('login')) 
    
    # Hapus data dari tabel 'mahasiswa'
    conn = get_db_conn()
    conn.execute("DELETE FROM mahasiswa WHERE id = ?", (mahasiswa_id,))
    conn.commit()
    conn.close()
    
    flash("Data mahasiswa berhasil dihapus.", "success")
    return redirect(url_for('manajemen_mahasiswa'))

# --- Route Lama (Dihapus) ---
# /profile, /profile/<username> tidak diperlukan lagi

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('user_username', None)
    session.pop('user_role', None) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)