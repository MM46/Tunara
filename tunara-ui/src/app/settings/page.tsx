import AppShell from "@/components/layout/app-shell";

export default function SettingsPage() {
  return (
    <AppShell>
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="mt-2 text-zinc-400">Local development configuration for Tunara.</p>
        <div className="mt-8 space-y-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
          <div>
            <p className="text-sm text-zinc-500">API URL</p>
            <p className="mt-1 text-zinc-200">http://localhost:8080</p>
          </div>
          <div className="border-t border-zinc-800 pt-4">
            <p className="text-sm text-zinc-500">AI service</p>
            <p className="mt-1 text-zinc-200">http://localhost:8000</p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
