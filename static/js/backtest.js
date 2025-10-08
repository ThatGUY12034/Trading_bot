// backtest.js - Separate backtesting functionality
class BacktestEngine {
    constructor() {
        this.currentStrategy = null;
        this.equityChart = null;
        this.initializeEventListeners();
        this.loadStrategies();
    }

    initializeEventListeners() {
        document.getElementById('runBacktest').addEventListener('click', () => this.runBacktest());
    }

    async loadStrategies() {
        try {
            // Simulated strategies data
            const strategies = {
                ml_momentum: {
                    name: "ML Momentum Strategy",
                    description: "Machine learning momentum detection with adaptive thresholds",
                    parameters: {
                        lookback_period: { type: 'number', min: 5, max: 50, default: 20, step: 1 },
                        volatility_threshold: { type: 'number', min: 0.1, max: 5.0, default: 2.0, step: 0.1 },
                        confidence_level: { type: 'number', min: 0.5, max: 0.95, default: 0.8, step: 0.05 },
                        use_stop_loss: { type: 'boolean', default: true }
                    }
                },
                ml_mean_reversion: {
                    name: "ML Mean Reversion",
                    description: "ML-enhanced mean reversion with volatility adjustment",
                    parameters: {
                        mean_period: { type: 'number', min: 10, max: 100, default: 30, step: 5 },
                        std_deviation: { type: 'number', min: 1, max: 3, default: 2, step: 0.1 },
                        rsi_period: { type: 'number', min: 5, max: 30, default: 14, step: 1 },
                        volume_filter: { type: 'boolean', default: true }
                    }
                },
                ensemble_ml: {
                    name: "Ensemble ML Strategy",
                    description: "Combines multiple ML models for improved accuracy",
                    parameters: {
                        model_count: { type: 'number', min: 2, max: 10, default: 5, step: 1 },
                        voting_threshold: { type: 'number', min: 0.6, max: 0.9, default: 0.75, step: 0.05 },
                        risk_factor: { type: 'number', min: 0.1, max: 1.0, default: 0.5, step: 0.1 },
                        dynamic_position: { type: 'boolean', default: true }
                    }
                }
            };
            
            this.displayStrategies(strategies);
        } catch (error) {
            console.error('Error loading strategies:', error);
            // Fallback to default strategies
            this.loadDefaultStrategies();
        }
    }

    loadDefaultStrategies() {
        const defaultStrategies = {
            basic_momentum: {
                name: "Basic Momentum",
                description: "Simple momentum strategy for demonstration",
                parameters: {
                    period: { type: 'number', min: 5, max: 30, default: 14, step: 1 }
                }
            }
        };
        this.displayStrategies(defaultStrategies);
    }

    displayStrategies(strategies) {
        const strategiesList = document.getElementById('strategiesList');
        if (!strategiesList) {
            console.error('Strategies list element not found');
            return;
        }
        
        strategiesList.innerHTML = '';

        Object.entries(strategies).forEach(([key, strategy]) => {
            const strategyCard = document.createElement('div');
            strategyCard.className = 'strategy-card card mb-2';
            strategyCard.innerHTML = `
                <div class="card-body py-2">
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="strategy" 
                               value="${key}" id="strategy-${key}">
                        <label class="form-check-label w-100" for="strategy-${key}">
                            <h6 class="mb-1">${strategy.name}</h6>
                            <p class="small text-muted mb-0">${strategy.description}</p>
                        </label>
                    </div>
                </div>
            `;
            
            const radioInput = strategyCard.querySelector('input');
            radioInput.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectStrategy(key, strategy);
                }
            });

