import React from "react";

export const AppSideBar: React.FC = () => {
  return (
    <aside className="w-64 h-full bg-white border-r border-gray-200 p-4">
      {/* Logo / Tiêu đề */}
      <div className="text-xl font-bold mb-6">
        <a href="/">Cryptonav</a>
      </div>

      {/* Menu */}
      <nav>
        <ul className="space-y-2">
          <li>
            <a href="/" className="block py-2 text-gray-700 hover:text-blue-600">
              Dashboard
            </a>
          </li>
          <li>
            <a href="/portfolio" className="block py-2 text-gray-700 hover:text-blue-600">
              Porfolio
            </a>
          </li>
          <li>
            <a href="/assets" className="block py-2 text-gray-700 hover:text-blue-600">
              Assets
            </a>
          </li>
          <li>
            <a href="/transactions" className="block py-2 text-gray-700 hover:text-blue-600">
              Transactions
            </a>
          </li>
          <li>
            <a href="#" className="block py-2 text-gray-700 hover:text-blue-600">
              Documents
            </a>
          </li>
          <li>
            <a href="#" className="block py-2 text-gray-700 hover:text-blue-600">
              Reports
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default AppSideBar;