"use client";

import { useEffect, useState, useRef } from "react";
import { Globe } from "lucide-react";

const languages = [
  { code: "en", name: "English" },
  { code: "hi", name: "Hindi" },
  { code: "bn", name: "Bengali" },
  { code: "te", name: "Telugu" },
  { code: "mr", name: "Marathi" },
  { code: "ta", name: "Tamil" },
  { code: "ur", name: "Urdu" },
  { code: "gu", name: "Gujarati" },
  { code: "kn", name: "Kannada" },
  { code: "or", name: "Odia" },
  { code: "ml", name: "Malayalam" },
  { code: "pa", name: "Punjabi" },
];

const GoogleTranslate = () => {
  const [isMounted, setIsMounted] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsMounted(true);
    
    // Set up the initialization callback
    (window as any).googleTranslateElementInit = () => {
      if ((window as any).google && (window as any).google.translate) {
        new (window as any).google.translate.TranslateElement(
          {
            pageLanguage: "en",
            includedLanguages: languages.map(l => l.code).join(","),
            autoDisplay: false,
          },
          "google_translate_element"
        );
      }
    };

    // Check if the script is already loaded
    if (!document.getElementById("google-translate-script")) {
      const script = document.createElement("script");
      script.id = "google-translate-script";
      script.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
      script.async = true;
      document.body.appendChild(script);
    }

    // Close dropdown on click outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!isMounted) return null;

  const handleLanguageChange = (code: string) => {
    const selectElement = document.querySelector(".goog-te-combo") as HTMLSelectElement;
    if (selectElement) {
      selectElement.value = code;
      selectElement.dispatchEvent(new Event("change", { bubbles: true }));
      setIsOpen(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[9999]" ref={dropdownRef}>
      {/* Hidden original widget */}
      <div id="google_translate_element" className="hidden opacity-0 w-0 h-0 overflow-hidden"></div>

      {isOpen && (
        <div className="absolute bottom-16 right-0 mb-2 w-48 bg-white dark:bg-[#0f172a] rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800 overflow-hidden glass-panel">
          <div className="max-h-64 overflow-y-auto">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className="w-full text-left px-4 py-3 text-sm text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-[#1e293b] transition-colors first:rounded-t-xl last:rounded-b-xl"
              >
                {lang.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 bg-primary hover:bg-primary/90 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-110 active:scale-95 border-2 border-white/20"
        aria-label="Select Language"
        title="Translate"
      >
        <Globe className="w-6 h-6" />
      </button>
    </div>
  );
};

export default GoogleTranslate;
