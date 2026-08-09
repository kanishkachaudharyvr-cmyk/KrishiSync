import { useState } from "react";
import { Check, PackagePlus, Truck, X } from "lucide-react";
import { useRole } from "@/lib/role-context";

export function ListLotDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { farmer } = useRole();
  const [crop, setCrop] = useState("");
  const [qty, setQty] = useState("");
  const [price, setPrice] = useState("");
  const [pickup, setPickup] = useState("");
  const [mode, setMode] = useState<"listing" | "pickup">("listing");
  const [done, setDone] = useState(false);

  if (!open) return null;

  const field =
    "mt-1.5 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-ring/40";

  return (
    <div className="fixed inset-0 z-50 grid place-items-end bg-foreground/30 p-4 backdrop-blur-sm sm:place-items-center">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card p-6 shadow-xl">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="font-display text-2xl leading-tight">Sell your harvest</h2>
            <p className="text-sm text-muted-foreground">
              {farmer.name} · {farmer.village}
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="rounded-full p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {done ? (
          <div className="mt-6 rounded-xl bg-accent p-5 text-accent-foreground">
            <p className="flex items-center gap-2 font-medium">
              <Check className="h-4 w-4" />
              {mode === "listing" ? "Lot listed on the market" : "Pickup booking confirmed"}
            </p>
            <p className="mt-1 text-sm">
              {crop || "Your lot"} · {qty || "—"} at ₹{price || "—"}
              {mode === "pickup" && pickup ? ` · pickup ${pickup}` : ""}
            </p>
            <button
              onClick={onClose}
              className="mt-4 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
            >
              Done
            </button>
          </div>
        ) : (
          <>
            <div className="mt-5 flex gap-2">
              {(
                [
                  ["listing", "List a lot", PackagePlus],
                  ["pickup", "Book a pickup", Truck],
                ] as const
              ).map(([v, label, Icon]) => (
                <button
                  key={v}
                  onClick={() => setMode(v)}
                  className={
                    "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition-colors " +
                    (mode === v
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-card text-muted-foreground hover:text-foreground")
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </button>
              ))}
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="text-sm sm:col-span-2">
                Crop / produce
                <input
                  className={field}
                  value={crop}
                  onChange={(e) => setCrop(e.target.value)}
                  placeholder="e.g. Red Onion / प्याज"
                />
              </label>
              <label className="text-sm">
                Quantity
                <input
                  className={field}
                  value={qty}
                  onChange={(e) => setQty(e.target.value)}
                  placeholder="120 kg"
                />
              </label>
              <label className="text-sm">
                Your price (₹ per unit)
                <input
                  className={field}
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  placeholder="28"
                />
              </label>
              {mode === "pickup" && (
                <label className="text-sm sm:col-span-2">
                  Pickup date & time
                  <input
                    className={field}
                    value={pickup}
                    onChange={(e) => setPickup(e.target.value)}
                    placeholder="Tomorrow, 8 am"
                  />
                </label>
              )}
            </div>

            <button
              onClick={() => setDone(true)}
              className="mt-5 w-full rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              {mode === "listing" ? "Publish lot to market" : "Confirm pickup booking"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
