"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  LoaderCircle,
  Sparkles,
  WandSparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  improvePrompt,
  type CreativeBrief,
} from "@/services/prompt-director.service";
import {
  createSong,
  type SongResponse,
} from "@/services/song.service";

export default function SongGenerator() {
  const [prompt, setPrompt] = useState("");
  const [genre, setGenre] = useState("Pop");
  const [voice, setVoice] = useState("Female Voice");
  const [language, setLanguage] = useState("Spanish");
  const [durationSeconds, setDurationSeconds] = useState(180);
  const [brief, setBrief] = useState<CreativeBrief | null>(null);
  const [showBrief, setShowBrief] = useState(true);
  const [isImproving, setIsImproving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [createdSong, setCreatedSong] = useState<SongResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  const genres = ["Rock", "Pop", "Hip Hop", "EDM", "Country", "Cinematic"];

  const handleImprovePrompt = async () => {
    if (!prompt.trim()) {
      setErrorMessage("Please enter a song idea first.");
      return;
    }

    setIsImproving(true);
    setErrorMessage("");
    setCreatedSong(null);

    try {
      const response = await improvePrompt({
        idea: prompt.trim(),
        genre,
        language,
        duration_seconds: durationSeconds,
      });

      setBrief(response.brief);
      setGenre(normalizeGenre(response.brief.genre));
      setShowBrief(true);
    } catch (error) {
      console.error("Unable to improve prompt:", error);
      setErrorMessage(
        "Unable to create the professional brief. Verify that Tunara AI is running."
      );
    } finally {
      setIsImproving(false);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setErrorMessage("Please enter a song description.");
      return;
    }

    setIsGenerating(true);
    setErrorMessage("");
    setCreatedSong(null);

    try {
      const generationPrompt = brief
        ? [
            brief.lyrics_prompt,
            brief.song_planner_prompt,
            brief.production_prompt,
          ].join("\n\n")
        : prompt.trim();

      const song = await createSong({
        prompt: generationPrompt,
        genre: brief?.genre ?? genre,
        voice,
        language,
        durationSeconds,
      });

      setCreatedSong(song);
    } catch (error) {
      console.error("Unable to create song:", error);
      setErrorMessage(
        "Unable to create the song. Verify that the Tunara API is running."
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const isBusy = isImproving || isGenerating;

  return (
    <div className="rounded-3xl border border-zinc-800 bg-gradient-to-b from-zinc-900 to-zinc-950 p-6 shadow-2xl">
      <div className="mb-4 flex items-center gap-2 text-sm font-medium text-violet-300">
        <WandSparkles size={18} />
        Write a simple idea. Tunara will turn it into a production brief.
      </div>

      <Textarea
        value={prompt}
        onChange={(event) => {
          setPrompt(event.target.value);
          setBrief(null);
        }}
        placeholder="Hazme una canción tipo Aitana o TINI sobre superar una ruptura..."
        className="min-h-[160px] resize-none border-zinc-700 bg-zinc-950 text-white placeholder:text-zinc-600"
        disabled={isBusy}
      />

      <div className="mt-4 flex justify-end">
        <Button
          type="button"
          variant="outline"
          onClick={handleImprovePrompt}
          disabled={isBusy || !prompt.trim()}
          className="border-violet-500/40 bg-violet-500/10 text-violet-200 hover:bg-violet-500/20"
        >
          {isImproving ? (
            <LoaderCircle className="animate-spin" size={18} />
          ) : (
            <Sparkles size={18} />
          )}
          {isImproving ? "Directing..." : "Improve Prompt"}
        </Button>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        {genres.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => {
              setGenre(item);
              setBrief(null);
            }}
            disabled={isBusy}
            className={`rounded-full border px-4 py-2 text-sm transition ${
              genre === item
                ? "border-violet-500 bg-violet-600 text-white"
                : "border-zinc-700 bg-zinc-900 text-zinc-300 hover:border-violet-500 hover:text-violet-300"
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        <select
          value={voice}
          onChange={(event) => setVoice(event.target.value)}
          disabled={isBusy}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white outline-none focus:border-violet-500"
        >
          <option value="Male Voice">Male Voice</option>
          <option value="Female Voice">Female Voice</option>
          <option value="Deep Voice">Deep Voice</option>
          <option value="Energetic Voice">Energetic Voice</option>
        </select>

        <select
          value={language}
          onChange={(event) => {
            setLanguage(event.target.value);
            setBrief(null);
          }}
          disabled={isBusy}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white outline-none focus:border-violet-500"
        >
          <option value="English">English</option>
          <option value="Spanish">Spanish</option>
          <option value="French">French</option>
          <option value="German">German</option>
        </select>

        <select
          value={durationSeconds}
          onChange={(event) => {
            setDurationSeconds(Number(event.target.value));
            setBrief(null);
          }}
          disabled={isBusy}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white outline-none focus:border-violet-500"
        >
          <option value={60}>1 Minute</option>
          <option value={120}>2 Minutes</option>
          <option value={180}>3 Minutes</option>
          <option value={240}>4 Minutes</option>
        </select>
      </div>

      {brief && (
        <section className="mt-7 overflow-hidden rounded-2xl border border-violet-500/30 bg-violet-500/5">
          <button
            type="button"
            onClick={() => setShowBrief((current) => !current)}
            className="flex w-full items-center justify-between px-5 py-4 text-left"
          >
            <div>
              <p className="font-semibold text-white">Creative Brief</p>
              <p className="mt-1 text-sm text-violet-300">
                {brief.genre} · {brief.subgenre} · {brief.bpm_range} BPM
              </p>
            </div>
            {showBrief ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>

          {showBrief && (
            <div className="grid gap-5 border-t border-violet-500/20 p-5 md:grid-cols-2">
              <BriefItem label="Theme" value={brief.lyrical_theme} />
              <BriefItem label="Mood" value={brief.mood} />
              <BriefItem label="Tonal direction" value={brief.tonal_direction} />
              <BriefItem
                label="Structure"
                value={brief.song_structure.join(" → ")}
              />
              <BriefItem
                label="Instrumentation"
                value={brief.instrumentation.join(", ")}
              />
              <BriefItem label="Vocal direction" value={brief.vocal_direction} />
              <div className="md:col-span-2">
                <BriefItem
                  label="Reference translation"
                  value={brief.safe_reference_translation}
                />
              </div>
            </div>
          )}
        </section>
      )}

      {errorMessage && (
        <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {errorMessage}
        </div>
      )}

      {createdSong && (
        <div className="mt-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-4">
          <p className="font-medium text-emerald-300">
            Song request created successfully
          </p>
          <p className="mt-1 text-sm text-zinc-300">{createdSong.title}</p>
          <p className="mt-2 text-xs uppercase tracking-wide text-emerald-400">
            Status: {createdSong.status}
          </p>
        </div>
      )}

      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Button
          type="button"
          size="lg"
          onClick={handleGenerate}
          disabled={isBusy || !prompt.trim()}
          className="min-w-56 bg-violet-600 px-10 hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isGenerating ? (
            <>
              <LoaderCircle className="animate-spin" size={18} />
              Creating...
            </>
          ) : brief ? (
            "Generate Automatically"
          ) : (
            "Generate Song"
          )}
        </Button>
      </div>
    </div>
  );
}

function BriefItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
        {label}
      </p>
      <p className="mt-2 text-sm leading-6 text-zinc-300">{value}</p>
    </div>
  );
}

function normalizeGenre(value: string): string {
  const normalized = value.toLowerCase();

  if (normalized.includes("rock")) return "Rock";
  if (normalized.includes("hip hop") || normalized.includes("urban")) {
    return "Hip Hop";
  }
  if (normalized.includes("edm") || normalized.includes("electro")) {
    return "EDM";
  }
  if (normalized.includes("country")) return "Country";
  if (normalized.includes("cinematic")) return "Cinematic";
  return "Pop";
}
