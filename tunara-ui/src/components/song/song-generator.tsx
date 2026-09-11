"use client";

import { useState } from "react";
import { LoaderCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  createSong,
  SongResponse,
} from "@/services/song.service";

export default function SongGenerator() {
  const [prompt, setPrompt] = useState("");
  const [genre, setGenre] = useState("Rock");
  const [voice, setVoice] = useState("Male Voice");
  const [language, setLanguage] = useState("English");
  const [durationSeconds, setDurationSeconds] = useState(60);
  const [isGenerating, setIsGenerating] = useState(false);
  const [createdSong, setCreatedSong] = useState<SongResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  const genres = [
    "Rock",
    "Pop",
    "Hip Hop",
    "EDM",
    "Country",
    "Cinematic",
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setErrorMessage("Please enter a song description.");
      return;
    }

    setIsGenerating(true);
    setErrorMessage("");
    setCreatedSong(null);

    try {
      const song = await createSong({
        prompt: prompt.trim(),
        genre,
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

  return (
    <div className="rounded-3xl border border-zinc-800 bg-gradient-to-b from-zinc-900 to-zinc-950 p-6 shadow-2xl">
      <Textarea
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        placeholder="Create a cinematic rock song about an AI developer building the future..."
        className="min-h-[160px] resize-none border-zinc-700 bg-zinc-950 text-white placeholder:text-zinc-600"
        disabled={isGenerating}
      />

      <div className="mt-6 flex flex-wrap gap-3">
        {genres.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setGenre(item)}
            disabled={isGenerating}
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
          disabled={isGenerating}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white outline-none focus:border-violet-500"
        >
          <option value="Male Voice">Male Voice</option>
          <option value="Female Voice">Female Voice</option>
          <option value="Deep Voice">Deep Voice</option>
          <option value="Energetic Voice">Energetic Voice</option>
        </select>

        <select
          value={language}
          onChange={(event) => setLanguage(event.target.value)}
          disabled={isGenerating}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white outline-none focus:border-violet-500"
        >
          <option value="English">English</option>
          <option value="Spanish">Spanish</option>
          <option value="French">French</option>
          <option value="German">German</option>
        </select>

        <select
          value={durationSeconds}
          onChange={(event) =>
            setDurationSeconds(Number(event.target.value))
          }
          disabled={isGenerating}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white outline-none focus:border-violet-500"
        >
          <option value={60}>1 Minute</option>
          <option value={120}>2 Minutes</option>
          <option value={180}>3 Minutes</option>
          <option value={240}>4 Minutes</option>
        </select>
      </div>

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

          <p className="mt-1 text-sm text-zinc-300">
            {createdSong.title}
          </p>

          <p className="mt-2 text-xs uppercase tracking-wide text-emerald-400">
            Status: {createdSong.status}
          </p>
        </div>
      )}

      <div className="mt-8 flex justify-center">
        <Button
          type="button"
          size="lg"
          onClick={handleGenerate}
          disabled={isGenerating}
          className="min-w-48 bg-violet-600 px-10 hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isGenerating ? (
            <>
              <LoaderCircle className="animate-spin" size={18} />
              Creating...
            </>
          ) : (
            "Generate Song"
          )}
        </Button>
      </div>
    </div>
  );
}