import { Link } from "@tanstack/react-router";
import { Leaf, Settings, ShoppingBasket, Sprout } from "lucide-react";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useRole } from "@/lib/role-context";

const links = [
  { to: "/", label: "Home" },
  { to: "/market", label: "Market" },
  { to: "/farmer", label: "Farmer Desk" },
] as const;

export function SiteHeader() {
  const { role } = useRole();

  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-5 py-3.5">
        <Link to="/" className="flex min-w-0 items-center gap-2.5">
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground">
            <Leaf className="h-4.5 w-4.5" />
          </span>
          <span className="truncate font-display text-xl tracking-tight">KrishiSync</span>
        </Link>

        <nav className="flex flex-wrap items-center gap-1 sm:gap-2">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              activeOptions={{ exact: l.to === "/" }}
              className="rounded-full px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              activeProps={{ className: "bg-secondary text-foreground" }}
            >
              {l.label}
            </Link>
          ))}

          <LanguageSwitcher className="ml-1" />

          <Link
            to="/settings"
            aria-label="Settings"
            className="rounded-full p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            activeProps={{ className: "bg-secondary text-foreground" }}
          >
            <Settings className="h-4 w-4" />
          </Link>

          {role === "farmer" ? (
            <Link
              to="/farmer"
              search={{ action: "list" }}
              className="ml-1 hidden items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 sm:inline-flex"
            >
              <Sprout className="h-4 w-4" />
              Sell
            </Link>
          ) : (
            <Link
              to="/market"
              search={{ q: "" }}
              className="ml-1 hidden items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 sm:inline-flex"
            >
              <ShoppingBasket className="h-4 w-4" />
              Basket
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-border/70 py-10">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-5 text-sm text-muted-foreground">
        <p>KrishiSync — खेत से सीधे घर तक.</p>
        <p>Fair price for the farmer. Fresh price for you.</p>
      </div>
    </footer>
  );
}
