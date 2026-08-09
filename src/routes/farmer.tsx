import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { CloudSun, Droplets, PackageCheck, Plus, Truck, TrendingUp } from "lucide-react";
import { SiteHeader, SiteFooter } from "@/components/site-header";
import { ListLotDialog } from "@/components/list-lot-dialog";
import { earningsByWeek, farmerOrders, produce } from "@/data/market";

export const Route = createFileRoute("/farmer")({
  validateSearch: (search: Record<string, unknown>) => ({
    action: search["action"] === "list" ? ("list" as const) : undefined,
  }),
  head: () => ({
    meta: [
      { title: "Farmer Desk — Listings, Orders & Payouts | KrishiSync" },
      {
        name: "description",
        content:
          "Manage your lots, track direct orders and see payouts against mandi rates — the KrishiSync desk for farmers.",
      },
      { property: "og:title", content: "Farmer Desk — Listings, Orders & Payouts | KrishiSync" },
      {
        property: "og:description",
        content: "Your lots, your rates, your buyers — all in one farmer dashboard.",
      },
    ],
  }),
  component: FarmerDesk,
});

const statusStyles: Record<string, string> = {
  Packing: "bg-accent text-accent-foreground",
  "In transit": "bg-harvest/25 text-harvest-foreground",
  Delivered: "bg-secondary text-secondary-foreground",
};

function FarmerDesk() {
  const { action } = Route.useSearch();
  const max = Math.max(...earningsByWeek.map((w) => w.direct));
  const myLots = produce.slice(0, 4);
  const [dialog, setDialog] = useState(false);

  useEffect(() => {
    if (action === "list") setDialog(true);
  }, [action]);

  return (
    <div className="min-h-screen field-bg">
      <SiteHeader />

      <main className="mx-auto max-w-6xl px-5 pb-20 pt-10">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
              नमस्कार, Ramesh
            </p>
            <h1 className="mt-1 truncate text-3xl sm:text-4xl">Farmer Desk</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setDialog(true)}
              className="inline-flex shrink-0 items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              <Plus className="h-4 w-4" />
              List a lot
            </button>
            <button
              onClick={() => setDialog(true)}
              className="inline-flex shrink-0 items-center gap-2 rounded-full border border-border bg-card px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
            >
              <Truck className="h-4 w-4 text-primary" />
              Book a pickup
            </button>
          </div>
        </header>

        <ListLotDialog open={dialog} onClose={() => setDialog(false)} />

        <section className="mt-7 grid gap-4 md:grid-cols-4">
          {[
            ["₹19,600", "Direct sales this week", "+13% vs last week"],
            ["4", "Live lots", "1 running low"],
            ["612", "Lifetime orders", "4.9★ buyer rating"],
            ["₹1,240", "Pending payout", "Credited tomorrow"],
          ].map(([v, l, s]) => (
            <div key={l} className="bento-tile p-5">
              <p className="font-display text-3xl">{v}</p>
              <p className="mt-1 text-sm text-foreground">{l}</p>
              <p className="mt-0.5 text-xs text-muted-foreground">{s}</p>
            </div>
          ))}
        </section>

        <section className="mt-4 grid gap-4 lg:grid-cols-3">
          <div className="bento-tile p-6 lg:col-span-2">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl">Direct vs mandi earnings</h2>
              <span className="inline-flex items-center gap-1.5 text-sm text-primary">
                <TrendingUp className="h-4 w-4" /> 6 weeks
              </span>
            </div>
            <div className="mt-7 flex items-end gap-4">
              {earningsByWeek.map((w) => (
                <div key={w.week} className="flex min-w-0 flex-1 flex-col items-center gap-2">
                  <div className="flex w-full items-end justify-center gap-1.5">
                    <div
                      className="w-1/2 rounded-t-md bg-primary transition-all"
                      style={{ height: `${Math.round((w.direct / max) * 176)}px` }}
                      title={`Direct ₹${w.direct}`}
                    />
                    <div
                      className="w-1/2 rounded-t-md bg-harvest/70"
                      style={{ height: `${Math.round((w.mandi / max) * 176)}px` }}
                      title={`Mandi ₹${w.mandi}`}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">{w.week}</span>
                </div>
              ))}
            </div>

            <div className="mt-4 flex gap-5 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <i className="h-2.5 w-2.5 rounded-full bg-primary" /> Direct to consumer
              </span>
              <span className="flex items-center gap-1.5">
                <i className="h-2.5 w-2.5 rounded-full bg-harvest/70" /> Mandi route
              </span>
            </div>
          </div>

          <div className="bento-tile flex flex-col gap-5 p-6">
            <h2 className="text-xl">Field today</h2>
            <div className="flex items-center gap-3">
              <CloudSun className="h-8 w-8 text-harvest" />
              <div>
                <p className="font-display text-2xl">31°C</p>
                <p className="text-sm text-muted-foreground">Nashik · partly cloudy</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Droplets className="h-8 w-8 text-primary" />
              <div>
                <p className="font-display text-2xl">64%</p>
                <p className="text-sm text-muted-foreground">Humidity · isolated rain by Thursday</p>
              </div>
            </div>
            <p className="mt-auto rounded-xl bg-accent p-4 text-sm text-accent-foreground">
              Advisory: harvest the onion lot before Thursday's showers to protect grade.
            </p>
          </div>
        </section>

        <section className="mt-4 grid gap-4 lg:grid-cols-3">
          <div className="bento-tile p-6 lg:col-span-2">
            <h2 className="text-xl">Recent direct orders</h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[34rem] text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wider text-muted-foreground">
                    <th className="pb-3 font-medium">Order</th>
                    <th className="pb-3 font-medium">Buyer</th>
                    <th className="pb-3 font-medium">Lot</th>
                    <th className="pb-3 font-medium">Payout</th>
                    <th className="pb-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {farmerOrders.map((o) => (
                    <tr key={o.id} className="border-t border-border">
                      <td className="py-3 font-medium">{o.id}</td>
                      <td className="py-3 text-muted-foreground">{o.buyer}</td>
                      <td className="py-3 text-muted-foreground">
                        {o.item} · {o.qty}
                      </td>
                      <td className="py-3">₹{o.amount}</td>
                      <td className="py-3">
                        <span
                          className={`rounded-full px-2.5 py-1 text-xs ${statusStyles[o.status]}`}
                        >
                          {o.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bento-tile p-6">
            <h2 className="text-xl">Your live lots</h2>
            <ul className="mt-4 space-y-4">
              {myLots.map((l) => (
                <li key={l.id} className="flex items-center gap-3">
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-secondary text-lg">
                    {l.emoji}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{l.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {l.stock} {l.unit} left · ₹{l.price}/{l.unit}
                    </p>
                  </div>
                  <PackageCheck className="h-4 w-4 shrink-0 text-primary" />
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
