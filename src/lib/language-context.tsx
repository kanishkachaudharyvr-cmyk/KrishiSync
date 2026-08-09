import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { type LangCode, languageByCode } from "./languages";

type Ctx = {
  lang: LangCode;
  setLang: (l: LangCode) => void;
  auto: boolean;
  setAuto: (a: boolean) => void;
};

const LanguageContext = createContext<Ctx | null>(null);

const KEY = "krishisync.lang";

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<LangCode>("en");
  const [auto, setAutoState] = useState(true);

  useEffect(() => {
    const stored = window.localStorage.getItem(KEY);
    if (stored) setLangState(languageByCode(stored).code);
    const storedAuto = window.localStorage.getItem(`${KEY}.auto`);
    if (storedAuto) setAutoState(storedAuto === "1");
  }, []);

  const value = useMemo<Ctx>(
    () => ({
      lang,
      auto,
      setLang: (l) => {
        setLangState(l);
        window.localStorage.setItem(KEY, l);
      },
      setAuto: (a) => {
        setAutoState(a);
        window.localStorage.setItem(`${KEY}.auto`, a ? "1" : "0");
      },
    }),
    [lang, auto],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used inside LanguageProvider");
  return ctx;
}
