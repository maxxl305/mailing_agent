# debug_app.py - Minimale Version zum Testen
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any
import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Debug Company Research Tool", version="1.0.0")

# Simple storage
jobs: Dict[str, Dict] = {}

class SimpleRequest(BaseModel):
    urls: list[str]
    sender_name: str = "Test"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve a minimal HTML page for debugging"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Company Research Tool</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .debug { background: #f0f0f0; padding: 15px; margin: 15px 0; border-radius: 5px; }
            .success { background: #d4edda; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .error { background: #f8d7da; padding: 10px; margin: 10px 0; border-radius: 5px; }
            input, textarea, button { padding: 10px; margin: 5px 0; font-size: 16px; }
            textarea { width: 400px; height: 60px; }
            button { background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>🔧 Debug Company Research Tool</h1>
        
        <div class="debug">
            <h3>Debug Panel</h3>
            <div id="status">Loading...</div>
            <button onclick="testBackend()">Backend Test</button>
            <button onclick="clearLogs()">Clear Logs</button>
        </div>
        
        <form id="testForm">
            <h3>URL Test</h3>
            <label>URL eingeben:</label><br>
            <textarea id="urls" placeholder="https://example.com"></textarea><br>
            
            <label>Name:</label><br>
            <input type="text" id="senderName" value="Jonas Kremser"><br>
            
            <button type="submit">🚀 Test starten</button>
        </form>
        
        <div id="logs" class="debug">
            <h3>Debug Logs</h3>
            <div id="logContent">Warten auf Events...</div>
        </div>
        
        <div id="result" style="display: none;">
            <h3>Result</h3>
            <pre id="resultContent"></pre>
        </div>
        
        <script>
            console.log('🔧 Debug page loaded');
            
            let logCounter = 0;
            
            function addLog(message, type = 'info') {
                logCounter++;
                const logs = document.getElementById('logContent');
                const timestamp = new Date().toLocaleTimeString();
                const className = type === 'error' ? 'error' : (type === 'success' ? 'success' : '');
                logs.innerHTML += `<div class="${className}">[${timestamp}] ${logCounter}: ${message}</div>`;
                logs.scrollTop = logs.scrollHeight;
                console.log(`[${type}] ${message}`);
            }
            
            function clearLogs() {
                document.getElementById('logContent').innerHTML = 'Logs cleared...';
                logCounter = 0;
            }
            
            // Test backend connection
            async function testBackend() {
                addLog('Testing backend connection...');
                try {
                    const response = await fetch('/debug');
                    const data = await response.json();
                    addLog(`Backend OK: ${JSON.stringify(data)}`, 'success');
                    document.getElementById('status').innerHTML = '✅ Backend connected';
                } catch (error) {
                    addLog(`Backend ERROR: ${error.message}`, 'error');
                    document.getElementById('status').innerHTML = '❌ Backend error';
                }
            }
            
            // Form submission
            document.getElementById('testForm').addEventListener('submit', async (e) => {
                addLog('=== FORM SUBMITTED ===');
                e.preventDefault();
                
                // Get form data
                const urls = document.getElementById('urls').value
                    .split('\\n')
                    .map(url => url.trim())
                    .filter(url => url.length > 0);
                
                const senderName = document.getElementById('senderName').value;
                
                addLog(`URLs: ${JSON.stringify(urls)}`);
                addLog(`Sender: ${senderName}`);
                
                if (urls.length === 0) {
                    addLog('ERROR: No URLs provided', 'error');
                    alert('Bitte URL eingeben!');
                    return;
                }
                
                const requestData = {
                    urls: urls,
                    sender_name: senderName
                };
                
                addLog(`Request data: ${JSON.stringify(requestData)}`);
                
                try {
                    addLog('Sending POST request to /test...');
                    
                    const response = await fetch('/test', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestData)
                    });
                    
                    addLog(`Response status: ${response.status}`);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`HTTP ${response.status}: ${errorText}`);
                    }
                    
                    const result = await response.json();
                    addLog(`SUCCESS: ${JSON.stringify(result)}`, 'success');
                    
                    // Show result
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('resultContent').textContent = JSON.stringify(result, null, 2);
                    
                } catch (error) {
                    addLog(`REQUEST ERROR: ${error.message}`, 'error');
                }
            });
            
            // Auto-test backend on load
            window.addEventListener('load', () => {
                addLog('Page loaded, testing backend...');
                testBackend();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/debug")
async def debug_endpoint():
    """Simple debug endpoint"""
    logger.info("🔧 Debug endpoint called")
    return {
        "status": "Backend is working!",
        "timestamp": datetime.now().isoformat(),
        "jobs_count": len(jobs)
    }

@app.post("/test")
async def test_endpoint(request: SimpleRequest):
    """Simple test endpoint"""
    logger.info(f"🚀 Test request: {request.urls}")
    
    job_id = str(uuid.uuid4())
    
    # Store job
    jobs[job_id] = {
        "job_id": job_id,
        "urls": request.urls,
        "sender_name": request.sender_name,
        "status": "completed",
        "created_at": datetime.now().isoformat()
    }
    
    logger.info(f"✅ Job created: {job_id}")
    
    return {
        "success": True,
        "job_id": job_id,
        "message": f"URLs received: {request.urls}",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🔧 Starting DEBUG Company Research Tool...")
    print("💻 Open http://localhost:8001 in your browser")
    
    uvicorn.run("debug_app:app", host="0.0.0.0", port=8001, reload=False)