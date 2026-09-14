import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

function App() {
  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="brand">SELVIN MEDICALS</div>
          <div className="sub">Pharmacy Billing & Inventory</div>
        </div>
        <div className="fy">Financial Year: 2026–27</div>
      </header>

      <main className="workspace">
        <section className="hero">
          <h1>Sales Billing</h1>
          <p>Fast, keyboard-first billing. This is the first working application screen.</p>
        </section>

        <section className="shortcuts">
          <button>F2&nbsp; Save Bill</button>
          <button>F7&nbsp; Clear Bill</button>
          <button>F11&nbsp; Previous Bill</button>
          <button>Ctrl+F&nbsp; Search Transaction</button>
        </section>

        <section className="bill-card">
          <div className="bill-header">
            <div><span>Bill No</span><strong>INV-001</strong></div>
            <div><span>Date</span><strong>14-09-2026</strong></div>
            <div><span>Customer</span><strong>Walk-in Customer</strong></div>
            <div><span>Payment</span><strong>Cash</strong></div>
          </div>

          <div className="search-row">
            <label>Medicine / Barcode</label>
            <input autoFocus placeholder="Scan barcode or type medicine name..." />
            <label>Qty</label>
            <input className="qty" defaultValue="1" />
            <button className="add">Add Item</button>
          </div>

          <div className="empty">No items added yet</div>

          <div className="totals">
            <div><span>Items</span><strong>0</strong></div>
            <div><span>Gross</span><strong>₹0.00</strong></div>
            <div><span>GST</span><strong>₹0.00</strong></div>
            <div><span>Round Off</span><strong>₹0.00</strong></div>
            <div className="net"><span>NET AMOUNT</span><strong>₹0.00</strong></div>
          </div>
        </section>

        <div className="status">Offline mode • Local database will be connected in the next step</div>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
