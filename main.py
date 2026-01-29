import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os
from fpdf import FPDF # مكتبة تصدير PDF

class AutoShopFinalERP:
    def __init__(self, root):
        self.root = root
        self.root.title("AUTOSHOP GROUP - نظام تصدير PDF v5.0")
        self.root.geometry("1350x850")
        
        self.db = "autoshop_pro.db"
        self.init_db()
        self.setup_ui()
        
    def init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, name TEXT,
                min_price REAL, normal_price REAL, wholesale_price REAL, qty REAL, branch TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT, bill_no TEXT, customer TEXT, 
                total REAL, date TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS invoice_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT, bill_no TEXT, item_name TEXT, 
                qty REAL, price REAL, total REAL)""")

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_inv = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_bill = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_arch = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_report = tk.Frame(self.notebook, bg="#f5f5f5")
        
        self.notebook.add(self.tab_inv, text=" 📦 المخزن ")
        self.notebook.add(self.tab_bill, text=" 🧾 فاتورة جديدة ")
        self.notebook.add(self.tab_arch, text=" 📜 أرشيف الفواتير ")
        self.notebook.add(self.tab_report, text=" 📊 كشف الحساب ")

        self.setup_inventory_tab()
        self.setup_billing_tab()
        self.setup_archive_tab()
        self.setup_reports_tab()

    # --- وظيفة تصدير الفاتورة PDF ---
    def export_to_pdf(self, b_no, cust, items, total):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                               initialfile=f"Invoice_{b_no}",
                                               filetypes=[("PDF files", "*.pdf")])
        if not file_path: return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            
            # رأس الفاتورة
            pdf.cell(190, 10, txt="AUTOSHOP GROUP - INVOICE", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.ln(10)
            pdf.cell(100, 10, txt=f"Customer: {cust}")
            pdf.cell(90, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
            pdf.cell(100, 10, txt=f"Bill No: {b_no}", ln=True)
            pdf.ln(5)

            # الجدول
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(80, 10, "Item Name", 1, 0, 'C', True)
            pdf.cell(30, 10, "Qty", 1, 0, 'C', True)
            pdf.cell(40, 10, "Price", 1, 0, 'C', True)
            pdf.cell(40, 10, "Total", 1, 1, 'C', True)

            for item in items:
                pdf.cell(80, 10, str(item[0]), 1)
                pdf.cell(30, 10, str(item[1]), 1, 0, 'C')
                pdf.cell(40, 10, f"{item[2]:,.2f}", 1, 0, 'C')
                pdf.cell(40, 10, f"{item[3]:,.2f}", 1, 1, 'C')

            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, txt=f"GRAND TOTAL: {total:,.2f} EGP", ln=True, align='R')
            
            pdf.output(file_path)
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")

    # --- وظيفة تصدير كشف الحساب PDF ---
    def export_report_pdf(self):
        cust = self.rep_search.get()
        if not self.rep_tree.get_children(): return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                               initialfile=f"Report_{cust}",
                                               filetypes=[("PDF files", "*.pdf")])
        if not file_path: return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt=f"Account Statement: {cust}", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, 10, "Date", 1, 0, 'C')
        pdf.cell(70, 10, "Invoice No", 1, 0, 'C')
        pdf.cell(60, 10, "Amount", 1, 1, 'C')

        for i in self.rep_tree.get_children():
            v = self.rep_tree.item(i)['values']
            pdf.cell(60, 10, str(v[0]), 1)
            pdf.cell(70, 10, str(v[1]), 1)
            pdf.cell(60, 10, str(v[2]), 1, 1)

        pdf.output(file_path)
        os.startfile(file_path)

    def setup_inventory_tab(self):
        f = tk.Frame(self.tab_inv, pady=10)
        f.pack(fill="x")
        tk.Button(f, text="📋 استيراد باللصق", bg="#2980b9", fg="white", command=self.import_from_clipboard).pack(side="left", padx=10)
        self.ent_search_inv = tk.Entry(f, width=40, font=("Arial", 12), justify="right")
        self.ent_search_inv.pack(side="right", padx=10)
        self.inv_tree = self.create_tree(self.tab_inv, ("id", "code", "name", "min", "norm", "whol", "qty", "branch"), 
                                        ["#", "الكود", "الصنف", "الأدنى", "العادي", "الجملة", "الكمية", "الفرع"])
        self.load_inventory()

    def setup_billing_tab(self):
        f_top = tk.LabelFrame(self.tab_bill, text=" إعداد الفاتورة ", font=("Arial", 12, "bold"), padx=10, pady=10)
        f_top.pack(fill="x", padx=10, pady=5)
        
        self.b_cust = tk.Entry(f_top, justify="right"); self.b_cust.grid(row=0, column=5)
        tk.Label(f_top, text="العميل:").grid(row=0, column=6)
        
        self.b_code = tk.Entry(f_top, width=15); self.b_code.grid(row=1, column=5)
        tk.Label(f_top, text="الكود:").grid(row=1, column=6)
        
        self.b_qty = tk.Entry(f_top, width=10); self.b_qty.grid(row=1, column=3)
        tk.Label(f_top, text="الكمية:").grid(row=1, column=4)

        tk.Button(f_top, text="➕ إضافة", bg="#27ae60", fg="white", command=self.add_to_bill).grid(row=1, column=0, padx=20)
        
        self.bill_tree = self.create_tree(self.tab_bill, ("n","q","p","t"), ["الصنف", "الكمية", "السعر", "الإجمالي"])
        tk.Button(self.tab_bill, text="💾 حفظ وتصدير الفاتورة PDF", bg="#c0392b", fg="white", font=("Arial", 12, "bold"), command=self.save_bill).pack(fill="x", padx=10, pady=10)

    def setup_archive_tab(self):
        f = tk.Frame(self.tab_arch, pady=10)
        f.pack(fill="x")
        tk.Button(f, text="🖨️ إعادة تصدير PDF", command=self.reprint_invoice).pack(side="left", padx=10)
        self.arch_tree = self.create_tree(self.tab_arch, ("no", "cu", "to", "da"), ["رقم الفاتورة", "العميل", "الإجمالي", "التاريخ"])
        self.load_archive()

    def setup_reports_tab(self):
        f = tk.Frame(self.tab_report, pady=10)
        f.pack(fill="x")
        self.rep_search = tk.Entry(f, width=30); self.rep_search.pack(side="right", padx=10)
        tk.Button(f, text="🔍 عرض", command=self.load_customer_report).pack(side="right")
        tk.Button(f, text="📥 تصدير كشف الحساب PDF", bg="#8e44ad", fg="white", command=self.export_report_pdf).pack(side="left", padx=10)
        self.rep_tree = self.create_tree(self.tab_report, ("da", "no", "tot"), ["التاريخ", "رقم الفاتورة", "القيمة"])
        self.lbl_total_rep = tk.Label(self.tab_report, text="0.00", font=("Arial", 14, "bold"))
        self.lbl_total_rep.pack()

    def create_tree(self, parent, cols, texts):
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c, t in zip(cols, texts):
            tree.heading(c, text=t)
            tree.column(c, anchor="center", width=100)
        tree.pack(fill="both", expand=True)
        return tree

    def save_bill(self):
        items_ids = self.bill_tree.get_children()
        cust = self.b_cust.get()
        if not items_ids or not cust: return
        
        b_no = datetime.now().strftime("%y%m%d%H%M%S")
        total_bill = 0
        items_data = []
        
        with sqlite3.connect(self.db) as conn:
            for i in items_ids:
                v = self.bill_tree.item(i)['values']
                total_bill += float(v[3])
                items_data.append(v)
                conn.execute("INSERT INTO invoice_details (bill_no, item_name, qty, price, total) VALUES (?,?,?,?,?)", (b_no, v[0], v[1], v[2], v[3]))
                conn.execute("UPDATE inventory SET qty = qty - ? WHERE name = ?", (v[1], v[0]))
            conn.execute("INSERT INTO invoices (bill_no, customer, total, date) VALUES (?,?,?,?)", (b_no, cust, total_bill, datetime.now().strftime("%Y-%m-%d")))
        
        self.export_to_pdf(b_no, cust, items_data, total_bill)
        for i in self.bill_tree.get_children(): self.bill_tree.delete(i)
        self.load_inventory(); self.load_archive()

    def reprint_invoice(self):
        sel = self.arch_tree.selection()
        if not sel: return
        v = self.arch_tree.item(sel[0])['values']
        with sqlite3.connect(self.db) as conn:
            items = conn.execute("SELECT item_name, qty, price, total FROM invoice_details WHERE bill_no=?", (str(v[0]),)).fetchall()
            self.export_to_pdf(v[0], v[1], items, v[2])

    def load_inventory(self, s=""):
        for i in self.inv_tree.get_children(): self.inv_tree.delete(i)
        with sqlite3.connect(self.db) as conn:
            q = f"SELECT * FROM inventory WHERE name LIKE '%{s}%' OR code LIKE '%{s}%'"
            for row in conn.execute(q).fetchall(): self.inv_tree.insert("", "end", values=row)

    def load_archive(self):
        for i in self.arch_tree.get_children(): self.arch_tree.delete(i)
        with sqlite3.connect(self.db) as conn:
            for r in conn.execute("SELECT bill_no, customer, total, date FROM invoices ORDER BY id DESC").fetchall():
                self.arch_tree.insert("", "end", values=r)

    def load_customer_report(self):
        cust = self.rep_search.get()
        for i in self.rep_tree.get_children(): self.rep_tree.delete(i)
        total_acc = 0
        with sqlite3.connect(self.db) as conn:
            data = conn.execute("SELECT date, bill_no, total FROM invoices WHERE customer LIKE ?", (f"%{cust}%",)).fetchall()
            for r in data:
                self.rep_tree.insert("", "end", values=r)
                total_acc += r[2]
        self.lbl_total_rep.config(text=f"Total: {total_acc:,.2f}")

    def add_to_bill(self):
        code, qty = self.b_code.get(), self.b_qty.get()
        with sqlite3.connect(self.db) as conn:
            res = conn.execute("SELECT name, wholesale_price FROM inventory WHERE code=?", (code,)).fetchone()
            if res: self.bill_tree.insert("", "end", values=(res[0], qty, res[1], float(qty)*res[1]))

    def import_from_clipboard(self):
        try:
            data = self.root.clipboard_get().strip().split('\n')
            with sqlite3.connect(self.db) as conn:
                for line in data:
                    p = line.split('\t')
                    if len(p) >= 6:
                        conn.execute("INSERT OR REPLACE INTO inventory (code,name,min_price,normal_price,wholesale_price,qty,branch) VALUES (?,?,?,?,?,?,?)", 
                                     (p[0], p[1], p[2], p[3], p[4], p[5], p[6] if len(p)>6 else "الرئيسي"))
            self.load_inventory(); messagebox.showinfo("تم", "تم الاستيراد")
        except: pass

    def select_all_rows(self, event=None):
        widget = self.root.focus_get()
        if isinstance(widget, ttk.Treeview): widget.selection_set(widget.get_children())
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoShopFinalERP(root)
    root.mainloop()