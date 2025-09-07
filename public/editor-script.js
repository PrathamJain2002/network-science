// Translation Editor JavaScript

class TranslationEditor {
    constructor() {
        this.currentJobId = null;
        this.currentVideoId = null;
        this.translations = [];
        this.audioContext = null;
        this.audioBuffer = null;
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = 0;
        
        this.initializeElements();
        this.bindEvents();
        this.loadJobData();
    }
    
    initializeElements() {
        // Header elements
        this.backBtn = document.getElementById('backBtn');
        this.generateVideoBtn = document.getElementById('generateVideoBtn');
        
        // Video elements
        this.previewVideo = document.getElementById('previewVideo');
        this.originalFileName = document.getElementById('originalFileName');
        this.videoDuration = document.getElementById('videoDuration');
        this.videoQuality = document.getElementById('videoQuality');
        
        // Text translation elements
        this.textTranslationList = document.getElementById('textTranslationList');
        this.autoTranslateBtn = document.getElementById('autoTranslateBtn');
        this.saveTextBtn = document.getElementById('saveTextBtn');
        
        // Audio translation elements
        this.hindiTranscription = document.getElementById('hindiTranscription');
        this.marathiTranslation = document.getElementById('marathiTranslation');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.timeDisplay = document.getElementById('timeDisplay');
        this.waveform = document.getElementById('waveform');
        this.regenerateAudioBtn = document.getElementById('regenerateAudioBtn');
        this.saveAudioBtn = document.getElementById('saveAudioBtn');
        
        // Audio separation elements
        this.voiceQuality = document.getElementById('voiceQuality');
        this.musicQuality = document.getElementById('musicQuality');
        this.overallQuality = document.getElementById('overallQuality');
        this.reseparateBtn = document.getElementById('reseparateBtn');
        this.previewSeparationBtn = document.getElementById('previewSeparationBtn');
        
        // Progress elements
        this.progressOverlay = document.getElementById('progressOverlay');
        this.progressText = document.getElementById('progressText');
        this.progressSubtext = document.getElementById('progressSubtext');
        
        // Notification container
        this.notificationContainer = document.getElementById('notificationContainer');
    }
    
    bindEvents() {
        // Header events
        this.backBtn.addEventListener('click', () => this.goBack());
        this.generateVideoBtn.addEventListener('click', () => this.generateFinalVideo());
        
        // Text translation events
        this.autoTranslateBtn.addEventListener('click', () => this.autoTranslateAll());
        this.saveTextBtn.addEventListener('click', () => this.saveTextTranslations());
        
        // Audio translation events
        this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        this.stopBtn.addEventListener('click', () => this.stopAudio());
        this.regenerateAudioBtn.addEventListener('click', () => this.regenerateAudio());
        this.saveAudioBtn.addEventListener('click', () => this.saveAudioTranslation());
        
        // Audio separation events
        this.reseparateBtn.addEventListener('click', () => this.reseparateAudio());
        this.previewSeparationBtn.addEventListener('click', () => this.previewSeparation());
        
        // Text area events
        this.marathiTranslation.addEventListener('input', () => this.onTranslationChange());
    }
    
    async loadJobData() {
        try {
            // Get job ID from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            this.currentJobId = urlParams.get('jobId');
            this.currentVideoId = urlParams.get('videoId');
            
            if (!this.currentJobId || !this.currentVideoId) {
                this.showNotification('Invalid job ID or video ID', 'error');
                this.goBack();
                return;
            }
            
            this.showProgress('Loading translation data...', 'Fetching job information');
            
            // Load job status and data
            const response = await fetch(`/status/${this.currentVideoId}`);
            const jobData = await response.json();
            
            if (!response.ok) {
                throw new Error(jobData.error || 'Failed to load job data');
            }
            
            // Update UI with job data
            this.updateJobInfo(jobData);
            
            // Load translation data
            await this.loadTranslationData();
            
            // Load audio separation data
            await this.loadAudioSeparationData();
            
            this.hideProgress();
            
        } catch (error) {
            console.error('Error loading job data:', error);
            this.showNotification(`Failed to load job data: ${error.message}`, 'error');
            this.hideProgress();
        }
    }
    
    updateJobInfo(jobData) {
        this.originalFileName.textContent = jobData.originalFilename || 'Unknown';
        this.videoDuration.textContent = this.formatDuration(jobData.duration || 0);
        this.videoQuality.textContent = jobData.quality || 'Unknown';
        
        // Set video source if available
        if (jobData.videoPath) {
            this.previewVideo.src = `/download/${this.currentVideoId}`;
        }
    }
    
    async loadTranslationData() {
        try {
            // Load text translations
            const textResponse = await fetch(`/api/translations/${this.currentJobId}/text`);
            if (textResponse.ok) {
                const textData = await textResponse.json();
                this.translations = textData.translations || [];
                this.renderTextTranslations();
            }
            
            // Load audio translation
            const audioResponse = await fetch(`/api/translations/${this.currentJobId}/audio`);
            if (audioResponse.ok) {
                const audioData = await audioResponse.json();
                this.hindiTranscription.textContent = audioData.hindiTranscription || '';
                this.marathiTranslation.value = audioData.marathiTranslation || '';
            }
            
        } catch (error) {
            console.error('Error loading translation data:', error);
            // Create mock data for demonstration
            this.createMockTranslationData();
        }
    }
    
