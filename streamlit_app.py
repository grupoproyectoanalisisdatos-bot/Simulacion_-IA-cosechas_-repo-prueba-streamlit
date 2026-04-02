import React, { useState, useMemo } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, Legend 
} from 'recharts';
import { 
  CloudSun, Thermometer, Droplets, MapPin, 
  Sprout, Info, AlertTriangle, ExternalLink, 
  TrendingUp, Download
} from 'lucide-react';

const App = () => {
  // --- ESTADO INICIAL ---
  const [municipio, setMunicipio] = useState('Antioquia - Urrao');
  const [cultivo, setCultivo] = useState('Maíz');
  const [tempDelta, setTempDelta] = useState(0);
  const [rainDelta, setRainDelta] = useState(0);

  // --- DATOS MAESTROS (Simulados basados en patrones históricos) ---
  const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  
  const baseData = useMemo(() => {
    // Generar curva base según el cultivo seleccionado
    const seed = cultivo === 'Maíz' ? 2.5 : cultivo === 'Café' ? 1.2 : 4.0;
    return meses.map((mes, i) => ({
      name: mes,
      historico: seed + Math.sin(i * 0.5) * 0.5 + (Math.random() * 0.2),
    }));
  }, [cultivo]);

  // --- LÓGICA DE SIMULACIÓN ---
  const simulatedData = useMemo(() => {
    return baseData.map(d => {
      // El calor excesivo reduce el rendimiento (-5% por grado)
      // La lluvia extrema o sequía reduce el rendimiento
      const tempImpact = 1 - (tempDelta * 0.05);
      const rainImpact = 1 - (Math.abs(rainDelta) * 0.002);
      const factor = Math.max(0.2, tempImpact * rainImpact);
      
      return {
        ...d,
        simulado: parseFloat((d.historico * factor).toFixed(2))
      };
    });
  }, [baseData, tempDelta, rainDelta]);

  // --- RECOMENDACIONES DINÁMICAS ---
  const getRecommendations = () => {
    let recs = [];
    if (tempDelta > 2) recs.push({ id: 1, text: "Instalar sistemas de riego por goteo para mitigar evaporación.", type: "critical" });
    if (rainDelta < -20) recs.push({ id: 2, text: "Implementar coberturas vegetales para mantener humedad.", type: "warning" });
    if (rainDelta > 20) recs.push({ id: 3, text: "Mejorar drenajes para evitar saturación de raíces.", type: "warning" });
    if (tempDelta > 3) recs.push({ id: 4, text: "Considerar variedades de semilla resistentes al calor.", type: "critical" });
    if (recs.length === 0) recs.push({ id: 0, text: "Condiciones estables. Mantener monitoreo preventivo.", type: "info" });
    return recs;
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      
      {/* SIDEBAR DE CONTROL */}
      <aside className="w-80 bg-white border-r border-slate-200 overflow-y-auto flex flex-col shadow-xl z-10">
        <div className="p-6 border-b border-slate-100 bg-emerald-900 text-white">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Sprout className="w-6 h-6" /> AgroSim Pro
          </h1>
          <p className="text-emerald-200 text-xs mt-1 uppercase tracking-widest font-semibold">Climate Intelligence</p>
        </div>

        <div className="p-6 space-y-8">
          {/* Selección Geográfica */}
          <div>
            <label className="text-xs font-bold text-slate-400 uppercase mb-3 block flex items-center gap-2">
              <MapPin className="w-3 h-3" /> Región de Análisis
            </label>
            <select 
              value={municipio}
              onChange={(e) => setMunicipio(e.target.value)}
              className="w-full p-3 bg-slate-100 border-none rounded-xl text-sm font-medium focus:ring-2 focus:ring-emerald-500 outline-none"
            >
              <option>Antioquia - Urrao</option>
              <option>Magdalena - Aracataca</option>
              <option>Casanare - Yopal</option>
              <option>Valle - Palmira</option>
            </select>
          </div>

          {/* Selección de Cultivo */}
          <div>
            <label className="text-xs font-bold text-slate-400 uppercase mb-3 block">Tipo de Cultivo</label>
            <div className="grid grid-cols-2 gap-2">
              {['Maíz', 'Café', 'Arroz', 'Cacao'].map(c => (
                <button
                  key={c}
                  onClick={() => setCultivo(c)}
                  className={`p-3 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                    cultivo === c 
                    ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-200 scale-105' 
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {/* Sliders Climáticos */}
          <div className="space-y-6 pt-4 border-t border-slate-100">
            <div>
              <div className="flex justify-between mb-2">
                <label className="text-xs font-bold text-slate-600 flex items-center gap-1">
                  <Thermometer className="w-4 h-4 text-orange-500" /> Temperatura
                </label>
                <span className="text-xs font-black text-orange-600">+{tempDelta}°C</span>
              </div>
              <input 
                type="range" min="0" max="5" step="0.5"
                value={tempDelta}
                onChange={(e) => setTempDelta(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
              />
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <label className="text-xs font-bold text-slate-600 flex items-center gap-1">
                  <Droplets className="w-4 h-4 text-blue-500" /> Precipitación
                </label>
                <span className={`text-xs font-black ${rainDelta >= 0 ? 'text-blue-600' : 'text-red-500'}`}>
                  {rainDelta > 0 ? '+' : ''}{rainDelta}%
                </span>
              </div>
              <input 
                type="range" min="-50" max="50" step="5"
                value={rainDelta}
                onChange={(e) => setRainDelta(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="mt-auto p-6 bg-slate-50 border-t border-slate-100">
           <div className="flex items-center gap-2 text-slate-400 mb-2">
             <Info className="w-4 h-4" />
             <span className="text-[10px] font-bold uppercase tracking-tighter">Fuentes de Datos Abiertos</span>
           </div>
           <div className="space-y-1">
             <a href="#" className="flex items-center justify-between text-[11px] text-emerald-700 hover:underline">IDEAM Colombia <ExternalLink className="w-3 h-3"/></a>
             <a href="#" className="flex items-center justify-between text-[11px] text-emerald-700 hover:underline">NASA Power API <ExternalLink className="w-3 h-3"/></a>
             <a href="#" className="flex items-center justify-between text-[11px] text-emerald-700 hover:underline">UPRA Agrícola <ExternalLink className="w-3 h-3"/></a>
           </div>
        </div>
      </aside>

      {/* ÁREA DE CONTENIDO PRINCIPAL */}
      <main className="flex-1 overflow-y-auto p-8">
        
        {/* Encabezado Dinámico */}
        <div className="mb-8 flex justify-between items-end">
          <div>
            <h2 className="text-3xl font-black text-slate-800 tracking-tight">Simulación de Rendimiento</h2>
            <p className="text-slate-500 flex items-center gap-2 mt-1">
              Escenario: <span className="font-bold text-emerald-600">{cultivo}</span> en <span className="font-bold text-slate-700">{municipio}</span>
            </p>
          </div>
          <button className="flex items-center gap-2 bg-white border border-slate-200 px-4 py-2 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 transition-all">
            <Download className="w-4 h-4" /> Exportar Reporte
          </button>
        </div>

        <div className="grid grid-cols-3 gap-6">
          
          {/* PANEL DE GRÁFICO PRINCIPAL */}
          <div className="col-span-3 lg:col-span-2 bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
            <div className="flex justify-between items-center mb-8">
              <h3 className="font-bold text-slate-700 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-500" /> Proyección Mensual (t/ha)
              </h3>
              <div className="flex gap-4 text-xs font-bold">
                <div className="flex items-center gap-1"><span className="w-3 h-3 bg-slate-300 rounded-full"></span> Histórico</div>
                <div className="flex items-center gap-1"><span className="w-3 h-3 bg-emerald-500 rounded-full"></span> Simulado</div>
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={simulatedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSim" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{fontSize: 12, fontWeight: 600, fill: '#94a3b8'}}
                    dy={10}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{fontSize: 12, fontWeight: 600, fill: '#94a3b8'}}
                  />
                  <Tooltip 
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="historico" 
                    stroke="#cbd5e1" 
                    strokeWidth={3}
                    fill="transparent" 
                    strokeDasharray="5 5"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="simulado" 
                    stroke="#10b981" 
                    strokeWidth={4}
                    fillOpacity={1} 
                    fill="url(#colorSim)" 
                    animationDuration={1000}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* RESUMEN EJECUTIVO E IMPACTO */}
          <div className="col-span-3 lg:col-span-1 space-y-6">
            <div className="bg-emerald-900 text-white p-6 rounded-3xl shadow-lg">
              <h3 className="font-bold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-emerald-300" /> Análisis de Impacto
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-emerald-800 pb-2">
                  <span className="text-emerald-300 text-sm">Cambio en Rendimiento</span>
                  <span className={`font-black ${simulatedData[0].simulado < baseData[0].historico ? 'text-red-400' : 'text-emerald-400'}`}>
                    {(((simulatedData[0].simulado / baseData[0].historico) - 1) * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-xs leading-relaxed text-emerald-100 opacity-80">
                  El aumento de **{tempDelta}°C** proyecta un estrés térmico significativo en las etapas de floración del **{cultivo}**, reduciendo la biomasa efectiva.
                </p>
              </div>
            </div>

            {/* TARJETAS DE RECOMENDACIÓN */}
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
              <h3 className="font-bold text-slate-700 mb-4">Recomendaciones Expertas</h3>
              <div className="space-y-3">
                {getRecommendations().map(rec => (
                  <div 
                    key={rec.id} 
                    className={`p-3 rounded-2xl text-xs font-medium border-l-4 flex items-start gap-3 ${
                      rec.type === 'critical' ? 'bg-red-50 border-red-500 text-red-700' : 
                      rec.type === 'warning' ? 'bg-orange-50 border-orange-500 text-orange-700' : 
                      'bg-blue-50 border-blue-500 text-blue-700'
                    }`}
                  >
                    <span className="mt-0.5">{rec.type === 'critical' ? '🚨' : rec.type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                    {rec.text}
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
};

export default App;
