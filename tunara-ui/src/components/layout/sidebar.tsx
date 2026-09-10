import { Music, PlusCircle, Clock3, Library } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-zinc-800 bg-zinc-950">
      <div className="border-b border-zinc-800 p-6">
        <h1 className="text-2xl font-bold text-white">
          TUNARA
        </h1>
      </div>

      <nav className="flex flex-1 flex-col gap-2 p-4">
        <button className="flex items-center gap-3 rounded-lg bg-violet-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-violet-500">
          <PlusCircle size={18} />
          Create Song
        </button>

        <button className="flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-zinc-300 transition hover:bg-zinc-900 hover:text-white">
          <Library size={18} />
          Library
        </button>

        <button className="flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-zinc-300 transition hover:bg-zinc-900 hover:text-white">
          <Music size={18} />
          Songs
        </button>

        <button className="flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-zinc-300 transition hover:bg-zinc-900 hover:text-white">
          <Clock3 size={18} />
          History
        </button>
      </nav>

      <div className="border-t border-zinc-800 p-4">
        <p className="text-xs text-zinc-500">
          Tunara v0.1
        </p>
      </div>
    </aside>
  );
}