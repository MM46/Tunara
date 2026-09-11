import Header from "@/components/layout/header";
import Sidebar from "@/components/layout/sidebar";
import RecentSongs from "@/components/song/recent-songs";
import SongGenerator from "@/components/song/song-generator";

export default function DashboardPage() {
  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto px-10 py-8">
          <div className="mx-auto max-w-6xl">
            <div className="mb-10 text-center">
              <div className="mb-4 inline-flex rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-2 text-sm text-violet-300">
                AI Powered Music Creation
              </div>

              <h1 className="mb-3 text-6xl font-bold">
                What&apos;s your next hit?
              </h1>

              <p className="text-zinc-400">
                Describe your idea and let Tunara create a complete song.
              </p>
            </div>

            <SongGenerator />

            <RecentSongs />
          </div>
        </main>
      </div>
    </div>
  );
}