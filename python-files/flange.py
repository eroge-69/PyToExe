import React, { useState } from "react";
import "./App.css";
 
const flangeData = {
  "½": [0.38, 0.06, 0.5, 0.2343, 0.5, 0.125, 0.14, 2.754, 69.941],
  "¾": [0.44, 0.06, 0.5, 0.2343, 0.5, 0.125, 0.14, 2.874, 72.989],
  1: [0.5, 0.06, 0.5, 0.2343, 0.5, 0.125, 0.14, 2.994, 76.037],
  "1¼": [0.56, 0.06, 0.5, 0.2343, 0.5, 0.125, 0.14, 3.114, 79.085],
  "1½": [0.62, 0.06, 0.5, 0.2343, 0.5, 0.125, 0.14, 3.234, 82.133],
  2: [0.69, 0.06, 0.625, 0.2811, 0.625, 0.125, 0.14, 3.717, 94.417],
  "2½": [0.81, 0.06, 0.625, 0.2811, 0.625, 0.125, 0.14, 3.957, 100.513],
  3: [0.88, 0.06, 0.625, 0.2811, 0.625, 0.125, 0.14, 4.097, 104.069],
  4: [0.88, 0.06, 0.625, 0.2811, 0.625, 0.125, 0.14, 4.097, 104.069],
  6: [0.94, 0.06, 0.75, 0.327, 0.75, 0.125, 0.14, 4.559, 115.799],
  8: [1.06, 0.06, 0.75, 0.327, 0.75, 0.125, 0.14, 4.799, 121.895],
  10: [1.12, 0.06, 0.875, 0.375, 0.875, 0.125, 0.14, 5.265, 133.731],
  12: [1.19, 0.06, 0.875, 0.375, 0.875, 0.125, 0.14, 5.405, 137.287],
  14: [1.31, 0.06, 1, 0.375, 1, 0.125, 0.14, 5.895, 149.733],
  16: [1.38, 0.06, 1, 0.375, 1, 0.125, 0.14, 6.035, 153.289],
  18: [1.5, 0.06, 1.125, 0.42, 1.125, 0.125, 0.14, 6.615, 168.021],
  20: [1.62, 0.06, 1.125, 0.42, 1.125, 0.125, 0.14, 6.855, 174.117],
  24: [1.81, 0.06, 1.25, 0.42, 1.25, 0.125, 0.14, 7.485, 190.119],
};
 
const labels = [
  "Flange Thickness (T)",
  "+RF",
  "Stud Diameter (in)",
  "Stud Pitch (in)",
  "Nut Thickness (in)",
  "Gasket Thickness (in)",
  "Washer Thickness (in)",
  "Stud Length (in)",
  "Stud Length (mm)",
];
 
export default function App() {
  const [selectedNPS, setSelectedNPS] = useState("1");
  const values = flangeData[selectedNPS] || [];
 
  return (
    <div className="container">
      <h1 className="title">ASME B 16.5 Stud Calculator</h1>
 
      <label htmlFor="nps-select" className="label">
        Select NPS:
        <select
          id="nps-select"
          value={selectedNPS}
          onChange={(e) => setSelectedNPS(e.target.value)}
          className="select"
        >
          {Object.keys(flangeData).map((nps) => (
            <option key={nps} value={nps}>
              {nps}
            </option>
          ))}
        </select>
      </label>