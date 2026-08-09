import { createRoute } from "@tanstack/react-router";
import { Route as RootRoute } from "./__root";
import { useEffect, useMemo, useState } from "react";
import { Mic, Search } from "lucide-react";
import { SiteHeader, SiteFooter } from "@/components/site-header";
import { ProduceCard } from "@/components/produce-card";
import { categories, produce } from "@/data/market";

export const Route = createRoute({
  getParentRoute: () => RootRoute,
  path: "/market",
  validateSearch: (search: Record<string, unknown>) => ({
    q: typeof search["q"] === "string" ? (search["q"] as string) : "",
    intent: search["intent"] === "buy" ? ("buy" as const) : undefined,
  }),
  component: Market,
});

function Market() {
  const { q: initialQ, intent } = Route.useSearch();
  const [cat, setCat] = useState<(typeof categories)[number]>("All");
  const [q, setQ] = useState(initialQ);

  useEffect(() => {
    setQ(initialQ);
  }, [initialQ]);

  const list = useMemo(
    () =>
      produce.filter(
        (p) =>
          (cat === "All" || p.category === cat) &&
          (q.trim() === "" ||
            `${p.name} ${p.local} ${p.farmer} ${p.village}`.toLowerCase().includes(q.toLowerCase())),
      ),
    [cat, q],
  );

  return (
    <div className="min-h-screen field-bg">
      <SiteHeader />

      <main className="mx-auto max-w-6xl px-5 pb-20 pt-10">
        <h1 className="text-4xl">The market</h1>
        <p className="mt-2 max-w-xl text-muted-foreground">
          Every lot below is listed by the farmer who grew it, with the village and harvest date
          attached.
        </p>

        {intent === "buy" && q.trim() !== "" && (
          <div className="mt-5 flex flex-wrap items-center gap-2 rounded-2xl border border-primary/40 bg-accent px-4 py-3 text-sm text-accent-foreground">
            <Mic className="h-4 w-4 shrink-0 text-primary" />
            <span>
              You asked to buy <strong>{q}</strong> — {list.length}{" "}
              {list.length === 1 ? "lot" : "lots"} available right now.
            </span>
          </div>
        )}

        <div className="mt-7 grid gap-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
          <div className="relative min-w-0">
            <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search crop, farmer or village…"
              className="w-full rounded-full border border-border bg-card py-3 pl-11 pr-4 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus:ring-2 focus:ring-ring/40"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {categories.map((c) => (
              <button
                key={c}
                onClick={() => setCat(c)}
                className={
                  "rounded-full border px-4 py-2 text-sm transition-colors " +
                  (cat === c
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-card text-muted-foreground hover:text-foreground")
                }
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {list.map((item) => (
            <ProduceCard key={item.id} item={item} />
          ))}
        </div>

        {list.length === 0 && (
          <p className="mt-16 text-center text-muted-foreground">
            No lots match that search. Try another crop or village.
          </p>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
