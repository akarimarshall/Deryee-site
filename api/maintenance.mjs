// deryee.pro — 维护模式网关（Vercel Edge Function，零构建）
// 开关：Vercel 后台环境变量 MAINTENANCE_MODE = "true" 时进入维护，
// 任何非资产 / 非维护页自身的请求都被 307 重定向到 /maintenance/。
// 设为空或 "false" 即恢复正常运行（通常无需重新部署即生效）。
//
// 重要：维护关闭时【不能】fetch 原始 URL —— Vercel 会对函数子请求再次套用
// vercel.json 的 routes，页面路径永远命中本函数 → 508 INFINITE_LOOP_DETECTED。
// 解法：把目录式路径映射成真实文件（/about/ → /about/index.html）。
// vercel.json 的 routes 已把 .html 排除在匹配之外，该子请求直接命中静态文件，
// 物理上不可能再次进入本函数，循环被打断。

export const config = { runtime: "edge" };

export default function handler(request) {
  const on = (process.env.MAINTENANCE_MODE || "").toLowerCase() === "true";
  const url = new URL(request.url);
  const p = url.pathname;

  // 维护开启：维护页自身 / 静态资产 / 函数自身放行，其余一律 307 到维护页
  if (on) {
    if (
      p.startsWith("/maintenance") ||
      p.startsWith("/assets") ||
      p.startsWith("/api")
    ) {
      return fetch(request);
    }
    return Response.redirect(new URL("/maintenance/", url.origin), 307);
  }

  // 维护关闭：映射到真实 .html 文件（该路径被 routes 排除 → 不会循环）
  const filePath = p.endsWith("/") ? p + "index.html" : p + "/index.html";
  return fetch(new URL(filePath + url.search, url.origin));
}
