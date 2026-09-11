"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  Clock3,
  Download,
  FileText,
  LoaderCircle,
  Mic2,
  Music2,
  RefreshCw,
} from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  getGenerationJobBySongId,
  type GenerationJobResponse,
} from "@/services/generation-job.service";
import {
  getSongById,
  type SongResponse,
} from "@/services/song.service";

interface SongDetailProps {
  songId: string;
}

function formatDuration(durationSeconds: number): string {
  const minutes = Math.floor(durationSeconds / 60);
  const seconds = durationSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function formatDate(createdAt: string): string {
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
      return "border-zinc-700 bg-zinc-900 text-zinc-300";
  }
}

export default function SongDetail({ songId }: SongDetailProps) {
  const router = useRouter();
  const [song, setSong] = useState<SongResponse | null>(null);
  const [generationJob, setGenerationJob] =
    useState<GenerationJobResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const loadSong = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const songResponse = await getSongById(songId);
      setSong(songResponse);

      try {
        setGenerationJob(await getGenerationJobBySongId(songId));
      } catch (jobError) {
        console.error("Unable to retrieve generation job:", jobError);
        setGenerationJob(null);
      }
    } catch (error) {
      console.error("Unable to retrieve song:", error);
      setErrorMessage(
        "Unable to load this song. Verify that the Tunara API is running."
      );
    } finally {
      setIsLoading(false);
    }
  }, [songId]);

  useEffect(() => {
    void loadSong();
  }, [loadSong]);

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-zinc-400">
          <LoaderCircle className="animate-spin" size={22} />
          Loading song...
        </div>
      </div>
    );
  }

  if (errorMessage || !song) {
    return (
      <div className="mx-auto max-w-4xl">
        <Button
          type="button"
          variant="ghost"
          onClick={() => router.back()}
          className="mb-6 text-zinc-400 hover:bg-zinc-900 hover:text-white"
        >
          <ArrowLeft size={18} />
          Back
        </Button>

        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-red-300">
          {errorMessage || "Song not found."}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <Button
          type="button"
          variant="ghost"
          onClick={() => router.back()}
          className="text-zinc-400 hover:bg-zinc-900 hover:text-white"
        >
          <ArrowLeft size={18} />
          Back
        </Button>

        <Button
          type="button"
          variant="outline"
          onClick={() => void loadSong()}
          disabled={isLoading}
          className="border-zinc-700 bg-zinc-950 text-zinc-300 hover:bg-zinc-900 hover:text-white"
        >
          <RefreshCw size={17} />
          Refresh
        </Button>
      </div>

      <section className="grid gap-8 lg:grid-cols-[360px_minmax(0,1fr)]">
        <div>
          <div className="flex aspect-square items-center justify-center rounded-3xl bg-gradient-to-br from-violet-600 via-fuchsia-600 to-pink-500 shadow-2xl shadow-violet-950/30">
            <Music2 className="text-white/80" size={88} />
          </div>

          <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
              Song information
            </h2>

            <div className="mt-5 space-y-4">
              <div className="flex items-center gap-3">
                <Music2 className="text-violet-400" size={18} />
                <div>
                  <p className="text-xs text-zinc-500">Genre</p>
                  <p className="text-sm text-zinc-200">{song.genre}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Mic2 className="text-violet-400" size={18} />
                <div>
                  <p className="text-xs text-zinc-500">Voice</p>
                  <p className="text-sm text-zinc-200">{song.voice}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Clock3 className="text-violet-400" size={18} />
                <div>
                  <p className="text-xs text-zinc-500">Duration</p>
                  <p className="text-sm text-zinc-200">
                    {formatDuration(song.durationSeconds)}
                  </p>
                </div>
              </div>

              <div className="border-t border-zinc-800 pt-4">
                <p className="text-xs text-zinc-500">Created</p>
                <p className="mt-1 text-sm text-zinc-200">
                  {formatDate(song.createdAt)}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="min-w-0">
          <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-6 lg:p-8">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="text-sm font-medium text-violet-400">
                  {song.language}
                </p>
                <h1 className="mt-2 break-words text-4xl font-bold tracking-tight text-white">
                  {song.title}
                </h1>
              </div>

              <span
                className={`shrink-0 rounded-full border px-4 py-2 text-sm font-medium ${getStatusStyles(
                  song.status
                )}`}
              >
                {song.status}
              </span>
            </div>

            <div className="mt-6 rounded-2xl border border-zinc-800 bg-black/30 p-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Original prompt
              </p>
              <p className="mt-3 leading-7 text-zinc-300">{song.prompt}</p>
            </div>

            {generationJob && (
              <div className="mt-6 rounded-2xl border border-zinc-800 bg-black/30 p-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                      Generation progress
                    </p>
                    <p className="mt-2 text-sm text-zinc-300">
                      {generationJob.status}
                    </p>
                  </div>
                  <p className="text-2xl font-semibold text-white">
                    {generationJob.progress}%
                  </p>
                </div>

                <div className="mt-4 h-2 overflow-hidden rounded-full bg-zinc-800">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 transition-all"
                    style={{ width: `${generationJob.progress}%` }}
                  />
                </div>

                {generationJob.errorMessage && (
                  <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
                    {generationJob.errorMessage}
                  </div>
                )}
              </div>
            )}

            <div className="mt-6 rounded-2xl border border-dashed border-zinc-800 bg-black/20 p-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-zinc-300">Audio generation</p>
                  <p className="mt-1 text-sm text-zinc-500">
                    Instrumental and vocals will appear here.
                  </p>
                </div>

                <Button
                  type="button"
                  variant="outline"
                  disabled={!song.mp3Url}
                  className="border-zinc-700 bg-zinc-950"
                >
                  <Download size={17} />
                  Download
                </Button>
              </div>
            </div>
          </div>

          <section className="mt-8 rounded-3xl border border-zinc-800 bg-zinc-950 p-6 lg:p-8">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-violet-500/30 bg-violet-500/10">
                <FileText className="text-violet-400" size={21} />
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-white">Lyrics</h2>
                <p className="text-sm text-zinc-500">
                  Generated locally with Ollama
                </p>
              </div>
            </div>

            {song.lyrics ? (
              <pre className="whitespace-pre-wrap font-sans text-base leading-8 text-zinc-300">
                {song.lyrics}
              </pre>
            ) : (
              <div className="rounded-2xl border border-dashed border-zinc-800 p-8 text-center text-zinc-500">
                Lyrics are not available yet.
              </div>
            )}
          </section>
        </div>
      </section>
    </div>
  );
}
