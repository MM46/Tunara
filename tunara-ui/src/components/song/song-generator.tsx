"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export default function SongGenerator() {
  const [prompt, setPrompt] = useState("");
  const [genre, setGenre] = useState("Rock");
  const [voice, setVoice] = useState("Male Voice");
  const [language, setLanguage] = useState("English");
  const [duration, setDuration] = useState("1 Minute");
  const [isGenerating, setIsGenerating] = useState(false);

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
      alert("Please enter a song description.");
      return;
    }

    setIsGenerating(true);

    console.log({
      prompt,
      genre,
      voice,
      language,
      duration,
    });

    await new Promise((resolve) => setTimeout(resolve, 3000));

    setIsGenerating(false);

    alert("Song generation request created.");
  };

  return (
    <div className="rounded-3xl border border-zinc-800 bg-gradient-to-b from-zinc-900 to-zinc-950 p-6 shadow-2xl">
      <Textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Create a cinematic rock song about an AI developer building the future..."
        className="min-h-[160px] border-zinc-700 bg-zinc-950 text-white"
      />

      <div className="mt-6 flex flex-wrap gap-3">
        {genres.map((item) => (
          <button
            key={item}
            onClick={() => setGenre(item)}
            className={`rounded-full border px-4 py-2 text-sm transition ${
              genre === item
                ? "border-violet-500 bg-violet-600 text-white"
                : "border-zinc-700 bg-zinc-900 hover:border-violet-500 hover:text-violet-300"
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        <select
          value={voice}
          onChange={(e) => setVoice(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3"
        >
          <option>Male Voice</option>
          <option>Female Voice</option>
          <option>Deep Voice</option>
          <option>Energetic Voice</option>
        </select>

        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3"
        >
          <option>English</option>
          <option>Spanish</option>
          <option>French</option>
          <option>German</option>
        </select>

        <select
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 p-3"
        >
          <option>1 Minute</option>
          <option>2 Minutes</option>
          <option>3 Minutes</option>
          <option>4 Minutes</option>
        </select>
      </div>

      <div className="mt-8 flex justify-center">
        <Button
          size="lg"
          onClick={handleGenerate}
          disabled={isGenerating}
          className="bg-violet-600 px-10 hover:bg-violet-500"
        >
          {isGenerating ? "Generating..." : "Generate Song"}
        </Button>
      </div>
    </div>
  );
}