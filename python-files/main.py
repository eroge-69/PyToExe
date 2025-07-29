<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lightweight Live Streaming Tool</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .live-indicator {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }
        /* Hide file inputs but keep them accessible */
        #image-input, #video-input {
            display: none;
        }
    </style>
</head>
<body class="bg-gray-900 text-white flex flex-col items-center min-h-screen p-4">

    <div class="w-full max-w-5xl">
        <h1 class="text-3xl font-bold text-center mb-6">Lightweight Live Streaming Tool</h1>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Main Preview -->
            <div class="md:col-span-2 bg-gray-800 rounded-lg shadow-lg p-4">
                <div class="relative">
                    <video id="preview" class="w-full rounded-md bg-black" autoplay muted playsinline></video>
                    <div id="live-indicator" class="absolute top-2 right-2 bg-red-600 text-white text-xs font-bold px-2 py-1 rounded-full flex items-center hidden">
                        <span class="live-indicator w-2 h-2 bg-white rounded-full mr-2"></span>
                        LIVE
                    </div>
                </div>
                <div class="mt-4 text-center text-gray-400 text-sm">
                    <p>This is the main preview of your stream.</p>
                </div>
            </div>

            <!-- Controls and Scenes -->
            <div class="bg-gray-800 rounded-lg shadow-lg p-4 flex flex-col">
                <div>
                    <h2 class="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">Controls</h2>
                    <div class="space-y-4">
                        <div>
                            <label for="stream-key" class="block text-sm font-medium text-gray-300 mb-1">YouTube Stream Key</label>
                            <input type="password" id="stream-key" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="paste-your-key-here">
                        </div>
                        <div class="space-y-2">
                            <button id="start-stream" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">Start Stream</button>
                            <button id="stop-stream" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition-colors" disabled>Stop Stream</button>
                        </div>
                    </div>
                </div>

                <div class="mt-6 flex-grow">
                    <h2 class="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">Scenes</h2>
                    <div id="scenes-list" class="space-y-2">
                        <!-- Scenes will be dynamically added here -->
                    </div>
                    <button id="add-scene" class="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">Add Scene</button>
                </div>
            </div>
        </div>

        <!-- Sources Panel -->
        <div class="mt-6 bg-gray-800 rounded-lg shadow-lg p-4">
            <h2 class="text-xl font-semibold mb-2">Sources for Selected Scene</h2>
            <p class="text-sm text-gray-400 mb-4">Sources are layered. The last source added will be on top.</p>
            <div id="sources-list" class="mb-4 space-y-2">
                <!-- Sources for the active scene will be listed here -->
            </div>
            <div class="relative">
                 <button id="add-source-btn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">Add Source</button>
                 <div id="source-options" class="absolute bottom-full mb-2 w-full bg-gray-700 rounded-lg shadow-xl p-2 space-y-2 hidden">
                    <button data-type="webcam" class="source-option-btn w-full text-left p-2 hover:bg-gray-600 rounded">Webcam</button>
                    <button data-type="screen" class="source-option-btn w-full text-left p-2 hover:bg-gray-600 rounded">Screen Share</button>
                    <button data-type="image" class="source-option-btn w-full text-left p-2 hover:bg-gray-600 rounded">Image</button>
                    <button data-type="video" class="source-option-btn w-full text-left p-2 hover:bg-gray-600 rounded">Video File</button>
                    <button data-type="text" class="source-option-btn w-full text-left p-2 hover:bg-gray-600 rounded">Text</button>
                 </div>
            </div>
        </div>
    </div>

    <!-- Hidden canvas for composing scenes -->
    <canvas id="composition-canvas" class="hidden"></canvas>
    <!-- Hidden file inputs -->
    <input type="file" id="image-input" accept="image/*">
    <input type="file" id="video-input" accept="video/*">


    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // DOM Elements
            const preview = document.getElementById('preview');
            const startStreamBtn = document.getElementById('start-stream');
            const stopStreamBtn = document.getElementById('stop-stream');
            const liveIndicator = document.getElementById('live-indicator');
            const addSceneBtn = document.getElementById('add-scene');
            const scenesList = document.getElementById('scenes-list');
            const sourcesList = document.getElementById('sources-list');
            const compositionCanvas = document.getElementById('composition-canvas');
            const streamKeyInput = document.getElementById('stream-key');
            const addSourceBtn = document.getElementById('add-source-btn');
            const sourceOptions = document.getElementById('source-options');
            const imageInput = document.getElementById('image-input');
            const videoInput = document.getElementById('video-input');
            const ctx = compositionCanvas.getContext('2d');

            // App State
            let scenes = [];
            let activeSceneId = null;
            let stream = null;
            let compositionStream = null;
            let animationFrameId = null;

            // --- Scene Management ---
            function addScene() {
                const sceneId = `scene-${Date.now()}`;
                const scene = { id: sceneId, name: `Scene ${scenes.length + 1}`, sources: [] };
                scenes.push(scene);
                renderScenes();
                setActiveScene(sceneId);
            }

            function setActiveScene(sceneId) {
                activeSceneId = sceneId;
                renderScenes();
                renderSources();
                updateComposition();
            }

            function getActiveScene() {
                return scenes.find(s => s.id === activeSceneId);
            }

            function renderScenes() {
                scenesList.innerHTML = '';
                scenes.forEach(scene => {
                    const sceneEl = document.createElement('div');
                    sceneEl.className = `p-2 rounded-lg cursor-pointer transition-colors ${scene.id === activeSceneId ? 'bg-blue-500' : 'bg-gray-700 hover:bg-gray-600'}`;
                    sceneEl.textContent = scene.name;
                    sceneEl.onclick = () => setActiveScene(scene.id);
                    scenesList.appendChild(sceneEl);
                });
            }

            // --- Source Management ---
            async function addSource(type) {
                const activeScene = getActiveScene();
                if (!activeScene) {
                    alert("Please add and select a scene first!");
                    return;
                }

                const sourceId = `source-${Date.now()}`;
                let source = { id: sourceId, type };

                try {
                    switch (type) {
                        case 'webcam':
                        case 'screen':
                            const mediaStream = type === 'webcam' 
                                ? await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                                : await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
                            
                            const videoElement = document.createElement('video');
                            videoElement.srcObject = mediaStream;
                            videoElement.muted = true;
                            videoElement.play();
                            source.stream = mediaStream;
                            source.element = videoElement;
                            source.name = type === 'webcam' ? 'Webcam' : 'Screen Share';
                            break;

                        case 'image':
                            const imageFile = await new Promise(resolve => {
                                imageInput.onchange = e => resolve(e.target.files[0]);
                                imageInput.click();
                            });
                            if (!imageFile) return;
                            const imageUrl = URL.createObjectURL(imageFile);
                            const img = new Image();
                            img.src = imageUrl;
                            source.element = img;
                            source.name = `Image: ${imageFile.name}`;
                            break;

                        case 'video':
                             const videoFile = await new Promise(resolve => {
                                videoInput.onchange = e => resolve(e.target.files[0]);
                                videoInput.click();
                            });
                            if (!videoFile) return;
                            const videoUrl = URL.createObjectURL(videoFile);
                            const vidElement = document.createElement('video');
                            vidElement.src = videoUrl;
                            vidElement.loop = true;
                            vidElement.muted = true; // Mute to control audio via composition
                            vidElement.play();
                            source.element = vidElement;
                            source.name = `Video: ${videoFile.name}`;
                            // You could create a separate audio source from this if needed
                            break;

                        case 'text':
                            const text = prompt("Enter text to display:", "Hello, World!");
                            if (!text) return;
                            source.text = text;
                            source.color = prompt("Enter text color (e.g., #FFFFFF):", "#FFFFFF");
                            source.fontSize = parseInt(prompt("Enter font size (e.g., 48):", "48"));
                            source.name = `Text: "${text}"`;
                            break;

                        default:
                            return;
                    }
                } catch (error) {
                    console.error(`Error getting ${type} source:`, error);
                    alert(`Could not access ${type}. Please ensure permissions are granted.`);
                    return;
                }

                activeScene.sources.push(source);
                renderSources();
                updateComposition();
            }
            
            function removeSource(sourceId) {
                const activeScene = getActiveScene();
                if (!activeScene) return;

                const sourceIndex = activeScene.sources.findIndex(s => s.id === sourceId);
                if (sourceIndex > -1) {
                    const source = activeScene.sources[sourceIndex];
                    if (source.stream) {
                        source.stream.getTracks().forEach(track => track.stop());
                    }
                    if (source.element && source.element.src) {
                        URL.revokeObjectURL(source.element.src);
                    }
                    activeScene.sources.splice(sourceIndex, 1);
                }
                renderSources();
                updateComposition();
            }

            function renderSources() {
                sourcesList.innerHTML = '';
                const activeScene = getActiveScene();
                if (activeScene) {
                    if (activeScene.sources.length === 0) {
                        sourcesList.innerHTML = '<p class="text-gray-500">No sources in this scene.</p>';
                    } else {
                        activeScene.sources.forEach(source => {
                            const sourceEl = document.createElement('div');
                            sourceEl.className = 'flex justify-between items-center bg-gray-700 p-2 rounded-lg';
                            sourceEl.innerHTML = `
                                <span>${source.name}</span>
                                <button data-source-id="${source.id}" class="remove-source-btn bg-red-500 hover:bg-red-600 text-white px-2 py-1 text-xs rounded">Remove</button>
                            `;
                            sourcesList.appendChild(sourceEl);
                        });
                    }
                } else {
                     sourcesList.innerHTML = '<p class="text-gray-500">Select a scene to manage sources.</p>';
                }
            }

            // --- Stream Composition ---
            function updateComposition() {
                if (!stream) {
                    ctx.clearRect(0, 0, compositionCanvas.width, compositionCanvas.height);
                    return;
                }
                
                compositionCanvas.width = 1280;
                compositionCanvas.height = 720;
                ctx.clearRect(0, 0, compositionCanvas.width, compositionCanvas.height);
                ctx.fillStyle = 'black';
                ctx.fillRect(0, 0, compositionCanvas.width, compositionCanvas.height);

                const activeScene = getActiveScene();
                if (activeScene) {
                    activeScene.sources.forEach(source => {
                        ctx.save();
                        switch (source.type) {
                            case 'webcam':
                            case 'screen':
                            case 'video':
                                if (source.element && source.element.readyState >= 2) { // HAVE_CURRENT_DATA
                                    ctx.drawImage(source.element, 0, 0, compositionCanvas.width, compositionCanvas.height);
                                }
                                break;
                            case 'image':
                                if (source.element && source.element.complete) {
                                    ctx.drawImage(source.element, 0, 0, compositionCanvas.width, compositionCanvas.height);
                                }
                                break;
                            case 'text':
                                ctx.font = `bold ${source.fontSize || 48}px Inter`;
                                ctx.fillStyle = source.color || '#FFFFFF';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                ctx.fillText(source.text, compositionCanvas.width / 2, compositionCanvas.height / 2);
                                break;
                        }
                        ctx.restore();
                    });
                }

                animationFrameId = requestAnimationFrame(updateComposition);
            }

            // --- Stream Control ---
            function startStream() {
                if (stream) return;
                const streamKey = streamKeyInput.value.trim();
                if (!streamKey) {
                    alert("Please enter your YouTube stream key before starting.");
                    return;
                }
                if (scenes.length === 0 || !getActiveScene()) {
                    alert("Please create and select a scene before starting.");
                    return;
                }
                
                console.log(`Simulating stream start with key: ${streamKey}`);
                
                compositionStream = compositionCanvas.captureStream(30);

                const activeScene = getActiveScene();
                const audioSource = activeScene.sources.find(s => s.stream && s.stream.getAudioTracks().length > 0);
                if (audioSource) {
                    compositionStream.addTrack(audioSource.stream.getAudioTracks()[0]);
                }

                stream = compositionStream;
                preview.srcObject = stream;
                preview.play();

                startStreamBtn.disabled = true;
                stopStreamBtn.disabled = false;
                liveIndicator.classList.remove('hidden');
                updateComposition();
            }

            function stopStream() {
                if (!stream) return;
                stream.getTracks().forEach(track => track.stop());
                stream = null;
                preview.srcObject = null;

                startStreamBtn.disabled = false;
                stopStreamBtn.disabled = true;
                liveIndicator.classList.add('hidden');

                if (animationFrameId) {
                    cancelAnimationFrame(animationFrameId);
                    animationFrameId = null;
                }
                scenes.forEach(scene => scene.sources.forEach(source => {
                    if (source.stream) source.stream.getTracks().forEach(t => t.stop());
                }));
                scenes = [];
                renderScenes();
                renderSources();
            }

            // --- Event Listeners ---
            startStreamBtn.addEventListener('click', startStream);
            stopStreamBtn.addEventListener('click', stopStream);
            addSceneBtn.addEventListener('click', addScene);
            
            addSourceBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                sourceOptions.classList.toggle('hidden');
            });

            document.addEventListener('click', () => {
                if (!sourceOptions.classList.contains('hidden')) {
                    sourceOptions.classList.add('hidden');
                }
            });

            sourceOptions.addEventListener('click', (e) => {
                if (e.target.matches('.source-option-btn')) {
                    const type = e.target.dataset.type;
                    addSource(type);
                }
            });

            sourcesList.addEventListener('click', (e) => {
                if (e.target.classList.contains('remove-source-btn')) {
                    const sourceId = e.target.dataset.sourceId;
                    removeSource(sourceId);
                }
            });

            // --- Initial Setup ---
            addScene();
        });
    </script>
</body>
</html>
