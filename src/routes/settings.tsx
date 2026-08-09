import { createRoute } from "@tanstack/react-router";
import { Route as RootRoute } from "./__root";
import { useState } from "react";
import { Check, Languages, ShoppingBasket, Sprout, UserRound } from "lucide-react";
import { SiteHeader, SiteFooter } from "@/components/site-header";
import { useRole } from "@/lib/role-context";
import { useLanguage } from "@/lib/language-context";
import { languages } from "@/lib/languages";

export const Route = createRoute({
  getParentRoute: () => RootRoute,
  path: "/settings",
  component: SettingsPage,
});

const field =
  "mt-1.5 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-ring/40";

function SettingsPage() {
  const { role, setRole, customer, setCustomer, farmer, setFarmer } = useRole();
  const { lang, setLang, auto, setAuto } = useLanguage();
  const [saved, setSaved] = useState(false);

  const flash = () => {
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  };

  return (
    <div className="min-h-screen field-bg">
      <SiteHeader />

      <main className="mx-auto max-w-4xl px-5 pb-20 pt-10">
        <h1 className="text-4xl">Settings</h1>
        <p className="mt-2 max-w-xl text-muted-foreground">
          Choose how you use KrishiSync, set your personal details and pick the language you are
          most comfortable in.
        </p>

        <section className="bento-tile mt-7 p-6">
          <h2 className="flex items-center gap-2 text-xl">
            <UserRound className="h-5 w-5 text-primary" /> I am using KrishiSync as
          </h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {(
              [
                ["customer", "Customer", "Buy fresh lots direct from farms", ShoppingBasket],
                ["farmer", "Farmer", "List lots, take orders, get payouts", Sprout],
              ] as const
            ).map(([value, label, desc, Icon]) => (
              <button
                key={value}
                onClick={() => setRole(value)}
                className={
                  "flex items-start gap-3 rounded-2xl border p-4 text-left transition-colors " +
                  (role === value
                    ? "border-primary bg-accent"
                    : "border-border bg-card hover:border-primary/50")
                }
              >
                <Icon className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                <span className="min-w-0">
                  <span className="block text-sm font-medium text-foreground">{label}</span>
                  <span className="block text-xs text-muted-foreground">{desc}</span>
                </span>
              </button>
            ))}
          </div>
        </section>

        <section className="bento-tile mt-4 p-6">
          <h2 className="flex items-center gap-2 text-xl">
            <Languages className="h-5 w-5 text-primary" /> App language
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            This language is used across the app and by the voice assistant.
          </p>
          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            {languages.map((l) => (
              <button
                key={l.code}
                onClick={() => setLang(l.code)}
                className={
                  "flex items-center justify-between gap-2 rounded-xl border px-3 py-2 text-sm transition-colors " +
                  (lang === l.code
                    ? "border-primary bg-accent text-foreground"
                    : "border-border bg-card text-muted-foreground hover:text-foreground")
                }
              >
                <span className="truncate">
                  {l.native} <span className="text-xs text-muted-foreground">· {l.label}</span>
                </span>
                {lang === l.code && <Check className="h-4 w-4 shrink-0 text-primary" />}
              </button>
            ))}
          </div>
          <label className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={auto}
              onChange={(e) => setAuto(e.target.checked)}
              className="h-4 w-4 accent-current"
            />
            Let the voice assistant auto-detect the language I speak
          </label>
        </section>

        {role === "customer" ? (
          <section className="bento-tile mt-4 p-6">
            <h2 className="text-xl">Customer settings</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label className="text-sm">
                Full name
                <input
                  className={field}
                  value={customer.name}
                  onChange={(e) => setCustomer({ name: e.target.value })}
                />
              </label>
              <label className="text-sm">
                Phone
                <input
                  className={field}
                  value={customer.phone}
                  onChange={(e) => setCustomer({ phone: e.target.value })}
                />
              </label>
              <label className="text-sm sm:col-span-2">
                Delivery address
                <input
                  className={field}
                  value={customer.address}
                  onChange={(e) => setCustomer({ address: e.target.value })}
                />
              </label>
              <label className="text-sm">
                Preferred delivery slot
                <select
                  className={field}
                  value={customer.deliverySlot}
                  onChange={(e) => setCustomer({ deliverySlot: e.target.value })}
                >
                  <option>Morning (7–10 am)</option>
                  <option>Afternoon (12–3 pm)</option>
                  <option>Evening (5–8 pm)</option>
                </select>
              </label>
              <label className="mt-7 flex items-center gap-2 text-sm text-muted-foreground">
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-current"
                  checked={customer.organicOnly}
                  onChange={(e) => setCustomer({ organicOnly: e.target.checked })}
                />
                Show organic lots first
              </label>
            </div>
          </section>
        ) : (
          <section className="bento-tile mt-4 p-6">
            <h2 className="text-xl">Farmer settings</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label className="text-sm">
                Farmer name
                <input
                  className={field}
                  value={farmer.name}
                  onChange={(e) => setFarmer({ name: e.target.value })}
                />
              </label>
              <label className="text-sm">
                Village / district
                <input
                  className={field}
                  value={farmer.village}
                  onChange={(e) => setFarmer({ village: e.target.value })}
                />
              </label>
              <label className="text-sm">
                Farm size
                <input
                  className={field}
                  value={farmer.farmSize}
                  onChange={(e) => setFarmer({ farmSize: e.target.value })}
                />
              </label>
              <label className="text-sm">
                Payout UPI ID
                <input
                  className={field}
                  value={farmer.payoutUpi}
                  onChange={(e) => setFarmer({ payoutUpi: e.target.value })}
                />
              </label>
              <label className="flex items-center gap-2 text-sm text-muted-foreground sm:col-span-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-current"
                  checked={farmer.autoAcceptOrders}
                  onChange={(e) => setFarmer({ autoAcceptOrders: e.target.checked })}
                />
                Auto-accept orders that match my listed price
              </label>
            </div>
          </section>
        )}

        <div className="mt-5 flex items-center gap-3">
          <button
            onClick={flash}
            className="rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Save preferences
          </button>
          {saved && (
            <span className="flex items-center gap-1.5 text-sm text-primary">
              <Check className="h-4 w-4" /> Saved on this device
            </span>
          )}
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
