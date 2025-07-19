import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { FaHome } from "react-icons/fa";
import { MdBarChart } from "react-icons/md";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";
import isEqual from "lodash/isEqual";

// =========== LOGOS ============
const SPONSOR_LOGO_SIZE = 54;
const SPONSOR_LOGO_GAP = 28;
const SPONSOR_LOGOS = [
  { alt: "Logo 1", src: "src/logo_feec.png", bg: "#255ec2", size: 80 },
  { alt: "Logo 5", src: "src/unicamp_logo.svg", bg: "#143752" },
];

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const BUS_OPTIONS = Array.from({ length: 13 }, (_, i) => i + 1);

const MINUTE_OPTIONS = [
  1, 5, 10, 15, 30, 45,
  60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720,
  780, 840, 900, 960, 1020, 1080, 1140, 1200, 1260, 1320, 1380, 1440
];

function formatMinutes(min) {
  if (min < 60) return `${min} min`;
  if (min % 60 === 0) return `${min / 60} h`;
  return `${Math.floor(min / 60)}h ${min % 60}min`;
}

const GRAPH_CONFIGS = [
  { key: "freq", label: "Frequência (Hz)", fields: ["freq_a", "freq_b", "freq_c"], colors: ["#3e95cd", "#8e5ea2", "#3cba9f"] },
  { key: "va_rms", label: "Tensão RMS (V)", fields: ["va_rms", "vb_rms", "vc_rms"], colors: ["#fc6c85", "#fda65d", "#2dbe98"] },
  { key: "ia_rms", label: "Corrente RMS (A)", fields: ["ia_rms", "ib_rms", "ic_rms"], colors: ["#b8d9eb", "#ffc658", "#ff7300"] },
  { key: "p", label: "Potência Ativa (W)", fields: ["pa", "pb", "pc"], colors: ["#ff6f69", "#ffcc5c", "#88d8b0"] },
  { key: "q", label: "Potência Reativa (VAr)", fields: ["qa", "qb", "qc"], colors: ["#3d3d6b", "#edae49", "#d1495b"] },
  { key: "s", label: "Potência Aparente (VA)", fields: ["sa", "sb", "sc"], colors: ["#476C9B", "#ED6A5E", "#F4F1BB"] },
  { key: "pf", label: "Fator de Potência (%)", fields: ["pfa", "pfb", "pfc"], colors: ["#85C1E9", "#F7DC6F", "#F1948A"] },
  { key: "va_p", label: "Tensão P (%)", fields: ["va_p", "vb_p", "vc_p"], colors: ["#95A5A6", "#BB8FCE", "#48C9B0"] },
  { key: "va_th", label: "Tensão THD (%)", fields: ["va_th", "vb_th", "vc_th"], colors: ["#F5B041", "#7DCEA0", "#5D6D7E"] },
  { key: "ia_p", label: "Corrente P (%)", fields: ["ia_p", "ib_p", "ic_p"], colors: ["#C39BD3", "#85C1E9", "#F7DC6F"] },
  { key: "ia_th", label: "Corrente THD (%)", fields: ["ia_th", "ib_th", "ic_th"], colors: ["#F5B041", "#5DADE2", "#48C9B0"] },
];

