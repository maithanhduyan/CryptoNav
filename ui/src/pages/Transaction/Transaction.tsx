import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  readUserPortfoliosPortfoliosMyPortfoliosGet,
  readAssetsAssetsGet,
  createTransactionTransactionsPost,
  updateTransactionTransactionsTransactionIdPut,
  deleteTransactionTransactionsTransactionIdDelete,
  transactionsByPortfolioTransactionsPortfolioPortfolioIdGet,
} from "../../client/sdk.gen";

interface Transaction {
  id: number;
  portfolio_id: number;
  asset_id: number;
  quantity: number;
  price: number;
  transaction_type: string;
  transaction_date?: string | null;
}

interface Portfolio {
  id: number;
  name: string;
}

interface Asset {
  id: number;
  symbol: string;
}

const Transaction: React.FC = () => {
  const { token } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newTransaction, setNewTransaction] = useState({
    portfolio_id: 0,
    asset_id: 0,
    quantity: 0,
    price: 0,
    transaction_type: "BUY",
  });
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchTransactions = async (portfolioId: number) => {
    try {
      const transRes = await transactionsByPortfolioTransactionsPortfolioPortfolioIdGet({
        path: { portfolio_id: portfolioId },
        headers: { Authorization: `Bearer ${token}` },
      });
      setTransactions(transRes.data as Transaction[]);
      setError(null);
    } catch (err) {
      setError("Không thể tải transactions");
    }
  };


  // Sửa fetchData để không gọi transactions ngay lập tức
  const fetchData = async () => {
    try {
      const [portfolioRes, assetRes] = await Promise.all([
        readUserPortfoliosPortfoliosMyPortfoliosGet({ headers: { Authorization: `Bearer ${token}` } }),
        readAssetsAssetsGet({ headers: { Authorization: `Bearer ${token}` } }),
      ]);
      setPortfolios(portfolioRes.data as Portfolio[]);
      setAssets(assetRes.data as Asset[]);
      if (portfolioRes.data && portfolioRes.data.length > 0) {
        setNewTransaction(prev => ({ ...prev, portfolio_id: portfolioRes.data[0].id }));
        fetchTransactions(portfolioRes.data[0].id);
      }
    } catch (err) {
      setError("Không thể tải dữ liệu");
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransaction = async () => {
    try {
      await createTransactionTransactionsPost({
        body: newTransaction,
        headers: { Authorization: `Bearer ${token}` },
      });
      setNewTransaction({ portfolio_id: 0, asset_id: 0, quantity: 0, price: 0, transaction_type: "BUY" });
      fetchData();
    } catch (err) {
      setError("Không thể thêm transaction");
    }
  };

  const handleUpdateTransaction = async () => {
    if (!editingTransaction) return;
    try {
      await updateTransactionTransactionsTransactionIdPut({
        path: { transaction_id: editingTransaction.id },
        body: editingTransaction,
        headers: { Authorization: `Bearer ${token}` },
      });
      setEditingTransaction(null);
      fetchData();
    } catch (err) {
      setError("Không thể cập nhật transaction");
    }
  };

  const handleDeleteTransaction = async (id: number) => {
    try {
      await deleteTransactionTransactionsTransactionIdDelete({
        path: { transaction_id: id },
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchData();
    } catch (err) {
      setError("Không thể xóa transaction");
    }
  };

  if (loading) return <div className="p-6">Đang tải...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Quản lý Transactions</h2>

      {/* Form thêm transaction */}
      <div className="mb-6 flex space-x-2">
        <select
          value={newTransaction.portfolio_id}
          onChange={(e) => setNewTransaction({ ...newTransaction, portfolio_id: Number(e.target.value) })}
          className="border p-2 rounded-md"
        >
          <option value={0}>Chọn Portfolio</option>
          {portfolios.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <select
          value={newTransaction.asset_id}
          onChange={(e) => setNewTransaction({ ...newTransaction, asset_id: Number(e.target.value) })}
          className="border p-2 rounded-md"
        >
          <option value={0}>Chọn Asset</option>
          {assets.map((a) => (
            <option key={a.id} value={a.id}>{a.symbol}</option>
          ))}
        </select>
        <input
          type="number"
          placeholder="Quantity"
          value={newTransaction.quantity}
          onChange={(e) => setNewTransaction({ ...newTransaction, quantity: Number(e.target.value) })}
          className="border p-2 rounded-md"
        />
        <input
          type="number"
          placeholder="Price"
          value={newTransaction.price}
          onChange={(e) => setNewTransaction({ ...newTransaction, price: Number(e.target.value) })}
          className="border p-2 rounded-md"
        />
        <select
          value={newTransaction.transaction_type}
          onChange={(e) => setNewTransaction({ ...newTransaction, transaction_type: e.target.value })}
          className="border p-2 rounded-md"
        >
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <button
          onClick={handleAddTransaction}
          className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600"
        >
          Thêm Transaction
        </button>
      </div>

      {/* Danh sách transactions */}
      <ul className="space-y-2">
        {transactions.map((transaction) => (
          <li key={transaction.id} className="flex items-center space-x-4">
            {editingTransaction?.id === transaction.id ? (
              <>
                <select
                  value={editingTransaction.portfolio_id}
                  onChange={(e) =>
                    setEditingTransaction({ ...editingTransaction, portfolio_id: Number(e.target.value) })
                  }
                  className="border p-1 rounded-md"
                >
                  {portfolios.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                <select
                  value={editingTransaction.asset_id}
                  onChange={(e) =>
                    setEditingTransaction({ ...editingTransaction, asset_id: Number(e.target.value) })
                  }
                  className="border p-1 rounded-md"
                >
                  {assets.map((a) => (
                    <option key={a.id} value={a.id}>{a.symbol}</option>
                  ))}
                </select>
                <input
                  type="number"
                  value={editingTransaction.quantity}
                  onChange={(e) =>
                    setEditingTransaction({ ...editingTransaction, quantity: Number(e.target.value) })
                  }
                  className="border p-1 rounded-md"
                />
                <input
                  type="number"
                  value={editingTransaction.price}
                  onChange={(e) =>
                    setEditingTransaction({ ...editingTransaction, price: Number(e.target.value) })
                  }
                  className="border p-1 rounded-md"
                />
                <select
                  value={editingTransaction.transaction_type}
                  onChange={(e) =>
                    setEditingTransaction({ ...editingTransaction, transaction_type: e.target.value })
                  }
                  className="border p-1 rounded-md"
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
                <button
                  onClick={handleUpdateTransaction}
                  className="bg-green-500 text-white p-1 rounded-md hover:bg-green-600"
                >
                  Lưu
                </button>
                <button
                  onClick={() => setEditingTransaction(null)}
                  className="bg-gray-500 text-white p-1 rounded-md hover:bg-gray-600"
                >
                  Hủy
                </button>
              </>
            ) : (
              <>
                <span>
                  {portfolios.find((p) => p.id === transaction.portfolio_id)?.name} -
                  {assets.find((a) => a.id === transaction.asset_id)?.symbol} -
                  {transaction.quantity} @ {transaction.price} ({transaction.transaction_type})
                </span>
                <button
                  onClick={() => setEditingTransaction(transaction)}
                  className="bg-yellow-500 text-white p-1 rounded-md hover:bg-yellow-600"
                >
                  Sửa
                </button>
                <button
                  onClick={() => handleDeleteTransaction(transaction.id)}
                  className="bg-red-500 text-white p-1 rounded-md hover:bg-red-600"
                >
                  Xóa
                </button>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Transaction;

