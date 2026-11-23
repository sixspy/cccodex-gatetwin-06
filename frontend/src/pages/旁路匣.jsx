import React, { useEffect, useState } from "react";
import { 取 } from "../api.js";

export default function 旁路匣() {
  const [行, 设] = useState([]);
  const [孤儿, 设孤] = useState([]);
  const 刷 = () => {
    取("/旁路匣").then(设);
    取("/孤儿出站").then(设孤);
  };
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">旁路匣</h1>
      <p className="述">缺腿超时、出站孤儿、重复进站、未知站等旁路原因。</p>
      <div className="行"><button className="次" onClick={刷}>刷新</button></div>

      <h2 className="题" style={{ fontSize: "1rem", marginTop: "1rem" }}>
        孤儿出站只读视图（口径：当场旁路终态）
      </h2>
      <p className="讯" style={{ marginTop: 0 }}>
        无在途开腿的出站当场入匣为终态：不写行程、不造虚进、不入待配缓冲（缓冲键恒 —）。
      </p>
      {!孤儿.length ? <div className="空态">暂无孤儿出站。</div> : (
        <table>
          <thead>
            <tr><th>卡号</th><th>出站事件</th><th>处置</th><th>旁路键</th><th>缓冲键</th><th>valid</th><th>问题</th></tr>
          </thead>
          <tbody>
            {孤儿.map((r) => (
              <tr key={r.旁路键}>
                <td>{r.卡号}</td>
                <td>{r.出站事件编号}</td>
                <td>{r.处置}</td>
                <td>{r.旁路键}</td>
                <td>{r.缓冲键 ?? "—"}</td>
                <td>
                  <span className={`徽章 ${r.valid ? "通" : "败"}`}>{r.valid ? "valid" : "撕裂"}</span>
                </td>
                <td className="讯">{r.问题?.length ? r.问题.join("；") : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2 className="题" style={{ fontSize: "1rem", marginTop: "1.2rem" }}>全部旁路</h2>
      {!行.length ? <div className="空态">旁路匣空。</div> : (
        <table>
          <thead><tr><th>#</th><th>原因</th><th>卡号</th><th>事件</th><th>时刻</th><th>载荷</th></tr></thead>
          <tbody>
            {行.map((r) => (
              <tr key={r.编号}>
                <td>{r.编号}</td><td>{r.原因}</td><td>{r.卡号}</td>
                <td>{r.事件编号}</td><td>{r.时刻}</td>
                <td style={{ maxWidth: 360, wordBreak: "break-all" }}>{r.载荷}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