export default function GraphPage() {
  const [selectedBus, setSelectedBus] = useState(1);
  const [selectedMinutes, setSelectedMinutes] = useState(1);
  const [data, setData] = useState([]);
  const [updateInterval, setUpdateInterval] = useState(5000);
  const [isLoading, setIsLoading] = useState(false);
  const pollingRef = useRef();
  const requestIdRef = useRef(0);
  const navigate = useNavigate();

  useEffect(() => {
    let isActive = true;
    let localRequestId = ++requestIdRef.current;
    let abortController = new AbortController();

    async function fetchDataLoop() {
      let newInterval = 5000;
      try {
        const resp = await fetch(`${API_URL}/settings/api_update_time`, { signal: abortController.signal });
        if (resp.ok) {
          const j = await resp.json();
          if (j?.value) newInterval = Number(j.value) * 1000;
        }
      } catch {}
      setUpdateInterval(newInterval);

      setIsLoading(true);
      try {
        const url = `${API_URL}/buses/${selectedBus}/measurements/lastminutes?minutes=${selectedMinutes}`;
        const resp = await fetch(url, { signal: abortController.signal });
        if (!resp.ok) throw new Error("Erro ao buscar dados do barramento");
        const arr = await resp.json();

        if (isActive && localRequestId === requestIdRef.current) {
          const nextData = arr.map(row => {
            let timeLabel;
            const date = new Date(row.timestamp);
            if (selectedMinutes < 60) {
              timeLabel = date.toLocaleTimeString("pt-BR", { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            } else {
              timeLabel = date.toLocaleTimeString("pt-BR", { hour: '2-digit', minute: '2-digit' });
            }
            return { ...row, time: timeLabel };
          });

          setData(prevData => (!isEqual(nextData, prevData) ? nextData : prevData));
        }
      } catch {
        if (isActive && localRequestId === requestIdRef.current) setData([]);
      }
      setIsLoading(false);

      pollingRef.current = setTimeout(fetchDataLoop, newInterval);
    }

    setData([]);
    fetchDataLoop();

    return () => {
      isActive = false;
      abortController.abort();
      if (pollingRef.current) clearTimeout(pollingRef.current);
      requestIdRef.current++;
    };
    // eslint-disable-next-line
  }, [selectedBus, selectedMinutes]);

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, []);

  function Carousel({ options, value, setValue, label, labelFn }) {
    const idx = options.indexOf(value);
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontWeight: 600, color: "#255ec2" }}>{label}</span>
        <button
          onClick={() => setValue(options[Math.max(0, idx - 1)])}
          disabled={idx === 0}
          style={{ fontSize: 18, border: "none", background: "#eee", borderRadius: 6, padding: "0 8px", cursor: "pointer" }}
        >‹</button>
        <span style={{ fontSize: 19, minWidth: 55, display: "inline-block", textAlign: "center" }}>{labelFn ? labelFn(value) : value}</span>
        <button
          onClick={() => setValue(options[Math.min(options.length - 1, idx + 1)])}
          disabled={idx === options.length - 1}
          style={{ fontSize: 18, border: "none", background: "#eee", borderRadius: 6, padding: "0 8px", cursor: "pointer" }}
        >›</button>
      </div>
    );
  }

  function xTickFormatter(time) {
    return time;
  }

  const graphContainerStyle = {
    background: "#fff",
    borderRadius: 12,
    padding: "16px 18px 8px 16px",
    boxShadow: "0 2.5px 10px #0001",
    width: "97vw",
    maxWidth: 900,
    minWidth: 280,
    minHeight: 240,
    marginBottom: 18,
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    boxSizing: "border-box",
    transition: "opacity 0.3s",
    opacity: isLoading ? 0.55 : 1,
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        overflowY: "auto",
        overflowX: "hidden",
        background: "#f4f7fb",
        display: "flex",
        flexDirection: "column",
        boxSizing: "border-box",
        zIndex: 100
      }}
    >
      <div
        style={{
          width: "100%",
          background: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1.5px solid #dde5ef",
          minHeight: 70,
          padding: "0 16px",
          position: "sticky", top: 0, zIndex: 10,
          boxSizing: "border-box"
        }}
      >
        <span style={{
          fontSize: 26,
          fontWeight: 700,
          color: "#183d74"
        }}>
          Gráficos do Barramento
        </span>
        <button
          style={{
            border: "none",
            background: "none",
            cursor: "pointer",
            padding: 8,
            borderRadius: 8,
            display: "flex",
            alignItems: "center",
            fontWeight: 600,
            color: "#183d74",
            fontSize: 17,
            marginLeft: 24
          }}
          title="Voltar para o painel"
          onClick={() => navigate("/")}
        >
          <FaHome size={21} style={{ marginRight: 7 }} />
          Home
        </button>
      </div>
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: 26,
        justifyContent: "center",
        margin: "34px 0 10px 0"
      }}>
        <Carousel options={BUS_OPTIONS} value={selectedBus} setValue={setSelectedBus} label="Barramento" />
        <Carousel
          options={MINUTE_OPTIONS}
          value={selectedMinutes}
          setValue={setSelectedMinutes}
          label="Período"
          labelFn={formatMinutes}
        />
        <div style={{
          background: "#fff", borderRadius: 5, padding: "2px 16px", marginLeft: 32,
          boxShadow: "0 1.5px 5px #0001", fontWeight: 500, fontSize: 16, color: "#183d74"
        }}>
          Atualiza a cada {updateInterval / 1000}s
        </div>
      </div>
      <div style={{
        display: "flex",
        flexDirection: "column",
        gap: 32,
        padding: "24px 0 38px 0",
        width: "100vw",
        maxWidth: "100vw",
        boxSizing: "border-box",
        alignItems: "center"
      }}>
        {GRAPH_CONFIGS.map(({ key, label, fields, colors }) => (
          <div key={key} style={graphContainerStyle}>
            <div style={{ fontWeight: 700, color: "#183d74", marginBottom: 4, fontSize: 18, display: "flex", alignItems: "center" }}>
              <MdBarChart size={23} color={colors[0]} style={{ marginRight: 8 }} />
              {label}
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={data}>
                <CartesianGrid stroke="#e0e0e0" strokeDasharray="5 5" />
                <XAxis
                  dataKey="time"
                  minTickGap={selectedMinutes < 60 ? 25 : 12}
                  fontSize={12}
                  tickFormatter={xTickFormatter}
                  interval="preserveEnd"
                  angle={selectedMinutes < 60 ? -15 : 0}
                  height={selectedMinutes < 60 ? 40 : 30}
                />
                <YAxis fontSize={12} />
                <Tooltip />
                <Legend />
                {fields.map((f, idx) =>
                  <Line
                    key={f}
                    type="monotone"
                    dataKey={f}
                    stroke={colors[idx]}
                    strokeWidth={2}
                    dot={false}
                    isAnimationActive={true}
                    animationDuration={600}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ))}
      </div>
      {/* Logos dos patrocinadores */}
      <div
        style={{
          width: "100%",
          padding: "18px 0 30px 0",
          background: "#fff",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: `${SPONSOR_LOGO_GAP}px`,
          borderTop: "1.5px solid #dde5ef"
        }}
      >
        {SPONSOR_LOGOS.map((logo, i) =>
          logo.src ? (
            <img
              key={i}
              src={logo.src}
              alt={logo.alt}
              style={{
                width: logo.size || SPONSOR_LOGO_SIZE,
                height: logo.size || SPONSOR_LOGO_SIZE,
                objectFit: "contain"
              }}
            />
          ) : (
            <div
              key={i}
              style={{
                width: logo.size || SPONSOR_LOGO_SIZE,
                height: logo.size || SPONSOR_LOGO_SIZE,
                background: logo.bg,
                borderRadius: 12,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontWeight: "bold",
                fontSize: 22,
                border: "1.5px solid #e3e9f3",
                boxShadow: "0 1.5px 5px #0001"
              }}
            >
              {i + 1}
            </div>
          )
        )}
      </div>
    </div>
  );
}
