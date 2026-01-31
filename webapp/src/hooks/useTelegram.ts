import { useEffect, useState } from "react";
import { getTelegram, isTelegramWebApp, TelegramWebApp } from "@/lib/telegram";

export function useTelegram() {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const tg = getTelegram();
    if (tg) {
      tg.ready();
      tg.expand();
      setWebApp(tg);
      setIsReady(true);

      // Apply Telegram theme
      if (tg.colorScheme === "dark") {
        document.documentElement.classList.add("dark");
      }
    } else {
      // Running outside Telegram - still mark as ready for development
      setIsReady(true);
    }
  }, []);

  return {
    webApp,
    isReady,
    isTelegram: isTelegramWebApp(),
    user: webApp?.initDataUnsafe?.user,
    colorScheme: webApp?.colorScheme || "light",
    themeParams: webApp?.themeParams,
    haptic: webApp?.HapticFeedback,
  };
}