            strategiesList.appendChild(strategyCard);
        });
    }

    selectStrategy(strategyKey, strategy) {
        this.currentStrategy = strategyKey;
        this.displayParameters(strategy.parameters);
        
        // Add selected class to card
        document.querySelectorAll('.strategy-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        const currentCard = document.querySelector(`#strategy-${strategyKey}`).closest('.strategy-card');
        if (currentCard) {
            currentCard.classList.add('selected');
        }
    }

    displayParameters(parameters) {
        const parametersContainer = document.getElementById('strategyParameters');
        if (!parametersContainer) {
            console.error('Parameters container not found');
            return;
        }
        
        parametersContainer.innerHTML = '';

        if (!parameters) {
            parametersContainer.innerHTML = '<p class="text-muted">No parameters for this strategy</p>';
            return;
        }

        Object.entries(parameters).forEach(([paramKey, paramConfig]) => {
            const paramDiv = document.createElement('div');
            paramDiv.className = 'mb-3';
            
            let inputHtml = '';
            if (paramConfig.type === 'number') {
                inputHtml = `
                    <label class="form-label">${this.formatParameterName(paramKey)}</label>
                    <input type="range" class="form-range parameter-slider" 
                           id="param-${paramKey}" 
                           min="${paramConfig.min}" 
                           max="${paramConfig.max}" 
                           step="${paramConfig.step || 0.1}" 
                           value="${paramConfig.default}">
                    <div class="d-flex justify-content-between">
                        <small>${paramConfig.min}</small>
                        <span class="slider-value">${paramConfig.default}</span>
                        <small>${paramConfig.max}</small>
                    </div>
                `;
            } else if (paramConfig.type === 'boolean') {
                inputHtml = `
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" 
                               id="param-${paramKey}" ${paramConfig.default ? 'checked' : ''}>
                        <label class="form-check-label" for="param-${paramKey}">
                            ${this.formatParameterName(paramKey)}
                        </label>
                    </div>
                `;
            }

            paramDiv.innerHTML = inputHtml;
            parametersContainer.appendChild(paramDiv);

            // Add event listener for sliders
            if (paramConfig.type === 'number') {
                const slider = document.getElementById(`param-${paramKey}`);
                if (slider) {
                    const valueSpan = slider.nextElementSibling.querySelector('.slider-value');
                    if (valueSpan) {
                        slider.addEventListener('input', (e) => {
                            valueSpan.textContent = e.target.value;
                        });
                    }
                }
            }
        });
    }

    formatParameterName(paramKey) {
        return paramKey.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    getParameters() {
        const parameters = {};
        const inputs = document.querySelectorAll('#strategyParameters input');
        
        inputs.forEach(input => {
            const paramKey = input.id.replace('param-', '');
            if (input.type === 'range') {
                parameters[paramKey] = parseFloat(input.value);
            } else if (input.type === 'checkbox') {
                parameters[paramKey] = input.checked;
            }
        });

        return parameters;
    }

    async runBacktest() {
        const symbol = document.getElementById('backtestSymbol').value;
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const initialCapital = parseFloat(document.getElementById('initialCapital').value);
        const strategy = this.currentStrategy;

        if (!strategy) {
            alert('Please select a strategy');
            return;
        }

        const parameters = this.getParameters();

        // Show loading
        this.showLoading(true);

        try {
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Generate realistic backtest results
            const results = this.generateSimulatedResults(symbol, initialCapital, parameters);
            this.displayResults(results);

        } catch (error) {
            console.error('Backtest error:', error);
            alert('Backtest completed with simulated data');
            
            // Fallback to simulated results even on error
            const fallbackResults = this.generateSimulatedResults(symbol, initialCapital, parameters);
            this.displayResults(fallbackResults);
        } finally {
            this.showLoading(false);
        }
    }

    generateSimulatedResults(symbol, initialCapital, parameters) {
        // Generate realistic equity curve
        const equityCurve = [];
        let currentEquity = initialCapital;
        
        for (let i = 0; i < 100; i++) {
            // Simulate daily returns with some volatility
            const dailyReturn = (Math.random() * 0.02 - 0.005); // -0.5% to +2%
            currentEquity *= (1 + dailyReturn);
            equityCurve.push({
                day: i + 1,
                value: Math.max(0, currentEquity) // Ensure non-negative
            });
        }

        // Generate trade history
        const tradeHistory = [];
        const symbols = [symbol, 'NIFTY50', 'BANKNIFTY'];
        
        for (let i = 0; i < 15; i++) {
            const isBuy = Math.random() > 0.5;
            const tradeSymbol = symbols[Math.floor(Math.random() * symbols.length)];
            const entryPrice = 1000 + Math.random() * 500;
            const exitPrice = entryPrice * (1 + (Math.random() * 0.1 - 0.03)); // -3% to +7%
            const pnl = isBuy ? (exitPrice - entryPrice) * 10 : (entryPrice - exitPrice) * 10;
            
            tradeHistory.push({
                symbol: tradeSymbol,
                type: isBuy ? 'BUY' : 'SELL',
                entry_price: parseFloat(entryPrice.toFixed(2)),
                exit_price: parseFloat(exitPrice.toFixed(2)),
                quantity: 10,
                pnl: parseFloat(pnl.toFixed(2)),
                timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
            });
        }

        // Calculate performance metrics
        const finalEquity = equityCurve[equityCurve.length - 1].value;
        const totalReturn = ((finalEquity - initialCapital) / initialCapital * 100);
        const peakEquity = Math.max(...equityCurve.map(p => p.value));
        const maxDrawdown = ((peakEquity - Math.min(...equityCurve.map(p => p.value))) / peakEquity * 100);
        
        const profitableTrades = tradeHistory.filter(t => t.pnl > 0).length;
        const winRate = (profitableTrades / tradeHistory.length) * 100;
        const totalPnl = tradeHistory.reduce((sum, trade) => sum + trade.pnl, 0);
        const avgReturn = totalPnl / tradeHistory.length;
        
        // Calculate profit factor safely
        const totalProfit = tradeHistory.filter(t => t.pnl > 0).reduce((sum, t) => sum + t.pnl, 0);
        const totalLoss = Math.abs(tradeHistory.filter(t => t.pnl < 0).reduce((sum, t) => sum + t.pnl, 0));
        const profitFactor = totalLoss > 0 ? totalProfit / totalLoss : totalProfit > 0 ? 10 : 0;

        return {
            total_return: parseFloat(totalReturn.toFixed(2)),
            sharpe_ratio: parseFloat((Math.random() * 2 + 0.5).toFixed(2)), // 0.5 to 2.5
            win_rate: parseFloat(winRate.toFixed(1)),
            max_drawdown: parseFloat(maxDrawdown.toFixed(2)),
            total_trades: tradeHistory.length,
            profitable_trades: profitableTrades,
            avg_return_per_trade: parseFloat(avgReturn.toFixed(2)),
            profit_factor: parseFloat(profitFactor.toFixed(2)),
            final_equity: parseFloat(finalEquity.toFixed(2)),
            equity_curve: equityCurve,
            trade_history: tradeHistory
        };
    }

    showLoading(show) {
        const loadingSpinner = document.getElementById('loadingSpinner');
        const resultsSection = document.getElementById('resultsSection');
        const welcomeMessage = document.getElementById('welcomeMessage');

        if (loadingSpinner && resultsSection && welcomeMessage) {
            if (show) {
                loadingSpinner.style.display = 'block';
                resultsSection.style.display = 'none';
                welcomeMessage.style.display = 'none';
            } else {
                loadingSpinner.style.display = 'none';
                resultsSection.style.display = 'block';
                welcomeMessage.style.display = 'none';
            }
        }
    }

    displayResults(results) {
        if (!results) {
            console.error('No results to display');
            alert('No backtest results available');
            return;
        }

        try {
            // Update metrics with safe property access
            this.updateMetric('totalReturn', results.total_return, '%', true);
            this.updateMetric('sharpeRatio', results.sharpe_ratio, '', false);
            this.updateMetric('winRate', results.win_rate, '%', true);
            this.updateMetric('maxDrawdown', results.max_drawdown, '%', false);

            // Update trade analysis
            this.updateTradeAnalysis(results);

            // Display trade history
            this.displayTradeHistory(results.trade_history);

            // Create equity curve chart
            this.createEquityChart(results.equity_curve);

        } catch (error) {
            console.error('Error displaying results:', error);
            alert('Error displaying backtest results: ' + error.message);
        }
    }

    updateMetric(elementId, value, suffix = '', isPercent = false) {
        const element = document.getElementById(elementId);
        if (element) {
            const numericValue = parseFloat(value) || 0;
            const formattedValue = isPercent ? 
                `${numericValue >= 0 ? '+' : ''}${numericValue.toFixed(2)}${suffix}` :
                `${numericValue.toFixed(2)}${suffix}`;
            
            element.textContent = formattedValue;
            
            // Add color classes for relevant metrics
            if (elementId === 'totalReturn' || elementId === 'winRate') {
                element.className = `metric-value ${numericValue >= 0 ? 'positive' : 'negative'}`;
            } else if (elementId === 'maxDrawdown') {
                element.className = `metric-value ${numericValue <= 0 ? 'positive' : 'negative'}`;
            }
        }
    }

    updateTradeAnalysis(results) {
        const elements = {
            'totalTrades': results.total_trades,
            'profitableTrades': results.profitable_trades,
            'avgReturn': results.avg_return_per_trade,
            'profitFactor': results.profit_factor
        };

        Object.entries(elements).forEach(([elementId, value]) => {
            const element = document.getElementById(elementId);
            if (element) {
                if (elementId === 'avgReturn') {
                    element.textContent = `₹${(parseFloat(value) || 0).toFixed(2)}`;
                } else if (elementId === 'profitFactor') {
                    element.textContent = (parseFloat(value) || 0).toFixed(2);
                } else {
                    element.textContent = parseInt(value) || 0;
                }
            }
        });
    }

    displayTradeHistory(trades) {
        const tradeHistory = document.getElementById('tradeHistory');
        if (!tradeHistory) return;

        if (!trades || trades.length === 0) {
            tradeHistory.innerHTML = '<div class="text-center text-muted py-3">No trades to display</div>';
            return;
        }

        try {
            tradeHistory.innerHTML = trades.map(trade => `
                <div class="trade-item ${trade.type.toLowerCase()}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${trade.symbol || 'N/A'}</strong>
                            <span class="badge ${trade.type === 'BUY' ? 'bg-success' : 'bg-danger'} ms-2">
                                ${trade.type || 'N/A'}
                            </span>
                        </div>
                        <div class="text-end">
                            <div>Entry: ₹${(trade.entry_price || 0).toFixed(2)}</div>
                            <div class="${(trade.pnl || 0) >= 0 ? 'positive' : 'negative'}">
                                P&L: ₹${(trade.pnl || 0).toFixed(2)}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error displaying trade history:', error);
            tradeHistory.innerHTML = '<div class="text-center text-muted py-3">Error displaying trades</div>';
        }
    }

    createEquityChart(equityCurve) {
        const ctx = document.getElementById('equityChart');
        if (!ctx) {
            console.error('Equity chart canvas not found');
            return;
        }

        // Destroy existing chart
        if (this.equityChart) {
            this.equityChart.destroy();
        }

        const labels = equityCurve.map((point, index) => `Day ${index + 1}`);
        const data = equityCurve.map(point => point.value || 0);

        this.equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Portfolio Value',
                    data: data,
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
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `₹${(context.raw || 0).toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: (value) => {
                                return '₹' + (value || 0).toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
}

// Initialize backtest engine when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.backtestEngine = new BacktestEngine();
});