"use client";

import { Download, FileArchive, FileMusic, Music2 } from "lucide-react";

import type { SongResponse } from "@/services/song.service";

interface SongDownloadsProps {
  song: SongResponse;
}

function downloadHref(url: string, name: string): string {
  const parameters = new URLSearchParams({ url, name });
  return `/api/download?${parameters.toString()}`;
}

function fileName(title: string, suffix: string): string {
  const normalized = title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^A-Za-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return `${normalized || "Tunara-Song"}-${suffix}`;
}

const downloadButtonClass =
  "inline-flex h-10 w-full items-center justify-center gap-2 rounded-md border border-zinc-700 bg-zinc-950 px-4 py-2 text-sm font-medium text-zinc-100 transition hover:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-violet-500";

const primaryDownloadButtonClass =
  "inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-500";

export default function SongDownloads({ song }: SongDownloadsProps) {
  return (
    <section className="mt-6 rounded-2xl border border-zinc-800 bg-black/20 p-6">
      <div>
        <p className="font-medium text-zinc-200">Production files</p>
        <p className="mt-1 text-sm text-zinc-500">
          The WAV is instrumental only. The MIDI and Logic Pro Pack contain
          the editable composition guide. Sung vocals are not generated yet.
        </p>
      </div>

      {song.wavUrl ? (
        <audio
          controls
          preload="metadata"
          className="mt-5 w-full"
          src={song.wavUrl}
        >
          Your browser does not support audio playback.
        </audio>
      ) : (
        <div className="mt-5 rounded-xl border border-dashed border-zinc-800 p-5 text-sm text-zinc-500">
          Instrumental is not available yet.
        </div>
      )}

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {song.wavUrl && (
          <a
            href={downloadHref(
              song.wavUrl,
              fileName(song.title, "Instrumental.wav")
            )}
            className={downloadButtonClass}
          >
            <Music2 size={17} />
            Download Instrumental
          </a>
        )}

        {song.midiUrl && (
          <a
            href={downloadHref(
              song.midiUrl,
              fileName(song.title, "Composer.mid")
            )}
            className={downloadButtonClass}
          >
            <FileMusic size={17} />
            Download MIDI
          </a>
        )}

        {song.logicPackUrl && (
          <a
            href={downloadHref(
              song.logicPackUrl,
              fileName(song.title, "Logic-Pro-Pack.zip")
            )}
            className={primaryDownloadButtonClass}
          >
            <FileArchive size={17} />
            Download Logic Pro Pack
          </a>
        )}
      </div>

      {!song.wavUrl && !song.midiUrl && !song.logicPackUrl && (
        <div className="mt-5 flex items-center gap-2 text-sm text-zinc-500">
          <Download size={16} />
          No production files are available for this generation.
        </div>
      )}
    </section>
  );
}
