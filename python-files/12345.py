# Code Refactored
```javascript
import { useState } from 'react';
import { Button } from "/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "/components/ui/card";
import { Shield, Clock, Users, Check, X, AlertTriangle, HardDrive } from "lucide-react";

interface DiskHealthResult {
  overallHealth: 'healthy' | 'warning' | 'critical';
  temperature: number;
  powerOnHours: number;
  startStopCycles: number;
  readErrorRate: number;
  reallocatedSectors: number;
  pendingSectors: number;
  lastCheck: string;
}

export default function HardDiskHealthCheck() {
  const [isChecking, setIsChecking] = useState(false);
  const [healthResult, setHealthResult] = useState<DiskHealthResult | null>(null);

  const simulateHealthCheck = (): DiskHealthResult => {
    const random = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

    const healthMetrics = {
      temperature: random(35, 65),
      powerOnHours: random(1000, 50000),
      startStopCycles: random(100, 10000),
      readErrorRate: random(0, 100),
      reallocatedSectors: random(0, 50),
      pendingSectors: random(0, 20),
    };

    const overallHealth = determineHealthStatus(healthMetrics);

    return {
      ...healthMetrics,
      overallHealth,
      lastCheck: new Date().toLocaleString(),
    };
  };

  const determineHealthStatus = (metrics: Omit<DiskHealthResult, 'overallHealth' | 'lastCheck'>): 'healthy' | 'warning' | 'critical' => {
    if (metrics.temperature > 60 || metrics.reallocatedSectors > 30 || metrics.pendingSectors > 15 || metrics.readErrorRate > 80) {
      return 'critical';
    }
    if (metrics.temperature > 55 || metrics.reallocatedSectors > 10 || metrics.pendingSectors > 5 || metrics.readErrorRate > 50) {
      return 'warning';
    }
    return 'healthy';
  };

  const handleHealthCheck = async () => {
    setIsChecking(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    const result = simulateHealthCheck();
    setHealthResult(result);
    setIsChecking(false);
  };

  const getHealthIcon = (health: string) => {
    const icons = {
      healthy: <Check className="w-6 h-6 text-green-500" />,
      warning: <AlertTriangle className="w-6 h-6 text-yellow-500" />,
      critical: <X className="w-6 h-6 text-red-500" />,
    };
    return icons[health] || null;
  };

  const getHealthColor = (health: string) => {
    const colors = {
      healthy: 'text-green-600 bg-green-50',
      warning: 'text-yellow-600 bg-yellow-50',
      critical: 'text-red-600 bg-red-50',
    };
    return colors[health] || '';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HardDrive className="w-6 h-6" />
              AI Hard Disk Health Check
            </CardTitle>
            <CardDescription>
              Monitor your hard disk health with AI-powered diagnostics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={handleHealthCheck} 
              disabled={isChecking}
              className="w-full"
            >
              {isChecking ? 'Checking...' : 'Run Health Check'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
