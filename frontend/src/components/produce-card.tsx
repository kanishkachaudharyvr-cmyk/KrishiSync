import { MapPin, Sprout } from "lucide-react";
import type { Produce } from "@/data/market";

export function ProduceCard({ item }: { item: Produce }) {
  const saving = Math.round(((item.mandiPrice - item.price) / item.mandiPrice) * 100);

  return (
    <article className="bento-tile flex flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-lg leading-tight">{item.name}</h3>
          <p className="text-sm text-muted-foreground">{item.local}</p>
        </div>
        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-accent text-xl">
          {item.emoji}
        </span>
      </div>

      <div className="mt-4 space-y-1.5 text-sm text-muted-foreground">
        <p className="flex items-center gap-1.5">
          <Sprout className="h-3.5 w-3.5 shrink-0 text-primary" />
          <span className="truncate">{item.farmer}</span>
        </p>
        <p className="flex items-center gap-1.5">
          <MapPin className="h-3.5 w-3.5 shrink-0 text-primary" />
          <span className="truncate">
            {item.village} · harvested {item.harvested.toLowerCase()}
          </span>
        </p>
      </div>

      <div className="mt-5 flex items-end justify-between gap-3 border-t border-border pt-4">
        <div>
          <p className="font-display text-2xl">
            ₹{item.price}
            <span className="ml-1 text-sm text-muted-foreground">/ {item.unit}</span>
          </p>
          <p className="text-xs text-muted-foreground">
            <span className="line-through">₹{item.mandiPrice}</span> in mandi · save {saving}%
          </p>
        </div>
        <button className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
          Add
        </button>
      </div>
    </article>
  );
}
