from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'speakz11za'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bank_db'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        username = request.form['username']
        balance = float(request.form['balance'])

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # ตรวจสอบว่าหมายเลขบัญชีมีอยู่แล้วหรือไม่
        cursor.execute('SELECT * FROM accounts WHERE account_number = %s', [account_number])
        account = cursor.fetchone()

        if account:
            flash('เกิดข้อผิดพลาด: หมายเลขบัญชีนี้มีอยู่แล้ว!', 'danger')
        elif balance < 0:
            flash('เกิดข้อผิดพลาด: ยอดเงินเริ่มต้นต้องไม่ติดลบ!', 'danger')
        else:
            cursor.execute('INSERT INTO accounts (account_number, username, balance) VALUES (%s, %s, %s)', (account_number, username, balance))
            mysql.connection.commit()
            flash('สร้างเลขบัญชีสำเร็จ!', 'success')
        
        cursor.close()
        return redirect(url_for('index'))
    
    return render_template('create_account.html')


@app.route('/view_balance', methods=['GET', 'POST'])
def view_balance():
    if request.method == 'POST':
        account_number = request.form['account_number']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE account_number = %s', [account_number])
        account = cursor.fetchone()
        cursor.close()
        if account:
            return render_template('view_balance.html', account=account)
        flash('เกิดข้อผิดพลาด: ไม่พบบัญชีนี้', 'danger')
    return render_template('view_balance.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        
        if amount <= 0:
            flash('เกิดข้อผิดพลาด: จำนวนเงินต้องเป็นค่าบวก.', 'danger')
            return redirect(url_for('deposit'))

        cursor = mysql.connection.cursor()
        
        # ตรวจสอบว่าบัญชีมีอยู่หรือไม่
        cursor.execute('SELECT balance FROM accounts WHERE account_number = %s', (account_number,))
        result = cursor.fetchone()
        
        if result is None:
            flash('เกิดข้อผิดพลาด: ไม่พบบัญชีนี้.', 'danger')
            cursor.close()
            return redirect(url_for('deposit'))
        
        # ทำการฝากเงินถ้าบัญชีมีอยู่
        cursor.execute('UPDATE accounts SET balance = balance + %s WHERE account_number = %s', (amount, account_number))
        mysql.connection.commit()
        cursor.close()
        flash('ฝากเงินสำเร็จแล้ว!', 'success')
        return redirect(url_for('index'))
    
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT balance FROM accounts WHERE account_number = %s', [account_number])
        account = cursor.fetchone()

        if account:
            if amount <= 0:
                flash('เกิดข้อผิดพลาด: จำนวนเงินต้องเป็นค่าบวก', 'danger')
            elif account['balance'] < amount:
                flash('เกิดข้อผิดพลาด อิอิ', 'danger')
            else:
                cursor.execute('UPDATE accounts SET balance = balance - %s WHERE account_number = %s', (amount, account_number))
                mysql.connection.commit()
                flash('ถอนเงิน สำเร็จแล้ว อิอิ!', 'success')
        else:
            flash('เกิดข้อผิดพลาด: ไม่พบบัญชีนี้', 'danger')
        
        cursor.close()
        
    return render_template('withdraw.html')


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        
        # Additional security check, e.g., confirm account number or password
        # Check if the account exists before attempting to delete
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_number = %s', [account_number])
        account = cursor.fetchone()
        
        if account:
            cursor.execute('DELETE FROM accounts WHERE account_number = %s', [account_number])
            mysql.connection.commit()
            flash('ลบบัญชีไปแล้วครับ คุณครู.', 'success')
        else:
            flash('บัญชีที่คุณครูเขียนมันไม่มีในระบบครับ!', 'danger')
        
        cursor.close()
        
    
    return render_template('delete_account.html')


if __name__ == '__main__':
    app.run(debug=True)