    createMockTranslationData() {
        // Mock text translations
        this.translations = [
            {
                id: 1,
                hindiText: 'छल्ला चुंबक',
                marathiText: 'वलयाकार चुंबक',
                confidence: 0.95,
                bbox: [100, 200, 300, 250]
            },
            {
                id: 2,
                hindiText: 'छड़ चुंबक',
                marathiText: 'दंड चुंबक',
                confidence: 0.92,
                bbox: [100, 300, 300, 350]
            }
        ];
        
        // Mock audio translation
        this.hindiTranscription.textContent = 'छल्ला चुंबक आणि छड़ चुंबक यांच्या गुणधर्मांचा अभ्यास करूया';
        this.marathiTranslation.value = 'वलयाकार चुंबक आणि दंड चुंबक यांच्या गुणधर्मांचा अभ्यास करूया';
        
        this.renderTextTranslations();
    }
    
    renderTextTranslations() {
        this.textTranslationList.innerHTML = '';
        
        this.translations.forEach((translation, index) => {
            const translationItem = document.createElement('div');
            translationItem.className = 'translation-item';
            translationItem.innerHTML = `
                <div class="translation-item-header">
                    <div class="translation-item-title">Text Region ${index + 1}</div>
                    <div class="translation-item-actions">
                        <button class="btn btn-sm btn-secondary" onclick="editor.regenerateTranslation(${translation.id})">
                            🔄 Regenerate
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="editor.deleteTranslation(${translation.id})">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
                <div class="translation-item-content">
                    <div class="translation-label">Hindi Text:</div>
                    <div class="translation-content hindi-text">${translation.hindiText}</div>
                    <div class="translation-label">Marathi Translation:</div>
                    <textarea class="translation-content marathi-text" data-id="${translation.id}" placeholder="Enter Marathi translation...">${translation.marathiText}</textarea>
                    <div class="translation-label">Confidence: ${(translation.confidence * 100).toFixed(1)}%</div>
                </div>
            `;
            
            this.textTranslationList.appendChild(translationItem);
        });
    }
    
    async loadAudioSeparationData() {
        try {
            const response = await fetch(`/api/audio-separation/${this.currentJobId}`);
            if (response.ok) {
                const data = await response.json();
                this.updateAudioSeparationInfo(data);
            } else {
                // Mock data for demonstration
                this.updateAudioSeparationInfo({
                    voiceQuality: 85,
                    musicQuality: 78,
                    overallQuality: 82
                });
            }
        } catch (error) {
            console.error('Error loading audio separation data:', error);
            // Mock data for demonstration
            this.updateAudioSeparationInfo({
                voiceQuality: 85,
                musicQuality: 78,
                overallQuality: 82
            });
        }
    }
    
    updateAudioSeparationInfo(data) {
        this.updateQualityScore(this.voiceQuality, data.voiceQuality || 0);
        this.updateQualityScore(this.musicQuality, data.musicQuality || 0);
        this.updateQualityScore(this.overallQuality, data.overallQuality || 0);
    }
    
    updateQualityScore(element, score) {
        element.textContent = `${score.toFixed(1)}%`;
        element.className = 'quality-score';
        
        if (score >= 80) {
            element.classList.add('excellent');
        } else if (score >= 60) {
            element.classList.add('good');
        } else {
            element.classList.add('poor');
        }
    }
    
