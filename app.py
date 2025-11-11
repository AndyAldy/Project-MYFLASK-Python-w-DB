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

def is_admin():
    """Cek apakah user adalah admin"""
    return 'role' in session and session['role'] == 'admin'

def is_mahasiswa():
    """Cek apakah user adalah mahasiswa"""
    return 'role' in session and session['role'] == 'mahasiswa'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin():
        return redirect(url_for('manajemen_mahasiswa'))
    if is_mahasiswa():
        return redirect(url_for('dashboard_mahasiswa'))

    error = None
    if request.method == 'POST':
        login_id = request.form['username']
        password = request.form['password']
        
        conn = get_db_conn()
        
        admin = conn.execute("SELECT * FROM users WHERE username = ?", (login_id,)).fetchone()
        
        if admin and check_password_hash(admin['password'], password):
            session['user_id'] = admin['id']
            session['role'] = 'admin'
            session['username'] = admin['nama_lengkap']
            conn.close()
            return redirect(url_for('manajemen_mahasiswa'))
        
        mahasiswa = conn.execute("SELECT * FROM mahasiswa WHERE nim = ?", (login_id,)).fetchone()
        
        if mahasiswa and check_password_hash(mahasiswa['password'], password):
            session['user_id'] = mahasiswa['id']
            session['role'] = 'mahasiswa'
            session['username'] = mahasiswa['nama_lengkap']
            conn.close()
            return redirect(url_for('dashboard_mahasiswa'))

        conn.close()
        error = "NIM/Username atau Password salah."
            
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama_lengkap = request.form['nama_lengkap']
        nim = request.form['nim']
        jurusan = request.form['jurusan']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        try:
            conn = get_db_conn()
            conn.execute("""
                INSERT INTO mahasiswa (nama_lengkap, nim, jurusan, email, password)
                VALUES (?, ?, ?, ?, ?)
            """, (nama_lengkap, nim, jurusan, email, hashed_password))
            conn.commit()
            conn.close()
            flash("Akun berhasil dibuat! Silakan login menggunakan NIM dan password Anda.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash(f"NIM '{nim}' sudah terdaftar. Gunakan NIM lain.", "error")
            return render_template('register.html')

    return render_template('register.html')

@app.route('/')
def show_beranda():
    if not 'role' in session:
        return redirect(url_for('login'))
    
    if is_admin():
        return redirect(url_for('manajemen_mahasiswa'))
    
    if is_mahasiswa():
        return redirect(url_for('dashboard_mahasiswa'))
        
    return redirect(url_for('login'))

@app.route('/beranda')
def dashboard_mahasiswa():
    if not is_mahasiswa():
        flash("Anda harus login sebagai mahasiswa untuk mengakses halaman ini.", "error")
        return redirect(url_for('login'))
        
    conn = get_db_conn()
    mhs_data = conn.execute("SELECT * FROM mahasiswa WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    
    if not mhs_data:
        flash("Data Anda tidak ditemukan.", "error")
        return redirect(url_for('logout'))
    return render_template('dashboard_mahasiswa.html', mhs=mhs_data, logged_in_user=session['username'])

@app.route('/dashboard')
def manajemen_mahasiswa():
    if not is_admin():
        flash("Anda harus login sebagai admin untuk mengakses halaman ini.", "error")
        return redirect(url_for('login')) 
        
    conn = get_db_conn()
    admin_data = conn.execute("SELECT nama_lengkap, username, email FROM users WHERE id = ?", 
                              (session['user_id'],)).fetchone()
    list_mahasiswa = conn.execute("SELECT id, nama_lengkap, nim, jurusan, email FROM mahasiswa").fetchall()
    conn.close()
    
    return render_template('dashboard.html', mahasiswa=list_mahasiswa, admin=admin_data)

@app.route('/add', methods=['POST'])
def add_mahasiswa():
    if not is_admin():
        return redirect(url_for('login'))
    
    nama_lengkap = request.form['nama_lengkap']
    nim = request.form['nim']
    jurusan = request.form['jurusan']
    email = request.form['email']
    
    try:
        conn = get_db_conn()

        hashed_password = "TIDAK_AKTIF"
        
        conn.execute("""
            INSERT INTO mahasiswa (nama_lengkap, nim, jurusan, email, password)
            VALUES (?, ?, ?, ?, ?)
        """, (nama_lengkap, nim, jurusan, email, hashed_password))
        conn.commit()
        conn.close()
        flash("Data mahasiswa baru berhasil ditambahkan! (Akun non-aktif)", "success")
    except sqlite3.IntegrityError:
        flash(f"NIM '{nim}' sudah ada di database. Gunakan NIM lain.", "error")
        
    return redirect(url_for('manajemen_mahasiswa'))

@app.route('/edit/<int:mahasiswa_id>', methods=['GET', 'POST'])
def edit_mahasiswa(mahasiswa_id):
    if not is_admin():
        return redirect(url_for('login')) 
    
    conn = get_db_conn()
    
    if request.method == 'POST':
        nama_lengkap = request.form['nama_lengkap']
        nim = request.form['nim']
        jurusan = request.form['jurusan']
        email = request.form['email']
        
        password_baru = request.form['password_baru']
        
        try:
            if password_baru:
                hashed_password = generate_password_hash(password_baru, method='pbkdf2:sha256')
                conn.execute("""
                    UPDATE mahasiswa SET nama_lengkap = ?, nim = ?, jurusan = ?, email = ?, password = ?
                    WHERE id = ?
                """, (nama_lengkap, nim, jurusan, email, hashed_password, mahasiswa_id))
                flash("Data mahasiswa dan password berhasil diupdate.", "success")
            else:
                conn.execute("""
                    UPDATE mahasiswa SET nama_lengkap = ?, nim = ?, jurusan = ?, email = ?
                    WHERE id = ?
                """, (nama_lengkap, nim, jurusan, email, mahasiswa_id))
                flash("Data mahasiswa berhasil diupdate (password tidak berubah).", "success")

            conn.commit()
        except sqlite3.IntegrityError:
            flash(f"NIM '{nim}' sudah digunakan oleh mahasiswa lain.", "error")
        finally:
            conn.close()
            
        return redirect(url_for('manajemen_mahasiswa'))
    
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
    
    conn = get_db_conn()
    conn.execute("DELETE FROM mahasiswa WHERE id = ?", (mahasiswa_id,))
    conn.commit()
    conn.close()
    
    flash("Data mahasiswa berhasil dihapus.", "success")
    return redirect(url_for('manajemen_mahasiswa'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None) 
    session.pop('username', None)
    flash("Anda telah berhasil logout.", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)