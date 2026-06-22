export type LoginUser = {
  email: string;
  nickname: string;
  profile_image?: string | null;
};

export function getLoginUser(): LoginUser | null {
  if (typeof window === "undefined") return null;

  const savedUser = localStorage.getItem("user");
  if (!savedUser) return null;

  try {
    return JSON.parse(savedUser);
  } catch {
    localStorage.removeItem("user");
    return null;
  }
}

export function logout() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("user");
  window.location.href = "/";
}