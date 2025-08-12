import React, { useState, useCallback } from 'react';
import { Upload, Download, Calculator, LineChart, AlertCircle } from 'lucide-react';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const MLSDepthAnalysis = () => {
  const [data, setData] = useState([]);
  const [results, setResults] = useState(null);
  const [parameters, setParameters] = useState({
    heatPower: 15, // W/m - potenza per metro lineare
    radius: 0.003, // m - raggio del sensore
    timeSteps: [0.0, 2.84, 4.86, 6.86, 72.87], // ore - tempi di misura
    thermalDiffusivity: 1.4e-6, // m²/s - diffusività termica del suolo
    fluidThermalConductivity: 0.6, // W/(m·K) - conducibilità del fluido
    fluidSpecificHeat: 4180, // J/(kg·K) - calore specifico del fluido
    fluidDensity: 1000 // kg/m³ - densità del fluido
  });
  const [loading, setLoading] = useState(false);

  // Funzione per calcolare la resistenza termica del borehole
  const calculateBoreholeResistance = (thermalConductivity) => {
    // Formula semplificata per resistenza termica del borehole
    // Rb = ln(rb/rp) / (2π * k) dove rb è raggio borehole, rp raggio tubo
    const rb = 0.075; // raggio borehole tipico (m)
    const rp = 0.02; // raggio tubo tipico (m)
    return Math.log(rb / rp) / (2 * Math.PI * thermalConductivity);
  };

  // Funzione per il calcolo MLS
  const calculateMLS = (tempData, timeSteps, depth) => {
    const { heatPower, radius, thermalDiffusivity } = parameters;
    
    // Converti tempi da ore a secondi per i calcoli
    const timeStepsSeconds = timeSteps.map(t => t * 3600);
    
    // Calcola le variazioni di temperatura rispetto al tempo iniziale
    const tempRises = tempData.slice(1).map((temp, i) => temp - tempData[0]);
    
    // Metodo della pendenza per calcolare la conducibilità termica
    const timeRatios = [];
    const tempRatioLogs = [];
    
    for (let i = 1; i < tempRises.length; i++) {
      if (tempRises[i] > 0 && tempRises[i-1] > 0) {
        const timeRatio = timeStepsSeconds[i+1] / timeStepsSeconds[i];
        const tempRatio = tempRises[i] / tempRises[i-1];
        if (tempRatio > 0) {
          timeRatios.push(Math.log(timeRatio));
          tempRatioLogs.push(Math.log(tempRatio));
        }
      }
    }
    
    // Calcolo della conducibilità termica usando il metodo della line source
    let thermalConductivity = 0;
    if (tempRises.length > 1 && tempRises[tempRises.length - 1] > tempRises[0]) {
      const deltaTemp = tempRises[tempRises.length - 1] - tempRises[0];
      const deltaTime = Math.log(timeStepsSeconds[timeStepsSeconds.length - 1] / timeStepsSeconds[1]);
      thermalConductivity = (heatPower * deltaTime) / (4 * Math.PI * deltaTemp);
    }
    
    // Calcola la resistenza termica del borehole
    const boreholeResistance = calculateBoreholeResistance(thermalConductivity);
    
    // Calcola la velocità darciana usando il metodo del moving line source
    // Usa la diffusività termica apparente per stimare il flusso
    const apparentDiffusivity = calculateApparentDiffusivity(tempRises, timeStepsSeconds);
    const darcyVelocity = calculateDarcyVelocity(apparentDiffusivity, thermalDiffusivity);
    
    return {
      thermalConductivity: Math.max(0, thermalConductivity),
      boreholeResistance,
      darcyVelocity,
      tempRises,
      apparentDiffusivity
    };
  };

  const calculateApparentDiffusivity = (tempRises, timeSteps) => {
    // Calcola la diffusività apparente dal profilo di temperatura
    if (tempRises.length < 2) return parameters.thermalDiffusivity;
    
    const { radius } = parameters;
    let sumDiff = 0;
    let count = 0;
    
    for (let i = 1; i < tempRises.length; i++) {
      if (tempRises[i] > 0) {
        const time = timeSteps[i];
        const temp = tempRises[i];
        // Stima della diffusività usando la soluzione della line source
        const diffusivity = (radius * radius) / (4 * time * Math.log(temp + 1));
        if (diffusivity > 0 && diffusivity < 1e-3) {
          sumDiff += diffusivity;
          count++;
        }
      }
    }
    
    return count > 0 ? sumDiff / count : parameters.thermalDiffusivity;
  };

  const calculateDarcyVelocity = (apparentDiffusivity, thermalDiffusivity) => {
    // Calcola la velocità darciana dal rapporto tra diffusività apparente e teorica
    const { fluidSpecificHeat, fluidDensity } = parameters;
    const diffusivityRatio = apparentDiffusivity / thermalDiffusivity;
    
    // Formula empirica per velocità darciana
    const velocity = Math.abs(diffusivityRatio - 1) * Math.sqrt(thermalDiffusivity) * fluidSpecificHeat * fluidDensity / 1000;
    
    return Math.min(velocity, 1e-6); // Limita a valori ragionevoli
  };

  const calculateTemperature = (depth, time, k, v, rb) => {
    // Calcola la temperatura teorica usando il modello MLS
    const { heatPower, radius, thermalDiffusivity, fluidThermalConductivity } = parameters;
    
    // Soluzione della line source con correzione per il flusso
    const alpha = thermalDiffusivity;
    const u = (radius * radius) / (4 * alpha * time);
    
    // Funzione esponenziale integrale approssimata
    const ei = u < 1 ? -0.5772 - Math.log(u) + u - u*u/4 + u*u*u/18 : Math.exp(-u) / u * (1 - 1/u);
    
    // Temperature rise con correzione per velocità
    const tempRise = (heatPower / (4 * Math.PI * k)) * (-ei);
    
    // Correzione per il flusso advettivo
    const advectionCorrection = v > 0 ? Math.exp(-v * Math.sqrt(time) / (2 * Math.sqrt(alpha))) : 1;
    
    return tempRise * advectionCorrection;
  };

  const calculateRMS = (observed, calculated) => {
    if (observed.length !== calculated.length) return null;
    
    const sumSquaredDiff = observed.reduce((sum, obs, i) => {
      const diff = obs - calculated[i];
      return sum + diff * diff;
    }, 0);
    
    return Math.sqrt(sumSquaredDiff / observed.length);
  };

  const processData = useCallback(() => {
    if (data.length === 0) return;
    
    setLoading(true);
    
    try {
      const processedResults = data.map((row, index) => {
        const depth = row[0];
        const temperatures = row.slice(1);
        
        // Calcola i parametri MLS per questa profondità
        const mlsResult = calculateMLS(temperatures, parameters.timeSteps, depth);
        
        // Calcola le temperature teoriche (converti tempi in secondi per il calcolo)
        const calculatedTemps = parameters.timeSteps.map(time => 
          calculateTemperature(depth, time * 3600, mlsResult.thermalConductivity, mlsResult.darcyVelocity, mlsResult.boreholeResistance)
        );
        
        // Calcola RMS tra osservato e calcolato
        const tempRises = mlsResult.tempRises;
        const rms = calculateRMS(tempRises, calculatedTemps.slice(1));
        
        return {
          depth,
          thermalConductivity: mlsResult.thermalConductivity,
          boreholeResistance: mlsResult.boreholeResistance,
          darcyVelocity: mlsResult.darcyVelocity,
          rms,
          observedTemps: temperatures,
          calculatedTemps: calculatedTemps,
          tempRises: tempRises
        };
      });
      
      setResults(processedResults);
    } catch (error) {
      console.error('Error processing data:', error);
      alert('Errore nell\'elaborazione dei dati');
    } finally {
      setLoading(false);
    }
  }, [data, parameters]);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const lines = text.split('\n').filter(line => line.trim());
        const parsedData = lines.map(line => {
          const values = line.split(/[,;\t]/).map(val => parseFloat(val.trim()));
          return values.filter(val => !isNaN(val));
        }).filter(row => row.length >= 6); // depth + 5 temperature columns

        setData(parsedData);
      } catch (error) {
        alert('Errore nella lettura del file');
      }
    };
    reader.readAsText(file);
  };

  const exportResults = () => {
    if (!results) return;

    const csv = [
      ['Profondità (m)', 'Conducibilità Termica (W/m·K)', 'Resistenza Termica (K·m/W)', 'Velocità Darciana (m/s)', 'RMS'],
      ...results.map(r => [
        r.depth.toFixed(1),
        r.thermalConductivity.toFixed(4),
        r.boreholeResistance.toFixed(4),
        r.darcyVelocity.toExponential(3),
        r.rms ? r.rms.toFixed(4) : 'N/A'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mls_depth_analysis_results.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const chartData = results ? results.map(r => ({
    depth: r.depth,
    conducibilita: r.thermalConductivity,
    resistenza: r.boreholeResistance * 1000, // scala per visualizzazione
    velocita: r.darcyVelocity * 1e6, // scala per visualizzazione
    rms: r.rms || 0
  })) : [];

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Analisi MLS Depth-wise</h1>
        <p className="text-gray-600">Calcolo di conducibilità termica, resistenza termica e velocità darciana per profili di temperatura</p>
      </div>

      {/* Upload section */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Upload className="mr-2" size={20} />
          Caricamento Dati
        </h2>
        <div className="mb-4">
          <input
            type="file"
            accept=".csv,.txt"
            onChange={handleFileUpload}
            className="mb-2 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p className="text-sm text-gray-500">
            Formato: Prima colonna = profondità (m), colonne 2-6 = temperature nei 5 intervalli temporali
          </p>
        </div>
        {data.length > 0 && (
          <div className="text-sm text-green-600">
            ✓ Caricati {data.length} punti di misura
          </div>
        )}
      </div>

      {/* Parameters section */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Parametri di Calcolo</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Potenza (W/m)</label>
            <input
              type="number"
              value={parameters.heatPower}
              onChange={(e) => setParameters({...parameters, heatPower: parseFloat(e.target.value)})}
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Raggio sensore (m)</label>
            <input
              type="number"
              step="0.001"
              value={parameters.radius}
              onChange={(e) => setParameters({...parameters, radius: parseFloat(e.target.value)})}
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Diffusività termica (m²/s)</label>
            <input
              type="number"
              step="1e-7"
              value={parameters.thermalDiffusivity}
              onChange={(e) => setParameters({...parameters, thermalDiffusivity: parseFloat(e.target.value)})}
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Densità fluido (kg/m³)</label>
            <input
              type="number"
              value={parameters.fluidDensity}
              onChange={(e) => setParameters({...parameters, fluidDensity: parseFloat(e.target.value)})}
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
        </div>
        
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Intervalli temporali (ore)</label>
          <input
            type="text"
            value={parameters.timeSteps.join(', ')}
            onChange={(e) => {
              const steps = e.target.value.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
              setParameters({...parameters, timeSteps: steps});
            }}
            className="w-full p-2 border border-gray-300 rounded-md text-sm"
            placeholder="0.0, 2.84, 4.86, 6.86, 72.87"
          />
        </div>
      </div>

      {/* Process button */}
      <div className="mb-6">
        <button
          onClick={processData}
          disabled={data.length === 0 || loading}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
        >
          <Calculator className="mr-2" size={20} />
          {loading ? 'Elaborazione...' : 'Elabora Dati'}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Summary table */}
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-6 py-3 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold">Risultati per Profondità</h3>
              <button
                onClick={exportResults}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center text-sm"
              >
                <Download className="mr-1" size={16} />
                Esporta CSV
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-700">Profondità (m)</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700">k (W/m·K)</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700">Rb (K·m/W)</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700">v (m/s)</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700">RMS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {results.map((result, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium">{result.depth.toFixed(1)}</td>
                      <td className="px-4 py-3">{result.thermalConductivity.toFixed(4)}</td>
                      <td className="px-4 py-3">{result.boreholeResistance.toFixed(4)}</td>
                      <td className="px-4 py-3">{result.darcyVelocity.toExponential(3)}</td>
                      <td className="px-4 py-3">{result.rms ? result.rms.toFixed(4) : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <LineChart className="mr-2" size={20} />
                Conducibilità Termica vs Profondità
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsLineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="depth" label={{ value: 'Profondità (m)', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'k (W/m·K)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip formatter={(value) => [value.toFixed(4), 'k (W/m·K)']} />
                  <Line type="monotone" dataKey="conducibilita" stroke="#2563eb" strokeWidth={2} dot={{ r: 4 }} />
                </RechartsLineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Velocità Darciana vs Profondità</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsLineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="depth" label={{ value: 'Profondità (m)', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'v (×10⁻⁶ m/s)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip formatter={(value) => [(value/1e6).toExponential(3), 'v (m/s)']} />
                  <Line type="monotone" dataKey="velocita" stroke="#dc2626" strokeWidth={2} dot={{ r: 4 }} />
                </RechartsLineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Statistics */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center text-blue-800">
              <AlertCircle className="mr-2" size={20} />
              Statistiche Generali
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="font-medium text-blue-700">k media</div>
                <div>{(results.reduce((sum, r) => sum + r.thermalConductivity, 0) / results.length).toFixed(4)} W/m·K</div>
              </div>
              <div>
                <div className="font-medium text-blue-700">k min/max</div>
                <div>{Math.min(...results.map(r => r.thermalConductivity)).toFixed(4)} / {Math.max(...results.map(r => r.thermalConductivity)).toFixed(4)}</div>
              </div>
              <div>
                <div className="font-medium text-blue-700">v media</div>
                <div>{(results.reduce((sum, r) => sum + r.darcyVelocity, 0) / results.length).toExponential(3)} m/s</div>
              </div>
              <div>
                <div className="font-medium text-blue-700">RMS medio</div>
                <div>{(results.filter(r => r.rms).reduce((sum, r) => sum + r.rms, 0) / results.filter(r => r.rms).length).toFixed(4)}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MLSDepthAnalysis;