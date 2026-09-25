"use client";
import { useCallback, useSyncExternalStore } from "react";
const eventName = "dgn-session-change";
function subscribe(listener: () => void) {
  window.addEventListener("storage", listener);
  window.addEventListener(eventName, listener);
  return () => { window.removeEventListener("storage", listener); window.removeEventListener(eventName, listener); };
}
export function useStoredValue(key: string, fallback = ""): [string, (value: string) => void] {
  const value = useSyncExternalStore(subscribe, () => localStorage.getItem(key) ?? fallback, () => fallback);
  const setValue = useCallback((next: string) => {
    if (next) localStorage.setItem(key, next); else localStorage.removeItem(key);
    window.dispatchEvent(new Event(eventName));
  }, [key]);
  return [value, setValue];
}
