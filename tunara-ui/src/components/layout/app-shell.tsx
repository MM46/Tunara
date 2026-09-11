import Header from "@/components/layout/header";
import Sidebar from "@/components/layout/sidebar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto px-6 py-8 lg:px-10">{children}</main>
      </div>
    </div>
  );
}
