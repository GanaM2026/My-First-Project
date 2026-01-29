import sqlite3

# دالة للاتصال بقاعدة البيانات
def create_connection():
    conn = sqlite3.connect("inventory.db")
    return conn

# دالة لإنشاء الجدول (المنتجات)
def setup_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("تم إنشاء ملف قاعدة البيانات والجدول بنجاح!")

if __name__ == "__main__":
    setup_database()