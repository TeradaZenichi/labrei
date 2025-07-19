import { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { FiSettings, FiBarChart2 } from "react-icons/fi";
import './App.css';
import LabreiSVG from './labrei.svg?react';

// =========== LOGOS ============
const SPONSOR_LOGO_SIZE = 54;
const SPONSOR_LOGO_GAP = 28;
const SPONSOR_LOGOS = [
  { alt: "Logo 1", src: "src/logo_feec.png", bg: "#255ec2", size: 80 }, // maior
  // { alt: "Logo 2", src: null, bg: "#ffc700" },
  // { alt: "Logo 3", src: null, bg: "#31d573" },
  // { alt: "Logo 4", src: null, bg: "#fe4e38" },
  { alt: "Logo 5", src: "src/unicamp_logo.svg", bg: "#143752" }, // padrão
];

// =====================
// SIMULAÇÃO DE DADOS INICIAIS
// =====================
const NUM_BARRAMENTOS = 13;
const DADOS_INICIAIS = Array.from({ length: NUM_BARRAMENTOS }, (_, i) => ({
  id: i + 1,
  tensao: { A: "-", B: "-", C: "-" },
  corrente: { A: "-", B: "-", C: "-" },
  P: { A: "-", B: "-", C: "-" },
  Q: { A: "-", B: "-", C: "-" }
}));

// ========== URL BASE DA API ===========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const svgWrapperRef = useRef(null);
  const svgRef = useRef(null);
  const [positions, setPositions] = useState([]);
  const [barramentos, setBarramentos] = useState(DADOS_INICIAIS);
  const [updateInterval, setUpdateInterval] = useState(5000); // em ms, só serve para mostrar na tela
  const pollingRef = useRef();
  const navigate = useNavigate();

  // Busca dados dos barramentos
  const fetchAllBuses = useCallback(async () => {
    try {
      const results = await Promise.all(
        Array.from({ length: NUM_BARRAMENTOS }, (_, i) => {
          const url = `${API_URL}/buses/${i + 1}/measurements/last`;
          return fetch(url)
            .then(resp => {
              if (!resp.ok) throw new Error(`Erro ao buscar bus ${i + 1}`);
              return resp.json();
            })
            .catch(e => {
              console.error(`[API] Erro no barramento ${i + 1}:`, e);
              return null;
            });
        })
      );
      const dados = results.map((d, i) => {
        if (!d) return DADOS_INICIAIS[i];
        return {
          id: d.bus_id,
          tensao: { A: d.va_rms, B: d.vb_rms, C: d.vc_rms },
          corrente: { A: d.ia_rms, B: d.ib_rms, C: d.ic_rms },
          P: { A: d.pa, B: d.pb, C: d.pc },
          Q: { A: d.qa, B: d.qb, C: d.qc }
        };
      });
      setBarramentos(dados);
    } catch (e) {
      console.error("Falha ao buscar dados dos barramentos:", e);
    }
  }, []);

  // Polling AUTOMÁTICO que busca o novo intervalo da API SEMPRE!
  useEffect(() => {
    let cancelled = false;
    async function poll() {
      if (cancelled) return;
      // 1. Busca intervalo da API
      let newInterval = 5000;
      try {
        const url = `${API_URL}/settings/api_update_time`;
        const resp = await fetch(url);
        if (resp.ok) {
          const data = await resp.json();
          if (data?.value) newInterval = Number(data.value) * 1000;
        }
      } catch (e) {
        // Se der erro, mantém padrão
      }
      setUpdateInterval(newInterval); // atualiza valor exibido na tela

      // 2. Busca os dados dos barramentos
      await fetchAllBuses();

      // 3. Agenda novo ciclo
      pollingRef.current = setTimeout(poll, newInterval);
    }
    poll();
    return () => {
      cancelled = true;
      clearTimeout(pollingRef.current);
    };
  }, [fetchAllBuses]);

  // POSICIONAMENTO ABSOLUTO COMO NO ORIGINAL
  useEffect(() => {
    function updatePositions() {
      if (!svgRef.current || !svgWrapperRef.current) return;
      const svg = svgRef.current;
      const viewBox = svg.viewBox.baseVal;
      const { width: vbW } = viewBox;

      const wrapperRect = svgWrapperRef.current.getBoundingClientRect();

      const scale = (wrapperRect.width * 0.9) / vbW;
      const svgDisplayWidth = vbW * scale;

      const offsetX = (wrapperRect.width - svgDisplayWidth) / 2;
      const offsetY = 0;

      const positions = barramentos.map((b) => {
        const busEl = svg.getElementById
          ? svg.getElementById(`bus${b.id}`)
          : svg.querySelector(`#bus${b.id}`);
        if (!busEl) return null;
        const bbox = busEl.getBBox();
        const cx = bbox.x + bbox.width / 2;
        const cy = bbox.y + bbox.height + 14;

        return {
          id: b.id,
          left: offsetX + cx * scale - (35 * scale) / 2,
          top: offsetY + cy * scale,
          width: 35 * scale,
          height: 63 * scale
        };
      });
      setPositions(positions);
    }
    updatePositions();
    window.addEventListener("resize", updatePositions);
    return () => window.removeEventListener("resize", updatePositions);
  }, [barramentos]);

  useEffect(() => {
    setTimeout(() => {
      if (svgRef.current) window.dispatchEvent(new Event("resize"));
    }, 100);
  }, []);

  return (
    <div
      style={{
        width: "95%",
        height: "100%",
        overflow: "hidden",
        background: "#eee",
        display: "flex",
        flexDirection: "column",
        position: "relative",
      }}
    >
      {/* Cabeçalho */}
      <div style={{ flex: "0 0 auto", position: "relative" }}>
        <h1
          style={{
            textAlign: "center",
            margin: 0,
            padding: "18px 0 8px 0",
            fontSize: "2rem",
            background: "#fff",
            height: 64,
            lineHeight: `64px`
          }}
        >
          Aplicativo de Monitoramento do LabREI
        </h1>
        {/* Botão de Gráfico (esquerda do Settings) */}
        <button
          style={{
            position: "absolute",
            right: 90,
            top: "60%",
            transform: "translateY(-50%)",
            background: "none",
            border: "none",
            cursor: "pointer",
            padding: 0,
            zIndex: 10
          }}
          onClick={() => navigate("/graph")}
          aria-label="Gráficos"
          title="Gráficos"
        >
          <FiBarChart2 size={32} color="#337ab7" />
        </button>
        {/* Botão de Configurações */}
        <button
          style={{
            position: "absolute",
            right: 40,
            top: "60%",
            transform: "translateY(-50%)",
            background: "none",
            border: "none",
            cursor: "pointer",
            padding: 0,
            zIndex: 10
          }}
          onClick={() => navigate("/config")}
          aria-label="Configurações"
          title="Configurações"
        >
          <FiSettings size={32} color="#337ab7" />
        </button>
      </div>

      {/* Região central ajustável */}
      <div
        ref={svgWrapperRef}
        style={{
          flex: "1 1 0%",
          minHeight: 0,
          minWidth: 0,
          position: "relative",
          width: "100%",
          height: "100%",
          background: "#eee",
          overflow: "hidden",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          paddingLeft: 0,
          paddingRight: 0,
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            position: "relative",
            overflow: "hidden"
          }}
        >
          {/* Indicador de atualização */}
          <div style={{
            position: 'absolute',
            top: 5,
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#fff',
            padding: '4px 10px',
            borderRadius: '4px',
            fontSize: '0.9rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
            zIndex: 5
          }}>
            Intervalo de atualização: {updateInterval / 1000}s
          </div>
          <div
            style={{
              width: `90%`,
              height: "auto",
              position: "absolute",
              left: "40%",
              top: "20%",
              transform: "translate(-40%, -50%)",
              display: "block"
            }}
          >
            <LabreiSVG
              ref={svgRef}
              style={{
                width: "100%",
                height: "auto",
                display: "block",
                objectFit: "contain"
              }}
              preserveAspectRatio="xMidYMid meet"
            />
            {/* Boxes com posição/tamanho ABSOLUTOS */}
            {positions.map((pos, idx) =>
              pos ? (
                <div
                  key={pos.id}
                  style={{
                    position: "absolute",
                    left: `${pos.left - 80}px`,
                    top: `${pos.top - 10}px`,
                    width: `${pos.width + 20}px`,
                    height: `${pos.height + 55}px`,
                    border: `2px solid #337ab7`,
                    borderRadius: `6px`,
                    background: "#fafdffea",
                    color: "#143752",
                    fontFamily: "sans-serif",
                    fontWeight: 500,
                    boxShadow: "0 1.5px 5px #0002",
                    padding: `${2 * (pos.height / 63)}px ${2 * (pos.width / 35)}px`,
                    boxSizing: "border-box",
                    zIndex: 2,
                    fontSize: `${4.9 * (pos.width / 35)}px`,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    justifyContent: "center",
                    textAlign: "left",
                    lineHeight: 1.12,
                    overflow: "hidden"
                  }}
                >
                  <b style={{ marginBottom: 2, fontSize: `${1.1 * 100}%`, width: "100%" }}>
                    B{pos.id}
                  </b>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>V<sub>A</sub>:</span><span>{barramentos[idx].tensao.A} V</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>V<sub>B</sub>:</span><span>{barramentos[idx].tensao.B} V</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>V<sub>C</sub>:</span><span>{barramentos[idx].tensao.C} V</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>I<sub>A</sub>:</span><span>{barramentos[idx].corrente.A} A</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>I<sub>B</sub>:</span><span>{barramentos[idx].corrente.B} A</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>I<sub>C</sub>:</span><span>{barramentos[idx].corrente.C} A</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>P<sub>A</sub>:</span><span>{barramentos[idx].P.A} W</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>P<sub>B</sub>:</span><span>{barramentos[idx].P.B} W</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>P<sub>C</sub>:</span><span>{barramentos[idx].P.C} W</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>Q<sub>A</sub>:</span><span>{barramentos[idx].Q.A} VAr</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>Q<sub>B</sub>:</span><span>{barramentos[idx].Q.B} VAr</span></div>
                  <div style={{ display: "flex" }}><span style={{ minWidth: 33, display: "inline-block" }}>Q<sub>C</sub>:</span><span>{barramentos[idx].Q.C} VAr</span></div>
                </div>
              ) : null
            )}
          </div>
        </div>
      </div>

      {/* Logos dos patrocinadores */}
      <div
        style={{
          flex: "0 0 auto",
          width: "100%",
          padding: "20px 0 50px 0",
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

export default App;
