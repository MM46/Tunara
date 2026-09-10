import Sidebar from "@/components/layout/sidebar";
import Header from "@/components/layout/header";
import SongGenerator from "@/components/song/song-generator";

export default function DashboardPage() {
  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-auto">
        <Header />

        <main className="flex-1 px-10 py-8">
          <div className="mx-auto max-w-6xl">
            <div className="mb-10 text-center">
              <div className="mb-4 inline-flex rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-2 text-sm text-violet-300">
                AI Powered Music Creation
              </div>

              <h1 className="mb-3 text-6xl font-bold">
                What's your next hit?
              </h1>

              <p className="text-zinc-400">
                Describe your idea and let Tunara create a complete song.
              </p>
            </div>

            <SongGenerator />

            <div className="mt-12">
              <h2 className="mb-6 text-2xl font-semibold">
                Recent Creations
              </h2>

              <div className="grid gap-6 md:grid-cols-3">
                {[1, 2, 3].map((item) => (
                  <div
                    key={item}
                    className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4 transition hover:border-violet-600"
                  >
                    <div className="mb-4 h-40 rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-600" />

                    <h3 className="font-semibold">
                      Untitled Song #{item}
                    </h3>

                    <p className="mt-2 text-sm text-zinc-400">
                      Generated with Tunara AI
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}