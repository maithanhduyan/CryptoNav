import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { readPriceHistoryAssetsAssetIdPriceHistoryGet } from "../../client/sdk.gen";

const PriceHistory: React.FC = () => {
  const { token } = useAuth();
  const [priceHistory, setPriceHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPriceHistory = async () => {
      try {
        const response = await readPriceHistoryAssetsAssetIdPriceHistoryGet({
          path: { asset_id: 1 }, // Ví dụ: asset_id cố định, có thể thay bằng dropdown
          headers: { Authorization: `Bearer ${token}` },
        });
        setPriceHistory(response.data);
      } catch (err) {
        setError("Không thể tải lịch sử giá");
      } finally {
        setLoading(false);
      }
    };
    fetchPriceHistory();
  }, [token]);

  if (loading) return <div className="p-6">Đang tải...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Lịch sử giá</h2>
      <ul>
        {priceHistory.map((entry) => (
          <li key={entry.id}>
            {entry.date}: Open: {entry.open_price}, Close: {entry.close_price}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PriceHistory;