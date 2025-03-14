import Sidebar from "./Sidebar";
import Header from "./Header";

export default function Layout({ children }) {
  return (
    <div className="flex flex-col h-screen bg-gray-950">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
