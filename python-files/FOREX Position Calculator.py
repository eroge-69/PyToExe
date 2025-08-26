import React, { useState, useEffect, useMemo } from 'react';
import { Calculator, DollarSign, Percent, ArrowDown, Scale, HandCoins, TrendingUp, LineChart, TrendingDown } from 'lucide-react'; // Using lucide-react for icons

// Main App component
const App = () => {
  // State variables for inputs
  const [accountBalance, setAccountBalance] = useState(10000);
  const [riskPercentage, setRiskPercentage] = useState(1.0); // e.g., 1.0 for 1%
  const [stopLossPips, setStopLossPips] = useState(20);
  const [selectedPair, setSelectedPair] = useState('EURUSD'); // Default selected pair

  // Simulated data for major FOREX pairs (mock current prices and standard lot pip values for a USD account)
  // In a real application, these would come from a live data API.
  const majorPairsData = useMemo(() => ({
    'EURUSD': { currentPrice: 1.0850, pipValue: 10.00 }, // $10 per standard lot for 4-decimal USD quote pairs
    'GBPUSD': { currentPrice: 1.2710, pipValue: 10.00 },
    'USDJPY': { currentPrice: 157.80, pipValue: 6.33 }, // (0.01 / USDJPY_rate) * 100,000 units = 1000 JPY. 1000 JPY / 157.80 = ~6.33 USD
    'AUDUSD': { currentPrice: 0.6650, pipValue: 10.00 },
    'USDCAD': { currentPrice: 1.3680, pipValue: 7.31 }, // (0.0001 * 100,000) = 10 CAD. 10 CAD / 1.3680 = ~7.31 USD
    'USDCHF': { currentPrice: 0.8950, pipValue: 11.17 }, // (0.0001 * 100,000) = 10 CHF. 10 CHF / 0.8950 = ~11.17 USD
    'NZDUSD': { currentPrice: 0.6120, pipValue: 10.00 },
    'EURJPY': { currentPrice: 171.15, pipValue: 5.84 }, // (0.01 * 100,000) = 1000 JPY. 1000 JPY / USDJPY_mock_rate (e.g., 171.15) = ~5.84 USD
  }), []);

  const currentPairData = majorPairsData[selectedPair];
  const pipValuePerPip = currentPairData ? currentPairData.pipValue : 0;
  const currentPrice = currentPairData ? currentPairData.currentPrice : 0;


  // State variables for calculated outputs
  const [riskAmount, setRiskAmount] = useState(0);
  const [lotSize, setLotSize] = useState(0);
  const [message, setMessage] = useState('');
  const [tradeActionMessage, setTradeActionMessage] = useState(''); // New state for trade action messages

  // Function to calculate trading position
  const calculatePosition = () => {
    // Basic validation
    if (accountBalance <= 0 || riskPercentage <= 0 || stopLossPips <= 0 || pipValuePerPip <= 0) {
      setMessage("Please ensure all input values are positive numbers and a valid pair is selected.");
      setRiskAmount(0);
      setLotSize(0);
      setTradeActionMessage(''); // Clear trade action message on error
      return;
    }

    // Calculate risk amount
    const calculatedRiskAmount = accountBalance * (riskPercentage / 100);
    setRiskAmount(calculatedRiskAmount);

    // Calculate lot size
    // Formula: Lot Size = Risk Amount / (Stop Loss in Pips * Pip Value Per Pip Per Standard Lot)
    const calculatedLotSize = calculatedRiskAmount / (stopLossPips * pipValuePerPip);
    setLotSize(calculatedLotSize);
    setMessage(''); // Clear any previous messages
    setTradeActionMessage(''); // Clear trade action message when re-calculating
  };

  // Handler for Buy/Sell buttons
  const handleTradeAction = (actionType) => {
    if (lotSize > 0) {
      setTradeActionMessage(
        `Initiated a ${actionType} order for ${lotSize.toFixed(3)} lots of ${selectedPair}. (Simulated)`
      );
    } else {
      setTradeActionMessage("Please calculate a valid lot size first.");
    }
  };

  // Recalculate whenever input values or selected pair changes
  useEffect(() => {
    calculatePosition();
  }, [accountBalance, riskPercentage, stopLossPips, selectedPair, pipValuePerPip]); // Added selectedPair and pipValuePerPip as dependencies

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 to-purple-800 text-white p-4 sm:p-8 flex flex-col lg:flex-row items-center justify-center font-sans gap-8">
      {/* Calculator Section */}
      <div className="bg-gray-800 p-6 sm:p-8 rounded-xl shadow-2xl w-full max-w-lg space-y-6 border border-indigo-700">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-center text-indigo-300 mb-6">
          <Calculator className="inline-block mr-3 text-indigo-400" size={36} />
          FOREX Position Calculator
        </h1>

        {/* Input fields */}
        <div className="space-y-4">
          {/* Account Balance */}
          <div className="flex items-center bg-gray-700 rounded-lg p-3 shadow-inner">
            <DollarSign className="text-green-400 mr-3" size={24} />
            <label htmlFor="accountBalance" className="sr-only">Account Balance</label>
            <input
              type="number"
              id="accountBalance"
              value={accountBalance}
              onChange={(e) => setAccountBalance(parseFloat(e.target.value) || 0)}
              className="flex-grow bg-transparent border-none text-white focus:ring-0 text-lg placeholder-gray-400"
              placeholder="Account Balance"
              aria-label="Account Balance"
              step="100"
            />
          </div>

          {/* Risk Percentage */}
          <div className="flex items-center bg-gray-700 rounded-lg p-3 shadow-inner">
            <Percent className="text-red-400 mr-3" size={24} />
            <label htmlFor="riskPercentage" className="sr-only">Risk Percentage (%)</label>
            <input
              type="number"
              id="riskPercentage"
              value={riskPercentage}
              onChange={(e) => setRiskPercentage(parseFloat(e.target.value) || 0)}
              className="flex-grow bg-transparent border-none text-white focus:ring-0 text-lg placeholder-gray-400"
              placeholder="Risk Percentage (%)"
              aria-label="Risk Percentage"
              step="0.1"
            />
          </div>

          {/* Stop Loss in Pips */}
          <div className="flex items-center bg-gray-700 rounded-lg p-3 shadow-inner">
            <ArrowDown className="text-blue-400 mr-3" size={24} />
            <label htmlFor="stopLossPips" className="sr-only">Stop Loss (Pips)</label>
            <input
              type="number"
              id="stopLossPips"
              value={stopLossPips}
              onChange={(e) => setStopLossPips(parseFloat(e.target.value) || 0)}
              className="flex-grow bg-transparent border-none text-white focus:ring-0 text-lg placeholder-gray-400"
              placeholder="Stop Loss (Pips)"
              aria-label="Stop Loss in Pips"
              step="1"
            />
          </div>

          {/* Trading Pair Selection */}
          <div className="flex items-center bg-gray-700 rounded-lg p-3 shadow-inner">
            <LineChart className="text-purple-400 mr-3" size={24} />
            <label htmlFor="tradingPair" className="sr-only">Select Trading Pair</label>
            <select
              id="tradingPair"
              value={selectedPair}
              onChange={(e) => setSelectedPair(e.target.value)}
              className="flex-grow bg-transparent border-none text-white focus:ring-0 text-lg appearance-none cursor-pointer"
              aria-label="Select Trading Pair"
            >
              {Object.keys(majorPairsData).map((pair) => (
                <option key={pair} value={pair} className="bg-gray-700 text-white">
                  {pair}
                </option>
              ))}
            </select>
          </div>

          {/* Pip Value per Pip (Dynamic Display) */}
          <div className="flex justify-between items-center bg-gray-700 rounded-lg p-3 shadow-inner">
            <span className="text-gray-300 flex items-center">
              <HandCoins className="mr-3 text-yellow-400" size={24} /> Pip Value per Lot (USD):
            </span>
            <span className="font-bold text-yellow-300 text-lg">${pipValuePerPip.toFixed(2)}</span>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={calculatePosition}
          className="w-full bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-bold py-3 px-4 rounded-lg shadow-lg transition duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-900 mb-4"
        >
          Calculate Trading Position
        </button>

        {/* Buy and Sell Buttons */}
        <div className="flex gap-4">
          <button
            onClick={() => handleTradeAction('Buy')}
            className="flex-1 bg-green-600 hover:bg-green-700 active:bg-green-800 text-white font-bold py-3 px-4 rounded-lg shadow-lg transition duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900 flex items-center justify-center"
          >
            <TrendingUp className="mr-2" size={20} /> Buy ({lotSize.toFixed(3)} Lots)
          </button>
          <button
            onClick={() => handleTradeAction('Sell')}
            className="flex-1 bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold py-3 px-4 rounded-lg shadow-lg transition duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-900 flex items-center justify-center"
          >
            <TrendingDown className="mr-2" size={20} /> Sell ({lotSize.toFixed(3)} Lots)
          </button>
        </div>


        {/* Display Results */}
        <div className="bg-gray-700 rounded-xl p-5 shadow-lg border border-gray-600 space-y-3 mt-6">
          <h2 className="text-xl font-semibold text-indigo-300 mb-3 text-center">Calculated Results</h2>
          {message && (
            <p className="text-red-400 text-center text-sm font-medium mb-2">{message}</p>
          )}
          {tradeActionMessage && ( // Display trade action message
            <p className="text-green-300 text-center text-sm font-medium mb-2">{tradeActionMessage}</p>
          )}
          <div className="flex justify-between items-center py-2 border-b border-gray-600 last:border-b-0">
            <span className="text-gray-300 flex items-center">
              <DollarSign className="mr-2 text-green-300" size={18} /> Risk Amount:
            </span>
            <span className="font-bold text-green-500 text-xl">${riskAmount.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-300 flex items-center">
              <Scale className="mr-2 text-blue-300" size={18} /> Recommended Lot Size:
            </span>
            <span className="font-bold text-yellow-500 text-xl">{lotSize.toFixed(3)}</span>
          </div>
        </div>

        {/* Note on Lot Sizes */}
        <p className="text-center text-gray-400 text-sm mt-4">
          <span className="font-semibold">Note:</span> 1 Standard Lot = 100,000 units, 1 Mini Lot = 10,000 units, 1 Micro Lot = 1,000 units.
        </p>
      </div>

      {/* Live Data & Chart Simulation Section */}
      <div className="bg-gray-800 p-6 sm:p-8 rounded-xl shadow-2xl w-full max-w-lg space-y-6 border border-indigo-700 flex flex-col justify-between">
        <div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-center text-indigo-300 mb-6">
            <TrendingUp className="inline-block mr-3 text-indigo-400" size={36} />
            {selectedPair} Live Data
          </h2>

          <div className="bg-gray-700 rounded-xl p-5 shadow-lg border border-gray-600 space-y-3 mb-6">
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-300 text-lg flex items-center">
                Current Price:
              </span>
              <span className="font-bold text-green-400 text-3xl">
                {currentPrice.toFixed(4)}
                {selectedPair.includes('JPY') && <span className="text-lg ml-1"> (2-decimal)</span>}
                {!selectedPair.includes('JPY') && <span className="text-lg ml-1"> (4-decimal)</span>}
              </span>
            </div>
            <p className="text-gray-400 text-sm text-center italic">
              (This price is simulated and does not reflect real-time market data)
            </p>
          </div>

          <h3 className="text-2xl font-semibold text-indigo-300 mb-4 text-center">
            Trading Chart (Simulated)
          </h3>
          <div className="w-full h-64 bg-gray-700 rounded-lg flex items-center justify-center text-gray-500 text-center border-dashed border-2 border-gray-600 p-4">
            <p>
              Chart for {selectedPair} would appear here. <br />
              In a real application, a charting library (e.g., Chart.js, Highcharts)
              would render live or historical data fetched from a FOREX API.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;