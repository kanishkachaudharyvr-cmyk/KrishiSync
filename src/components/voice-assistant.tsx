import { useNavigate } from "@tanstack/react-router";
import { Loader2, Mic, Square, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { useLanguage } from "@/lib/language-context";
import { languageByCode, languages, t } from "@/lib/languages";
import { useRole } from "@/lib/role-context";
import { produce, type Produce } from "@/data/market";
import { encodeWav } from "@/lib/wav";

type Status = "idle" | "recording" | "thinking";

function matchProduce(query: string): Produce[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return produce.filter((p) =>
    `${p.name} ${p.local} ${p.category} ${p.farmer} ${p.village}`.toLowerCase().includes(q),
  );
}

export function VoiceAssistant() {
  const { lang, auto, setLang, setAuto } = useLanguage();
  const { setRole } = useRole();
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [transcript, setTranscript] = useState("");
  const [reply, setReply] = useState("");
  const [error, setError] = useState("");
  const [matches, setMatches] = useState<Produce[]>([]);

  const ctxRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const nodeRef = useRef<ScriptProcessorNode | null>(null);
  const chunksRef = useRef<Float32Array[]>([]);

  const cleanup = useCallback(() => {
    nodeRef.current?.disconnect();
    nodeRef.current = null;
    streamRef.current?.getTracks().forEach((tr) => tr.stop());
    streamRef.current = null;
    void ctxRef.current?.close();
    ctxRef.current = null;
  }, []);

  const start = useCallback(async () => {
    setError("");
    setTranscript("");
    setReply("");
    setMatches([]);
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
      });
    } catch {
      setError(t(lang, "micError"));
      return;
    }
    const AudioCtx =
      window.AudioContext ??
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = new AudioCtx();
    const source = ctx.createMediaStreamSource(stream);
    const node = ctx.createScriptProcessor(4096, 1, 1);
    chunksRef.current = [];
    node.onaudioprocess = (e) => {
      chunksRef.current.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    };
    source.connect(node);
    node.connect(ctx.destination);

    ctxRef.current = ctx;
    streamRef.current = stream;
    nodeRef.current = node;
    setStatus("recording");
  }, [lang]);

  const stop = useCallback(async () => {
    const ctx = ctxRef.current;
    const rate = ctx?.sampleRate ?? 48000;
    const chunks = chunksRef.current;
    cleanup();
    setStatus("thinking");

    const blob = encodeWav(chunks, rate);
    if (blob.size < 4096) {
      setStatus("idle");
      setError(t(lang, "tryAgain"));
      return;
    }

    const body = new FormData();
    body.append("file", blob, "recording.wav"); // FastAPI expects "file" parameter
    if (!auto) body.append("lang", languageByCode(lang).iso);
    body.append("replyLanguage", languageByCode(lang).label);

    try {
      const res = await fetch("/api/voice", { 
        method: "POST",
        headers: {
          "X-Farmer-ID": "1" // Scopes request to seeded mock farmer
        },
        body 
      });
      const data = (await res.json()) as {
        error?: string;
        transcript?: string;
        reply?: string;
        action?: { type: string; to?: string; query?: string };
      };
      if (!res.ok) {
        setError(data.error ?? t(lang, "tryAgain"));
        setStatus("idle");
        return;
      }
      setTranscript(data.transcript ?? "");
      setReply(data.reply ?? "");
      setStatus("idle");

      const action = data.action;
      const query = action?.query ?? "";
      if (action?.type === "search") {
        setMatches(matchProduce(query));
        setRole("customer");
        void navigate({ to: "/market", search: { q: query, intent: "buy" } });
      } else if (action?.type === "sell") {
        setMatches([]);
        setRole("farmer");
        void navigate({ to: "/farmer", search: { action: "list" } });
      } else if (action?.type === "settings") {
        setMatches([]);
        void navigate({ to: "/settings" });
      } else if (action?.type === "navigate" && action.to) {
        setMatches([]);
        const to = action.to;
        if (to === "/market") void navigate({ to, search: { q: "" } });
        else if (to === "/farmer") void navigate({ to, search: {} });
        else if (to === "/settings") void navigate({ to });
        else void navigate({ to: "/" });
      } else {
        setMatches([]);
      }
    } catch {
      setError(t(lang, "tryAgain"));
      setStatus("idle");
    }
  }, [auto, cleanup, lang, navigate, setRole]);

  return (
    <>
      {open && (
        <div className="fixed bottom-24 right-4 z-50 w-[min(22rem,calc(100vw-2rem))] rounded-2xl border border-border bg-card p-5 shadow-xl">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-display text-lg leading-tight">{t(lang, "title")}</p>
              <p className="text-xs text-muted-foreground">{t(lang, "hint")}</p>
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label="Close voice assistant"
              className="rounded-full p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-4">
            <label
              htmlFor="assistant-lang"
              className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
            >
              {t(lang, "language")}
            </label>
            <select
              id="assistant-lang"
              value={lang}
              onChange={(e) => setLang(e.target.value as typeof lang)}
              className="mt-1.5 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground"
            >
              {languages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.native} · {l.label}
                </option>
              ))}
            </select>
            <label className="mt-2.5 flex items-center gap-2 text-xs text-muted-foreground">
              <input
                type="checkbox"
                checked={auto}
                onChange={(e) => setAuto(e.target.checked)}
                className="h-3.5 w-3.5 accent-current"
              />
              {t(lang, "autoDetect")}
            </label>
          </div>

          <div className="mt-4 flex items-center gap-3">
            <button
              onClick={() => (status === "recording" ? void stop() : void start())}
              disabled={status === "thinking"}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-60"
            >
              {status === "thinking" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : status === "recording" ? (
                <Square className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
              {status === "thinking"
                ? t(lang, "thinking")
                : status === "recording"
                  ? t(lang, "tapToStop")
                  : t(lang, "tapToSpeak")}
            </button>
            {status === "recording" && (
              <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="h-2 w-2 animate-pulse rounded-full bg-destructive" />
                {t(lang, "listening")}
              </span>
            )}
          </div>

          {error && <p className="mt-3 text-sm text-destructive">{error}</p>}

          {transcript && (
            <div className="mt-4 rounded-xl bg-secondary/60 p-3">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">
                {t(lang, "you")}
              </p>
              <p className="mt-1 text-sm text-foreground">{transcript}</p>
            </div>
          )}
          {reply && <p className="mt-3 text-sm leading-relaxed text-foreground">{reply}</p>}

          {matches.length > 0 && (
            <ul className="mt-3 max-h-56 space-y-2 overflow-y-auto">
              {matches.map((m) => (
                <li
                  key={m.id}
                  className="flex items-center gap-3 rounded-xl border border-border bg-background p-2.5"
                >
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-accent text-base">
                    {m.emoji}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-medium">
                      {m.name} · {m.local}
                    </span>
                    <span className="block text-xs text-muted-foreground">
                      ₹{m.price}/{m.unit} · {m.farmer}, {m.village}
                    </span>
                  </span>
                  <button
                    onClick={() => {
                      setOpen(false);
                      void navigate({ to: "/market", search: { q: m.name, intent: "buy" } });
                    }}
                    className="shrink-0 rounded-full bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
                  >
                    Buy
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        aria-label={t(lang, "title")}
        className="fixed bottom-5 right-4 z-50 grid h-14 w-14 place-items-center rounded-full bg-primary text-primary-foreground shadow-lg transition-transform hover:scale-105"
      >
        <Mic className="h-6 w-6" />
      </button>
    </>
  );
}
