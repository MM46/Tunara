"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  Clock3,
  Library,
  Music,
  PlusCircle,
  Settings,
} from "lucide-react";

const navigation = [
  {
    name: "Create Song",
    href: "/dashboard",
    icon: PlusCircle,
  },
  {
    name: "Library",
    href: "/library",
    icon: Library,
  },
  {
    name: "Songs",
    href: "/songs",
    icon: Music,
  },
  {
    name: "History",
    href: "/history",
    icon: Clock3,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-zinc-800 bg-zinc-950">
      <div className="border-b border-zinc-800 p-6">
        <button
          type="button"
          onClick={() => router.push("/dashboard")}
          className="text-left"
        >
          <h1 className="text-2xl font-bold tracking-wide text-white">
            TUNARA
          </h1>
        </button>
      </div>

      <nav className="flex flex-1 flex-col gap-2 p-4">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <button
              key={item.href}
              type="button"
              onClick={() => router.push(item.href)}
              className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition ${
                isActive
                  ? "bg-violet-600 text-white"
                  : "text-zinc-300 hover:bg-zinc-900 hover:text-white"
              }`}
            >
              <Icon size={18} />
              <span>{item.name}</span>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-zinc-800 p-4">
        <button
          type="button"
          onClick={() => router.push("/settings")}
          className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm transition ${
            pathname === "/settings"
              ? "bg-violet-600 text-white"
              : "text-zinc-300 hover:bg-zinc-900 hover:text-white"
          }`}
        >
          <Settings size={18} />
          <span>Settings</span>
        </button>

        <p className="mt-4 px-4 text-xs text-zinc-600">
          Tunara v0.1.0
        </p>
      </div>
    </aside>
  );
}