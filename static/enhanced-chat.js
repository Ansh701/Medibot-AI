// enhanced-chat.js - FIXED EventSource Handling Version
console.log('🚀 MediBot Enhanced Chat Loading...');

class MediBotChat {
    constructor() {
        this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.isRecording = false;
        this.recognition = null;
        this.conversationHistory = [];
        this.currentMessageId = null;

        console.log('MediBotChat initialized with session:', this.sessionId);
        this.init();
    }

    init() {
        console.log('🔧 Starting MediBot initialization...');
        this.setupElements();
        this.setupEventListeners();
        this.initializeVoiceRecognition();
        this.injectMobileStyles();
        this.hideLoadingScreen();
        this.showWelcomeMessage();
        this.loadConversationHistory();
        this.ensureInputVisible();
        console.log('✅ MediBot initialization complete!');
    }

    setupElements() {
        this.elements = {
            messageForm: document.getElementById('message-form'),
            messageInput: document.getElementById('message-input'),
            sendBtn: document.getElementById('send-btn'),
            voiceBtn: document.getElementById('voice-btn'),
            attachBtn: document.getElementById('attach-btn'),
            messagesContainer: document.getElementById('messages-container'),
            characterCount: document.querySelector('.character-count'),
            conversationHistory: document.getElementById('conversation-history'),
            settingsBtn: document.getElementById('settings-btn'),
            helpBtn: document.getElementById('help-btn')
        };

        const foundElements = Object.keys(this.elements).filter(k => this.elements[k]);
        console.log('📋 Elements found:', foundElements);
    }

