// deryee.pro — 维护模式网关（Vercel Edge Function，零构建）
// 开关：Vercel 后台环境变量 MAINTENANCE_MODE = "true" 时进入维护，
// 任何非资产 / 非维护页自身的请求都被 307 重定向到 /maintenance/。
// 设为空或 "false" 即恢复正常运行（通常无需重新部署即生效）。

export const config = { runtime: "edge" };

export default function handler(request) {
  const on = (process.env.MAINTENANCE_MODE || "").toLowerCase() === "true";
  const url = new URL(request.url);

  // 维护关闭：原样放行，交给 Vercel 静态服务
  if (!on) return fetch(request);

  // 维护页自身 / 静态资产 / 函数自身：直接放行，避免重定向死循环
  if (
    url.pathname.startsWith("/maintenance") ||
    url.pathname.startsWith("/assets") ||
    url.pathname.startsWith("/api")
  ) {
    return fetch(request);
  }

  // 其余所有路径（含任意子地址）→ 维护页
  return Response.redirect(new URL("/maintenance/", url.origin), 307);
}
