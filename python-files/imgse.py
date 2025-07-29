<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulk Image Generator with AI Prompts</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.7.77/Tone.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .prompt-card {
            transition: all 0.3s ease-in-out;
        }
        .prompt-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .sparkle-btn {
            background: linear-gradient(45deg, #6366f1, #a855f7, #ec4899);
            background-size: 200% 200%;
            animation: gradient-animation 5s ease infinite;
        }
        @keyframes gradient-animation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .aspect-video {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
        }
        .aspect-video > * {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        /* Toggle Switch Styles */
        .toggle-bg:after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            background: white;
            border-radius: 9999px;
            width: 1.25rem;
            height: 1.25rem;
            transition: transform 0.2s ease-in-out;
        }
        input:checked + .toggle-bg:after {
            transform: translateX(100%);
        }
        input:checked + .toggle-bg {
            background-color: #4f46e5;
        }
        /* Modal and Animation Styles */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 50;
        }
        .modal-content {
            background: black;
            padding: 1rem;
            border-radius: 0.5rem;
            max-width: 90vw;
            max-height: 90vh;
        }
        .animated-image {
            width: 100%;
            height: 100%;
            object-fit: contain;
            animation: zoom-in 10s ease-in-out forwards;
        }
        @keyframes zoom-in {
            from {
                transform: scale(1);
            }
            to {
                transform: scale(1.2);
            }
        }
    </style>
