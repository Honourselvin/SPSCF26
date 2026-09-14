import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB = 'pharmacy.db'


def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = db()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        batch TEXT NOT NULL,
        expiry TEXT NOT NULL,
        mrp REAL NOT NULL DEFAULT 0,
        purchase_price REAL NOT NULL DEFAULT 0,
        gst REAL NOT NULL DEFAULT 0,
        stock INTEGER NOT NULL DEFAULT 0,
        reorder_level INTEGER NOT NULL DEFAULT 10
    );
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        customer TEXT,
        phone TEXT,
        payment TEXT NOT NULL,
        total REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        medicine_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        rate REAL NOT NULL,
        gst REAL NOT NULL,
        amount REAL NOT NULL
    );
    ''')
    c.commit(); c.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('SP Pharmacy Billing')
        self.geometry('1100x700')
        self.minsize(900, 600)
        self.cart = []
        self.build()
        self.refresh_medicines()
        self.refresh_cart()

    def build(self):
        top = ttk.Frame(self, padding=12); top.pack(fill='x')
        ttk.Label(top, text='SP PHARMACY BILLING', font=('Segoe UI', 20, 'bold')).pack(side='left')
        ttk.Button(top, text='Medicine Master', command=self.medicine_window).pack(side='right', padx=4)
        ttk.Button(top, text='New Bill', command=self.new_bill).pack(side='right', padx=4)

        customer = ttk.LabelFrame(self, text='Customer', padding=8); customer.pack(fill='x', padx=12)
        ttk.Label(customer, text='Name').grid(row=0,column=0,padx=5)
        self.customer = ttk.Entry(customer, width=28); self.customer.grid(row=0,column=1)
        ttk.Label(customer, text='Phone').grid(row=0,column=2,padx=5)
        self.phone = ttk.Entry(customer, width=18); self.phone.grid(row=0,column=3)
        ttk.Label(customer, text='Payment').grid(row=0,column=4,padx=5)
        self.payment = ttk.Combobox(customer, values=['Cash','UPI','Card','Credit'], state='readonly', width=12)
        self.payment.set('Cash'); self.payment.grid(row=0,column=5)

        add = ttk.LabelFrame(self, text='Add Medicine', padding=8); add.pack(fill='x', padx=12, pady=8)
        ttk.Label(add, text='Medicine').grid(row=0,column=0)
        self.med = ttk.Combobox(add, width=55); self.med.grid(row=0,column=1,padx=5)
        self.qty = ttk.Spinbox(add, from_=1, to=999, width=8); self.qty.set(1); self.qty.grid(row=0,column=2,padx=5)
        ttk.Button(add, text='Add (Enter)', command=self.add_item).grid(row=0,column=3,padx=5)
        self.med.bind('<Return>', lambda e: self.add_item())
        self.qty.bind('<Return>', lambda e: self.add_item())
        self.med.focus()

        body = ttk.Frame(self, padding=12); body.pack(fill='both', expand=True)
        cols=('name','batch','expiry','qty','rate','gst','amount')
        self.tree=ttk.Treeview(body, columns=cols, show='headings')
        heads={'name':'Medicine','batch':'Batch','expiry':'Expiry','qty':'Qty','rate':'Rate','gst':'GST%','amount':'Amount'}
        for c in cols:
            self.tree.heading(c,text=heads[c]); self.tree.column(c,width=120, anchor='center')
        self.tree.column('name',width=300,anchor='w'); self.tree.pack(fill='both',expand=True)

        bottom=ttk.Frame(self,padding=12); bottom.pack(fill='x')
        self.total_var=tk.StringVar(value='TOTAL: ₹0.00')
        ttk.Label(bottom,textvariable=self.total_var,font=('Segoe UI',18,'bold')).pack(side='right',padx=10)
        ttk.Button(bottom,text='Remove Selected',command=self.remove_item).pack(side='left')
        ttk.Button(bottom,text='SAVE & PRINT BILL',command=self.save_bill).pack(side='right')

    def refresh_medicines(self):
        c=db(); rows=c.execute('SELECT * FROM medicines ORDER BY name,batch').fetchall(); c.close()
        self.med_rows=rows
        self.med['values']=[f"{r['name']} | {r['batch']} | {r['expiry']} | Stock:{r['stock']} | ₹{r['mrp']:.2f}" for r in rows]

    def add_item(self):
        i=self.med.current()
        if i<0: return messagebox.showwarning('Medicine','Select a medicine')
        r=self.med_rows[i]; q=int(self.qty.get())
        already=sum(x['qty'] for x in self.cart if x['id']==r['id'])
        if q+already>r['stock']: return messagebox.showerror('Stock','Insufficient stock')
        item={'id':r['id'],'name':r['name'],'batch':r['batch'],'expiry':r['expiry'],'qty':q,'rate':r['mrp'],'gst':r['gst']}
        self.cart.append(item); self.refresh_cart(); self.qty.set(1); self.med.focus()

    def refresh_cart(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        total=0
        for x in self.cart:
            amount=x['qty']*x['rate']; total+=amount
            self.tree.insert('', 'end', values=(x['name'],x['batch'],x['expiry'],x['qty'],f"₹{x['rate']:.2f}",f"{x['gst']:.2f}",f"₹{amount:.2f}"))
        self.total=total; self.total_var.set(f'TOTAL: ₹{total:.2f}')

    def remove_item(self):
        s=self.tree.selection()
        if not s:return
        idx=self.tree.index(s[0]); self.cart.pop(idx); self.refresh_cart()

    def new_bill(self):
        self.cart=[]; self.customer.delete(0,'end'); self.phone.delete(0,'end'); self.payment.set('Cash'); self.refresh_cart(); self.med.focus()

    def save_bill(self):
        if not self.cart:return messagebox.showwarning('Bill','Add at least one medicine')
        c=db(); now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); no='INV-'+datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]
        cur=c.execute('INSERT INTO invoices(invoice_no,created_at,customer,phone,payment,total) VALUES(?,?,?,?,?,?)',(no,now,self.customer.get(),self.phone.get(),self.payment.get(),self.total))
        inv=cur.lastrowid
        for x in self.cart:
            c.execute('INSERT INTO invoice_items(invoice_id,medicine_id,name,qty,rate,gst,amount) VALUES(?,?,?,?,?,?,?)',(inv,x['id'],x['name'],x['qty'],x['rate'],x['gst'],x['qty']*x['rate']))
            c.execute('UPDATE medicines SET stock=stock-? WHERE id=?',(x['qty'],x['id']))
        c.commit(); c.close()
        self.write_invoice(no,now); messagebox.showinfo('Saved',f'Bill {no} saved.\nInvoice text file created.')
        self.new_bill(); self.refresh_medicines()

    def write_invoice(self,no,now):
        lines=['SP PHARMACY','='*42,f'Invoice: {no}',f'Date: {now}',f'Customer: {self.customer.get()}',f'Phone: {self.phone.get()}', '-'*42]
        for x in self.cart: lines.append(f"{x['name']} x{x['qty']}  ₹{x['qty']*x['rate']:.2f}")
        lines += ['-'*42,f'TOTAL: ₹{self.total:.2f}',f'Payment: {self.payment.get()}']
        with open(f'{no}.txt','w',encoding='utf-8') as f:f.write('\n'.join(lines))

    def medicine_window(self):
        w=tk.Toplevel(self); w.title('Medicine Master'); w.geometry('850x500')
        f=ttk.Frame(w,padding=10); f.pack(fill='x')
        labels=['Name','Batch','Expiry (YYYY-MM-DD)','MRP','Purchase','GST %','Stock','Reorder']
        es=[]
        for i,l in enumerate(labels):
            ttk.Label(f,text=l).grid(row=0,column=i,padx=2)
            e=ttk.Entry(f,width=12); e.grid(row=1,column=i,padx=2); es.append(e)
        def add():
            try: vals=[es[0].get(),es[1].get(),es[2].get(),float(es[3].get()),float(es[4].get()),float(es[5].get()),int(es[6].get()),int(es[7].get())]
            except ValueError:return messagebox.showerror('Input','Check numeric fields')
            if not vals[0] or not vals[1] or not vals[2]:return messagebox.showerror('Input','Name, batch and expiry are required')
            c=db(); c.execute('INSERT INTO medicines(name,batch,expiry,mrp,purchase_price,gst,stock,reorder_level) VALUES(?,?,?,?,?,?,?,?)',vals); c.commit(); c.close(); self.refresh_medicines(); w.destroy()
        ttk.Button(f,text='Add Medicine',command=add).grid(row=2,column=0,columnspan=2,pady=8)
        tv=ttk.Treeview(w,columns=('name','batch','expiry','mrp','stock','gst'),show='headings')
        for x in tv['columns']:tv.heading(x,text=x.upper())
        tv.pack(fill='both',expand=True,padx=10,pady=10)
        for r in self.med_rows:tv.insert('', 'end',values=(r['name'],r['batch'],r['expiry'],r['mrp'],r['stock'],r['gst']))


if __name__=='__main__':
    init_db(); App().mainloop()
