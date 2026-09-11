"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Clock3, LoaderCircle, Music2, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { getSongs, type SongResponse } from "@/services/song.service";

const coverStyles = [
  "from-violet-600 via-fuchsia-600 to-pink-500",
  "from-cyan-500 via-blue-600 to-violet-700",
  "from-emerald-500 via-teal-600 to-cyan-700",
  "from-orange-500 via-rose-600 to-purple-700",
  "from-indigo-500 via-purple-600 to-fuchsia-600",
  "from-amber-500 via-orange-600 to-red-700",
];

function formatDuration(durationSeconds: number): string {
  const minutes = Math.floor(durationSeconds / 60);
  const seconds = durationSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function formatCreatedAt(createdAt: string): string {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(createdAt));
}

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
      return "border-zinc-600 bg-zinc-800 text-zinc-300";
  }
}

export default function RecentSongs() {
  const [songs, setSongs] = useState<SongResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const loadSongs = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      setSongs(await getSongs());
    } catch (error) {
      console.error("Unable to load songs:", error);
      setErrorMessage(
        "Unable to load recent songs. Verify that the Tunara API is running."
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSongs();
  }, [loadSongs]);

  return (
    <section className="mt-12">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">
            Recent Creations
          </h2>
          <p className="mt-1 text-sm text-zinc-500">
            Songs recently created with Tunara
          </p>
        </div>

        <Button
          type="button"
          variant="outline"
          onClick={() => void loadSongs()}
          disabled={isLoading}
          className="border-zinc-700 bg-zinc-950 text-zinc-300 hover:bg-zinc-900 hover:text-white"
        >
          {isLoading ? (
            <LoaderCircle className="animate-spin" size={17} />
          ) : (
            <RefreshCw size={17} />
          )}
          Refresh
        </Button>
      </div>

      {isLoading && (
        <div className="flex min-h-48 items-center justify-center rounded-2xl border border-zinc-800 bg-zinc-950">
          <div className="flex items-center gap-3 text-sm text-zinc-400">
            <LoaderCircle className="animate-spin" size={20} />
            Loading recent songs...
          </div>
        </div>
      )}

      {!isLoading && errorMessage && (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-300">
          {errorMessage}
        </div>
      )}

      {!isLoading && !errorMessage && songs.length === 0 && (
        <div className="flex min-h-48 flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-800 bg-zinc-950 px-6 text-center">
          <Music2 className="mb-4 text-zinc-600" size={32} />
          <h3 className="font-medium text-zinc-300">No songs created yet</h3>
          <p className="mt-2 text-sm text-zinc-500">
            Your generated songs will appear here.
          </p>
        </div>
      )}

      {!isLoading && !errorMessage && songs.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {songs.slice(0, 6).map((song, index) => (
            <Link
              key={song.id}
              href={`/songs/${song.id}`}
              aria-label={`Open ${song.title}`}
              className="group block overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950 transition hover:-translate-y-1 hover:border-violet-500/50 focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <article>
                <div
                  className={`flex h-40 items-center justify-center bg-gradient-to-br ${
                    coverStyles[index % coverStyles.length]
                  }`}
                >
                  <Music2
                    className="text-white/80 transition group-hover:scale-110"
                    size={42}
                  />
                </div>

                <div className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="line-clamp-1 font-semibold text-white">
                      {song.title}
                    </h3>
                    <span
                      className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium ${getStatusStyles(
                        song.status
                      )}`}
                    >
                      {song.status}
                    </span>
                  </div>

                  <p className="mt-2 line-clamp-2 min-h-10 text-sm text-zinc-400">
                    {song.prompt}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <span className="rounded-full bg-zinc-900 px-3 py-1 text-xs text-zinc-400">
                      {song.genre}
                    </span>
                    <span className="rounded-full bg-zinc-900 px-3 py-1 text-xs text-zinc-400">
                      {song.language}
                    </span>
                    <span className="rounded-full bg-zinc-900 px-3 py-1 text-xs text-zinc-400">
                      {formatDuration(song.durationSeconds)}
                    </span>
                  </div>

                  <div className="mt-5 flex items-center gap-2 border-t border-zinc-800 pt-4 text-xs text-zinc-500">
                    <Clock3 size={14} />
                    {formatCreatedAt(song.createdAt)}
                  </div>
                </div>
              </article>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