</head>
<body class="bg-gray-100 text-gray-800">

    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900">Professional Bulk Image Generator</h1>
            <p class="text-lg text-gray-600 mt-2">Use the power of AI to generate both creative prompts and stunning images.</p>
        </header>

        <main>
            <!-- Gemini Prompt Idea Generator -->
            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 class="text-2xl font-semibold mb-4">Need Inspiration?</h2>
                <p class="text-gray-600 mb-4">Enter a theme or keyword, and let AI generate creative prompts for you.</p>
                <div class="flex flex-col sm:flex-row gap-4">
                    <input type="text" id="idea-input" class="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="e.g., 'Enchanted Forest' or 'Cyberpunk City'">
                    <button id="idea-btn" class="sparkle-btn text-white font-bold py-3 px-6 rounded-lg hover:opacity-90 transition-opacity duration-300 flex items-center justify-center">
                        ✨ Generate Ideas
                    </button>
                </div>
                 <p id="idea-error-message" class="text-red-500 mt-2 text-sm text-center hidden"></p>
            </div>

            <!-- Main Prompts Area -->
            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-2xl font-semibold">Enter Your Prompts</h2>
                    <button id="clear-btn" class="text-sm text-gray-500 hover:text-red-500 transition-colors">Clear All</button>
                </div>
                <p class="text-gray-600 mb-4">Enter one prompt per line (the action or scene). For character consistency, use the section below.</p>
                <textarea id="prompts-input" class="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition" placeholder="standing on a mountain peak&#10;walking through a dark forest&#10;reading a book in a cozy library"></textarea>
                
                <div class="mt-6 border-t pt-6">
                    <div class="flex justify-between items-center">
                        <h3 class="text-xl font-semibold">Consistent Character (Optional)</h3>
                        <label for="character-toggle" class="flex items-center cursor-pointer">
                            <span class="mr-3 text-sm font-medium text-gray-900">Enable</span>
                            <div class="relative">
                                <input type="checkbox" id="character-toggle" class="sr-only">
                                <div class="block bg-gray-200 w-12 h-7 rounded-full toggle-bg"></div>
                            </div>
                        </label>
                    </div>
                    <p class="text-gray-600 my-4">Describe your character. This description will be added to every prompt to maintain consistency.</p>
                    <input type="text" id="character-input" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="e.g., a brave knight with a golden sword and silver armor">
                </div>

                <div class="mt-6">
                    <label for="quality-select" class="block text-sm font-medium text-gray-700">Image Quality</label>
                    <select id="quality-select" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                        <option value="standard">Standard</option>
                        <option value="enhanced">Enhanced (4K)</option>
                        <option value="flux">Flux 1.1 Pro Ultra</option>
                    </select>
                </div>

                <button id="generate-btn" class="mt-6 w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition-all duration-300 ease-in-out flex items-center justify-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l-1.586-1.586a2 2 0 00-2.828 0L6 14m6-6l.586-.586a2 2 0 012.828 0L20 12M4 16v4a2 2 0 002 2h12a2 2 0 002-2v-4M4 16l4.586-4.586a2 2 0 012.828 0L16 16"></path></svg>
                    Generate Images
                </button>
                <p id="error-message" class="text-red-500 mt-2 text-sm text-center hidden"></p>
            </div>

            <div id="gallery-controls" class="text-right mb-4 hidden">
                 <button id="download-zip-btn" class="bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center ml-auto">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    Download All as ZIP
                </button>
            </div>

            <div id="image-gallery" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- Generated images will be appended here -->
            </div>
        </main>

        <!-- Video Modal -->
        <div id="video-modal" class="modal-overlay hidden">
            <div class="modal-content">
                <div id="video-container" class="aspect-video"></div>
                <button id="close-modal-btn" class="mt-4 w-full bg-red-600 text-white font-bold py-2 px-4 rounded-lg">Close</button>
            </div>
        </div>

        <footer class="text-center mt-12 text-gray-500">
            <p>&copy; 2025 Bulk Image Generator. Powered by Gemini.</p>
        </footer>
    </div>

    <script>
        // --- Element References ---
        const ideaInput = document.getElementById('idea-input');
        const ideaBtn = document.getElementById('idea-btn');
        const ideaErrorMessage = document.getElementById('idea-error-message');
        const generateBtn = document.getElementById('generate-btn');
        const promptsInput = document.getElementById('prompts-input');
        const imageGallery = document.getElementById('image-gallery');
        const errorMessage = document.getElementById('error-message');
        const clearBtn = document.getElementById('clear-btn');
        const qualitySelect = document.getElementById('quality-select');
        const characterToggle = document.getElementById('character-toggle');
        const characterInput = document.getElementById('character-input');
        const videoModal = document.getElementById('video-modal');
        const videoContainer = document.getElementById('video-container');
        const closeModalBtn = document.getElementById('close-modal-btn');
        const galleryControls = document.getElementById('gallery-controls');
        const downloadZipBtn = document.getElementById('download-zip-btn');

        // --- Loading State SVGs ---
        const thinkingSpinner = `<svg class="animate-spin h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> Thinking...`;
        const generatingSpinner = (count, total) => `<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Generating ${count} of ${total}...`;
        const defaultGenerateBtnHTML = generateBtn.innerHTML;
        const defaultIdeaBtnHTML = ideaBtn.innerHTML;
        
        // --- Sound Synthesis ---
        let synth;
        function setupSound() {
            if (!synth) {
                synth = new Tone.PolySynth(Tone.Synth, {
                    oscillator: { type: "fatsawtooth" },
                    envelope: { attack: 2, decay: 1, sustain: 0.4, release: 2 },
                }).toDestination();
                const filter = new Tone.AutoFilter("4n").toDestination().start();
                const reverb = new Tone.Reverb({ decay: 10, wet: 0.5 }).toDestination();
                synth.connect(filter);
                synth.connect(reverb);
            }
        }

        function playSound() {
            if (Tone.context.state !== 'running') {
                Tone.start();
            }
            setupSound();
            synth.triggerAttackRelease(["C2", "E2", "G2"], "8n");
        }

        function stopSound() {
            if (synth) {
                synth.releaseAll();
            }
        }

        // --- Utility Functions ---
        function showError(element, message) {
            element.textContent = message;
            element.classList.remove('hidden');
        }

        function hideError(element) {
            element.classList.add('hidden');
        }

        // --- Event Listeners ---
        clearBtn.addEventListener('click', () => { promptsInput.value = ''; });
        ideaBtn.addEventListener('click', handleGenerateIdeas);
        generateBtn.addEventListener('click', handleGenerateImages);
        closeModalBtn.addEventListener('click', () => {
            videoModal.classList.add('hidden');
            videoContainer.innerHTML = '';
            stopSound();
        });
        downloadZipBtn.addEventListener('click', handleDownloadZip);

        // --- Core Logic ---
        async function handleGenerateIdeas() {
            const keyword = ideaInput.value.trim();
            if (!keyword) {
                showError(ideaErrorMessage, 'Please enter a keyword or theme.');
                return;
            }
            hideError(ideaErrorMessage);
            ideaBtn.disabled = true;
            ideaBtn.innerHTML = thinkingSpinner;
            try {
                const prompt = `Generate 5 creative, detailed, and visually rich image generation prompts based on the theme: "${keyword}". Each prompt must be on a new line. Do not include numbering or bullet points.`;
                const payload = { contents: [{ role: "user", parts: [{ text: prompt }] }] };
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`;
                const result = await callApi(apiUrl, payload);
                if (result.candidates && result.candidates.length > 0) {
                    const generatedText = result.candidates[0].content.parts[0].text;
                    const existingText = promptsInput.value.trim();
                    promptsInput.value = (existingText ? existingText + '\n' : '') + generatedText.trim();
                } else {
                    throw new Error('Unexpected API response structure.');
                }
            } catch (error) {
                console.error('Error generating prompt ideas:', error);
                showError(ideaErrorMessage, `Could not generate ideas: ${error.message}`);
            } finally {
                ideaBtn.disabled = false;
                ideaBtn.innerHTML = defaultIdeaBtnHTML;
            }
        }

        async function handleGenerateImages() {
            hideError(errorMessage);
            galleryControls.classList.add('hidden');
            const scenePrompts = promptsInput.value.trim().split('\n').filter(p => p.trim() !== '');
            if (scenePrompts.length === 0) {
                showError(errorMessage, 'Please enter at least one scene prompt.');
                return;
            }
            if (scenePrompts.length > 100) {
                showError(errorMessage, 'You can generate a maximum of 100 images at a time.');
                return;
            }
            const useCharacter = characterToggle.checked;
            const characterDesc = characterInput.value.trim();
            if (useCharacter && !characterDesc) {
                showError(errorMessage, 'Please describe your character or disable the character consistency feature.');
                return;
            }
            imageGallery.innerHTML = '';
            generateBtn.disabled = true;
            const quality = qualitySelect.value;
            const finalPrompts = scenePrompts.map(scene => useCharacter ? `${characterDesc}, ${scene}` : scene);
            let count = 1;
            for (const prompt of finalPrompts) {
                generateBtn.innerHTML = generatingSpinner(count, finalPrompts.length);
                const card = createPromptCard(prompt);
                imageGallery.appendChild(card);
                await generateSingleImage(prompt, card, quality);
                count++;
            }
            generateBtn.disabled = false;
            generateBtn.innerHTML = defaultGenerateBtnHTML;
            if (imageGallery.children.length > 0) {
                galleryControls.classList.remove('hidden');
            }
        }

        async function generateSingleImage(prompt, card, quality) {
            const imageContainer = card.querySelector('.image-container');
            const footer = card.querySelector('.card-footer');
            try {
                let finalPrompt = prompt;
                if (quality === 'enhanced') {
                    finalPrompt += ", photorealistic, cinematic lighting, 4K, ultra detailed, sharp focus";
                } else if (quality === 'flux') {
                    finalPrompt += ", flux 1.1 pro, ultra realistic, professional photography, 8k, sharp focus";
                }
                const payload = { 
                    instances: [{ prompt: finalPrompt }], 
                    parameters: { "sampleCount": 1, "aspectRatio": "16:9" } 
                };
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict`;
                const result = await callApi(apiUrl, payload);
                if (result.predictions && result.predictions.length > 0 && result.predictions[0].bytesBase64Encoded) {
                    const imageUrl = `data:image/png;base64,${result.predictions[0].bytesBase64Encoded}`;
                    imageContainer.innerHTML = `<img src="${imageUrl}" alt="${prompt}" class="w-full h-full object-cover">`;
                    footer.innerHTML = '';
                    footer.appendChild(createDownloadButton(imageUrl, prompt));
                    footer.appendChild(createAnimateButton(imageUrl));
                } else {
                    throw new Error('Invalid response structure from API.');
                }
            } catch (error) {
                console.error('Error generating image:', prompt, error);
                imageContainer.innerHTML = `<div class="p-4 text-red-500 text-center flex items-center justify-center h-full">Failed to generate image.</div>`;
                footer.innerHTML = `<p class="text-red-500 text-sm text-center" title="${error.message}">Error</p>`;
            }
        }

        async function handleDownloadZip() {
            const originalBtnHTML = downloadZipBtn.innerHTML;
            downloadZipBtn.disabled = true;
            downloadZipBtn.innerHTML = `<svg class="animate-spin h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> Zipping...`;

            const zip = new JSZip();
            const imageCards = imageGallery.querySelectorAll('.prompt-card');
            let imageCount = 0;

            imageCards.forEach((card, index) => {
                const imgElement = card.querySelector('img');
                if (imgElement) {
                    const prompt = card.querySelector('p').title;
                    const filename = prompt.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50) + '.png';
                    const base64Data = imgElement.src.split(',')[1];
                    zip.file(filename, base64Data, { base64: true });
                    imageCount++;
                }
            });

            if (imageCount > 0) {
                zip.generateAsync({ type: "blob" }).then(function(content) {
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(content);
                    link.download = "generated_images.zip";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                });
            } else {
                showError(errorMessage, "No images found to download.");
            }

            downloadZipBtn.disabled = false;
            downloadZipBtn.innerHTML = originalBtnHTML;
        }

        async function callApi(url, payload) {
            const apiKey = ""; // Handled by the environment
            const fullUrl = `${url}?key=${apiKey}`;
            try {
                const response = await fetch(fullUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!response.ok) {
                    const errorBody = await response.json().catch(() => ({ error: { message: "Unknown API error." } }));
                    throw new Error(errorBody.error?.message || `HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                throw error;
            }
        }

        function createPromptCard(prompt) {
            const card = document.createElement('div');
            card.className = 'prompt-card bg-white rounded-lg shadow-md overflow-hidden flex flex-col';
            card.innerHTML = `
                <div class="aspect-video bg-gray-200 flex items-center justify-center image-container">
                    <div class="loader"></div>
                </div>
                <div class="p-4 border-t border-gray-200">
                    <p class="text-gray-700 text-sm truncate" title="${prompt}">${prompt}</p>
                </div>
                <div class="p-4 bg-gray-50 text-right mt-auto card-footer flex gap-2 justify-end">
                    <!-- Buttons will be added here -->
                </div>
            `;
            return card;
        }

        function createDownloadButton(imageUrl, prompt) {
            const downloadBtn = document.createElement('a');
            downloadBtn.href = imageUrl;
            downloadBtn.download = prompt.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50) + '.png';
            downloadBtn.className = 'inline-block bg-green-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-600 transition-colors';
            downloadBtn.innerHTML = `<svg class="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg> Download`;
            return downloadBtn;
        }

        function createAnimateButton(imageUrl) {
            const animateBtn = document.createElement('button');
            animateBtn.className = 'inline-block bg-purple-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors';
            animateBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 inline-block mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" /></svg> Animate`;
            animateBtn.addEventListener('click', () => {
                videoContainer.innerHTML = `<img src="${imageUrl}" class="animated-image">`;
                videoModal.classList.remove('hidden');
                playSound();
            });
            return animateBtn;
        }
    </script>
</body>
</html>
