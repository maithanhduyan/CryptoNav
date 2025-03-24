import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { readAssetsAssetsGet, readPriceHistoryAssetsAssetIdPriceHistoryGet } from "../../client/sdk.gen";
import Asset from "../Asset/Asset";
import { PriceHistoryResponse } from "../../client";


const PriceHistory: React.FC = () => {
  const { token } = useAuth();
  const [priceHistory, setPriceHistory] = useState<PriceHistoryResponse[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const assetRes = await readAssetsAssetsGet({
          headers: { Authorization: `Bearer ${token}` },
        });
        const assetsData = assetRes.data || [];
        setAssets(assetsData as Asset[]);
        if (assetsData.length > 0) {
          setSelectedAsset(assetsData[0].id);
          fetchPriceHistory(assetsData[0].id);
        }
      } catch (err) {
        setError("Không thể tải danh sách assets");
      } finally {
        setLoading(false);
      }
    };
    fetchAssets();
  }, [token]);

  const fetchPriceHistory = async (assetId: number) => {
    try {
      const response = await readPriceHistoryAssetsAssetIdPriceHistoryGet({
        path: { asset_id: assetId },
        headers: { Authorization: `Bearer ${token}` },
      });
      setPriceHistory(response.data || []);
    } catch (err) {
      setError("Không thể tải lịch sử giá");
    }
  };

  const handleAssetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const assetId = Number(e.target.value);
    setSelectedAsset(assetId);
    if (assetId) fetchPriceHistory(assetId);
  };

  if (loading) return <div className="p-6">Đang tải...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Lịch sử giá</h2>
      <div className="mb-4">
        <select
          value={selectedAsset || ""}
          onChange={handleAssetChange}
          className="border p-2 rounded-md"
        >
          <option value="">Chọn Asset</option>
          {assets.map((a) => (
            <option key={a.id} value={a.id}>{a.symbol}</option>
          ))}
        </select>
      </div>
      <ul className="space-y-2">
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