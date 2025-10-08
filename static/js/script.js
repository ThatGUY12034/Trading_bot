// ENHANCED TRADING DASHBOARD WITH ANGEL ONE USER AUTHENTICATION AND PROPER EVENT BINDING

class TradingDashboard {
    constructor() {
        this.chart = null;
        this.dataUpdateInterval = null;
        this.botStatus = 'stopped';
        this.selectedStock = null;
        this.stocks = [];
        this.currencySymbol = '₹';
        this.isAPIConnected = false;
        this.currentDataSource = 'simulated';
        this.currentUser = null;
        this.isAuthenticated = false;
        this.userPortfolio = null;
        
        // Bind all methods to maintain 'this' context
        this.initializeDashboard = this.initializeDashboard.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        this.setupAuthEventListeners = this.setupAuthEventListeners.bind(this);
        this.handleLogin = this.handleLogin.bind(this);
        this.handleLogout = this.handleLogout.bind(this);
        this.checkAuthStatus = this.checkAuthStatus.bind(this);
        this.updateAuthUI = this.updateAuthUI.bind(this);
        this.loadUserPortfolio = this.loadUserPortfolio.bind(this);
        this.loadUserOrders = this.loadUserOrders.bind(this);
        this.updatePortfolioDisplay = this.updatePortfolioDisplay.bind(this);
        this.updateOrderBookDisplay = this.updateOrderBookDisplay.bind(this);
        this.placeManualOrder = this.placeManualOrder.bind(this);
        this.validateQuantity = this.validateQuantity.bind(this);
        this.enableRealTradingFeatures = this.enableRealTradingFeatures.bind(this);
        this.disableRealTradingFeatures = this.disableRealTradingFeatures.bind(this);
        this.startBot = this.startBot.bind(this);
        this.pauseBot = this.pauseBot.bind(this);
        this.stopBot = this.stopBot.bind(this);
        this.startRealTimeUpdates = this.startRealTimeUpdates.bind(this);
        this.updateBotControls = this.updateBotControls.bind(this);
        this.changeTimeframe = this.changeTimeframe.bind(this);
        this.updateTime = this.updateTime.bind(this);
        this.showNotification = this.showNotification.bind(this);
        this.clearNotifications = this.clearNotifications.bind(this);
        this.checkAPIStatus = this.checkAPIStatus.bind(this);
        this.updateConnectionStatus = this.updateConnectionStatus.bind(this);
        this.createStatusIndicator = this.createStatusIndicator.bind(this);
        this.connectAPI = this.connectAPI.bind(this);
        this.disconnectAPI = this.disconnectAPI.bind(this);
        this.loadStocks = this.loadStocks.bind(this);
        this.displayStocks = this.displayStocks.bind(this);
        this.filterStocks = this.filterStocks.bind(this);
        this.selectStock = this.selectStock.bind(this);
        this.fetchMarketData = this.fetchMarketData.bind(this);
        this.updateDashboardWithRealData = this.updateDashboardWithRealData.bind(this);
        this.updateDataSourceIndicator = this.updateDataSourceIndicator.bind(this);
        this.createDataSourceIndicator = this.createDataSourceIndicator.bind(this);
        this.updateCandlestickChart = this.updateCandlestickChart.bind(this);
        this.createFinancialCandlestickChart = this.createFinancialCandlestickChart.bind(this);
        this.createOHLCBarChart = this.createOHLCBarChart.bind(this);
        this.updateLineChart = this.updateLineChart.bind(this);
        this.updateTradingSignals = this.updateTradingSignals.bind(this);
        this.updatePortfolio = this.updatePortfolio.bind(this);
        this.updateUserPortfolioDisplay = this.updateUserPortfolioDisplay.bind(this);
        this.updateTradeHistory = this.updateTradeHistory.bind(this);
        this.updateWithSimulatedData = this.updateWithSimulatedData.bind(this);
        this.getBasePrice = this.getBasePrice.bind(this);
        this.generateSimulatedCandlestickData = this.generateSimulatedCandlestickData.bind(this);
        this.updateGauge = this.updateGauge.bind(this);
        this.initializeGauges = this.initializeGauges.bind(this);
        
        this.initializeDashboard();
    }

    initializeDashboard() {
        console.log("🚀 Initializing Trading Dashboard with Angel One User Authentication...");
        
        this.setupEventListeners();
        this.initializeAuth();
        this.loadStocks();
        this.updateTime();
        this.initializeGauges();
        this.checkAPIStatus();
        
        setInterval(() => this.updateTime(), 1000);
        setInterval(() => this.checkAPIStatus(), 30000);
        setInterval(() => this.checkAuthStatus(), 60000);
        
        this.showNotification('Dashboard initialized successfully', 'success');
    }

    initializeAuth() {
        // Check if user is already authenticated
        const savedUser = localStorage.getItem('angelOneUser');
        if (savedUser) {
            this.currentUser = JSON.parse(savedUser);
            this.checkAuthStatus();
        }
        
        this.setupAuthEventListeners();
    }

