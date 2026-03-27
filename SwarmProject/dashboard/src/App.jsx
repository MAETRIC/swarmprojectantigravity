import React, { useState, useEffect, useRef } from 'react';
import { Shield, AlertTriangle, Activity, Lock, Cpu, Wifi, WifiOff, Clock, BarChart3, Terminal, Zap } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [nodes, setNodes] = useState({});
  const [logs, setLogs] = useState([]);
  const [systemState, setSystemState] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [currentTime, setCurrentTime] = useState('');
  const ws = useRef(null);
  const logContainerRef = useRef(null);

  // Live clock
  useEffect(() => {
    const tick = () => setCurrentTime(new Date().toLocaleTimeString('en-US', { hour12: true }));
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection — only once
  useEffect(() => {
    if (!ws.current) connectWebSocket();
    return () => {};
  }, []);

  // Auto-scroll logs container
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTo({
        top: logContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [logs, autoScroll]);

  const handleLogScroll = () => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
      setAutoScroll(scrollHeight - scrollTop - clientHeight < 50);
    }
  };

  const connectWebSocket = () => {
    ws.current = new WebSocket('ws://localhost:8000/ws/simulation');

    ws.current.onopen = () => {
      setIsConnected(true);
      addLog('Connected to SWED-A Swarm API', 'success');
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      ws.current = null;
      addLog('Connection lost. Retrying...', 'error');
      setTimeout(connectWebSocket, 3000);
    };

    ws.current.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'log') addLog(msg.message, 'info');
        else if (msg.type === 'state') handleStateUpdate(msg.data);
        else if (msg.type === 'containment') addLog(msg.message, 'critical');
      } catch (err) {
        console.error('Parse error', err);
      }
    };
  };

  const handleStateUpdate = (data) => {
    setSystemState(data);
    setNodes(data.node_results);

    setChartData(prev => {
      const newPoint = {
        time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        threat: +(data.threat_level * 100).toFixed(1),
        votes: data.attack_votes
      };
      const updated = [...prev, newPoint];
      if (updated.length > 30) updated.shift();
      return updated;
    });

    if (data.is_attack_detected) {
      addLog(`Anomaly detected — IP: ${data.attacker_ip} | Threat: ${(data.threat_level * 100).toFixed(1)}%`, 'warning');
    }
  };

  const addLog = (message, type = 'info') => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(prev => {
      const updated = [...prev, { time, message, type }];
      if (updated.length > 100) return updated.slice(-100);
      return updated;
    });
  };

  const stats = systemState?.stats || {};

  return (
    <div className="relative z-10 h-screen flex flex-col p-4 gap-3 overflow-hidden">

      {/* ===== HEADER ===== */}
      <header className="flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Shield className="w-9 h-9 neon-cyan" />
            <div className="absolute inset-0 blur-lg opacity-30" style={{ background: 'var(--color-cyan)' }}></div>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-[0.2em] text-white uppercase">
              SWED-A <span className="neon-cyan font-light">Mission Control</span>
            </h1>
            <p className="text-xs text-[var(--color-text-muted)] tracking-wider">Swarm Edge Defence • Air-Gapped Networks</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
            <Clock className="w-3.5 h-3.5" />
            <span className="terminal-font">{currentTime}</span>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
            isConnected 
              ? 'border-[var(--color-green)] bg-[var(--color-green-dim)] text-[var(--color-green)]'
              : 'border-[var(--color-red-hot)] bg-[var(--color-red-dim)] text-[var(--color-red-hot)]'
          }`}>
            <div className={`status-dot ${!isConnected ? 'status-dot-red' : ''}`}></div>
            {isConnected ? 'LIVE' : 'OFFLINE'}
          </div>
        </div>
      </header>

      {/* ===== KPI CARDS ===== */}
      <div className="grid grid-cols-4 gap-3 flex-shrink-0">
        <KpiCard
          title="Samples Analyzed"
          value={stats.total_samples || 0}
          icon={<BarChart3 className="w-4 h-4" />}
          color="cyan"
        />
        <KpiCard
          title="Threats Detected"
          value={stats.attacks_detected || 0}
          icon={<Zap className="w-4 h-4" />}
          color="red"
          alert={stats.attacks_detected > 0}
        />
        <KpiCard
          title="Containments"
          value={stats.containment_events || 0}
          icon={<Lock className="w-4 h-4" />}
          color="amber"
          alert={stats.containment_events > 0}
        />
        <KpiCard
          title="Consensus"
          value="60%"
          icon={<Cpu className="w-4 h-4" />}
          color="cyan"
          subtitle="Threshold"
        />
      </div>

      {/* ===== MAIN CONTENT ===== */}
      <div className="flex-1 grid grid-cols-12 gap-3 min-h-0">

        {/* --- Left Column: Chart + Nodes --- */}
        <div className="col-span-8 flex flex-col gap-3 min-h-0">

          {/* Threat Chart */}
          <div className="glass-card p-4 flex-1 flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-3 flex-shrink-0">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 neon-cyan" />
                Realtime Threat Topology
              </h2>
              <span className="text-xs text-[var(--color-text-muted)] terminal-font">
                {chartData.length} data points
              </span>
            </div>
            <div className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="threatGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ff2d55" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ff2d55" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="votesGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#00f0ff" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(51,65,85,0.3)" />
                  <XAxis
                    dataKey="time"
                    stroke="var(--color-text-muted)"
                    fontSize={10}
                    tickLine={false}
                    axisLine={{ stroke: 'var(--color-border)' }}
                    fontFamily="JetBrains Mono"
                  />
                  <YAxis
                    stroke="var(--color-text-muted)"
                    fontSize={10}
                    tickLine={false}
                    axisLine={{ stroke: 'var(--color-border)' }}
                    fontFamily="JetBrains Mono"
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="threat"
                    stroke="#ff2d55"
                    strokeWidth={2}
                    fill="url(#threatGradient)"
                    dot={false}
                    activeDot={{ r: 4, fill: '#ff2d55', stroke: '#fff', strokeWidth: 1 }}
                    name="Threat %"
                  />
                  <Area
                    type="monotone"
                    dataKey="votes"
                    stroke="#00f0ff"
                    strokeWidth={2}
                    fill="url(#votesGradient)"
                    dot={false}
                    activeDot={{ r: 4, fill: '#00f0ff', stroke: '#fff', strokeWidth: 1 }}
                    name="Votes"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Edge Nodes Row */}
          <div className="glass-card p-4 flex-shrink-0">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <Cpu className="w-4 h-4 neon-cyan" />
              Edge Swarm Nodes
            </h2>
            <div className="grid grid-cols-3 gap-3">
              {Object.keys(nodes).length > 0 ? Object.entries(nodes).map(([id, node]) => (
                <NodeCard key={id} id={id} node={node} />
              )) : (
                <div className="col-span-3 text-center text-[var(--color-text-muted)] py-6 text-sm">
                  Awaiting swarm initialization...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* --- Right Column: Action Logs --- */}
        <div className="col-span-4 flex flex-col min-h-0">
          <div className="glass-card flex-1 flex flex-col min-h-0 overflow-hidden">
            {/* Terminal Header */}
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-[var(--color-border)] flex-shrink-0 bg-[rgba(0,0,0,0.3)] rounded-t-2xl">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#febc2e]"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]"></div>
                </div>
                <span className="text-xs text-[var(--color-text-muted)] ml-2 terminal-font">swed-a://action-logs</span>
              </div>
              <Terminal className="w-3.5 h-3.5 text-[var(--color-text-muted)]" />
            </div>
            {/* Log Content */}
            <div
              ref={logContainerRef}
              onScroll={handleLogScroll}
              className="flex-1 overflow-y-auto p-3 min-h-0"
            >
              {logs.map((log, i) => (
                <LogEntry key={i} log={log} index={i} />
              ))}
              {logs.length === 0 && (
                <div className="text-center text-[var(--color-text-muted)] py-8 text-xs terminal-font">
                  $ waiting for simulation feed...<span className="animate-[blink_1s_infinite]">_</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ===== CUSTOM TOOLTIP ===== */
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card p-3 text-xs border border-[var(--color-border)]" style={{ backdropFilter: 'blur(20px)' }}>
      <p className="terminal-font text-[var(--color-text-muted)] mb-1.5">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} className="flex items-center gap-2" style={{ color: entry.color }}>
          <span className="w-2 h-2 rounded-full" style={{ background: entry.color }}></span>
          {entry.name}: <span className="font-bold">{entry.value}</span>
        </p>
      ))}
    </div>
  );
}

/* ===== KPI CARD ===== */
function KpiCard({ title, value, icon, color, alert, subtitle }) {
  const colors = {
    cyan: {
      border: alert ? 'border-[var(--color-cyan)]' : 'border-[var(--color-border)]',
      bg: alert ? 'bg-[var(--color-cyan-dim)]' : '',
      text: 'text-[var(--color-cyan)]',
      iconBg: 'bg-[var(--color-cyan-dim)]',
      glow: alert ? 'glow-cyan' : ''
    },
    red: {
      border: alert ? 'border-[var(--color-red-hot)]' : 'border-[var(--color-border)]',
      bg: alert ? 'bg-[var(--color-red-dim)]' : '',
      text: 'text-[var(--color-red-hot)]',
      iconBg: 'bg-[var(--color-red-dim)]',
      glow: alert ? 'glow-red' : ''
    },
    amber: {
      border: alert ? 'border-[var(--color-amber)]' : 'border-[var(--color-border)]',
      bg: alert ? 'bg-[var(--color-amber-dim)]' : '',
      text: 'text-[var(--color-amber)]',
      iconBg: 'bg-[var(--color-amber-dim)]',
      glow: ''
    }
  };
  const c = colors[color] || colors.cyan;

  return (
    <div className={`glass-card p-3.5 transition-all duration-500 ${c.border} ${c.bg} ${c.glow}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] uppercase tracking-widest text-[var(--color-text-muted)] font-medium">{title}</span>
        <div className={`p-1.5 rounded-lg ${c.iconBg}`}>
          <span className={c.text}>{icon}</span>
        </div>
      </div>
      <div className={`text-2xl font-bold terminal-font ${alert ? c.text : 'text-white'}`}>
        {value}
      </div>
      {subtitle && <span className="text-[10px] text-[var(--color-text-muted)]">{subtitle}</span>}
    </div>
  );
}

