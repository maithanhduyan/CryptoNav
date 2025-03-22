import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  readUserPortfoliosPortfoliosMyPortfoliosGet,
  createPortfolioPortfoliosPost,
  updatePortfolioPortfoliosPortfolioIdPut,
  deletePortfolioPortfoliosPortfolioIdDelete,
} from "../../client/sdk.gen";

interface Portfolio {
  id: number;
  name: string;
  description?: string | null;
  user_id: number;
  created_at: string;
}

const Portfolio: React.FC = () => {
  const { token, user } = useAuth();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newPortfolio, setNewPortfolio] = useState({ name: "", description: "" });
  const [editingPortfolio, setEditingPortfolio] = useState<Portfolio | null>(null);

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    try {
      const response = await readUserPortfoliosPortfoliosMyPortfoliosGet({
        headers: { Authorization: `Bearer ${token}` },
      });
      setPortfolios(response.data as Portfolio[]);
    } catch (err) {
      setError("Không thể tải danh sách portfolios");
    } finally {
      setLoading(false);
    }
  };

  const handleAddPortfolio = async () => {
    if (!user) return;
    try {
      await createPortfolioPortfoliosPost({
        body: { ...newPortfolio, user_id: user.id }, // Giả định user có id
        headers: { Authorization: `Bearer ${token}` },
      });
      setNewPortfolio({ name: "", description: "" });
      fetchPortfolios();
    } catch (err) {
      setError("Không thể thêm portfolio");
    }
  };

  const handleUpdatePortfolio = async () => {
    if (!editingPortfolio) return;
    try {
      await updatePortfolioPortfoliosPortfolioIdPut({
        path: { portfolio_id: editingPortfolio.id },
        query: { name: editingPortfolio.name, description: editingPortfolio.description || "" },
        headers: { Authorization: `Bearer ${token}` },
      });
      setEditingPortfolio(null);
      fetchPortfolios();
    } catch (err) {
      setError("Không thể cập nhật portfolio");
    }
  };

  const handleDeletePortfolio = async (id: number) => {
    try {
      await deletePortfolioPortfoliosPortfolioIdDelete({
        path: { portfolio_id: id },
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchPortfolios();
    } catch (err) {
      setError("Không thể xóa portfolio");
    }
  };

  if (loading) return <div className="p-6">Đang tải...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Quản lý Portfolios</h2>

      {/* Form thêm portfolio */}
      <div className="mb-6 flex space-x-2">
        <input
          type="text"
          placeholder="Name"
          value={newPortfolio.name}
          onChange={(e) => setNewPortfolio({ ...newPortfolio, name: e.target.value })}
          className="border p-2 rounded-md"
        />
        <input
          type="text"
          placeholder="Description"
          value={newPortfolio.description}
          onChange={(e) => setNewPortfolio({ ...newPortfolio, description: e.target.value })}
          className="border p-2 rounded-md"
        />
        <button
          onClick={handleAddPortfolio}
          className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600"
        >
          Thêm Portfolio
        </button>
      </div>

      {/* Danh sách portfolios */}
      <ul className="space-y-2">
        {portfolios.map((portfolio) => (
          <li key={portfolio.id} className="flex items-center space-x-4">
            {editingPortfolio?.id === portfolio.id ? (
              <>
                <input
                  type="text"
                  value={editingPortfolio.name}
                  onChange={(e) =>
                    setEditingPortfolio({ ...editingPortfolio, name: e.target.value })
                  }
                  className="border p-1 rounded-md"
                />
                <input
                  type="text"
                  value={editingPortfolio.description || ""}
                  onChange={(e) =>
                    setEditingPortfolio({ ...editingPortfolio, description: e.target.value })
                  }
                  className="border p-1 rounded-md"
                />
                <button
                  onClick={handleUpdatePortfolio}
                  className="bg-green-500 text-white p-1 rounded-md hover:bg-green-600"
                >
                  Lưu
                </button>
                <button
                  onClick={() => setEditingPortfolio(null)}
                  className="bg-gray-500 text-white p-1 rounded-md hover:bg-gray-600"
                >
                  Hủy
                </button>
              </>
            ) : (
              <>
                <span>
                  {portfolio.name} {portfolio.description && `(${portfolio.description})`}
                </span>
                <button
                  onClick={() => setEditingPortfolio(portfolio)}
                  className="bg-yellow-500 text-white p-1 rounded-md hover:bg-yellow-600"
                >
                  Sửa
                </button>
                <button
                  onClick={() => handleDeletePortfolio(portfolio.id)}
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

export default Portfolio;