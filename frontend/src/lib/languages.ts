export type LangCode = "en" | "hi" | "mr" | "gu";

export const languages = [
  { code: "en" as const, iso: "en", label: "English", native: "English" },
  { code: "hi" as const, iso: "hi", label: "Hindi", native: "हिन्दी" },
  { code: "mr" as const, iso: "mr", label: "Marathi", native: "मराठी" },
  { code: "gu" as const, iso: "gu", label: "Gujarati", native: "ગુજરાતી" }
];

export function languageByCode(code: string) {
  return languages.find(l => l.code === code) || languages[0];
}

const dict: Record<string, Record<string, string>> = {
  en: {
    title: "KrishiSync Voice Assistant",
    hint: "Tap the mic and speak in any language...",
    micError: "Microphone permission denied.",
    tryAgain: "I didn't catch that. Please speak again.",
    thinking: "Analyzing your voice...",
    tapToStop: "Tap to stop",
    tapToSpeak: "Tap to speak",
    listening: "Listening...",
    you: "You said:"
  },
  hi: {
    title: "कृषिसिंक वॉइस असिस्टेंट",
    hint: "माइक दबाकर किसी भी भाषा में बोलें...",
    micError: "माइक एक्सेस की अनुमति नहीं है।",
    tryAgain: "समझ नहीं आया। कृपया दोबारा बोलें।",
    thinking: "आपके वॉइस का विश्लेषण हो रहा है...",
    tapToStop: "रुकने के लिए दबाएं",
    tapToSpeak: "बोलने के लिए दबाएं",
    listening: "सुन रहा हूँ...",
    you: "आपने कहा:"
  },
  mr: {
    title: "कृषिसिंक व्हॉइस असिस्टंट",
    hint: "माईक दाबा आणि कोणत्याही भाषेत बोला...",
    micError: "माईक प्रवेशास परवानगी नाकारली.",
    tryAgain: "समजले नाही. कृपया पुन्हा बोला.",
    thinking: "तुमच्या आवाजाचे विश्लेषण चालू आहे...",
    tapToStop: "थांबण्यासाठी दाबा",
    tapToSpeak: "बोलण्यासाठी दाबा",
    listening: "ऐकत आहे...",
    you: "तुम्ही म्हणालात:"
  },
  gu: {
    title: "કૃષિસિંક વોઇસ આસિસ્ટન્ટ",
    hint: "માઇક દબાવો અને કોઈપણ ભાષામાં બોલો...",
    micError: "માઇક પ્રવેશની પરવાનગી નકારી.",
    tryAgain: "સમજાયું નથી. કૃપા કરીને ફરીથી બોલો.",
    thinking: "તમારા અવાજનું વિશ્લેષણ થઈ રહ્યું છે...",
    tapToStop: "રોકવા માટે દબાવો",
    tapToSpeak: "બોલવા માટે દબાવો",
    listening: "સાંભળી રહ્યો છે...",
    you: "તમે કહ્યું:"
  }
};

export function t(lang: LangCode, key: string): string {
  return dict[lang]?.[key] || dict["en"]?.[key] || key;
}