/* ===== NODE CARD ===== */
function NodeCard({ id, node }) {
  const isAttack = node.status === 'ATTACK';

  return (
    <div className={`relative overflow-hidden rounded-xl border p-3 transition-all duration-500 ${
      isAttack
        ? 'border-[var(--color-red-hot)] bg-[var(--color-red-dim)] glow-red'
        : 'border-[var(--color-border)] bg-[var(--color-bg-elevated)]'
    }`}>
      {/* Scan line animation on attack */}
      {isAttack && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute inset-x-0 h-8 bg-gradient-to-b from-[var(--color-red-hot)] to-transparent opacity-20 animate-scan"></div>
        </div>
      )}

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="terminal-font text-xs font-bold text-white">{id}</span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
            isAttack
              ? 'bg-[var(--color-red-hot)] text-white animate-pulse-glow'
              : 'bg-[var(--color-green-dim)] text-[var(--color-green)]'
          }`}>
            {isAttack ? '⚠ THREAT' : '● SECURE'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-1">
          <div>
            <span className="text-[10px] text-[var(--color-text-muted)] block">Score</span>
            <span className={`terminal-font text-sm font-bold ${isAttack ? 'neon-red' : 'text-white'}`}>
              {node.score.toFixed(3)}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-[var(--color-text-muted)] block">Confidence</span>
            <span className="terminal-font text-sm font-bold text-white">
              {node.confidence.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ===== LOG ENTRY ===== */
function LogEntry({ log, index }) {
  const typeStyles = {
    success: 'text-[var(--color-green)]',
    info: 'text-[var(--color-text-secondary)]',
    warning: 'text-[var(--color-amber)]',
    error: 'text-[var(--color-red-hot)]',
    critical: 'text-[var(--color-red-hot)] font-bold',
  };

  const typeIcons = {
    success: '●',
    info: '›',
    warning: '▲',
    error: '✕',
    critical: '◆',
  };

  return (
    <div
      className={`flex items-start gap-2 py-1.5 border-b border-[rgba(51,65,85,0.2)] text-xs terminal-font animate-fade-in ${typeStyles[log.type] || typeStyles.info}`}
      style={{ animationDelay: `${index * 0.02}s` }}
    >
      <span className="text-[var(--color-text-muted)] flex-shrink-0 w-16">{log.time}</span>
      <span className="flex-shrink-0 w-3 text-center">{typeIcons[log.type] || '›'}</span>
      <span className="flex-1 break-words leading-relaxed">{log.message}</span>
    </div>
  );
}

export default App;