    setupEventListeners() {
        // Form submission
        if (this.elements.messageForm) {
            this.elements.messageForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Input handling
        if (this.elements.messageInput) {
            this.elements.messageInput.addEventListener('input', (e) => this.handleInputChange(e));
            this.elements.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
            this.elements.messageInput.addEventListener('input', this.autoResize);
        }

        // Voice input
        if (this.elements.voiceBtn) {
            this.elements.voiceBtn.addEventListener('click', () => this.toggleVoiceRecording());
        }

        // File attachment
        if (this.elements.attachBtn) {
            this.elements.attachBtn.addEventListener('click', () => this.handleFileAttachment());
        }

        // Quick actions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-action-btn')) {
                const query = e.target.dataset.query;
                if (query) {
                    this.sendQuickAction(query);
                }
            }
        });

        // Settings and help
        if (this.elements.settingsBtn) {
            this.elements.settingsBtn.addEventListener('click', () => this.showSettings());
        }

        if (this.elements.helpBtn) {
            this.elements.helpBtn.addEventListener('click', () => this.showHelp());
        }

        // Feedback modal
        this.setupFeedbackModal();

        console.log('🎯 Event listeners attached');
    }

    hideLoadingScreen() {
        console.log('🎬 Hiding loading screen...');
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            const mainApp = document.getElementById('main-app');

            if (loadingScreen) {
                loadingScreen.style.opacity = '0';
                loadingScreen.style.visibility = 'hidden';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 300);
                console.log('✅ Loading screen hidden');
            }

            if (mainApp) {
                mainApp.style.display = 'block';
                mainApp.style.opacity = '1';
                console.log('✅ Main app displayed');
            }
        }, 1200);
    }

    showWelcomeMessage() {
        if (!this.elements.messagesContainer) {
            console.warn('⚠️ Messages container not found');
            return;
        }

        const welcomeMessage = {
            type: 'bot',
            content: this.createCompactWelcomeContent(),
            timestamp: new Date(),
            sources: []
        };

        this.displayMessage(welcomeMessage);
        console.log('👋 Compact welcome message displayed');
    }

    createCompactWelcomeContent() {
        return `
            <div class="welcome-message-compact">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 15px;">
                    <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold; flex-shrink: 0;">M</div>
                    <div>
                        <h3 style="color: #2563EB; margin: 0 0 4px 0; font-size: 20px; font-weight: 600;">MediBot AI Ready!</h3>
                        <p style="color: #6B7280; margin: 0; font-size: 14px;">23,436+ medical documents loaded</p>
                    </div>
                </div>

                <div style="background: #EBF8FF; padding: 12px; border-radius: 10px; margin-bottom: 12px; border-left: 3px solid #3B82F6;">
                    <p style="color: #1E40AF; margin: 0; font-size: 13px; font-weight: 500;">💬 Ask me about symptoms, treatments, medications, or health advice</p>
                </div>

                <details style="cursor: pointer;">
                    <summary style="color: #6B7280; font-size: 12px; font-weight: 500;">ⓘ View capabilities & disclaimer</summary>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #e5e7eb;">
                        <div style="background: #F0FDF4; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #22C55E;">
                            <strong style="color: #166534; font-size: 12px;">Capabilities:</strong>
                            <ul style="color: #166534; margin: 4px 0; padding-left: 16px; font-size: 11px; line-height: 1.4;">
                                <li>Medical symptoms and conditions</li>
                                <li>Medication information</li>
                                <li>Treatment options</li>
                                <li>Health and wellness advice</li>
                            </ul>
                        </div>
                        <div style="background: #FEF3C7; padding: 10px; border-radius: 8px; border-left: 3px solid #F59E0B;">
                            <p style="color: #92400E; margin: 0; font-size: 11px; font-weight: 500;">⚠️ For educational purposes only. Always consult healthcare professionals for medical advice.</p>
                        </div>
                    </div>
                </details>
            </div>
        `;
    }

    injectMobileStyles() {
        if (document.querySelector('#mobile-responsive-styles')) return;

        const style = document.createElement('style');
        style.id = 'mobile-responsive-styles';
        style.textContent = `
            @media (max-width: 768px) {
                .chat-container { padding: 10px !important; height: calc(100vh - 120px) !important; }
                .messages-container { height: calc(100vh - 200px) !important; padding: 15px !important; }
                .input-area { position: fixed !important; bottom: 0 !important; left: 0 !important; right: 0 !important; background: white !important; border-top: 1px solid #e5e7eb !important; padding: 10px !important; z-index: 1000 !important; }
                .message-form { margin: 0 !important; padding: 8px !important; gap: 8px !important; }
                .message-input { font-size: 16px !important; min-height: 40px !important; max-height: 80px !important; }
                .voice-btn, .attach-btn, .send-btn { width: 40px !important; height: 40px !important; font-size: 14px !important; }
                .message-bubble { font-size: 14px !important; padding: 12px 15px !important; max-width: 85% !important; }
                .message-avatar div { width: 35px !important; height: 35px !important; font-size: 16px !important; }
                .sidebar-col { display: none !important; }
                .main-chat-col { width: 100% !important; max-width: none !important; }
                body { padding-bottom: 80px !important; }
            }
            .messages-container { scroll-behavior: smooth; }
            .message { margin-bottom: 15px; }
            .send-btn:not(:disabled) { background: linear-gradient(135deg, #667eea, #764ba2) !important; }
            .send-btn:disabled { background: #d1d5db !important; }
        `;
        document.head.appendChild(style);
    }

    ensureInputVisible() {
        setTimeout(() => {
            window.scrollTo(0, document.body.scrollHeight);
            if (this.elements.messagesContainer) {
                this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
            }
        }, 1500);

        if (this.elements.messageInput) {
            this.elements.messageInput.addEventListener('focus', () => {
                setTimeout(() => {
                    window.scrollTo(0, document.body.scrollHeight);
                }, 300);
            });
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        const message = this.elements.messageInput.value.trim();

        if (!message) {
            this.showToast('Please enter a message', 'warning');
            return;
        }

        if (message.length > 1000) {
            this.showToast('Message too long. Please keep it under 1000 characters.', 'warning');
            return;
        }

        this.sendMessage(message);
    }

    handleInputChange(e) {
        const length = e.target.value.length;
        const maxLength = 1000;

        if (this.elements.characterCount) {
            this.elements.characterCount.textContent = `${length}/${maxLength}`;

            if (length > maxLength * 0.9) {
                this.elements.characterCount.className = 'character-count error';
            } else if (length > maxLength * 0.8) {
                this.elements.characterCount.className = 'character-count warning';
            } else {
                this.elements.characterCount.className = 'character-count';
            }
        }

        if (this.elements.sendBtn) {
            this.elements.sendBtn.disabled = length === 0 || length > maxLength;
        }
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSubmit(e);
        }
    }

    autoResize(e) {
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    }

    sendQuickAction(query) {
        if (this.elements.messageInput) {
            this.elements.messageInput.value = query;
            this.elements.messageInput.focus();
            this.sendMessage(query);
        }
    }

    // ✅ FIXED: Improved EventSource handling
    async sendMessage(message) {
        console.log('📤 Sending message:', message);

        const userMessage = {
            type: 'user',
            content: this.sanitizeInput(message),
            timestamp: new Date()
        };

        this.displayMessage(userMessage);
        this.addToConversationHistory(message, 'user');
        this.clearAndDisableInput();
        this.showTypingIndicator();

        try {
            const params = new URLSearchParams();
            params.append('msg', message);
            params.append('session_id', this.sessionId);

            console.log('📡 Opening EventSource connection...');
            const eventSource = new EventSource(`/get?${params.toString()}`);
            let fullResponse = '';
            let sources = [];
            let messageId = `msg_${Date.now()}`;
            let hasStartedResponse = false;
            let connectionClosed = false; // ✅ FIXED: Track connection state

            eventSource.onopen = () => {
                console.log('✅ EventSource connection opened');
            };

            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('📨 Received:', data.type, data.content?.substring(0, 30) + '...');

                    if (data.type === 'answer_chunk') {
                        if (!hasStartedResponse) {
                            this.hideTypingIndicator();
                            hasStartedResponse = true;
                        }
                        fullResponse += data.content;
                        this.updateBotMessage(messageId, fullResponse);

                    } else if (data.type === 'sources') {
                        sources = data.content;
                        this.updateBotMessageSources(messageId, sources);

                        // ✅ FIXED: Proper connection cleanup
                        connectionClosed = true;
                        eventSource.close();
                        this.enableForm();
                        this.addToConversationHistory(fullResponse, 'bot');
                        console.log('✅ Response completed successfully');

                    } else if (data.type === 'medical_warning') {
                        this.showMedicalWarning(data.content);

                    } else if (data.type === 'error') {
                        connectionClosed = true;
                        this.handleError(data.content);
                        eventSource.close();
                        this.enableForm();
                    }
                } catch (e) {
                    console.error('❌ Error parsing SSE data:', e, event.data);
                }
            };

            // ✅ FIXED: Improved error handling
            eventSource.onerror = (error) => {
                console.error('❌ EventSource error:', error, 'ReadyState:', eventSource.readyState);

                // ✅ Only show error if connection actually failed (not normal close)
                if (!connectionClosed && !hasStartedResponse) {
                    this.hideTypingIndicator();
                    this.handleError('Connection error. Please refresh the page and try again.');
                    this.enableForm();
                } else if (!connectionClosed && hasStartedResponse) {
                    // ✅ Connection closed after receiving response - this is normal
                    console.log('✅ Connection closed after receiving response (normal)');
                    this.enableForm();
                }

                if (!connectionClosed) {
                    eventSource.close();
                    connectionClosed = true;
                }
            };

            // ✅ FIXED: Reduced timeout and better cleanup
            setTimeout(() => {
                if (!connectionClosed && eventSource.readyState !== EventSource.CLOSED) {
                    console.warn('⏰ EventSource timeout, closing connection');
                    connectionClosed = true;
                    eventSource.close();

                    if (!hasStartedResponse) {
                        this.hideTypingIndicator();
                        this.handleError('Request timed out. Please try again.');
                        this.enableForm();
                    }
                }
            }, 15000); // Reduced from 30s to 15s

            this.currentMessageId = messageId;

        } catch (error) {
            console.error('❌ Send message error:', error);
            this.hideTypingIndicator();
            this.handleError('Failed to send message. Please try again.');
            this.enableForm();
        }
    }

    clearAndDisableInput() {
        if (this.elements.messageInput) {
            this.elements.messageInput.value = '';
            this.elements.messageInput.style.height = 'auto';
        }

        if (this.elements.characterCount) {
            this.elements.characterCount.textContent = '0/1000';
            this.elements.characterCount.className = 'character-count';
        }

        if (this.elements.sendBtn) {
            this.elements.sendBtn.disabled = true;
            this.elements.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    }

    displayMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${message.type}`;
        messageDiv.style.animation = 'messageSlideIn 0.4s ease-out';

        if (message.type === 'user') {
            messageDiv.innerHTML = this.createUserMessageHTML(message);
        } else {
            const messageId = `msg_${Date.now()}`;
            messageDiv.innerHTML = this.createBotMessageHTML(message, messageId);
        }

        this.elements.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    createUserMessageHTML(message) {
        return `
            <div class="message-content">
                <div class="message-bubble">
                    ${message.content}
                    <div class="message-time">${this.formatTime(message.timestamp)}</div>
                </div>
            </div>
            <div class="message-avatar">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #10B981, #059669); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: bold; box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);">U</div>
            </div>
        `;
    }

    createBotMessageHTML(message, messageId) {
        return `
            <div class="message-avatar">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; font-weight: bold; box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);">M</div>
            </div>
            <div class="message-content">
                <div class="message-bubble" id="${messageId}">
                    ${typeof message.content === 'string' ? this.formatMarkdown(message.content) : message.content}
                    <div class="message-time">${this.formatTime(message.timestamp)}</div>
                    ${message.sources && message.sources.length > 0 ? this.renderSources(message.sources) : ''}
                </div>
            </div>
        `;
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-bot';
        typingDiv.id = 'typing-indicator';
        typingDiv.style.animation = 'messageSlideIn 0.4s ease-out';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; font-weight: bold; box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);">M</div>
            </div>
            <div class="message-content">
                <div class="typing-indicator" style="background: #f8f9fa; padding: 16px 20px; border-radius: 20px; display: flex; align-items: center; gap: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
                    <span style="color: #6b7280; font-weight: 500;">Analyzing medical data...</span>
                    <div class="typing-dots" style="display: flex; gap: 4px;">
                        <div class="typing-dot" style="width: 8px; height: 8px; background: #667eea; border-radius: 50%; animation: typingDot 1.4s ease-in-out infinite;"></div>
                        <div class="typing-dot" style="width: 8px; height: 8px; background: #667eea; border-radius: 50%; animation: typingDot 1.4s ease-in-out infinite; animation-delay: 0.2s;"></div>
                        <div class="typing-dot" style="width: 8px; height: 8px; background: #667eea; border-radius: 50%; animation: typingDot 1.4s ease-in-out infinite; animation-delay: 0.4s;"></div>
                    </div>
                </div>
            </div>
        `;

        if (!document.querySelector('#typing-animation-styles')) {
            const style = document.createElement('style');
            style.id = 'typing-animation-styles';
            style.textContent = `
                @keyframes typingDot { 0%, 60%, 100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-8px); opacity: 1; } }
                @keyframes messageSlideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            `;
            document.head.appendChild(style);
        }

        this.elements.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    updateBotMessage(messageId, content) {
        let messageElement = document.getElementById(messageId);

        if (!messageElement) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message message-bot';
            messageDiv.style.animation = 'messageSlideIn 0.4s ease-out';
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; font-weight: bold; box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);">M</div>
                </div>
                <div class="message-content">
                    <div class="message-bubble" id="${messageId}">
                        <div class="message-time">${this.formatTime(new Date())}</div>
                    </div>
                </div>
            `;
            this.elements.messagesContainer.appendChild(messageDiv);
            messageElement = document.getElementById(messageId);
        }

        const timeElement = messageElement.querySelector('.message-time');
        const sourcesElement = messageElement.querySelector('.message-sources');

        const formattedContent = this.formatMarkdown(content);
        messageElement.innerHTML = formattedContent;

        if (timeElement) {
            messageElement.appendChild(timeElement);
        }
        if (sourcesElement) {
            messageElement.appendChild(sourcesElement);
        }

        this.scrollToBottom();
    }

    updateBotMessageSources(messageId, sources) {
        const messageElement = document.getElementById(messageId);
        if (messageElement && sources && sources.length > 0) {
            const sourcesHtml = this.renderSources(sources);
            messageElement.insertAdjacentHTML('beforeend', sourcesHtml);
        }
    }

    renderSources(sources) {
        if (!sources || sources.length === 0) return '';

        const sourcesList = sources.map(source => {
            let displayName, credibilityScore, icon;

            if (typeof source === 'object') {
                displayName = source.name || 'Unknown Source';
                credibilityScore = source.credibility || 0.7;
                icon = source.icon || '📚';
            } else {
                displayName = source.split(/[\\/]/).pop() || 'Medical Reference';
                credibilityScore = 0.7;
                icon = '📚';
            }

            const credibilityColor = credibilityScore >= 0.8 ? '#22c55e' :
                                   credibilityScore >= 0.6 ? '#f59e0b' : '#6b7280';

            return `
                <li class="source-item" style="display: flex; align-items: center; gap: 8px; padding: 6px; background: #f8f9fa; border-radius: 6px; margin-bottom: 4px;">
                    <span style="font-size: 14px;">${icon}</span>
                    <span style="flex: 1; font-size: 12px; color: #374151;">${this.sanitizeInput(displayName)}</span>
                    <div style="display: flex; align-items: center; gap: 4px; color: ${credibilityColor}; font-size: 10px; font-weight: 600;">
                        <span>★</span>
                        <span>${Math.round(credibilityScore * 100)}%</span>
                    </div>
                </li>
            `;
        }).join('');

        return `
            <div class="message-sources" style="margin-top: 15px; padding-top: 12px; border-top: 1px solid #e5e7eb;">
                <h6 style="font-size: 12px; color: #6b7280; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                    <span style="color: #059669;">📖</span>
                    Medical Sources
                </h6>
                <ul style="list-style: none; margin: 0; padding: 0;">
                    ${sourcesList}
                </ul>
            </div>
        `;
    }

    showMedicalWarning(content) {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'medical-warning';
        warningDiv.style.cssText = `
            background: linear-gradient(135deg, #fef3c7, #fed7aa);
            border: 1px solid #f59e0b;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            animation: warningFadeIn 0.5s ease-out;
            box-shadow: 0 4px 6px rgba(245, 158, 11, 0.1);
        `;
        warningDiv.innerHTML = `
            <div style="color: #f59e0b; font-size: 20px; line-height: 1; margin-top: 2px;">⚠️</div>
            <div style="flex: 1; color: #92400e; font-size: 14px; line-height: 1.5; font-weight: 500;">${content}</div>
        `;

        if (!document.querySelector('#warning-animation-styles')) {
            const style = document.createElement('style');
            style.id = 'warning-animation-styles';
            style.textContent = `
                @keyframes warningFadeIn {
                    from { opacity: 0; transform: translateY(-10px) scale(0.95); }
                    to { opacity: 1; transform: translateY(0) scale(1); }
                }
            `;
            document.head.appendChild(style);
        }

        this.elements.messagesContainer.appendChild(warningDiv);
        this.scrollToBottom();
    }

    handleError(message) {
        console.error('💥 Chat error:', message);
        this.hideTypingIndicator();
        this.enableForm();

        // ✅ Only show error in chat, not as toast (reduces duplicate errors)
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            background: #fee2e2;
            color: #dc2626;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 12px 0;
            border-left: 4px solid #dc2626;
            font-size: 14px;
            animation: messageSlideIn 0.4s ease-out;
        `;
        errorDiv.innerHTML = `<strong>❌ Error:</strong> ${message}`;

        this.elements.messagesContainer.appendChild(errorDiv);
        this.scrollToBottom();
    }

    enableForm() {
        if (this.elements.sendBtn) {
            this.elements.sendBtn.disabled = this.elements.messageInput ? this.elements.messageInput.value.trim().length === 0 : false;
            this.elements.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }

        if (this.elements.messageInput) {
            this.elements.messageInput.focus();
        }
    }

    scrollToBottom() {
        if (this.elements.messagesContainer) {
            this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
        }
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    sanitizeInput(input) {
        if (!input) return '';
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }

    formatMarkdown(text) {
        if (!text) return '';
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.9em;">$1</code>')
            .replace(/\n\n/g, '</p><p style="margin: 12px 0;">')
            .replace(/\n/g, '<br>')
            .replace(/^(.+)/, '<p style="margin: 8px 0;">$1')
            .replace(/(.+)$/, '$1</p>');
    }

    // Placeholder methods for compatibility
    initializeVoiceRecognition() { console.log('🎤 Voice recognition placeholder'); }
    toggleVoiceRecording() { console.log('Voice recording not implemented'); }
    handleFileAttachment() { console.log('File attachment not implemented'); }
    addToConversationHistory() { }
    loadConversationHistory() { }
    updateConversationHistorySidebar() { }
    groupConversationsByDate() { return []; }
    loadConversation() { }
    setupFeedbackModal() { }
    updateStarRating() { }
    maybeShowFeedbackModal() { }
    showFeedbackModal() { }
    submitFeedback() { }
    showSettings() { }
    showHelp() { }
    showToast(message, type = 'info') {
        console.log(`Toast [${type}]:`, message);
    }
}

// Initialize
console.log('🚀 Setting up MediBot initialization...');

function initializeMediBot() {
    if (!window.mediBotChat) {
        try {
            window.mediBotChat = new MediBotChat();
            console.log('✅ MediBot Chat initialized successfully!');
        } catch (error) {
            console.error('❌ MediBot initialization error:', error);
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMediBot);
} else {
    setTimeout(initializeMediBot, 100);
}

window.addEventListener('load', () => {
    if (!window.mediBotChat) {
        setTimeout(initializeMediBot, 500);
    }
});

setTimeout(() => {
    if (!window.mediBotChat) {
        initializeMediBot();
    }
}, 2000);

console.log('🎯 MediBot Enhanced Chat script loaded successfully!');
