import Cookies from "js-cookie";

const ACCESS_KEY = "ctmsn_access_token";
const REFRESH_KEY = "ctmsn_refresh_token";

const COOKIE_OPTS: Cookies.CookieAttributes = {
  sameSite: "strict",
  path: "/",
};

export function getAccessToken(): string | undefined {
  return Cookies.get(ACCESS_KEY);
}

export function getRefreshToken(): string | undefined {
  return Cookies.get(REFRESH_KEY);
}

export function setTokens(access: string, refresh: string): void {
  Cookies.set(ACCESS_KEY, access, COOKIE_OPTS);
  Cookies.set(REFRESH_KEY, refresh, COOKIE_OPTS);
}

export function clearTokens(): void {
  Cookies.remove(ACCESS_KEY, { path: "/" });
  Cookies.remove(REFRESH_KEY, { path: "/" });
}
