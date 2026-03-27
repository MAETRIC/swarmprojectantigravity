import React, { useState, useEffect, useRef } from 'react';
import { Shield, AlertTriangle, Activity, Lock, Cpu, Server } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [nodes, setNodes] = useState({});
  const [logs, setLogs] = useState([]);
  const [systemState, setSystemState] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const ws = useRef(null);
  const logsEndRef = useRef(null);
  const logContainerRef = useRef(null);

  const handleScroll = () => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
      setAutoScroll(scrollHeight - scrollTop - clientHeight < 50);
    }
  };

  useEffect(() => {
    let active = true;
    if (!ws.current) {
      connectWebSocket();
    }
    return () => {
      active = false;
      if (ws.current) {
        // ws.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [logs, autoScroll]);

  const connectWebSocket = () => {
    ws.current = new WebSocket('ws://localhost:8000/ws/simulation');
    
    ws.current.onopen = () => {
      setIsConnected(true);
      addLog('🔌 Connected to Swarm Defence API', 'info');
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      addLog('⚠️ Connection lost. Retrying...', 'error');
      setTimeout(connectWebSocket, 3000);
    };

    ws.current.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'log') {
          addLog(msg.message, 'info');
        } else if (msg.type === 'state') {
          handleStateUpdate(msg.data);
        } else if (msg.type === 'containment') {
          addLog(msg.message, 'critical');
        }
      } catch (err) {
        console.error("Parse error", err);
      }
    };
  };

  const handleStateUpdate = (data) => {
    setSystemState(data);
    setNodes(data.node_results);
    
    setChartData(prev => {
      const newPoint = {
        time: new Date().toLocaleTimeString().split(' ')[0],
        threat: data.threat_level * 100, // Scale for UI
        votes: data.attack_votes
      };
      const newData = [...prev, newPoint];
      if (newData.length > 20) newData.shift();
      return newData;
    });

    if (data.is_attack_detected) {
      addLog(`🔥 Anomaly detected at IP: ${data.attacker_ip} (Threat Level: ${(data.threat_level * 100).toFixed(1)}%)`, 'warning');
    }
  };

  const addLog = (message, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time, message, type }]);
  };

  return (
    <div className="min-h-screen bg-background text-slate-200 p-6 flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-slate-700 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <Shield className="w-10 h-10 text-primary" />
          <div>
            <h1 className="text-2xl font-bold text-white tracking-widest">SWED-A MISSION CONTROL</h1>
            <p className="text-slate-400 text-sm">Swarm Edge Defence for Air-Gapped Networks</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className={`px-4 py-2 rounded-full border ${isConnected ? 'bg-success/20 border-success text-success' : 'bg-danger/20 border-danger text-danger'} flex items-center gap-2`}>
            <Activity className="w-4 h-4" />
            {isConnected ? 'LIVE FEED ACTIVE' : 'DISCONNECTED'}
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-12 gap-6">
        
        {/* Left Column: Stats & Chart */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-6">
          
          {/* Top KPI Cards */}
          <div className="grid grid-cols-4 gap-4">
            <KpiCard title="Total Samples" value={systemState?.stats?.total_samples || 0} icon={<Activity />} />
            <KpiCard title="Threats Prevented" value={systemState?.stats?.attacks_detected || 0} icon={<Shield className="text-primary"/>} />
            <KpiCard title="Containments" value={systemState?.stats?.containment_events || 0} icon={<Lock className="text-warning"/>} alert={systemState?.stats?.containment_events > 0}/>
            <KpiCard title="Consensus Threshold" value="60%" icon={<Server />} />
          </div>

          {/* Realtime Chart */}
          <div className="bg-surface border border-slate-800 rounded-xl p-5 flex-1 shadow-xl">
            <h2 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-secondary" /> Realtime Threat Topology
            </h2>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                  <Line type="monotone" dataKey="threat" stroke="#ef4444" strokeWidth={2} dot={false} activeDot={{ r: 6 }} name="Threat Score" />
                  <Line type="monotone" dataKey="votes" stroke="#3b82f6" strokeWidth={2} dot={false} name="Consensus Votes" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right Column: Node Grid & Logs */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
          
          {/* Node Grid */}
          <div className="bg-surface border border-slate-800 rounded-xl p-5 shadow-xl">
            <h2 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-primary" /> Edge Swarm Nodes
            </h2>
            <div className="grid grid-cols-2 gap-3">
              {Object.keys(nodes).length > 0 ? Object.entries(nodes).map(([id, node]) => (
                <div key={id} className={`p-3 rounded-lg border relative overflow-hidden transition-all duration-300 ${node.status === 'ATTACK' ? 'bg-danger/10 border-danger/50 shadow-[0_0_15px_rgba(239,68,68,0.3)]' : 'bg-slate-800/50 border-slate-700'}`}>
                   {node.status === 'ATTACK' && (
                     <div className="absolute inset-0 bg-danger/10 animate-pulse"></div>
                   )}
                   <div className="flex justify-between items-start relative z-10">
                    <span className="font-mono text-sm font-bold text-slate-300">{id}</span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${node.status === 'ATTACK' ? 'bg-danger text-white' : 'bg-success/20 text-success'}`}>
                      {node.status}
                    </span>
                   </div>
                   <div className="mt-2 text-xs text-slate-400 relative z-10">
                     <div>Score: {node.score.toFixed(2)}</div>
                     <div>Conf: {node.confidence.toFixed(1)}%</div>
                   </div>
                </div>
              )) : (
                <div className="col-span-2 text-center text-slate-500 py-4">Waiting for initialization...</div>
              )}
            </div>
          </div>

          {/* Event Terminal */}
          <div className="bg-surface border border-slate-800 rounded-xl p-5 flex-1 flex flex-col shadow-xl min-h-[300px]">
            <h2 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500" /> Action Logs
            </h2>
            <div 
              ref={logContainerRef}
              onScroll={handleScroll}
              className="bg-[#0f172a] rounded flex-1 p-3 overflow-y-auto h-[450px] font-mono text-xs border border-slate-800"
            >
              {logs.map((log, i) => (
                <div key={i} className={`mb-2 pb-1 border-b border-slate-800/50 ${log.type === 'critical' ? 'text-danger font-bold' : log.type === 'warning' ? 'text-yellow-400' : 'text-slate-400'}`}>
                  <span className="text-slate-600 mr-2">[{log.time}]</span>
                  {log.message}
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

function KpiCard({ title, value, icon, alert }) {
  return (
    <div className={`bg-surface border rounded-xl p-4 shadow-lg ${alert ? 'border-danger/50 bg-danger/5' : 'border-slate-800'}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
        {icon}
      </div>
      <div className={`text-2xl font-bold ${alert ? 'text-danger' : 'text-slate-100'}`}>{value}</div>
    </div>
  );
}

export default App;
