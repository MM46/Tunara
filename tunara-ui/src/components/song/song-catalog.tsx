"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { LoaderCircle, Music2, RefreshCw, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getSongs, type SongResponse } from "@/services/song.service";

export default function SongCatalog({ title }: { title: string }) {
  const [songs, setSongs] = useState<SongResponse[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setSongs(await getSongs());
    } catch {
      setError("Unable to load songs. Verify that the Tunara API is running.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const filtered = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return songs;
    return songs.filter((song) =>
      [song.title, song.prompt, song.genre, song.language, song.status]
        .some((field) => field?.toLowerCase().includes(value))
    );
  }, [query, songs]);

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="mt-2 text-zinc-400">Browse every song request stored in Tunara.</p>
        </div>
        <Button variant="outline" onClick={() => void load()} disabled={loading}
          className="border-zinc-700 bg-zinc-950 text-zinc-300">
          {loading ? <LoaderCircle className="animate-spin" /> : <RefreshCw />}
          Refresh
        </Button>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
        <Input value={query} onChange={(event) => setQuery(event.target.value)}
          placeholder="Search title, genre, language or status"
          className="h-11 border-zinc-800 bg-zinc-950 pl-10 text-white" />
      </div>

      {loading && <div className="py-20 text-center text-zinc-400">Loading songs...</div>}
      {!loading && error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">{error}</div>}
      {!loading && !error && filtered.length === 0 && <div className="py-20 text-center text-zinc-500">No matching songs.</div>}

      {!loading && !error && filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.map((song) => (
            <article key={song.id} className="flex items-center gap-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-600">
                <Music2 />
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="truncate font-semibold">{song.title}</h2>
                <p className="mt-1 truncate text-sm text-zinc-400">{song.prompt}</p>
                <p className="mt-2 text-xs text-zinc-500">{song.genre} · {song.language} · {song.durationSeconds}s</p>
              </div>
              <span className="rounded-full border border-zinc-700 px-3 py-1 text-xs text-zinc-300">{song.status}</span>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
