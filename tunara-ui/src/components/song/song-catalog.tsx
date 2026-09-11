"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { LoaderCircle, Music2, RefreshCw, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getSongs, type SongResponse } from "@/services/song.service";

function getStatusStyles(status: SongResponse["status"]): string {
  switch (status) {
    case "COMPLETED":
      return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
    case "FAILED":
      return "border-red-500/30 bg-red-500/10 text-red-300";
    case "PROCESSING":
      return "border-blue-500/30 bg-blue-500/10 text-blue-300";
    case "PENDING":
      return "border-amber-500/30 bg-amber-500/10 text-amber-300";
    default:
      return "border-zinc-700 bg-zinc-900 text-zinc-300";
  }
}

function formatDuration(durationSeconds: number): string {
  const minutes = Math.floor(durationSeconds / 60);
  const seconds = durationSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

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
    } catch (loadError) {
      console.error("Unable to load songs:", loadError);
      setError("Unable to load songs. Verify that the Tunara API is running.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) {
      return songs;
    }

    return songs.filter((song) =>
      [song.title, song.prompt, song.genre, song.language, song.status].some(
        (field) => field?.toLowerCase().includes(value)
      )
    );
  }, [query, songs]);

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="mt-2 text-zinc-400">
            Browse every song request stored in Tunara.
          </p>
        </div>

        <Button
          type="button"
          variant="outline"
          onClick={() => void load()}
          disabled={loading}
          className="border-zinc-700 bg-zinc-950 text-zinc-300 hover:bg-zinc-900 hover:text-white"
        >
          {loading ? (
            <LoaderCircle className="animate-spin" size={17} />
          ) : (
            <RefreshCw size={17} />
          )}
          Refresh
        </Button>
      </div>

      <div className="relative mb-6">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
          size={18}
        />
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search title, genre, language or status"
          className="h-11 border-zinc-800 bg-zinc-950 pl-10 text-white"
        />
      </div>

      {loading && (
        <div className="flex items-center justify-center gap-3 py-20 text-zinc-400">
          <LoaderCircle className="animate-spin" size={20} />
          Loading songs...
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
          {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="py-20 text-center text-zinc-500">
          No matching songs.
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.map((song) => (
            <Link
              key={song.id}
              href={`/songs/${song.id}`}
              aria-label={`Open ${song.title}`}
              className="group flex items-center gap-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-4 transition hover:border-violet-500/50 hover:bg-zinc-900/80 focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-600">
                <Music2 className="transition group-hover:scale-110" />
              </div>

              <div className="min-w-0 flex-1">
                <h2 className="truncate font-semibold text-white">
                  {song.title}
                </h2>
                <p className="mt-1 truncate text-sm text-zinc-400">
                  {song.prompt}
                </p>
                <p className="mt-2 text-xs text-zinc-500">
                  {song.genre} · {song.language} · {formatDuration(song.durationSeconds)}
                </p>
              </div>

              <span
                className={`shrink-0 rounded-full border px-3 py-1 text-xs font-medium ${getStatusStyles(
                  song.status
                )}`}
              >
                {song.status}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