    setupEventListeners() {
        // Trading controls - use arrow functions or bind to maintain context
        document.getElementById('startBtn').addEventListener('click', () => this.startBot());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pauseBot());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopBot());
        document.getElementById('connectBtn').addEventListener('click', () => this.connectAPI());
        document.getElementById('loadStocksBtn').addEventListener('click', () => this.loadStocks());
        document.getElementById('stockSearch').addEventListener('input', (e) => this.filterStocks(e.target.value));
        document.getElementById('timeframeSelect').addEventListener('change', (e) => {
            this.changeTimeframe(e.target.value);
        });
        document.getElementById('clearNotifications').addEventListener('click', () => this.clearNotifications());
        
        // Manual trading controls
        document.getElementById('buyBtn').addEventListener('click', () => this.placeManualOrder('BUY'));
        document.getElementById('sellBtn').addEventListener('click', () => this.placeManualOrder('SELL'));
        document.getElementById('quantity').addEventListener('input', (e) => this.validateQuantity(e.target.value));
        
        // Add disconnect button
        const disconnectBtn = document.createElement('button');
        disconnectBtn.className = 'btn btn-warning';
        disconnectBtn.innerHTML = '<i class="fas fa-plug"></i> Disconnect';
        disconnectBtn.addEventListener('click', () => this.disconnectAPI());
        document.querySelector('.header-right').appendChild(disconnectBtn);
    }

    setupAuthEventListeners() {
        // Login form submission
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }
        
        // Logout button - use event delegation for dynamically created elements
        document.addEventListener('click', (e) => {
            if (e.target.id === 'logoutBtn' || e.target.closest('#logoutBtn')) {
                this.handleLogout();
            }
        });
    }

    // AUTHENTICATION METHODS
    async handleLogin() {
    const clientId = document.getElementById('clientId').value;
    const apiKey = document.getElementById('apiKey').value;
    const clientPin = document.getElementById('clientPin').value;
    const totpSecret = document.getElementById('totpSecret').value;

    const loginBtn = document.getElementById('loginBtn');
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
    loginBtn.disabled = true;

    try {
        console.log('🔐 Attempting login with:', { clientId, apiKey: apiKey ? '***' : 'empty', clientPin: clientPin ? '***' : 'empty' });

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                client_id: clientId,
                api_key: apiKey,
                client_pin: clientPin,
                totp_secret: totpSecret
            })
        });

        console.log('📡 Response status:', response.status);
        console.log('📡 Response headers:', response.headers);

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            console.error('❌ Server returned non-JSON response:', textResponse.substring(0, 500));
            throw new Error(`Server error: ${response.status} - ${response.statusText}`);
        }

        const result = await response.json();
        console.log('📊 Login result:', result);

        if (result.success) {
            this.currentUser = {
                user_id: result.user_id,
                user_profile: result.user_profile,
                authenticated: true,
                demo_mode: result.demo_mode || false
            };
            
            this.isAuthenticated = true;
            
            // Save to localStorage
            localStorage.setItem('angelOneUser', JSON.stringify(this.currentUser));
            
            this.updateAuthUI();
            
            if (result.demo_mode) {
                this.showNotification('Demo mode activated with enhanced data', 'info');
            } else {
                this.showNotification('Angel One login successful! Real trading enabled.', 'success');
            }
            
            // Load user portfolio and orders
            await this.loadUserPortfolio();
            await this.loadUserOrders();
            
        } else {
            throw new Error(result.message);
        }

    } catch (error) {
        console.error('❌ Login error:', error);
        
        if (error.message.includes('Server error: 500')) {
            this.showNotification('Server error: Please check if the backend is running properly', 'error');
        } else if (error.message.includes('Unexpected token')) {
            this.showNotification('Server returned invalid response. Please check server logs.', 'error');
        } else {
            this.showNotification(`Login failed: ${error.message}`, 'error');
        }
        
        // Auto-fallback to demo mode for testing
        this.currentUser = {
            user_id: 'demo_auto',
            user_profile: {
                client_id: 'DEMO_AUTO',
                name: 'Demo User',
                email: 'demo@auto.com'
            },
            authenticated: true,
            demo_mode: true
        };
        
        this.isAuthenticated = true;
        localStorage.setItem('angelOneUser', JSON.stringify(this.currentUser));
        this.updateAuthUI();
        await this.loadUserPortfolio();
    }

    loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login to Angel One';
    loginBtn.disabled = false;
}

    async handleLogout() {
        try {
            if (this.currentUser) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: this.currentUser.user_id
                    })
                });
            }

            this.currentUser = null;
            this.isAuthenticated = false;
            this.userPortfolio = null;
            localStorage.removeItem('angelOneUser');
            
            this.updateAuthUI();
            this.showNotification('Logged out successfully', 'info');

        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    async checkAuthStatus() {
        if (!this.currentUser) return;

        try {
            const response = await fetch(`/api/auth/status?user_id=${this.currentUser.user_id}`);
            const result = await response.json();

            if (result.success && result.authenticated) {
                this.isAuthenticated = true;
                this.updateAuthUI();
                // Refresh portfolio data
                await this.loadUserPortfolio();
            } else {
                this.handleLogout();
            }

        } catch (error) {
            console.error('Auth status check failed:', error);
        }
    }

    updateAuthUI() {
        const loginSection = document.getElementById('loginSection');
        const tradingSection = document.getElementById('tradingSection');
        const userInfo = document.getElementById('userInfo');

        if (this.isAuthenticated && this.currentUser) {
            if (loginSection) loginSection.style.display = 'none';
            if (tradingSection) tradingSection.style.display = 'block';
            
            if (userInfo) {
                userInfo.innerHTML = `
                    <div class="user-profile">
                        <i class="fas fa-user-circle"></i>
                        <span class="user-name">${this.currentUser.user_profile?.client_id || 'User'}</span>
                        <button id="logoutBtn" class="btn btn-sm btn-outline-danger">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </button>
                    </div>
                `;
            }
            
            // Enable real trading features
            this.enableRealTradingFeatures();
            
        } else {
            if (loginSection) loginSection.style.display = 'block';
            if (tradingSection) tradingSection.style.display = 'none';
            if (userInfo) userInfo.innerHTML = '';
            
            // Disable real trading features
            this.disableRealTradingFeatures();
        }
    }

    enableRealTradingFeatures() {
        // Enable manual trading buttons
        const buyBtn = document.getElementById('buyBtn');
        const sellBtn = document.getElementById('sellBtn');
        if (buyBtn) buyBtn.disabled = false;
        if (sellBtn) sellBtn.disabled = false;
        
        // Update trading mode indicator
        const tradingMode = document.getElementById('tradingMode');
        if (tradingMode) {
            tradingMode.innerHTML = '<i class="fas fa-bolt"></i> REAL TRADING MODE';
            tradingMode.className = 'trading-mode real-mode';
        }
        
        this.showNotification('Real trading features enabled', 'success');
    }

    disableRealTradingFeatures() {
        // Disable manual trading buttons
        const buyBtn = document.getElementById('buyBtn');
        const sellBtn = document.getElementById('sellBtn');
        if (buyBtn) buyBtn.disabled = true;
        if (sellBtn) sellBtn.disabled = true;
        
        // Update trading mode indicator
        const tradingMode = document.getElementById('tradingMode');
        if (tradingMode) {
            tradingMode.innerHTML = '<i class="fas fa-desktop"></i> SIMULATION MODE';
            tradingMode.className = 'trading-mode sim-mode';
        }
    }

    async loadUserPortfolio() {
        if (!this.isAuthenticated || !this.currentUser) return;

        try {
            const response = await fetch(`/api/user/portfolio?user_id=${this.currentUser.user_id}`);
            const result = await response.json();

            if (result.success) {
                this.userPortfolio = result.portfolio;
                this.updatePortfolioDisplay(this.userPortfolio);
            }

        } catch (error) {
            console.error('Portfolio load error:', error);
        }
    }

    async loadUserOrders() {
        if (!this.isAuthenticated || !this.currentUser) return;

        try {
            const response = await fetch(`/api/user/order-book?user_id=${this.currentUser.user_id}`);
            const result = await response.json();

            if (result.success) {
                this.updateOrderBookDisplay(result.order_book);
            }

        } catch (error) {
            console.error('Order book load error:', error);
        }
    }

    updatePortfolioDisplay(portfolio) {
        const portfolioElement = document.getElementById('userPortfolio');
        if (!portfolioElement) return;

        const margin = portfolio.margin?.data || {};
        const holdings = portfolio.holdings?.data || [];
        const positions = portfolio.positions?.data || [];

        portfolioElement.innerHTML = `
            <div class="portfolio-summary">
                <h4><i class="fas fa-wallet"></i> Your Portfolio</h4>
                <div class="portfolio-metrics">
                    <div class="metric">
                        <span class="label">Available Cash:</span>
                        <span class="value">₹${(margin.availablecash || 0).toLocaleString()}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Utilized Margin:</span>
                        <span class="value">₹${(margin.utilisedmargin || 0).toLocaleString()}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Open Positions:</span>
                        <span class="value">${positions.length}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Holdings:</span>
                        <span class="value">${holdings.length}</span>
                    </div>
                </div>
            </div>
        `;
    }

    updateOrderBookDisplay(orderBook) {
        const orderBookElement = document.getElementById('orderBook');
        if (!orderBookElement) return;

        const orders = orderBook?.data || [];

        if (orders.length === 0) {
            orderBookElement.innerHTML = '<div class="no-orders">No active orders</div>';
            return;
        }

        orderBookElement.innerHTML = `
            <h5><i class="fas fa-clipboard-list"></i> Active Orders</h5>
            <div class="orders-list">
                ${orders.slice(0, 5).map(order => `
                    <div class="order-item ${order.transactiontype?.toLowerCase()}">
                        <div class="order-symbol">${order.tradingsymbol}</div>
                        <div class="order-details">
                            <span class="order-type ${order.transactiontype?.toLowerCase()}">${order.transactiontype}</span>
                            <span class="order-quantity">Qty: ${order.quantity}</span>
                            <span class="order-status ${order.orderstatus?.toLowerCase()}">${order.orderstatus}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // MANUAL TRADING METHODS
    async placeManualOrder(orderType) {
        if (!this.isAuthenticated) {
            this.showNotification('Please login to Angel One to place real orders', 'warning');
            return;
        }

        if (!this.selectedStock) {
            this.showNotification('Please select a stock first', 'warning');
            return;
        }

        const quantityInput = document.getElementById('quantity');
        const quantity = parseInt(quantityInput.value) || 1;

        if (quantity <= 0) {
            this.showNotification('Please enter a valid quantity', 'error');
            return;
        }

        try {
            const response = await fetch('/api/user/place-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.currentUser.user_id,
                    symbol: this.selectedStock,
                    quantity: quantity,
                    order_type: orderType,
                    product_type: 'DELIVERY'
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(`${orderType} order placed for ${this.selectedStock} (Qty: ${quantity})`, 'success');
                
                // Refresh portfolio and orders
                await this.loadUserPortfolio();
                await this.loadUserOrders();
                
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            console.error('Order placement error:', error);
            this.showNotification(`Order failed: ${error.message}`, 'error');
        }
    }

    validateQuantity(value) {
        const quantity = parseInt(value);
        if (quantity <= 0) {
            document.getElementById('quantity').classList.add('error');
        } else {
            document.getElementById('quantity').classList.remove('error');
        }
    }

    // API CONNECTION METHODS
    async checkAPIStatus() {
        try {
            const response = await fetch('/api/api-status');
            const status = await response.json();
            
            this.isAPIConnected = status.connected;
            this.updateConnectionStatus();
            
        } catch (error) {
            console.log('API status check failed:', error);
            this.isAPIConnected = false;
            this.updateConnectionStatus();
        }
    }

    updateConnectionStatus() {
        const connectBtn = document.getElementById('connectBtn');
        const statusIndicator = document.getElementById('apiStatus') || this.createStatusIndicator();
        
        if (this.isAPIConnected) {
            connectBtn.innerHTML = '<i class="fas fa-check"></i> Connected';
            connectBtn.classList.remove('btn-primary');
            connectBtn.classList.add('btn-success');
            statusIndicator.className = 'status-indicator connected';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Angel One Connected';
        } else {
            connectBtn.innerHTML = '<i class="fas fa-plug"></i> Connect API';
            connectBtn.classList.remove('btn-success');
            connectBtn.classList.add('btn-primary');
            statusIndicator.className = 'status-indicator disconnected';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i> API Disconnected';
        }
    }

    createStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'apiStatus';
        indicator.className = 'status-indicator';
        document.querySelector('.header-left').appendChild(indicator);
        return indicator;
    }

    async connectAPI() {
        const connectBtn = document.getElementById('connectBtn');
        connectBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Connecting...';
        connectBtn.disabled = true;
        
        try {
            const response = await fetch('/api/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isAPIConnected = true;
                this.updateConnectionStatus();
                this.showNotification('Angel One API connected successfully! Real data enabled.', 'success');
                
                // Reload stocks with real data
                await this.loadStocks();
                
            } else {
                throw new Error(result.message || 'Connection failed');
            }
            
        } catch (error) {
            console.error('API connection failed:', error);
            this.showNotification(`Connection failed: ${error.message}`, 'error');
        }
        
        connectBtn.disabled = false;
        this.updateConnectionStatus();
    }

    async disconnectAPI() {
        try {
            const response = await fetch('/api/disconnect', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isAPIConnected = false;
                this.updateConnectionStatus();
                this.showNotification('Disconnected from Angel One API', 'warning');
            }
            
        } catch (error) {
            console.error('Disconnection failed:', error);
            this.showNotification('Disconnection failed', 'error');
        }
    }

    // STOCK MANAGEMENT METHODS
    async loadStocks() {
        const loadBtn = document.getElementById('loadStocksBtn');
        loadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        loadBtn.disabled = true;

        try {
            const response = await fetch('/api/stocks');
            const result = await response.json();
            
            if (result.success && Array.isArray(result.stocks)) {
                this.stocks = result.stocks;
                this.displayStocks();
                
                const sourceMsg = result.source === 'angel_one' ? ' (Real Data)' : ' (Static Data)';
                this.showNotification(`Loaded ${this.stocks.length} stocks${sourceMsg}`, 'success');
            } else {
                throw new Error(result.message || 'Failed to load stocks');
            }
            
        } catch (error) {
            console.error('Error loading stocks:', error);
            // Fallback to static stocks
            this.stocks = [
                { symbol: 'SBIN', name: 'State Bank of India', ltp: 545.25, change: 1.25 },
                { symbol: 'RELIANCE', name: 'Reliance Industries Ltd.', ltp: 2850.50, change: -0.75 },
                { symbol: 'INFY', name: 'Infosys Ltd.', ltp: 1850.75, change: 2.15 },
                { symbol: 'TCS', name: 'Tata Consultancy Services Ltd.', ltp: 3850.25, change: 0.45 },
                { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd.', ltp: 1650.80, change: -1.20 },
                { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd.', ltp: 1050.60, change: 0.80 },
                { symbol: 'TATAMOTORS', name: 'Tata Motors Ltd.', ltp: 785.40, change: 3.20 },
                { symbol: 'BHARTIARTL', name: 'Bharti Airtel Ltd.', ltp: 1023.45, change: 1.80 }
            ];
            this.displayStocks();
            this.showNotification('Using static stock data', 'info');
        }
        
        loadBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Load Stocks';
        loadBtn.disabled = false;
    }

    displayStocks() {
        const stocksList = document.getElementById('stocksList');
        const stockCount = document.getElementById('stockCount');
        
        if (!this.stocks.length) {
            stocksList.innerHTML = '<div class="no-stocks">No stocks found</div>';
            stockCount.textContent = '0 stocks';
            return;
        }
        
        stocksList.innerHTML = this.stocks.map(stock => `
            <div class="stock-item ${this.selectedStock === stock.symbol ? 'selected' : ''}" 
                 onclick="window.dashboard.selectStock('${stock.symbol}')">
                <div class="stock-info">
                    <div class="stock-symbol">${stock.symbol}</div>
                    <div class="stock-name">${stock.name}</div>
                    ${this.isAPIConnected ? '<div class="real-data-badge">LIVE</div>' : ''}
                </div>
                <div class="stock-price">
                    <div class="stock-ltp">${this.currencySymbol}${stock.ltp.toFixed(2)}</div>
                    <div class="stock-change ${stock.change >= 0 ? 'positive' : 'negative'}">
                        ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%
                    </div>
                </div>
            </div>
        `).join('');
        
        stockCount.textContent = `${this.stocks.length} stocks ${this.isAPIConnected ? '(LIVE)' : '(STATIC)'}`;
        
        if (!this.selectedStock && this.stocks.length > 0) {
            this.selectStock(this.stocks[0].symbol);
        }
    }

    filterStocks(searchTerm) {
        if (!this.stocks) return;
        const term = searchTerm.toLowerCase();
        const filteredStocks = this.stocks.filter(stock => 
            stock.symbol.toLowerCase().includes(term) || 
            stock.name.toLowerCase().includes(term)
        );
        
        const stocksList = document.getElementById('stocksList');
        if (filteredStocks.length === 0) {
            stocksList.innerHTML = '<div class="no-stocks">No matching stocks found</div>';
            return;
        }
        
        stocksList.innerHTML = filteredStocks.map(stock => `
            <div class="stock-item ${this.selectedStock === stock.symbol ? 'selected' : ''}" 
                 onclick="window.dashboard.selectStock('${stock.symbol}')">
                <div class="stock-info">
                    <div class="stock-symbol">${stock.symbol}</div>
                    <div class="stock-name">${stock.name}</div>
                    ${this.isAPIConnected ? '<div class="real-data-badge">LIVE</div>' : ''}
                </div>
                <div class="stock-price">
                    <div class="stock-ltp">${this.currencySymbol}${stock.ltp.toFixed(2)}</div>
                    <div class="stock-change ${stock.change >= 0 ? 'positive' : 'negative'}">
                        ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%
                    </div>
                </div>
            </div>
        `).join('');
    }

    async selectStock(symbol) {
        this.selectedStock = symbol;
        const stock = this.stocks.find(s => s.symbol === symbol);
        
        if (stock) {
            document.getElementById('selectedSymbol').textContent = symbol;
            document.getElementById('selectedStock').textContent = `${symbol} - ${stock.name}`;
            document.getElementById('tradingSymbol').textContent = symbol;
            document.getElementById('currentPrice').textContent = `${this.currencySymbol}${stock.ltp.toFixed(2)}`;
            document.getElementById('manualTradingSymbol').textContent = symbol;
            
            // Fetch real market data
            await this.fetchMarketData(symbol);
            this.showNotification(`Selected stock: ${symbol}`, 'info');
        }
        
        this.displayStocks();
    }

    // ENHANCED BOT METHODS WITH USER AUTH
    async startBot() {
        if (!this.selectedStock) {
            this.showNotification('Please select a stock first', 'warning');
            return;
        }

        // Check if user is authenticated for real trading
        if (!this.isAuthenticated) {
            const useRealTrading = confirm('You are not logged in. Start bot in simulation mode?');
            if (!useRealTrading) return;
        }

        try {
            const requestBody = {
                symbol: this.selectedStock
            };

            // Include user_id if authenticated
            if (this.isAuthenticated && this.currentUser) {
                requestBody.user_id = this.currentUser.user_id;
            }

            const response = await fetch('/api/bot/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.botStatus = 'running';
                this.updateBotControls();
                
                const tradingMode = result.user_authenticated ? 'REAL Angel One account' : 'simulated data';
                this.showNotification(`Trading bot started for ${this.selectedStock} with ${tradingMode}`, 'success');
                this.startRealTimeUpdates();
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Error starting bot:', error);
            this.showNotification('Error starting trading bot', 'error');
        }
    }

    async pauseBot() {
        try {
            const response = await fetch('/api/bot/pause', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.botStatus = 'paused';
                this.updateBotControls();
                this.showNotification('Trading bot paused', 'warning');
            }
            
        } catch (error) {
            console.error('Error pausing bot:', error);
        }
    }

    async stopBot() {
        try {
            const response = await fetch('/api/bot/stop', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.botStatus = 'stopped';
                this.updateBotControls();
                this.showNotification('Trading bot stopped', 'info');
                
                if (this.dataUpdateInterval) {
                    clearInterval(this.dataUpdateInterval);
                }
            }
            
        } catch (error) {
            console.error('Error stopping bot:', error);
        }
    }

    startRealTimeUpdates() {
        if (this.dataUpdateInterval) {
            clearInterval(this.dataUpdateInterval);
        }
        
        this.dataUpdateInterval = setInterval(async () => {
            if (this.botStatus === 'running' && this.selectedStock) {
                await this.fetchMarketData(this.selectedStock);
            }
        }, 5000);
    }

    updateBotControls() {
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const stopBtn = document.getElementById('stopBtn');
        const statusElement = document.getElementById('botStatus');
        
        startBtn.disabled = false;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
        
        switch(this.botStatus) {
            case 'running':
                startBtn.disabled = true;
                statusElement.textContent = 'Running';
                statusElement.className = 'status-text running';
                break;
            case 'paused':
                pauseBtn.disabled = true;
                statusElement.textContent = 'Paused';
                statusElement.className = 'status-text paused';
                break;
            case 'stopped':
                stopBtn.disabled = true;
                statusElement.textContent = 'Stopped';
                statusElement.className = 'status-text stopped';
                break;
        }
    }

    // ENHANCED MARKET DATA FETCHING
    async fetchMarketData(symbol) {
        try {
            console.log(`📡 Fetching market data for ${symbol}...`);
            
            let url = `/api/market-data?symbol=${symbol}`;
            
            // Include user_id if authenticated for personalized data
            if (this.isAuthenticated && this.currentUser) {
                url += `&user_id=${this.currentUser.user_id}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            console.log('📊 Received market data:', data.source, data);
            
            this.currentDataSource = data.source || 'unknown';
            this.updateDashboardWithRealData(data);
            
            // Show data source notification
            if (data.source && data.source.includes('angel_one_real')) {
                const mode = this.isAuthenticated ? 'Real Account' : 'Real Data';
                this.showNotification(`${mode} loaded for ${symbol}`, 'success');
            } else if (data.source && data.source.includes('ml_analysis')) {
                this.showNotification(`ML analysis data for ${symbol}`, 'info');
            } else {
                this.showNotification(`Simulated data for ${symbol}`, 'warning');
            }
            
        } catch (error) {
            console.error('❌ Error fetching market data:', error);
            this.updateWithSimulatedData(symbol);
            this.showNotification('Using simulated data due to connection issues', 'error');
        }
    }

    // ENHANCED DASHBOARD UPDATE WITH USER DATA
    updateDashboardWithRealData(data) {
        // Update current price
        if (data.currentPrice) {
            document.getElementById('currentPrice').textContent = `${this.currencySymbol}${data.currentPrice}`;
        }
        
        // Update trading signals
        if (data.signal) {
            this.updateTradingSignals(data.signal);
        }
        
        // Update support/resistance levels
        if (data.levels) {
            document.getElementById('supportLevel').textContent = `${this.currencySymbol}${data.levels.support}`;
            document.getElementById('resistanceLevel').textContent = `${this.currencySymbol}${data.levels.resistance}`;
        }
        
        // Update ML metrics
        if (data.mlMetrics) {
            this.updateGauge('accuracyGauge', data.mlMetrics.accuracy);
            this.updateGauge('confidenceGauge', data.mlMetrics.confidence);
            
            const statusElement = document.getElementById('modelStatus');
            if (statusElement) {
                statusElement.textContent = 'Model Active';
                statusElement.className = 'status-active';
            }
        }
        
        // Update portfolio - prefer user portfolio if available
        if (this.userPortfolio && this.isAuthenticated) {
            this.updateUserPortfolioDisplay();
        } else if (data.portfolio) {
            this.updatePortfolio(data.portfolio);
        }
        
        // Update chart with CANDLESTICK data
        if (data.candlestickData) {
            this.updateCandlestickChart(data.candlestickData);
        } else if (data.chartData) {
            this.updateLineChart(data.chartData);
        }
        
        // Update trade history
        if (data.tradeHistory) {
            this.updateTradeHistory(data.tradeHistory);
        }
        
        // Update data source indicator
        this.updateDataSourceIndicator(data.source);
    }

    updateUserPortfolioDisplay() {
        if (!this.userPortfolio) return;
        
        const margin = this.userPortfolio.margin?.data || {};
        const balance = margin.availablecash || 0;
        const utilized = margin.utilisedmargin || 0;
        const positions = this.userPortfolio.positions?.data || [];
        
        document.getElementById('balance').textContent = `${this.currencySymbol}${balance.toLocaleString()}`;
        
        const pnlElement = document.getElementById('dailyPnL');
        // Calculate approximate P&L from positions
        const totalPnl = positions.reduce((sum, pos) => sum + (parseFloat(pos.pnl) || 0), 0);
        pnlElement.textContent = `${totalPnl >= 0 ? '+' : ''}${this.currencySymbol}${Math.abs(totalPnl).toFixed(2)}`;
        pnlElement.className = `metric-value ${totalPnl >= 0 ? 'positive' : 'negative'}`;
        
        document.getElementById('openPositions').textContent = positions.length;
        
        // Calculate win rate from positions
        const winningTrades = positions.filter(pos => parseFloat(pos.pnl) > 0).length;
        const winRate = positions.length > 0 ? (winningTrades / positions.length * 100).toFixed(1) : 0;
        document.getElementById('winRate').textContent = `${winRate}%`;
    }

    updateCandlestickChart(candlestickData) {
        const ctx = document.getElementById('priceChart');
        if (!ctx) {
            console.error('Chart canvas not found!');
            return;
        }
        
        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }
        
        console.log('Creating candlestick chart with data:', candlestickData);
        
        // Check if we have the financial plugin
        if (typeof Chart.controllers.candlestick !== 'undefined') {
            // Use financial plugin if available
            this.createFinancialCandlestickChart(ctx, candlestickData);
        } else {
            // Fallback to OHLC bars
            this.createOHLCBarChart(ctx, candlestickData);
        }
    }

    createFinancialCandlestickChart(ctx, candlestickData) {
        // Prepare data for financial chart
        const financialData = candlestickData.map(candle => ({
            x: new Date(candle.time).getTime(), // Convert to timestamp
            o: candle.open,
            h: candle.high,
            l: candle.low,
            c: candle.close
        }));
        
        // Create proper financial/candlestick chart
        this.chart = new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: this.selectedStock,
                    data: financialData,
                    color: {
                        up: '#10b981',
                        down: '#ef4444',
                        unchanged: '#6b7280',
                    },
                    borderColor: {
                        up: '#10b981',
                        down: '#ef4444',
                        unchanged: '#6b7280',
                    },
                    backgroundColor: {
                        up: 'rgba(16, 185, 129, 0.8)',
                        down: 'rgba(239, 68, 68, 0.8)',
                        unchanged: 'rgba(107, 114, 128, 0.8)',
                    },
                    borderWidth: 1,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const point = context.raw;
                                return [
                                    `Open: ${this.currencySymbol}${point.o.toFixed(2)}`,
                                    `High: ${this.currencySymbol}${point.h.toFixed(2)}`,
                                    `Low: ${this.currencySymbol}${point.l.toFixed(2)}`,
                                    `Close: ${this.currencySymbol}${point.c.toFixed(2)}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        },
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 8,
                            maxRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            callback: (value) => {
                                return `${this.currencySymbol}${value.toFixed(0)}`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Financial candlestick chart created successfully');
    }

    createOHLCBarChart(ctx, candlestickData) {
        const labels = candlestickData.map(candle => {
            // Format time for display
            if (typeof candle.time === 'string') {
                return candle.time;
            } else if (candle.time instanceof Date) {
                return candle.time.toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    hour12: false 
                });
            }
            return candle.time;
        });
        
        // Create custom OHLC visualization using bar chart
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Price',
                    data: candlestickData.map(candle => ({
                        x: candle.time,
                        o: candle.open,
                        h: candle.high, 
                        l: candle.low,
                        c: candle.close,
                        // Use close price for bar height, but show OHLC in tooltip
                        y: candle.close
                    })),
                    backgroundColor: candlestickData.map(candle => 
                        candle.close >= candle.open ? 'rgba(16, 185, 129, 0.8)' : 'rgba(239, 68, 68, 0.8)'
                    ),
                    borderColor: candlestickData.map(candle => 
                        candle.close >= candle.open ? '#10b981' : '#ef4444'
                    ),
                    borderWidth: 1,
                    barPercentage: 0.6,
                    categoryPercentage: 0.8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const data = context.raw;
                                return [
                                    `Open: ${this.currencySymbol}${data.o.toFixed(2)}`,
                                    `High: ${this.currencySymbol}${data.h.toFixed(2)}`,
                                    `Low: ${this.currencySymbol}${data.l.toFixed(2)}`,
                                    `Close: ${this.currencySymbol}${data.c.toFixed(2)}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 8,
                            maxRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            callback: (value) => {
                                return `${this.currencySymbol}${value.toFixed(0)}`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ OHLC bar chart created successfully');
    }

    // Fallback line chart
    updateLineChart(chartData) {
        const ctx = document.getElementById('priceChart');
        if (!ctx) return;
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: this.selectedStock,
                    data: chartData.prices,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        ticks: {
                            callback: (value) => `${this.currencySymbol}${value}`
                        }
                    }
                }
            }
        });
    }

    updateTradingSignals(signal) {
        const signalElement = document.getElementById('currentSignal');
        const signalType = signalElement.querySelector('.signal-type');
        const signalConfidence = signalElement.querySelector('.signal-confidence');
        const signalIcon = signalElement.querySelector('.signal-icon i');
        
        signalType.textContent = signal.type;
        signalConfidence.textContent = `${signal.confidence}% confidence - ${signal.reason || 'Market analysis'}`;
        
        signalElement.className = 'signal';
        signalIcon.className = 'fas';
        
        switch(signal.type) {
            case 'BUY':
                signalElement.classList.add('buy-signal');
                signalIcon.classList.add('fa-arrow-up');
                break;
            case 'SELL':
                signalElement.classList.add('sell-signal');
                signalIcon.classList.add('fa-arrow-down');
                break;
            case 'HOLD':
                signalElement.classList.add('hold-signal');
                signalIcon.classList.add('fa-pause-circle');
                break;
        }
    }

    updatePortfolio(portfolio) {
        document.getElementById('balance').textContent = `${this.currencySymbol}${portfolio.balance.toLocaleString()}`;
        
        const pnlElement = document.getElementById('dailyPnL');
        pnlElement.textContent = `${portfolio.dailyPnL >= 0 ? '+' : ''}${this.currencySymbol}${Math.abs(portfolio.dailyPnL).toLocaleString()}`;
        pnlElement.className = `metric-value ${portfolio.dailyPnL >= 0 ? 'positive' : 'negative'}`;
        
        document.getElementById('openPositions').textContent = portfolio.openPositions;
        document.getElementById('winRate').textContent = `${portfolio.winRate}%`;
    }

    updateTradeHistory(trades) {
        const historyContainer = document.getElementById('tradeHistory');
        if (!historyContainer) return;
        
        if (!trades || trades.length === 0) {
            historyContainer.innerHTML = '<div class="no-trades">No trades yet</div>';
            return;
        }
        
        historyContainer.innerHTML = trades.map(trade => `
            <div class="trade-item ${trade.type ? trade.type.toLowerCase() : ''}">
                <div class="trade-info">
                    <div class="trade-symbol">${trade.symbol || 'N/A'}</div>
                    <div class="trade-time">${trade.timestamp || 'N/A'}</div>
                    ${trade.order_type === 'REAL' ? '<div class="real-trade-badge">REAL</div>' : ''}
                </div>
                <div class="trade-details">
                    <div class="trade-type ${trade.type ? trade.type.toLowerCase() : ''}">${trade.type || 'N/A'}</div>
                    <div class="trade-price">${this.currencySymbol}${trade.price || '0'}</div>
                    <div class="trade-pnl ${trade.pnl >= 0 ? 'positive' : 'negative'}">
                        ${trade.pnl >= 0 ? '+' : ''}${this.currencySymbol}${Math.abs(trade.pnl || 0).toFixed(2)}
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Fallback to simulated data when API fails
    updateWithSimulatedData(symbol) {
        console.log('🔄 Using simulated data for', symbol);
        
        const simulatedData = {
            currentPrice: (this.getBasePrice(symbol) + (Math.random() - 0.5) * 50).toFixed(2),
            signal: {
                type: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)],
                confidence: (70 + Math.random() * 25).toFixed(1),
                reason: 'Simulated market analysis'
            },
            levels: {
                support: (this.getBasePrice(symbol) * 0.95).toFixed(2),
                resistance: (this.getBasePrice(symbol) * 1.05).toFixed(2)
            },
            mlMetrics: {
                accuracy: (70 + Math.random() * 25).toFixed(1),
                confidence: (75 + Math.random() * 20).toFixed(1)
            },
            portfolio: {
                balance: (100000 + Math.random() * 5000).toFixed(2),
                dailyPnL: (Math.random() * 1000 - 300).toFixed(2),
                openPositions: Math.floor(Math.random() * 5),
                winRate: (65 + Math.random() * 25).toFixed(1)
            },
            candlestickData: this.generateSimulatedCandlestickData(symbol),
            source: 'simulated_fallback'
        };
        
        this.updateDashboardWithRealData(simulatedData);
    }

    getBasePrice(symbol) {
        const basePrices = {
            'SBIN': 545, 'RELIANCE': 2850, 'INFY': 1850, 'TCS': 3850,
            'HDFCBANK': 1650, 'ICICIBANK': 1050, 'TATAMOTORS': 785, 'BHARTIARTL': 1023
        };
        return basePrices[symbol] || 1000;
    }

    generateSimulatedCandlestickData(symbol) {
        const basePrice = this.getBasePrice(symbol);
        const candles = [];
        let currentPrice = basePrice;
        const now = new Date();
        
        for (let i = 19; i >= 0; i--) {
            const time = new Date(now);
            time.setMinutes(time.getMinutes() - i * 15);
            
            const open = i === 19 ? basePrice : candles[candles.length - 1].close;
            const change = (Math.random() - 0.5) * (basePrice * 0.02);
            const close = open + change;
            const high = Math.max(open, close) + Math.random() * (basePrice * 0.01);
            const low = Math.min(open, close) - Math.random() * (basePrice * 0.01);
            
            candles.push({
                time: time, // Keep as Date object for proper parsing
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(high.toFixed(2)),
                low: parseFloat(low.toFixed(2)),
                close: parseFloat(close.toFixed(2))
            });
            
            currentPrice = close;
        }
        
        return candles;
    }

    updateGauge(canvasId, value) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height;
        const radius = canvas.width / 2 - 5;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Background
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
        ctx.strokeStyle = '#374151';
        ctx.lineWidth = 8;
        ctx.stroke();
        
        // Value
        const percentage = Math.max(0, Math.min(1, value / 100));
        const endAngle = Math.PI + (percentage * Math.PI);
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, endAngle);
        ctx.strokeStyle = canvasId === 'accuracyGauge' ? '#10b981' : '#3b82f6';
        ctx.lineWidth = 8;
        ctx.stroke();
        
        // Text
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${Math.round(value)}%`, centerX, centerY - 10);
    }

    initializeGauges() {
        this.updateGauge('accuracyGauge', 75);
        this.updateGauge('confidenceGauge', 82);
    }

    updateDataSourceIndicator(source) {
        let indicator = document.getElementById('dataSourceIndicator');
        if (!indicator) {
            indicator = this.createDataSourceIndicator();
        }
        
        let sourceText = 'Unknown';
        let indicatorClass = 'unknown';
        
        if (source && source.includes('angel_one_real')) {
            sourceText = 'Angel One Real Data';
            indicatorClass = 'real';
        } else if (source && source.includes('ml_analysis')) {
            sourceText = 'ML Analysis Data';
            indicatorClass = 'ml';
        } else if (source && source.includes('simulated')) {
            sourceText = 'Simulated Data';
            indicatorClass = 'simulated';
        }
        
        indicator.textContent = sourceText;
        indicator.className = `data-source-indicator ${indicatorClass}`;
    }

    createDataSourceIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'dataSourceIndicator';
        indicator.className = 'data-source-indicator';
        document.querySelector('.header-left').appendChild(indicator);
        return indicator;
    }

    changeTimeframe(timeframe) {
        this.showNotification(`Timeframe changed to ${timeframe}`, 'info');
        if (this.selectedStock) {
            this.fetchMarketData(this.selectedStock);
        }
    }

    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour12: true, 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        const dateString = now.toLocaleDateString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        document.getElementById('currentTime').textContent = `${dateString} ${timeString}`;
    }

    showNotification(message, type = 'info') {
        const notificationsList = document.getElementById('notificationsList');
        const noNotifications = notificationsList.querySelector('.no-notifications');
        
        if (noNotifications) {
            notificationsList.removeChild(noNotifications);
        }
        
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${icons[type]}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${message}</div>
                <div class="notification-time">${new Date().toLocaleTimeString()}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        notificationsList.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    clearNotifications() {
        const notificationsList = document.getElementById('notificationsList');
        notificationsList.innerHTML = '<div class="no-notifications">No notifications</div>';
    }
}
// Login functionality
class LoginManager {
    constructor() {
        this.isLoading = false;
        this.initializeLoginEvents();
    }

    initializeLoginEvents() {
        // Toggle password visibility
        document.querySelectorAll('.toggle-password').forEach(button => {
            button.addEventListener('click', (e) => {
                const targetId = e.target.closest('.toggle-password').dataset.target;
                const input = document.getElementById(targetId);
                const icon = e.target.closest('.toggle-password').querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });

        // Login form submission
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Demo mode button
        document.getElementById('demoModeBtn').addEventListener('click', () => {
            this.enableDemoMode();
        });

        // Load saved credentials if any
        this.loadSavedCredentials();
    }

    async handleLogin() {
        if (this.isLoading) return;

        const loginBtn = document.getElementById('loginBtn');
        const formData = {
            clientId: document.getElementById('clientId').value.trim(),
            apiKey: document.getElementById('apiKey').value.trim(),
            clientPin: document.getElementById('clientPin').value.trim(),
            totpSecret: document.getElementById('totpSecret').value.trim()
        };

        // Validation
        if (!this.validateCredentials(formData)) {
            return;
        }

        this.setLoading(true);

        try {
            // Simulate API call - replace with actual Angel One API integration
            await this.simulateAPICall(formData);
            
            // Save credentials if remember me is checked
            if (document.getElementById('rememberCredentials').checked) {
                this.saveCredentials(formData);
            }

            this.showSuccess('Login successful! Connecting to Angel One...');
            setTimeout(() => {
                this.showTradingInterface();
            }, 1500);

        } catch (error) {
            this.showError('Login failed: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    }

    validateCredentials(data) {
        if (!data.clientId || data.clientId.length !== 8) {
            this.showError('Please enter a valid 8-digit Client ID');
            return false;
        }
        if (!data.apiKey) {
            this.showError('Please enter your API Key');
            return false;
        }
        if (!data.clientPin) {
            this.showError('Please enter your Client PIN');
            return false;
        }
        if (!data.totpSecret) {
            this.showError('Please enter your TOTP Secret');
            return false;
        }
        return true;
    }

    async simulateAPICall(credentials) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simulate random success/failure for demo
        if (Math.random() > 0.3) {
            return { success: true, message: 'Connected successfully' };
        } else {
            throw new Error('Invalid credentials or network error');
        }
    }

    enableDemoMode() {
        this.showSuccess('Starting in Demo Mode with simulated data...');
        setTimeout(() => {
            this.showTradingInterface();
            // Set demo mode flag
            window.isDemoMode = true;
            document.getElementById('tradingMode').textContent = 'DEMO MODE';
            document.getElementById('tradingMode').classList.add('demo-mode');
        }, 1000);
    }

    setLoading(loading) {
        this.isLoading = loading;
        const loginBtn = document.getElementById('loginBtn');
        
        if (loading) {
            loginBtn.classList.add('loading');
            loginBtn.disabled = true;
        } else {
            loginBtn.classList.remove('loading');
            loginBtn.disabled = false;
        }
    }

    showTradingInterface() {
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('tradingSection').style.display = 'block';
        
        // Initialize trading interface
        if (window.tradingDashboard) {
            window.tradingDashboard.initialize();
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // You can integrate this with your existing notification system
        console.log(`${type.toUpperCase()}: ${message}`);
        alert(message); // Replace with your notification system
    }

    saveCredentials(credentials) {
        localStorage.setItem('angelOneCredentials', JSON.stringify(credentials));
    }

    loadSavedCredentials() {
        const saved = localStorage.getItem('angelOneCredentials');
        if (saved) {
            try {
                const credentials = JSON.parse(saved);
                document.getElementById('clientId').value = credentials.clientId || '';
                document.getElementById('apiKey').value = credentials.apiKey || '';
                document.getElementById('clientPin').value = credentials.clientPin || '';
                document.getElementById('totpSecret').value = credentials.totpSecret || '';
                document.getElementById('rememberCredentials').checked = true;
            } catch (e) {
                console.error('Error loading saved credentials:', e);
            }
        }
    }
}

// Initialize login manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.loginManager = new LoginManager();
});

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TradingDashboard();
});