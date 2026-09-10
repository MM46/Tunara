export default function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-zinc-800 px-8">
      <div>
        <h2 className="text-lg font-semibold text-white">
          Create Music
        </h2>
      </div>

      <div className="flex items-center gap-4">
        <div className="h-10 w-10 rounded-full bg-violet-600" />
      </div>
    </header>
  );
}