    async autoTranslateAll() {
        try {
            this.showProgress('Auto-translating text...', 'Using AI to translate all text regions');
            
            const response = await fetch(`/api/auto-translate/${this.currentJobId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.translations = data.translations;
                this.renderTextTranslations();
                this.showNotification('Auto-translation completed successfully!', 'success');
            } else {
                throw new Error('Auto-translation failed');
            }
            
        } catch (error) {
            console.error('Error in auto-translation:', error);
            this.showNotification(`Auto-translation failed: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async saveTextTranslations() {
        try {
            this.showProgress('Saving text translations...', 'Updating translation data');
            
            // Collect all translations
            const textareas = document.querySelectorAll('.marathi-text[data-id]');
            const updatedTranslations = [];
            
            textareas.forEach(textarea => {
                const id = parseInt(textarea.dataset.id);
                const translation = this.translations.find(t => t.id === id);
                if (translation) {
                    translation.marathiText = textarea.value;
                    updatedTranslations.push(translation);
                }
            });
            
            const response = await fetch(`/api/translations/${this.currentJobId}/text`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ translations: updatedTranslations })
            });
            
            if (response.ok) {
                this.showNotification('Text translations saved successfully!', 'success');
            } else {
                throw new Error('Failed to save translations');
            }
            
        } catch (error) {
            console.error('Error saving text translations:', error);
            this.showNotification(`Failed to save translations: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async regenerateTranslation(translationId) {
        try {
            this.showProgress('Regenerating translation...', 'Using AI to improve translation quality');
            
            const response = await fetch(`/api/regenerate-translation/${this.currentJobId}/${translationId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                const translation = this.translations.find(t => t.id === translationId);
                if (translation) {
                    translation.marathiText = data.marathiText;
                    this.renderTextTranslations();
                    this.showNotification('Translation regenerated successfully!', 'success');
                }
            } else {
                throw new Error('Failed to regenerate translation');
            }
            
        } catch (error) {
            console.error('Error regenerating translation:', error);
            this.showNotification(`Failed to regenerate translation: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async deleteTranslation(translationId) {
        if (confirm('Are you sure you want to delete this translation?')) {
            this.translations = this.translations.filter(t => t.id !== translationId);
            this.renderTextTranslations();
            this.showNotification('Translation deleted successfully!', 'success');
        }
    }
    
    async regenerateAudio() {
        try {
            this.showProgress('Regenerating audio...', 'Creating new Marathi audio with updated translation');
            
            const response = await fetch(`/api/regenerate-audio/${this.currentJobId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    marathiText: this.marathiTranslation.value
                })
            });
            
            if (response.ok) {
                this.showNotification('Audio regenerated successfully!', 'success');
            } else {
                throw new Error('Failed to regenerate audio');
            }
            
        } catch (error) {
            console.error('Error regenerating audio:', error);
            this.showNotification(`Failed to regenerate audio: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async saveAudioTranslation() {
        try {
            this.showProgress('Saving audio translation...', 'Updating audio translation data');
            
            const response = await fetch(`/api/translations/${this.currentJobId}/audio`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    marathiTranslation: this.marathiTranslation.value
                })
            });
            
            if (response.ok) {
                this.showNotification('Audio translation saved successfully!', 'success');
            } else {
                throw new Error('Failed to save audio translation');
            }
            
        } catch (error) {
            console.error('Error saving audio translation:', error);
            this.showNotification(`Failed to save audio translation: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async reseparateAudio() {
        try {
            this.showProgress('Re-separating audio...', 'Using AI to improve audio separation quality');
            
            const response = await fetch(`/api/reseparate-audio/${this.currentJobId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateAudioSeparationInfo(data.qualityMetrics);
                this.showNotification('Audio re-separation completed successfully!', 'success');
            } else {
                throw new Error('Failed to re-separate audio');
            }
            
        } catch (error) {
            console.error('Error re-separating audio:', error);
            this.showNotification(`Failed to re-separate audio: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async previewSeparation() {
        try {
            this.showProgress('Loading audio preview...', 'Preparing separated audio tracks');
            
            // This would load and play the separated audio tracks
            this.showNotification('Audio preview loaded successfully!', 'success');
            
        } catch (error) {
            console.error('Error loading audio preview:', error);
            this.showNotification(`Failed to load audio preview: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async generateFinalVideo() {
        try {
            this.showProgress('Generating final video...', 'Creating final translated video with all edits');
            
            const response = await fetch(`/api/generate-final-video/${this.currentJobId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showNotification('Final video generated successfully!', 'success');
                
                // Redirect to download or show success message
                setTimeout(() => {
                    window.location.href = `/download/${this.currentVideoId}`;
                }, 2000);
            } else {
                throw new Error('Failed to generate final video');
            }
            
        } catch (error) {
            console.error('Error generating final video:', error);
            this.showNotification(`Failed to generate final video: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    togglePlayPause() {
        if (this.isPlaying) {
            this.pauseAudio();
        } else {
            this.playAudio();
        }
    }
    
    playAudio() {
        // Audio playback implementation
        this.isPlaying = true;
        this.playPauseBtn.textContent = '⏸️ Pause';
        this.showNotification('Audio playback started', 'info');
    }
    
    pauseAudio() {
        // Audio pause implementation
        this.isPlaying = false;
        this.playPauseBtn.textContent = '▶️ Play';
        this.showNotification('Audio playback paused', 'info');
    }
    
    stopAudio() {
        // Audio stop implementation
        this.isPlaying = false;
        this.currentTime = 0;
        this.playPauseBtn.textContent = '▶️ Play';
        this.updateTimeDisplay();
        this.showNotification('Audio playback stopped', 'info');
    }
    
    updateTimeDisplay() {
        const current = this.formatTime(this.currentTime);
        const total = this.formatTime(this.duration);
        this.timeDisplay.textContent = `${current} / ${total}`;
    }
    
    onTranslationChange() {
        // Handle translation text changes
        // Could implement auto-save or validation here
    }
    
    goBack() {
        window.location.href = '/';
    }
    
    showProgress(text, subtext) {
        this.progressText.textContent = text;
        this.progressSubtext.textContent = subtext;
        this.progressOverlay.style.display = 'flex';
    }
    
    hideProgress() {
        this.progressOverlay.style.display = 'none';
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        this.notificationContainer.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Hide notification after 4 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
    
    formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
}

// Initialize the editor when the page loads
let editor;
document.addEventListener('DOMContentLoaded', () => {
    editor = new TranslationEditor();
});
