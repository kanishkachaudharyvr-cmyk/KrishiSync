import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Banknote, Clock3, Route as RouteIcon, Truck } from "lucide-react";
import heroFarm from "@/assets/hero-farm.jpg";
import produceBasket from "@/assets/produce-basket.jpg";
import farmerPortrait from "@/assets/farmer-portrait.jpg";
import delivery from "@/assets/delivery.jpg";
import { SiteHeader, SiteFooter } from "@/components/site-header";
import { ProduceCard } from "@/components/produce-card";
import { produce } from "@/data/market";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "KrishiSync — Farm-Direct Produce from Indian Farmers" },
      {
        name: "description",
        content:
          "Buy fresh produce straight from the farmer who grew it. No middlemen, transparent prices, same-day dispatch across India.",
      },
      { property: "og:title", content: "KrishiSync — Farm-Direct Produce from Indian Farmers" },
      {
        property: "og:description",
        content: "Buy fresh produce straight from the farmer who grew it. No middlemen, transparent prices, same-day dispatch across India.",
      },
    ],
  }),
  component: Home,
});

function Home() {
  return (
    <div className="min-h-screen field-bg">
      <SiteHeader />

      <main className="mx-auto max-w-6xl px-5 pb-20">
        <section className="grid gap-4 pt-8 md:grid-cols-3 md:grid-rows-[auto_auto]">
          <div className="bento-tile relative md:col-span-2 md:row-span-2">
            <img
              src={heroFarm}
              alt="Farmer tending rows of leafy greens at sunrise"
              width={1600}
              height={1104}
              className="h-64 w-full object-cover md:h-full md:min-h-[26rem]"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-foreground/80 via-foreground/25 to-transparent" />
            <div className="absolute inset-x-0 bottom-0 p-6 md:p-9">
              <p className="text-xs uppercase tracking-[0.2em] text-primary-foreground/80">
                खेत की महक सीधे आपके घर तक
              </p>
              <h1 className="mt-3 max-w-lg font-display text-4xl leading-[1.05] text-primary-foreground md:text-5xl">
                The farmer sets the price. You skip everyone in between.
              </h1>
              <p className="mt-4 max-w-md text-sm text-primary-foreground/85">
                KrishiSync connects 12,400 verified farms directly to households and kitchens — one
                hop, fair margins, produce picked this week.
              </p>
              <div className="mt-6">
                <Link
                  to="/market"
                  className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-medium text-primary-foreground transition-transform hover:translate-x-0.5"
                >
                  Browse today's harvest
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>

          <div className="bento-tile p-6">
            <p className="text-sm text-muted-foreground">Average farmer earning, per quintal</p>
            <p className="mt-3 font-display text-4xl text-primary">+38%</p>
            <p className="mt-2 text-sm text-muted-foreground">
              versus the same crop routed through an APMC mandi chain.
            </p>
            <div className="mt-5 flex items-center gap-2 text-sm text-foreground">
              <Banknote className="h-4 w-4 text-primary" />
              Paid within 24 hours of delivery
            </div>
          </div>

          <div className="bento-tile relative">
            <img
              src={produceBasket}
              alt="Basket of freshly harvested vegetables on linen"
              width={1024}
              height={1024}
              loading="lazy"
              className="h-44 w-full object-cover"
            />
            <div className="p-5">
              <p className="font-display text-lg">Picked, not stored</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Median 19 hours from field to doorstep.
              </p>
            </div>
          </div>
        </section>

        <section className="mt-4 grid gap-4 md:grid-cols-3">
          {[
            {
              icon: RouteIcon,
              title: "One hop, not five",
              body: "Farmer lists the lot, you order it. No commission agent, no repacker, no cold-storage markup.",
            },
            {
              icon: Clock3,
              title: "Harvest-day listings",
              body: "Every lot shows the exact village and harvest date. Nothing older than four days stays live.",
            },
            {
              icon: Truck,
              title: "Tracked dispatch",
              body: "Shared village routes keep delivery under ₹19 a crate, with live GPS on every trip.",
            },
          ].map((f) => (
            <div key={f.title} className="bento-tile p-6">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-secondary text-secondary-foreground">
                <f.icon className="h-5 w-5" />
              </span>
              <h2 className="mt-4 text-xl">{f.title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{f.body}</p>
            </div>
          ))}
        </section>

        <section className="mt-14">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-end gap-4">
            <div className="min-w-0">
              <h2 className="text-3xl">Today's harvest</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Live lots from farms within a day's drive.
              </p>
            </div>
            <Link
              to="/market"
              className="shrink-0 text-sm font-medium text-primary hover:underline"
            >
              See all
            </Link>
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {produce.slice(0, 6).map((item) => (
              <ProduceCard key={item.id} item={item} />
            ))}
          </div>
        </section>

        <section className="mt-14 grid gap-4 md:grid-cols-3">
          <div className="bento-tile md:col-span-1">
            <img
              src={farmerPortrait}
              alt="Ramesh Patil holding freshly picked produce in his field"
              width={900}
              height={1100}
              loading="lazy"
              className="h-72 w-full object-cover md:h-full"
            />
          </div>
          <div className="bento-tile flex flex-col justify-between p-7 md:col-span-2">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                Farmer of the week
              </p>
              <blockquote className="mt-4 font-display text-2xl leading-snug md:text-3xl">
                "Twelve years I sold onions at whatever rate the agent shouted. Now I open the app,
                set my rate, and 60 families buy from me every week."
              </blockquote>
              <p className="mt-4 text-sm text-muted-foreground">
                Ramesh Patil · 4.2 acres · Nashik, Maharashtra
              </p>
            </div>
            <div className="mt-8 grid grid-cols-3 gap-4 border-t border-border pt-6">
              {[
                ["₹1.9L", "earned this season"],
                ["612", "direct orders"],
                ["4.9★", "buyer rating"],
              ].map(([v, l]) => (
                <div key={l}>
                  <p className="font-display text-2xl">{v}</p>
                  <p className="text-xs text-muted-foreground">{l}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-4 grid gap-4 md:grid-cols-3">
          <div className="bento-tile relative md:col-span-2">
            <img
              src={delivery}
              alt="Crates of produce loaded into a delivery van at dawn"
              width={1200}
              height={800}
              loading="lazy"
              className="h-56 w-full object-cover md:h-64"
            />
          </div>
          <div className="bento-tile flex flex-col justify-center p-7">
            <h2 className="text-2xl">Grow with KrishiSync</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              List a lot in Hindi, Marathi or Gujarati and reach buyers directly.
            </p>
            <Link
              to="/farmer"
              className="mt-5 inline-flex items-center gap-2 self-start rounded-full border border-primary px-5 py-2.5 text-sm font-medium text-primary transition-colors hover:bg-primary hover:text-primary-foreground"
            >
              Open Farmer Desk
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
