import { useLanguage } from "@/lib/language-context";
import { languages } from "@/lib/languages";
import { Languages } from "lucide-react";

export function LanguageSwitcher({ className }: { className?: string }) {
  const { lang, setLang } = useLanguage();
  return (
    <div className={`flex items-center gap-1 bg-secondary rounded-full px-2 py-1 ${className}`}>
      <Languages className="h-3.5 w-3.5 text-muted-foreground ml-1" />
      <select
        value={lang}
        onChange={(e) => setLang(e.target.value as any)}
        className="bg-transparent text-xs text-foreground outline-none cursor-pointer pr-1"
      >
        {languages.map(l => (
          <option key={l.code} value={l.code}>
            {l.native}
          </option>
        ))}
      </select>
    </div>
  );
}
