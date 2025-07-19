import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import React from "react";
import { FaHome } from "react-icons/fa";

// =========== LOGOS ============
const SPONSOR_LOGO_SIZE = 54;
const SPONSOR_LOGO_GAP = 28;
const SPONSOR_LOGOS = [
  { alt: "Logo 1", src: null, bg: "#255ec2" },
  { alt: "Logo 2", src: null, bg: "#ffc700" },
  { alt: "Logo 3", src: null, bg: "#31d573" },
  { alt: "Logo 4", src: null, bg: "#fe4e38" },
  { alt: "Logo 5", src: null, bg: "#143752" },
];

// ========== URL BASE DA API ===========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ========== CHAVES E RÓTULOS ==========
const CONFIG_KEYS = [
  { key: "COMPRESS_AFTER_HOURS", label: "Comprimir após (h)" },
  { key: "RETENTION_DAYS", label: "Dias de Retenção" },
  { key: "RUN_INTERVAL_HOURS", label: "Intervalo da Rotina (h)" },
  { key: "api_update_time", label: "Intervalo API (s)" },
  { key: "modbus_update_time", label: "Intervalo Modbus (s)" },
];

export default function ConfigPage() {
  const [configs, setConfigs] = useState([]);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");
  const navigate = useNavigate();

  // Busca configs ao montar
  useEffect(() => {
    async function fetchConfigs() {
      try {
        const resp = await fetch(`${API_URL}/settings`);
        if (!resp.ok) throw new Error("Erro ao buscar configs");
        const arr = await resp.json();
        setConfigs(arr);
      } catch (e) {
        setStatus("Falha ao carregar configurações.");
        setConfigs(CONFIG_KEYS.map(item => ({ key: item.key, value: "" })));
      }
    }
    fetchConfigs();
  }, []);

  // Atualiza valor localmente
  function handleChange(idx, value) {
    setConfigs(cfgs =>
      cfgs.map((c, i) => (i === idx ? { ...c, value } : c))
    );
  }

  // Salva todas configs
  async function handleSave() {
    setSaving(true);
    setStatus("");
    try {
      for (let i = 0; i < CONFIG_KEYS.length; i++) {
        const k = CONFIG_KEYS[i].key;
        const v = configs.find(c => c.key === k)?.value ?? "";
        const url = `${API_URL}/settings/${k}?value=${v}`;
        // eslint-disable-next-line no-await-in-loop
        const resp = await fetch(url, { method: "PUT" });
        if (!resp.ok) throw new Error(`Erro ao salvar ${k}`);
      }
      setStatus("Configurações salvas com sucesso.");
      setTimeout(() => setStatus(""), 1800);
    } catch (e) {
      setStatus("Erro ao salvar configurações.");
    }
    setSaving(false);
  }

  return (
    <div
      style={{
        width: "100vw",
        minHeight: "100vh",
        background: "#f4f7fb",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start"
      }}
    >
      {/* HEADER: Home à esquerda, título central, salvar à direita */}
      <div
        style={{
          width: "100vw",
          background: "#fff",
          display: "flex",
          alignItems: "center",
          borderBottom: "1.5px solid #dde5ef",
          minHeight: 70,
          padding: "0 16px"
        }}
      >
        {/* HOME - ESQUERDA */}
        <div style={{ flex: "0 0 120px", display: "flex", alignItems: "center" }}>
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
              fontSize: 17
            }}
            title="Voltar para o painel"
            onClick={() => navigate("/")}
          >
            <FaHome size={21} style={{ marginRight: 7 }} />
            Home
          </button>
        </div>

        {/* Nome Centralizado */}
        <div style={{ flex: 1, textAlign: "center" }}>
          <span style={{
            fontSize: 26,
            fontWeight: 700,
            color: "#183d74"
          }}>
            Aplicativo de Monitoramento do LabREI
          </span>
        </div>

        {/* Salvar - DIREITA */}
        <div style={{ flex: "0 0 120px", display: "flex", justifyContent: "flex-end", alignItems: "center" }}>
          <button
            style={{
              border: "none",
              background: "none",
              cursor: "pointer",
              padding: 8,
              borderRadius: 8
            }}
            title="Salvar configurações"
            onClick={handleSave}
            disabled={saving}
          >
            {/* Ícone disquete SVG */}
            <svg width="28" height="28" viewBox="0 0 22 22" fill="none">
              <rect x="3" y="3" width="16" height="16" rx="2" stroke="#183d74" strokeWidth="2" fill="#e6f1fb" />
              <rect x="6" y="6" width="10" height="6" rx="1.2" fill="#3c80c9" />
              <rect x="8" y="14" width="6" height="3" rx="1" fill="#a2c4e6" />
              <rect x="9" y="7" width="4" height="2" rx="0.6" fill="#fff" />
            </svg>
          </button>
        </div>
      </div>

      {/* Subtítulo */}
      <div style={{
        textAlign: "center",
        maxWidth: 560,
        margin: "32px auto 4px auto",
        color: "#315189",
        fontSize: 22,
        fontWeight: 600,
        letterSpacing: 0.1
      }}>
        Página de Configuração
      </div>

      {/* Formulário */}
      <form
        style={{
          maxWidth: 520,
          margin: "34px auto 34px auto",
          background: "#fff",
          padding: 32,
          borderRadius: 14,
          boxShadow: "0 3px 12px #0002",
          border: "1px solid #e6ecf8",
        }}
        onSubmit={e => { e.preventDefault(); handleSave(); }}
      >
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 120px",
          rowGap: 18,
          columnGap: 22
        }}>
          {CONFIG_KEYS.map((item, i) => {
            const c = configs.find(cfg => cfg.key === item.key) || { value: "" };
            return (
              <React.Fragment key={item.key}>
                <label
                  htmlFor={item.key}
                  style={{
                    justifySelf: "start",
                    alignSelf: "center",
                    fontWeight: 500,
                    color: "#143752",
                    fontSize: 17,
                    textAlign: "left"
                  }}
                >
                  {item.label}
                </label>
                <input
                  id={item.key}
                  type="number"
                  value={c.value}
                  disabled={saving}
                  onChange={e => handleChange(i, e.target.value)}
                  style={{
                    fontSize: 18,
                    width: "100%",
                    borderRadius: 7,
                    padding: "4px 12px",
                    border: "1px solid #d8dbe6",
                    background: "#fafcff",
                    textAlign: "left"
                  }}
                />
              </React.Fragment>
            );
          })}
        </div>
        {status &&
          <div style={{
            textAlign: "center",
            color: status.includes("sucesso") ? "#27b84a" : "#cb2f38",
            fontSize: 16,
            marginTop: 20
          }}>
            {status}
          </div>
        }
      </form>

      {/* ==== LOGOS DOS PATROCINADORES ==== */}
      <div
        style={{
          width: "100vw",
          padding: "18px 0 18px 0",
          background: "#fff",
          display: "flex",
          justifyContent: "center",
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
                width: SPONSOR_LOGO_SIZE,
                height: SPONSOR_LOGO_SIZE,
                borderRadius: 12,
                objectFit: "contain",
                background: "#fff",
                border: "1.5px solid #e3e9f3",
                boxShadow: "0 1.5px 5px #0001"
              }}
            />
          ) : (
            <div
              key={i}
              style={{
                width: SPONSOR_LOGO_SIZE,
                height: SPONSOR_LOGO_SIZE,
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
