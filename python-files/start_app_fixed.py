#!/usr/bin/env python3
"""
CleanerApp - Fixed Version (No Loadscreen Blocking)
"""

import os
import sys
import tempfile
from pathlib import Path


# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    from cleaner import SystemCleaner
    from api import CleanerAPI
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install dependencies first:")
    print("pip install pywebview psutil send2trash")
    input("Press Enter to exit...")
    sys.exit(1)

def create_simple_html():
    """Create HTML interface with guaranteed loadscreen exit"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CleanerApp - Advanced System Cleaner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e);
            color: white;
            overflow-x: hidden;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        
        /* Loadscreen - GUARANTEED TO DISAPPEAR */
        .loadscreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #0f172a, #1e293b);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.5s ease-out;
        }
        
        .loadscreen.hidden {
            opacity: 0;
            pointer-events: none;
        }
        
        .logo {
            width: 100px;
            height: 100px;
            border: 3px solid #38bdf8;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            background: rgba(56, 189, 248, 0.1);
            animation: spin 2s linear infinite;
            margin-bottom: 30px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            font-size: 24px;
            color: #38bdf8;
            margin-bottom: 10px;
        }
        
        .loading-subtitle {
            color: #64748b;
            margin-bottom: 20px;
        }
        
        .countdown {
            color: #fbbf24;
            font-size: 18px;
            font-weight: bold;
        }
        
        /* Main App */
        .main-app {
            opacity: 0;
            transition: opacity 0.5s ease-in;
            min-height: 100vh;
            padding: 20px;
        }
        
        .main-app.visible {
            opacity: 1;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: transparent;
            padding: 20px;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .app-title {
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8, #0ea5e9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .app-subtitle {
            font-size: 18px;
            color: #94a3b8;
            margin-bottom: 30px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #64748b;
            text-transform: uppercase;
        }
        
        .buttons-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .btn {
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            color: white;
            border: none;
            padding: 18px 24px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ef4444, #dc2626);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #f59e0b, #d97706);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #10b981, #059669);
        }
        
        .results {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 30px;
            margin-top: 30px;
            min-height: 300px;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #64748b;
        }
        
        .footer-brand {
            color: #38bdf8;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <!-- Loadscreen with GUARANTEED exit -->
    <div class="loadscreen" id="loadscreen">
        <div class="logo">🧹</div>
        <div class="loading-text">CleanerApp</div>
        <div class="loading-subtitle">Advanced System Cleaner</div>
        <div class="countdown" id="countdown">Loading... 3</div>
    </div>

    <!-- Main App -->
    <div class="main-app" id="mainApp">
        <div class="container">
            <div class="header">
                <h1 class="app-title">🧹 CleanerApp</h1>
                <p class="app-subtitle">Advanced system cleaner for Windows. Safely remove temporary files and free up disk space.</p>
            </div>
            
            <!-- System Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" style="color: #38bdf8;" id="diskUsage">--</div>
                    <div class="stat-label">Disk Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #10b981;" id="freeSpace">--</div>
                    <div class="stat-label">Free Space</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #f59e0b;" id="tempFiles">--</div>
                    <div class="stat-label">Temp Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #ef4444;" id="tempSize">--</div>
                    <div class="stat-label">Temp Size</div>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="buttons-grid">
                <button class="btn" onclick="scanSystem()">🔍 Scan System</button>
                <button class="btn btn-warning" onclick="dryRun()" id="dryRunBtn" disabled>🧪 Dry Run</button>
                <button class="btn btn-success" onclick="cleanTemp()" id="cleanTempBtn" disabled>🗑️ Clean Temp</button>
                <button class="btn btn-danger" onclick="deepClean()" id="deepCleanBtn" disabled>🔥 Deep Clean C:</button>
                <button class="btn" onclick="refreshStats()" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);">🔄 Refresh Stats</button>
                <button class="btn" onclick="cleanBrowserCache()" style="background: linear-gradient(135deg, #06b6d4, #0891b2);">🌐 Clean Browsers</button>
                <button class="btn" onclick="cleanRecycleBin()" style="background: linear-gradient(135deg, #84cc16, #65a30d);">🗑️ Empty Recycle</button>
                <button class="btn" onclick="cleanMemoryDumps()" style="background: linear-gradient(135deg, #ef4444, #dc2626);">💾 Memory Dumps</button>
                <button class="btn" onclick="cleanDownloadCache()" style="background: linear-gradient(135deg, #14b8a6, #0d9488);">📥 Download Cache</button>
                <button class="btn" onclick="cleanGameCache()" style="background: linear-gradient(135deg, #a855f7, #9333ea);">🎮 Game Cache</button>
                <button class="btn" onclick="cleanFontCache()" style="background: linear-gradient(135deg, #f97316, #ea580c);">🔤 Font Cache</button>
                <button class="btn" onclick="toggleAutoStart()" id="autoStartBtn" style="background: linear-gradient(135deg, #f59e0b, #d97706);">⚡ Auto-Start</button>
                <button class="btn" onclick="showLanguageSelector()" style="background: linear-gradient(135deg, #6366f1, #4f46e5);">🌍 Language</button>
            </div>
            
            <!-- Results Panel -->
            <div class="results" id="results">
                <div style="text-align: center; color: #64748b; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🚀</div>
                    <h3 style="margin-bottom: 10px;">Ready to Clean</h3>
                    <p>Click "Scan System" to analyze temporary files and system cache.</p>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                    <div>Copyright © <span class="footer-brand">Jonhftn</span> - Advanced System Optimization</div>
                    <a href="https://instagram.com/jonhftn" target="_blank" style="color: #e1306c; text-decoration: none; display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: rgba(225, 48, 108, 0.1); border-radius: 20px; transition: all 0.3s ease;" onmouseover="this.style.background='rgba(225, 48, 108, 0.2)'" onmouseout="this.style.background='rgba(225, 48, 108, 0.1)'">
                        📸 @Jonhftn
                    </a>
                </div>
            </div>
        </div>
    </div>

    <script>
        let scanResults = null;
        let systemStats = null;
        let currentLanguage = 'en';
        let translations = {};
        
        // GUARANTEED LOADSCREEN EXIT - No blocking possible!
        window.addEventListener('load', function() {
            let countdown = 3;
            const countdownEl = document.getElementById('countdown');
            
            // Update countdown every second
            const countdownInterval = setInterval(() => {
                countdown--;
                countdownEl.textContent = `Loading... ${countdown}`;
                
                if (countdown <= 0) {
                    clearInterval(countdownInterval);
                    // FORCE SHOW APP - NO EXCEPTIONS!
                    document.getElementById('loadscreen').classList.add('hidden');
                    document.getElementById('mainApp').classList.add('visible');
                    
                    // Try to load stats after showing app
                    setTimeout(loadSystemStats, 500);
                    
                    // Load default translations
                    setTimeout(loadDefaultTranslations, 1000);
                }
            }, 1000);
        });
        
        async function loadSystemStats() {
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.get_disk_info();
                    if (response.success) {
                        systemStats = response.data;
                        updateStatsDisplay();
                    }
                }
            } catch (error) {
                console.log('Stats loading failed, using defaults');
            }
        }
        
        async function loadDefaultTranslations() {
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.get_translations();
                    if (response.success) {
                        translations = response.data;
                        console.log('Default translations loaded');
                    }
                }
            } catch (error) {
                console.log('Translations loading failed, using English');
            }
        }
        
        function updateStatsDisplay() {
            if (systemStats) {
                document.getElementById('diskUsage').textContent = systemStats.percent + '%';
                document.getElementById('freeSpace').textContent = systemStats.free_gb + ' GB';
            }
            
            if (scanResults) {
                document.getElementById('tempFiles').textContent = scanResults.total_files;
                document.getElementById('tempSize').textContent = scanResults.total_size_mb + ' MB';
            }
        }
        
        function showLoading(message) {
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 24px; margin-bottom: 20px;">⏳</div>
                    <h3 style="color: #38bdf8; margin-bottom: 10px;">Processing...</h3>
                    <p style="color: #64748b;">${message}</p>
                </div>
            `;
        }
        
        function showError(message) {
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">❌</div>
                    <h3 style="color: #ef4444; margin-bottom: 10px;">Error</h3>
                    <p style="color: #64748b;">${message}</p>
                </div>
            `;
        }
        
        async function scanSystem() {
            showLoading('Scanning temporary files...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.scan();
                    if (response.success) {
                        scanResults = response.data;
                        systemStats = response.data.disk_info;
                        updateStatsDisplay();
                        displayScanResults(scanResults);
                        
                        // Enable buttons
                        document.getElementById('dryRunBtn').disabled = false;
                        document.getElementById('cleanTempBtn').disabled = false;
                        document.getElementById('deepCleanBtn').disabled = false;
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available. Please run through the desktop app.');
                }
            } catch (error) {
                showError('Failed to scan system: ' + error.message);
            }
        }
        
        async function dryRun() {
            showLoading('Simulating cleanup...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.dry_run();
                    if (response.success) {
                        displayDryRunResults(response.data);
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to perform dry run: ' + error.message);
            }
        }
        
        async function cleanTemp() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🗑️</div>
                    <h3 style="color: #10b981; margin-bottom: 20px;">Clean Temporary Files</h3>
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #10b981; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>🗂️ Cleans <strong>%TEMP%</strong> folder (user temporary files)</li>
                            <li>🖥️ Cleans <strong>C:\\Windows\\Temp</strong> (system temporary files)</li>
                            <li>⚡ Optionally cleans <strong>Prefetch</strong> folder (requires admin)</li>
                            <li>♻️ Files are moved to <strong>Recycle Bin</strong> (recoverable)</li>
                            <li>🔒 Protected system files are automatically skipped</li>
                        </ul>
                        <div style="background: rgba(251, 191, 36, 0.1); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #fbbf24;">⚠️ Safe Operation:</strong> This only removes temporary files that are safe to delete.
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('🗑️ Clean temporary files?\\n\\nFiles will be moved to Recycle Bin (recoverable).')) {
                return;
            }
            
            const includePrefetch = confirm('⚠️ Include Prefetch folder?\\n\\nRequires admin privileges.');
            showLoading('Cleaning temporary files...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.clean(includePrefetch);
                    if (response.success) {
                        displayCleanResults(response.data);
                        
                        // Update stats immediately after cleaning
                        await loadSystemStats();
                        
                        // Re-scan to get updated file counts
                        showLoading('Updating scan results...');
                        const scanResponse = await pywebview.api.scan();
                        if (scanResponse.success) {
                            scanResults = scanResponse.data;
                            systemStats = scanResponse.data.disk_info;
                            updateStatsDisplay();
                            
                            // Show success message with updated stats
                            document.getElementById('results').innerHTML = `
                                <div style="text-align: center; padding: 40px;">
                                    <div style="font-size: 48px; margin-bottom: 20px;">✅</div>
                                    <h3 style="color: #10b981; margin-bottom: 20px;">Cleaning Complete!</h3>
                                    <div style="background: rgba(34, 197, 94, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                        <div style="font-size: 24px; font-weight: bold; color: #22c55e;">
                                            ${response.data.total_freed_mb} MB Freed
                                        </div>
                                    </div>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px;">
                                        <div style="background: rgba(56, 189, 248, 0.2); padding: 15px; border-radius: 8px;">
                                            <div style="font-size: 18px; font-weight: bold; color: #38bdf8;">${scanResults.total_size_mb} MB</div>
                                            <div style="color: #64748b; font-size: 12px;">Remaining Temp</div>
                                        </div>
                                        <div style="background: rgba(34, 197, 94, 0.2); padding: 15px; border-radius: 8px;">
                                            <div style="font-size: 18px; font-weight: bold; color: #22c55e;">${scanResults.total_files}</div>
                                            <div style="color: #64748b; font-size: 12px;">Remaining Files</div>
                                        </div>
                                        <div style="background: rgba(16, 185, 129, 0.2); padding: 15px; border-radius: 8px;">
                                            <div style="font-size: 18px; font-weight: bold; color: #10b981;">${systemStats.free_gb} GB</div>
                                            <div style="color: #64748b; font-size: 12px;">Free Space</div>
                                        </div>
                                    </div>
                                    <p style="color: #64748b; margin-top: 20px;">System statistics updated successfully!</p>
                                </div>
                            `;
                        }
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to clean system: ' + error.message);
            }
        }
        
        async function deepClean() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🔥</div>
                    <h3 style="color: #ef4444; margin-bottom: 20px;">Deep Clean System</h3>
                    <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #ef4444; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>🗂️ Cleans <strong>Windows Update cache</strong> (SoftwareDistribution)</li>
                            <li>📝 Removes <strong>system logs</strong> (CBS, DISM, DPX)</li>
                            <li>💥 Cleans <strong>error reports</strong> (WER ReportQueue)</li>
                            <li>🌐 Removes <strong>web cache</strong> (INetCache, WebCache)</li>
                            <li>📂 Cleans <strong>recent files</strong> history</li>
                        </ul>
                        <div style="background: rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #ef4444;">⚠️ Advanced Operation:</strong> This performs deeper system cleaning and may require admin privileges.
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('🔥 DEEP CLEAN WARNING\\n\\nThis will clean system cache and logs from C: drive.\\n\\nContinue?')) {
                return;
            }
            
            const confirmDangerous = confirm('⚠️ Include system directories?\\n\\nRecommended: Click Cancel for safer cleaning.');
            showLoading('Performing deep system cleaning...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.deep_clean(confirmDangerous);
                    if (response.success) {
                        displayCleanResults(response.data);
                        
                        // Update stats immediately after deep cleaning
                        await loadSystemStats();
                        
                        // Re-scan to get updated file counts
                        showLoading('Updating scan results after deep clean...');
                        const scanResponse = await pywebview.api.scan();
                        if (scanResponse.success) {
                            scanResults = scanResponse.data;
                            systemStats = scanResponse.data.disk_info;
                            updateStatsDisplay();
                            
                            // Show enhanced success message for deep clean
                            document.getElementById('results').innerHTML = `
                                <div style="text-align: center; padding: 40px;">
                                    <div style="font-size: 48px; margin-bottom: 20px;">🔥</div>
                                    <h3 style="color: #ef4444; margin-bottom: 20px;">Deep Clean Complete!</h3>
                                    <div style="background: rgba(239, 68, 68, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                        <div style="font-size: 24px; font-weight: bold; color: #ef4444;">
                                            ${response.data.total_freed_mb} MB Deep Cleaned
                                        </div>
                                    </div>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px;">
                                        <div style="background: rgba(56, 189, 248, 0.2); padding: 15px; border-radius: 8px;">
                                            <div style="font-size: 18px; font-weight: bold; color: #38bdf8;">${scanResults.total_size_mb} MB</div>
                                            <div style="color: #64748b; font-size: 12px;">Remaining Temp</div>
                                        </div>
                                        <div style="background: rgba(34, 197, 94, 0.2); padding: 15px; border-radius: 8px;">
                                            <div style="font-size: 18px; font-weight: bold; color: #22c55e;">${scanResults.total_files}</div>
                                            <div style="color: #64748b; font-size: 12px;">Remaining Files</div>
                                        </div>
                                        <div style="background: rgba(16, 185, 129, 0.2); padding: 15px; border-radius: 8px;">
                                            <div style="font-size: 18px; font-weight: bold; color: #10b981;">${systemStats.free_gb} GB</div>
                                            <div style="color: #64748b; font-size: 12px;">Free Space</div>
                                        </div>
                                        <div style="background: rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 8px;">
                                            <div style="font-size: 18px; font-weight: bold; color: #ef4444;">${systemStats.percent}%</div>
                                            <div style="color: #64748b; font-size: 12px;">Disk Usage</div>
                                        </div>
                                    </div>
                                    <p style="color: #64748b; margin-top: 20px;">Deep cleaning completed! System cache and logs removed.</p>
                                </div>
                            `;
                        }
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to perform deep clean: ' + error.message);
            }
        }
        
        async function refreshStats() {
            showLoading('Refreshing system statistics...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    // Get fresh disk info
                    await loadSystemStats();
                    
                    // Re-scan system
                    const scanResponse = await pywebview.api.scan();
                    if (scanResponse.success) {
                        scanResults = scanResponse.data;
                        systemStats = scanResponse.data.disk_info;
                        updateStatsDisplay();
                        
                        // Show updated stats
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🔄</div>
                                <h3 style="color: #8b5cf6; margin-bottom: 20px;">Statistics Refreshed!</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                                    <div style="background: rgba(56, 189, 248, 0.2); padding: 20px; border-radius: 12px;">
                                        <div style="font-size: 24px; font-weight: bold; color: #38bdf8;">${scanResults.total_size_mb} MB</div>
                                        <div style="color: #64748b;">Current Temp Size</div>
                                    </div>
                                    <div style="background: rgba(34, 197, 94, 0.2); padding: 20px; border-radius: 12px;">
                                        <div style="font-size: 24px; font-weight: bold; color: #22c55e;">${scanResults.total_files}</div>
                                        <div style="color: #64748b;">Current Temp Files</div>
                                    </div>
                                    <div style="background: rgba(16, 185, 129, 0.2); padding: 20px; border-radius: 12px;">
                                        <div style="font-size: 24px; font-weight: bold; color: #10b981;">${systemStats.free_gb} GB</div>
                                        <div style="color: #64748b;">Free Space</div>
                                    </div>
                                    <div style="background: rgba(139, 92, 246, 0.2); padding: 20px; border-radius: 12px;">
                                        <div style="font-size: 24px; font-weight: bold; color: #8b5cf6;">${systemStats.percent}%</div>
                                        <div style="color: #64748b;">Disk Usage</div>
                                    </div>
                                </div>
                                <p style="color: #64748b; margin-top: 20px;">All statistics updated to current values!</p>
                            </div>
                        `;
                        
                        // Re-enable buttons if scan was successful
                        document.getElementById('dryRunBtn').disabled = false;
                        document.getElementById('cleanTempBtn').disabled = false;
                        document.getElementById('deepCleanBtn').disabled = false;
                    } else {
                        showError('Failed to refresh scan data: ' + scanResponse.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to refresh statistics: ' + error.message);
            }
        }
        
        async function cleanBrowserCache() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🌐</div>
                    <h3 style="color: #06b6d4; margin-bottom: 20px;">Clean Browser Cache</h3>
                    <div style="background: rgba(6, 182, 212, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #06b6d4; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>🔵 Cleans <strong>Google Chrome</strong> cache and GPU cache</li>
                            <li>🦊 Cleans <strong>Mozilla Firefox</strong> cache2 folders</li>
                            <li>🔷 Cleans <strong>Microsoft Edge</strong> cache and code cache</li>
                            <li>🎭 Cleans <strong>Opera</strong> browser cache</li>
                            <li>⚡ Improves browser performance and frees disk space</li>
                        </ul>
                        <div style="background: rgba(6, 182, 212, 0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #06b6d4;">ℹ️ Note:</strong> You may need to restart browsers after cleaning. Login sessions will be preserved.
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('🌐 Clean browser cache?\\n\\nThis will clear cache from Chrome, Firefox, Edge, and Opera.')) {
                return;
            }
            
            showLoading('Cleaning browser cache...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.clean_browser_cache();
                    if (response.success) {
                        const data = response.data;
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🌐</div>
                                <h3 style="color: #06b6d4; margin-bottom: 20px;">Browser Cache Cleaned!</h3>
                                <div style="background: rgba(6, 182, 212, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #06b6d4;">
                                        ${data.total_freed_mb} MB Freed
                                    </div>
                                </div>
                                <p style="color: #64748b;">Browsers cleaned: ${data.browsers_found.join(', ')}</p>
                            </div>
                        `;
                        await loadSystemStats();
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to clean browser cache: ' + error.message);
            }
        }
        
        async function cleanRecycleBin() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🗑️</div>
                    <h3 style="color: #84cc16; margin-bottom: 20px;">Empty Recycle Bin</h3>
                    <div style="background: rgba(132, 204, 22, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #84cc16; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>🗑️ <strong>Permanently deletes</strong> all items in Recycle Bin</li>
                            <li>📁 Clears all deleted files and folders</li>
                            <li>🧹 Frees up disk space immediately</li>
                            <li>⚡ Uses Windows PowerShell for safe operation</li>
                            <li>🔒 Secure deletion (cannot be recovered)</li>
                        </ul>
                        <div style="background: rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #ef4444;">⚠️ Warning:</strong> Files will be permanently deleted and cannot be recovered!
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('🗑️ Empty Recycle Bin?\\n\\nThis will permanently delete all items in the recycle bin.')) {
                return;
            }
            
            showLoading('Emptying recycle bin...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.clean_recycle_bin();
                    if (response.success) {
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🗑️</div>
                                <h3 style="color: #84cc16; margin-bottom: 20px;">Recycle Bin Emptied!</h3>
                                <p style="color: #64748b;">All items in recycle bin have been permanently deleted.</p>
                            </div>
                        `;
                        await loadSystemStats();
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to empty recycle bin: ' + error.message);
            }
        }
        
        async function toggleAutoStart() {
            showLoading('Checking auto-start status...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const statusResponse = await pywebview.api.is_autostart_enabled();
                    if (statusResponse.success) {
                        const isEnabled = statusResponse.data.enabled;
                        
                        if (isEnabled) {
                            if (confirm('⚡ Auto-start is currently ENABLED\\n\\nDisable auto-start on Windows boot?')) {
                                const response = await pywebview.api.disable_autostart();
                                if (response.success) {
                                    document.getElementById('autoStartBtn').textContent = '⚡ Enable Auto-Start';
                                    document.getElementById('results').innerHTML = `
                                        <div style="text-align: center; padding: 40px;">
                                            <div style="font-size: 48px; margin-bottom: 20px;">⚡</div>
                                            <h3 style="color: #f59e0b; margin-bottom: 20px;">Auto-Start Disabled</h3>
                                            <p style="color: #64748b;">CleanerApp will no longer start automatically with Windows.</p>
                                        </div>
                                    `;
                                }
                            }
                        } else {
                            if (confirm('⚡ Auto-start is currently DISABLED\\n\\nEnable auto-start on Windows boot?')) {
                                const response = await pywebview.api.enable_autostart();
                                if (response.success) {
                                    document.getElementById('autoStartBtn').textContent = '⚡ Disable Auto-Start';
                                    document.getElementById('results').innerHTML = `
                                        <div style="text-align: center; padding: 40px;">
                                            <div style="font-size: 48px; margin-bottom: 20px;">⚡</div>
                                            <h3 style="color: #f59e0b; margin-bottom: 20px;">Auto-Start Enabled</h3>
                                            <p style="color: #64748b;">CleanerApp will now start automatically with Windows.</p>
                                        </div>
                                    `;
                                }
                            }
                        }
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to toggle auto-start: ' + error.message);
            }
        }
        
        async function cleanMemoryDumps() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">💾</div>
                    <h3 style="color: #ef4444; margin-bottom: 20px;">Clean Memory Dumps</h3>
                    <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #ef4444; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>💥 Removes <strong>crash dump files</strong> (C:\\Windows\\Minidump)</li>
                            <li>🗂️ Cleans <strong>memory dumps</strong> (MEMORY.DMP)</li>
                            <li>📊 Removes <strong>error reports</strong> (WER ReportQueue)</li>
                            <li>🔍 Cleans <strong>local crash dumps</strong> (%LOCALAPPDATA%\\CrashDumps)</li>
                            <li>🧹 Frees up significant disk space</li>
                        </ul>
                        <div style="background: rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #ef4444;">ℹ️ Safe:</strong> These files are only used for debugging and can be safely removed.
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('💾 Clean memory dumps?\\n\\nThis will remove crash dumps and error reports.')) {
                return;
            }
            
            showLoading('Cleaning memory dumps...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.clean_memory_dumps();
                    if (response.success) {
                        const data = response.data;
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">💾</div>
                                <h3 style="color: #ef4444; margin-bottom: 20px;">Memory Dumps Cleaned!</h3>
                                <div style="background: rgba(239, 68, 68, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #ef4444;">
                                        ${data.total_freed_mb} MB Freed
                                    </div>
                                </div>
                                <p style="color: #64748b;">Crash dumps and error reports removed.</p>
                            </div>
                        `;
                        await loadSystemStats();
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to clean memory dumps: ' + error.message);
            }
        }
        
        async function cleanDownloadCache() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">📥</div>
                    <h3 style="color: #14b8a6; margin-bottom: 20px;">Clean Download Cache</h3>
                    <div style="background: rgba(20, 184, 166, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #14b8a6; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>📥 Removes <strong>temporary downloads</strong> (.tmp, .crdownload, .part)</li>
                            <li>🌐 Cleans <strong>Internet Explorer cache</strong> (INetCache)</li>
                            <li>📁 Removes <strong>temporary internet files</strong></li>
                            <li>🧹 Cleans incomplete/failed downloads</li>
                            <li>⚡ Frees up download folder space</li>
                        </ul>
                        <div style="background: rgba(20, 184, 166, 0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #14b8a6;">ℹ️ Safe:</strong> Only removes temporary and incomplete download files.
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('📥 Clean download cache?\\n\\nThis will remove temporary download files and browser cache.')) {
                return;
            }
            
            showLoading('Cleaning download cache...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.clean_download_cache();
                    if (response.success) {
                        const data = response.data;
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">📥</div>
                                <h3 style="color: #14b8a6; margin-bottom: 20px;">Download Cache Cleaned!</h3>
                                <div style="background: rgba(20, 184, 166, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #14b8a6;">
                                        ${data.total_freed_mb} MB Freed
                                    </div>
                                </div>
                                <p style="color: #64748b;">Temporary downloads and internet cache removed.</p>
                            </div>
                        `;
                        await loadSystemStats();
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to clean download cache: ' + error.message);
            }
        }
        
        async function cleanGameCache() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🎮</div>
                    <h3 style="color: #a855f7; margin-bottom: 20px;">Clean Game Cache</h3>
                    <div style="background: rgba(168, 85, 247, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #a855f7; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>🎯 Cleans <strong>Steam</strong> appcache folder</li>
                            <li>🎪 Cleans <strong>Epic Games Launcher</strong> webcache</li>
                            <li>⚔️ Cleans <strong>Battle.net</strong> cache files</li>
                            <li>🎨 Cleans <strong>Origin</strong> cache folder</li>
                            <li>⚡ Improves game launcher performance</li>
                        </ul>
                        <div style="background: rgba(168, 85, 247, 0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #a855f7;">🎮 Gaming:</strong> This won't affect your games or saves, only launcher cache.
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('🎮 Clean game cache?\\n\\nThis will clear cache from Steam, Epic Games, Battle.net, and Origin.')) {
                return;
            }
            
            showLoading('Cleaning game cache...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.clean_game_cache();
                    if (response.success) {
                        const data = response.data;
                        const platforms = data.cleaned.map(item => item.platform).join(', ');
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🎮</div>
                                <h3 style="color: #a855f7; margin-bottom: 20px;">Game Cache Cleaned!</h3>
                                <div style="background: rgba(168, 85, 247, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #a855f7;">
                                        ${data.total_freed_mb} MB Freed
                                    </div>
                                </div>
                                <p style="color: #64748b;">Platforms cleaned: ${platforms || 'None found'}</p>
                            </div>
                        `;
                        await loadSystemStats();
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to clean game cache: ' + error.message);
            }
        }
        
        async function cleanFontCache() {
            // Show description first
            document.getElementById('results').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🔤</div>
                    <h3 style="color: #f97316; margin-bottom: 20px;">Clean Font Cache</h3>
                    <div style="background: rgba(249, 115, 22, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #f97316; margin-bottom: 15px;">📋 What this function does:</h4>
                        <ul style="color: #64748b; line-height: 1.8;">
                            <li>🔤 Cleans <strong>Windows font cache</strong> files</li>
                            <li>📁 Removes <strong>font service cache</strong> (LocalService)</li>
                            <li>⚡ Fixes font rendering issues</li>
                            <li>🔄 Forces font cache rebuild</li>
                            <li>🎨 Improves text display performance</li>
                        </ul>
                        <div style="background: rgba(249, 115, 22, 0.2); padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <strong style="color: #f97316;">🔄 Note:</strong> Font cache will be automatically rebuilt when needed.
                        </div>
                    </div>
                </div>
            `;
            
            if (!confirm('🔤 Clean font cache?\\n\\nThis will clear Windows font cache files.')) {
                return;
            }
            
            showLoading('Cleaning font cache...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.clean_font_cache();
                    if (response.success) {
                        const data = response.data;
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🔤</div>
                                <h3 style="color: #f97316; margin-bottom: 20px;">Font Cache Cleaned!</h3>
                                <div style="background: rgba(249, 115, 22, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #f97316;">
                                        ${data.total_freed_mb} MB Freed
                                    </div>
                                </div>
                                <p style="color: #64748b;">Windows font cache cleared.</p>
                            </div>
                        `;
                        await loadSystemStats();
                    } else {
                        showError(response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to clean font cache: ' + error.message);
            }
        }
        
        async function showLanguageSelector() {
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.get_languages();
                    if (response.success) {
                        const languages = response.data;
                        let languageButtons = '';
                        
                        for (const [code, name] of Object.entries(languages)) {
                            languageButtons += `
                                <button onclick="changeLanguage('${code}')" style="
                                    background: linear-gradient(135deg, #6366f1, #4f46e5);
                                    color: white;
                                    border: none;
                                    padding: 15px 25px;
                                    margin: 10px;
                                    border-radius: 12px;
                                    font-size: 16px;
                                    cursor: pointer;
                                    transition: all 0.3s ease;
                                " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                                    ${name}
                                </button>
                            `;
                        }
                        
                        document.getElementById('results').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🌍</div>
                                <h3 style="color: #6366f1; margin-bottom: 20px;">Select Language / Seleccionar Idioma</h3>
                                <div style="background: rgba(99, 102, 241, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                                    <p style="color: #64748b; margin-bottom: 20px;">Choose your preferred language for the interface:</p>
                                    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
                                        ${languageButtons}
                                    </div>
                                </div>
                                <p style="color: #64748b; font-size: 14px;">The interface will be translated to your selected language.</p>
                            </div>
                        `;
                    } else {
                        showError('Failed to load languages: ' + response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to show language selector: ' + error.message);
            }
        }
        
        async function changeLanguage(languageCode) {
            showLoading('Changing language...');
            
            try {
                if (window.pywebview && window.pywebview.api) {
                    const response = await pywebview.api.set_language(languageCode);
                    if (response.success) {
                        currentLanguage = languageCode;
                        
                        // Get translations for new language
                        const translationsResponse = await pywebview.api.get_translations();
                        if (translationsResponse.success) {
                            translations = translationsResponse.data;
                            updateInterfaceLanguage();
                            
                            document.getElementById('results').innerHTML = `
                                <div style="text-align: center; padding: 40px;">
                                    <div style="font-size: 48px; margin-bottom: 20px;">✅</div>
                                    <h3 style="color: #10b981; margin-bottom: 20px;">Language Changed Successfully!</h3>
                                    <p style="color: #64748b;">The interface has been updated to your selected language.</p>
                                </div>
                            `;
                        }
                    } else {
                        showError('Failed to change language: ' + response.error);
                    }
                } else {
                    showError('PyWebView API not available.');
                }
            } catch (error) {
                showError('Failed to change language: ' + error.message);
            }
        }
        
        function updateInterfaceLanguage() {
            // Update ALL button texts by onclick function or specific patterns
            const buttons = document.querySelectorAll('button');
            
            buttons.forEach(button => {
                const onclick = button.getAttribute('onclick');
                const text = button.textContent.trim();
                
                // Map by onclick function (most reliable)
                if (onclick) {
                    if (onclick.includes('scanSystem')) {
                        button.textContent = translations.scan_system || '🔍 Scan System';
                    } else if (onclick.includes('dryRun')) {
                        button.textContent = translations.dry_run || '🧪 Dry Run';
                    } else if (onclick.includes('cleanTemp')) {
                        button.textContent = translations.clean_temp || '🗑️ Clean Temp';
                    } else if (onclick.includes('deepClean')) {
                        button.textContent = translations.deep_clean || '🔥 Deep Clean C:';
                    } else if (onclick.includes('refreshStats')) {
                        button.textContent = translations.refresh_stats || '🔄 Refresh Stats';
                    } else if (onclick.includes('cleanBrowserCache')) {
                        button.textContent = translations.clean_browsers || '🌐 Clean Browsers';
                    } else if (onclick.includes('cleanRecycleBin')) {
                        button.textContent = translations.empty_recycle || '🗑️ Empty Recycle';
                    } else if (onclick.includes('cleanMemoryDumps')) {
                        button.textContent = translations.memory_dumps || '💾 Memory Dumps';
                    } else if (onclick.includes('cleanDownloadCache')) {
                        button.textContent = translations.download_cache || '📥 Download Cache';
                    } else if (onclick.includes('cleanGameCache')) {
                        button.textContent = translations.game_cache || '🎮 Game Cache';
                    } else if (onclick.includes('cleanFontCache')) {
                        button.textContent = translations.font_cache || '🔤 Font Cache';
                    } else if (onclick.includes('toggleAutoStart')) {
                        button.textContent = translations.auto_start || '⚡ Auto-Start';
                    } else if (onclick.includes('showLanguageSelector')) {
                        button.textContent = translations.language || '🌍 Language';
                    }
                }
                // Fallback to text matching for buttons without onclick
                else if (text.includes('🔍') && text.includes('Scan')) {
                    button.textContent = translations.scan_system || '🔍 Scan System';
                } else if (text.includes('🧪') && text.includes('Dry')) {
                    button.textContent = translations.dry_run || '🧪 Dry Run';
                } else if (text.includes('🗑️') && text.includes('Clean Temp')) {
                    button.textContent = translations.clean_temp || '🗑️ Clean Temp';
                } else if (text.includes('🔥') && text.includes('Deep')) {
                    button.textContent = translations.deep_clean || '🔥 Deep Clean C:';
                }
            });
            
            // Update stats labels
            const statLabels = document.querySelectorAll('.stat-label');
            const statKeys = ['disk_usage', 'free_space', 'temp_files', 'temp_size'];
            
            statLabels.forEach((label, index) => {
                if (translations[statKeys[index]]) {
                    label.textContent = translations[statKeys[index]];
                }
            });
            
            // Update title and subtitle
            const title = document.querySelector('.app-title');
            const subtitle = document.querySelector('.app-subtitle');
            
            if (title && translations.app_title) {
                title.textContent = translations.app_title;
            }
            
            if (subtitle && translations.app_subtitle) {
                subtitle.textContent = translations.app_subtitle;
            }
            
            // Update ready to clean section
            const readyTitle = document.querySelector('h3');
            const readySubtitle = document.querySelector('p');
            
            if (readyTitle && readyTitle.textContent.includes('Ready to Clean')) {
                readyTitle.textContent = translations.ready_title || 'Ready to Clean';
            }
            
            if (readySubtitle && readySubtitle.textContent.includes('Click "Scan System"')) {
                readySubtitle.textContent = translations.ready_subtitle || 'Click "Scan System" to analyze temporary files and system cache.';
            }
            
            // Update copyright
            const copyright = document.querySelector('.footer');
            if (copyright && translations.copyright) {
                const instagramLink = copyright.querySelector('a');
                const instagramHTML = instagramLink ? instagramLink.outerHTML : '';
                copyright.innerHTML = `
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                        <div>${translations.copyright}</div>
                        ${instagramHTML}
                    </div>
                `;
            }
        }
        
        function displayScanResults(data) {
            let html = `
                <h3>📊 Scan Results</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div style="background: rgba(56, 189, 248, 0.2); padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #38bdf8;">${data.total_size_mb} MB</div>
                        <div style="color: #64748b;">Total Size</div>
                    </div>
                    <div style="background: rgba(34, 197, 94, 0.2); padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #22c55e;">${data.total_files}</div>
                        <div style="color: #64748b;">Files Found</div>
                    </div>
                    <div style="background: rgba(251, 191, 36, 0.2); padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #fbbf24;">${data.folders.length}</div>
                        <div style="color: #64748b;">Locations</div>
                    </div>
                </div>
                <h4>📁 Folders Found:</h4>
            `;
            
            data.folders.forEach(folder => {
                const statusColor = folder.accessible ? '#22c55e' : '#ef4444';
                const adminBadge = folder.requires_admin ? ' <span style="color: #fbbf24; font-size: 12px;">[Admin Required]</span>' : '';
                
                html += `
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid ${statusColor};">
                        <div style="font-weight: bold;">${folder.path}${adminBadge}</div>
                        <div style="color: #64748b; font-size: 14px;">
                            ${folder.size_mb} MB • ${folder.file_count} files
                            ${folder.error ? ` • <span style="color: #ef4444;">${folder.error}</span>` : ''}
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('results').innerHTML = html;
        }
        
        function displayDryRunResults(data) {
            let html = `
                <h3>🧪 Dry Run Results</h3>
                <div style="background: rgba(251, 191, 36, 0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 20px; font-weight: bold; color: #fbbf24;">
                        Would free: ${data.total_space_freed_mb} MB
                    </div>
                </div>
            `;
            
            if (data.warnings && data.warnings.length > 0) {
                html += '<h4>⚠️ Warnings:</h4>';
                data.warnings.forEach(warning => {
                    html += `<div style="color: #fbbf24; margin-bottom: 5px;">• ${warning}</div>`;
                });
            }
            
            html += '<h4>✅ Would Delete:</h4>';
            data.would_delete.forEach(folder => {
                html += `
                    <div style="background: rgba(34, 197, 94, 0.1); padding: 10px; margin-bottom: 5px; border-radius: 5px;">
                        <strong>${folder.path}</strong> - ${folder.size_mb} MB
                    </div>
                `;
            });
            
            document.getElementById('results').innerHTML = html;
        }
        
        function displayCleanResults(data) {
            let html = `
                <h3>✅ Cleaning Complete</h3>
                <div style="background: rgba(34, 197, 94, 0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 20px; font-weight: bold; color: #22c55e;">
                        Freed: ${data.total_freed_mb} MB
                    </div>
                </div>
            `;
            
            if (data.cleaned && data.cleaned.length > 0) {
                html += '<h4>🗑️ Successfully Cleaned:</h4>';
                data.cleaned.forEach(item => {
                    html += `
                        <div style="background: rgba(34, 197, 94, 0.1); padding: 10px; margin-bottom: 5px; border-radius: 5px;">
                            <strong>${item.path}</strong><br>
                            <small>${item.files_removed} files removed • ${item.space_freed_mb} MB freed</small>
                        </div>
                    `;
                });
            }
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
    """
    
    # Create temporary HTML file
    temp_dir = tempfile.gettempdir()
    html_file = os.path.join(temp_dir, 'cleanerapp_fixed.html')
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file

def main():
    print("🧹 Starting CleanerApp (Fixed Version)...")
    
    try:
        import webview
        
        # Create API instance
        api = CleanerAPI()
        
        # Create HTML interface
        html_file = create_simple_html()
        
        print("✅ Dependencies loaded successfully!")
        print("🚀 Opening CleanerApp window...")
        
        # Create webview window
        webview.create_window(
            title='CleanerApp - Fixed',
            url=f'file://{html_file}',
            js_api=api,
            width=1000,
            height=700,
            min_size=(800, 600),
            resizable=True
        )
        
        # Start the application
        webview.start(debug=False)
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Please install the required packages:")
        print("pip install pywebview psutil send2trash")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
