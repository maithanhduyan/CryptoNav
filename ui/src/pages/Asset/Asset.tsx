import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  readAssetsAssetsGet,
  createAssetAssetsPost,
  updateAssetAssetsAssetIdPut,
  deleteAssetAssetsAssetIdDelete,
} from "../../client/sdk.gen";

interface Asset {
  id: number;
  symbol: string;
  name: string;
  description?: string | null;
}

const Asset: React.FC = () => {
  const { token } = useAuth(); // Lấy token từ AuthContext để xác thực API
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newAsset, setNewAsset] = useState({ symbol: "", name: "", description: "" });
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);

  // Lấy danh sách assets khi component mount
  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await readAssetsAssetsGet({
        headers: { Authorization: `Bearer ${token}` },
      });
      setAssets(response.data as Asset[]);
    } catch (err) {
      setError("Không thể tải danh sách assets");
    } finally {
      setLoading(false);
    }
  };

  const handleAddAsset = async () => {
    try {
      await createAssetAssetsPost({
        body: newAsset,
        headers: { Authorization: `Bearer ${token}` },
      });
      setNewAsset({ symbol: "", name: "", description: "" }); // Reset form
      fetchAssets(); // Cập nhật danh sách
    } catch (err) {
      setError("Không thể thêm asset");
    }
  };

  const handleUpdateAsset = async () => {
    if (!editingAsset) return;
    try {
      await updateAssetAssetsAssetIdPut({
        path: { asset_id: editingAsset.id },
        body: editingAsset,
        headers: { Authorization: `Bearer ${token}` },
      });
      setEditingAsset(null); // Thoát chế độ chỉnh sửa
      fetchAssets(); // Cập nhật danh sách
    } catch (err) {
      setError("Không thể cập nhật asset");
    }
  };

  const handleDeleteAsset = async (id: number) => {
    try {
      await deleteAssetAssetsAssetIdDelete({
        path: { asset_id: id },
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchAssets(); // Cập nhật danh sách
    } catch (err) {
      setError("Không thể xóa asset");
    }
  };

  if (loading) return <div className="p-6">Đang tải...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Quản lý Assets</h2>

      {/* Form thêm asset */}
      <div className="mb-6 flex space-x-2">
        <input
          type="text"
          placeholder="Symbol"
          value={newAsset.symbol}
          onChange={(e) => setNewAsset({ ...newAsset, symbol: e.target.value })}
          className="border p-2 rounded-md"
        />
        <input
          type="text"
          placeholder="Name"
          value={newAsset.name}
          onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
          className="border p-2 rounded-md"
        />
        <input
          type="text"
          placeholder="Description"
          value={newAsset.description}
          onChange={(e) => setNewAsset({ ...newAsset, description: e.target.value })}
          className="border p-2 rounded-md"
        />
        <button
          onClick={handleAddAsset}
          className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600"
        >
          Thêm Asset
        </button>
      </div>

      {/* Danh sách assets */}
      <ul className="space-y-2">
        {assets.map((asset) => (
          <li key={asset.id} className="flex items-center space-x-4">
            {editingAsset?.id === asset.id ? (
              <>
                <input
                  type="text"
                  value={editingAsset.symbol}
                  onChange={(e) =>
                    setEditingAsset({ ...editingAsset, symbol: e.target.value })
                  }
                  className="border p-1 rounded-md"
                />
                <input
                  type="text"
                  value={editingAsset.name}
                  onChange={(e) =>
                    setEditingAsset({ ...editingAsset, name: e.target.value })
                  }
                  className="border p-1 rounded-md"
                />
                <input
                  type="text"
                  value={editingAsset.description || ""}
                  onChange={(e) =>
                    setEditingAsset({ ...editingAsset, description: e.target.value })
                  }
                  className="border p-1 rounded-md"
                />
                <button
                  onClick={handleUpdateAsset}
                  className="bg-green-500 text-white p-1 rounded-md hover:bg-green-600"
                >
                  Lưu
                </button>
                <button
                  onClick={() => setEditingAsset(null)}
                  className="bg-gray-500 text-white p-1 rounded-md hover:bg-gray-600"
                >
                  Hủy
                </button>
              </>
            ) : (
              <>
                <span>
                  {asset.symbol} - {asset.name}{" "}
                  {asset.description && `(${asset.description})`}
                </span>
                <button
                  onClick={() => setEditingAsset(asset)}
                  className="bg-yellow-500 text-white p-1 rounded-md hover:bg-yellow-600"
                >
                  Sửa
                </button>
                <button
                  onClick={() => handleDeleteAsset(asset.id)}
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

export default Asset;