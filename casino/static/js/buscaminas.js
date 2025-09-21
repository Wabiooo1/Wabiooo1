// Buscaminas Mejorado - Inspirado en Stake con identidad Casino Gold
class MinesGame {
    constructor() {
        this.gameState = {
            isPlaying: false,
            isDemo: !document.getElementById('user-balance'), // Si no hay balance, es demo
            board: [],
            minePositions: [],
            revealedCells: [],
            gridSize: 5,
            mineCount: 3,
            betAmount: 1.00,
            currentMultiplier: 1.00,
            gemsFound: 0,
            totalGems: 22, // 25 - 3 minas por defecto
            balance: 1000.00 // Balance demo por defecto
        };

        this.multipliers = this.calculateMultipliers();
        this.initializeElements();
        this.bindEvents();
        this.updateUI();
        this.generateBoard();
    }

    // Calcular multiplicadores basados en probabilidades reales
    calculateMultipliers() {
        const { gridSize, mineCount } = this.gameState;
        const totalCells = gridSize * gridSize;
        const safeCells = totalCells - mineCount;
        const multipliers = [];
        
        // Fórmula correcta para multiplicadores basada en probabilidad real
        let cumulativeMultiplier = 1;
        
        for (let i = 0; i < safeCells; i++) {
            const cellsLeft = totalCells - i;
            const minesLeft = mineCount;
            const safeLeft = cellsLeft - minesLeft;
            
            // Probabilidad de encontrar una gema en este paso
            const probability = safeLeft / cellsLeft;
            
            // El multiplicador debe compensar el riesgo tomado
            // Fórmula: multiplicador anterior / probabilidad de éxito
            cumulativeMultiplier = cumulativeMultiplier / probability;
            
            // Redondear a 2 decimales y aplicar un pequeño margen de casa (3%)
            const multiplier = Math.round(cumulativeMultiplier * 0.97 * 100) / 100;
            
            multipliers.push(Math.max(1.01, multiplier));
        }
        
        return multipliers;
    }

    initializeElements() {
        this.elements = {
            // Configuración
            minesOptions: document.querySelectorAll('#mines-options .option-btn'),
            gridSizeOptions: document.querySelectorAll('#grid-size-options .option-btn'),
            
            // Estadísticas
            gemsCount: document.getElementById('gems-count'),
            gemsFound: document.getElementById('gems-found'),
            currentMultiplier: document.getElementById('current-multiplier'),
            potentialProfit: document.getElementById('potential-profit'),
            
            // Balance y apuestas
            userBalance: document.getElementById('user-balance'),
            betAmount: document.getElementById('bet-amount'),
            betModifiers: {
                half: document.getElementById('bet-half'),
                down: document.getElementById('bet-down'),
                up: document.getElementById('bet-up'),
                double: document.getElementById('bet-double')
            },
            quickBets: document.querySelectorAll('.quick-bet'),
            
            // Botones de acción
            betBtn: document.getElementById('bet-btn'),
            cashoutBtn: document.getElementById('cashout-btn'),
            
            // Tablero y UI
            board: document.getElementById('board'),
            boardOverlay: document.getElementById('board-overlay'),
            multiplierTrack: document.getElementById('multiplier-track'),
            gameMessages: document.getElementById('game-messages')
        };
    }

    bindEvents() {
        // Configuración de minas
        this.elements.minesOptions.forEach(btn => {
            btn.addEventListener('click', (e) => this.setMineCount(parseInt(e.target.dataset.mines)));
        });

        // Configuración de grid (actualmente solo 5x5)
        this.elements.gridSizeOptions.forEach(btn => {
            btn.addEventListener('click', (e) => this.setGridSize(parseInt(e.target.dataset.size)));
        });

        // Controles de apuesta
        Object.entries(this.elements.betModifiers).forEach(([key, btn]) => {
            if (btn) btn.addEventListener('click', () => this.modifyBet(key));
        });

        this.elements.quickBets.forEach(btn => {
            btn.addEventListener('click', (e) => this.setQuickBet(parseFloat(e.target.dataset.amount)));
        });

        this.elements.betAmount.addEventListener('input', (e) => this.setBetAmount(parseFloat(e.target.value)));

        // Botones principales
        this.elements.betBtn.addEventListener('click', () => this.startGame());
        this.elements.cashoutBtn.addEventListener('click', () => this.cashOut());

        // Eventos del tablero
        this.elements.board.addEventListener('click', (e) => this.handleCellClick(e));
    }

    setMineCount(count) {
        if (this.gameState.isPlaying) return;
        
        this.gameState.mineCount = count;
        this.gameState.totalGems = (this.gameState.gridSize * this.gameState.gridSize) - count;
        this.multipliers = this.calculateMultipliers();
        
        // Actualizar UI
        this.elements.minesOptions.forEach(btn => {
            btn.classList.toggle('selected', parseInt(btn.dataset.mines) === count);
        });
        
        this.updateUI();
        this.generateBoard();
    }

    setGridSize(size) {
        if (this.gameState.isPlaying) return;
        
        this.gameState.gridSize = size;
        this.gameState.totalGems = (size * size) - this.gameState.mineCount;
        this.multipliers = this.calculateMultipliers();
        
        this.elements.gridSizeOptions.forEach(btn => {
            btn.classList.toggle('selected', parseInt(btn.dataset.size) === size);
        });
        
        this.updateUI();
        this.generateBoard();
    }

    modifyBet(type) {
        if (this.gameState.isPlaying) return;
        
        let newAmount = this.gameState.betAmount;
        
        switch(type) {
            case 'half':
                newAmount = newAmount / 2;
                break;
            case 'down':
                newAmount = Math.max(0.01, newAmount - 0.01);
                break;
            case 'up':
                newAmount = newAmount + 0.01;
                break;
            case 'double':
                newAmount = newAmount * 2;
                break;
        }
        
        this.setBetAmount(newAmount);
    }

    setQuickBet(amount) {
        if (this.gameState.isPlaying) return;
        this.setBetAmount(amount);
    }

    setBetAmount(amount) {
        if (this.gameState.isPlaying) return;
        
        const maxBet = this.gameState.isDemo ? 1000 : (this.gameState.balance || 0);
        this.gameState.betAmount = Math.max(0.01, Math.min(amount, maxBet));
        
        this.elements.betAmount.value = this.gameState.betAmount.toFixed(2);
        this.updateUI();
    }

    updateUI() {
        // Actualizar estadísticas
        if (this.elements.gemsCount) {
            this.elements.gemsCount.textContent = this.gameState.totalGems;
        }
        
        if (this.elements.gemsFound) {
            this.elements.gemsFound.textContent = this.gameState.gemsFound;
        }
        
        if (this.elements.currentMultiplier) {
            this.elements.currentMultiplier.textContent = this.gameState.currentMultiplier.toFixed(2) + 'x';
        }
        
        if (this.elements.potentialProfit) {
            const profit = this.gameState.betAmount * this.gameState.currentMultiplier;
            this.elements.potentialProfit.textContent = 
             + profit.toFixed(2);
        }
        
        // Actualizar botones
        if (this.elements.betBtn) {
            const btnAmount = this.elements.betBtn.querySelector('.btn-amount');
            if (btnAmount) btnAmount.textContent = 
             + this.gameState.betAmount.toFixed(2);
        }
        
        if (this.elements.cashoutBtn) {
            const cashoutAmount = document.getElementById('cashout-amount');
            if (cashoutAmount) {
                const winAmount = this.gameState.betAmount * this.gameState.currentMultiplier;
                cashoutAmount.textContent = 
             + winAmount.toFixed(2);
            }
        }
        
        this.updateMultiplierTrack();
    }

    updateMultiplierTrack() {
        if (!this.elements.multiplierTrack) return;
        
        this.elements.multiplierTrack.innerHTML = '';
        
        this.multipliers.slice(0, 10).forEach((mult, index) => {
            const item = document.createElement('div');
            item.className = 'multiplier-item';
            item.textContent = mult.toFixed(2) + 'x';
            
            if (index < this.gameState.gemsFound) {
                item.classList.add('passed');
            } else if (index === this.gameState.gemsFound) {
                item.classList.add('active');
            }
            
            this.elements.multiplierTrack.appendChild(item);
        });
    }

    generateBoard() {
        if (!this.elements.board) return;
        
        const { gridSize } = this.gameState;
        this.elements.board.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;
        
        // Limpiar tablero existente
        const cells = this.elements.board.querySelectorAll('.cell');
        cells.forEach(cell => cell.remove());
        
        // Generar nuevas celdas
        for (let i = 0; i < gridSize * gridSize; i++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.index = i;
            this.elements.board.appendChild(cell);
        }
    }

    async startGame() {
        if (this.gameState.isPlaying) return;
        
        // Validar apuesta
        if (!this.gameState.isDemo) {
            try {
                const balanceResponse = await fetch('/api/get_balance');
                const balanceData = await balanceResponse.json();
                
                if (!balanceData.ok) {
                    this.showMessage('Error al obtener el balance');
                    return;
                }
                
                this.gameState.balance = balanceData.saldo;
                
                if (this.gameState.betAmount > this.gameState.balance) {
                    this.showMessage('Saldo insuficiente');
                    return;
                }
            } catch (error) {
                this.showMessage('Error de conexión');
                return;
            }
        }
        
        // Iniciar juego en el servidor
        try {
            const response = await fetch('/api/mines/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    bet: this.gameState.betAmount,
                    mines: this.gameState.mineCount,
                    grid_size: this.gameState.gridSize
                })
            });
            
            const data = await response.json();
            
            if (!data.ok) {
                this.showMessage(data.msg || 'Error al iniciar el juego');
                return;
            }
            
            // Actualizar estado del juego
            this.gameState.isPlaying = true;
            this.gameState.revealedCells = [];
            this.gameState.gemsFound = 0;
            this.gameState.currentMultiplier = 1.00;
            this.gameState.gameId = data.game_id;
            
            // Actualizar balance
            if (typeof data.saldo !== 'undefined') {
                this.gameState.balance = data.saldo;
                this.updateBalance(data.saldo);
            }
            
            // Actualizar UI
            this.elements.boardOverlay.style.display = 'none';
            this.elements.betBtn.style.display = 'none';
            this.elements.cashoutBtn.style.display = 'block';
            
            this.showMessage('¡Encuentra las gemas y evita las minas!');
            this.updateUI();
            
            this.playSound('click');
            
        } catch (error) {
            console.error('Error al iniciar juego:', error);
            this.showMessage('Error de conexión con el servidor');
        }
    }

    async handleCellClick(e) {
        if (!this.gameState.isPlaying) return;
        
        const cell = e.target.closest('.cell');
        if (!cell || cell.classList.contains('revealed')) return;
        
        const index = parseInt(cell.dataset.index);
        
        // Enviar solicitud al servidor para revelar celda
        try {
            const response = await fetch('/api/mines/reveal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cell: index
                })
            });
            
            const data = await response.json();
            
            if (!data.ok) {
                this.showMessage(data.msg || 'Error al revelar celda');
                return;
            }
            
            if (data.result === 'mine') {
                this.hitMine(cell, index, data);
            } else {
                this.revealGem(cell, index, data);
            }
            
        } catch (error) {
            console.error('Error al revelar celda:', error);
            this.showMessage('Error de conexión');
        }
    }

    async revealGem(cell, index, data) {
        this.gameState.revealedCells.push(index);
        this.gameState.gemsFound = data.gems_found;
        this.gameState.currentMultiplier = data.multiplier;
        
        // Animación de revelado
        cell.classList.add('revealed', 'gem');
        cell.innerHTML = '<img src="/static/img/gem.svg" class="cell-content" alt="Gem">';
        
        this.playSound('gem');
        this.updateUI();
        
        // Verificar si ganó
        if (data.game_over && data.victory) {
            // Victoria total
            if (typeof data.saldo !== 'undefined') {
                this.updateBalance(data.saldo);
            }
            this.showProfitPopup(data.payout - this.gameState.betAmount);
            this.showMessage(`¡VICTORIA TOTAL! Encontraste todas las gemas. Ganaste $${(data.payout - this.gameState.betAmount).toFixed(2)}`);
            setTimeout(() => this.endGame(), 2000);
        } else {
            this.showMessage(`¡Gema encontrada! Multiplicador: ${this.gameState.currentMultiplier.toFixed(2)}x`);
        }
    }

    async hitMine(cell, index, data) {
        this.gameState.isPlaying = false;
        
        // Revelar la mina que tocó
        cell.classList.add('revealed', 'bomb');
        cell.innerHTML = '<img src="/static/img/bomb.svg" class="cell-content" alt="Bomb">';
        
        this.playSound('bomb');
        
        // Revelar todas las minas
        if (data.mine_positions) {
            this.gameState.minePositions = data.mine_positions;
            setTimeout(() => {
                this.revealAllMines();
            }, 500);
        }
        
        // Shake effect
        this.elements.board.classList.add('shake');
        setTimeout(() => {
            this.elements.board.classList.remove('shake');
        }, 500);
        
        this.showMessage('💥 ¡BOOM! Tocaste una mina. Perdiste tu apuesta.');
        
        setTimeout(() => this.endGame(), 3000);
    }

    revealAllMines() {
        const cells = this.elements.board.querySelectorAll('.cell');
        
        this.gameState.minePositions.forEach((pos, i) => {
            setTimeout(() => {
                const cell = cells[pos];
                if (!cell.classList.contains('revealed')) {
                    cell.classList.add('revealed', 'bomb');
                    cell.innerHTML = '<img src="/static/img/bomb.svg" class="cell-content" alt="Bomb">';
                }
            }, i * 100);
        });
    }

    async cashOut() {
        if (!this.gameState.isPlaying || this.gameState.gemsFound === 0) return;
        
        const winAmount = this.gameState.betAmount * this.gameState.currentMultiplier;
        
        try {
            const response = await fetch('/api/mines/cashout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (!data.ok) {
                this.showMessage(data.msg || 'Error al retirar');
                return;
            }
            
            // Actualizar balance
            if (typeof data.saldo !== 'undefined') {
                this.gameState.balance = data.saldo;
                this.updateBalance(data.saldo);
            }
            
            this.showProfitPopup(data.profit || (winAmount - this.gameState.betAmount));
            this.playSound('cashout');
            this.showMessage(`¡Retiro exitoso! Ganaste $${data.profit.toFixed(2)}`);
            
            this.endGame();
            
        } catch (error) {
            console.error('Error en cashout:', error);
            this.showMessage('Error al procesar el retiro');
        }
    }


    endGame() {
        this.gameState.isPlaying = false;
        this.gameState.gemsFound = 0;
        this.gameState.currentMultiplier = 1.00;
        
        // Reset UI
        this.elements.boardOverlay.style.display = 'flex';
        this.elements.betBtn.style.display = 'block';
        this.elements.cashoutBtn.style.display = 'none';
        
        this.updateUI();
        this.generateBoard();
        
        setTimeout(() => {
            this.showMessage('Configura tu próxima apuesta y vuelve a jugar');
        }, 1000);
    }

    showProfitPopup(profit) {
        const popup = document.createElement('div');
        popup.className = 'profit-popup';
        popup.textContent = `+${profit.toFixed(2)}`;
        
        document.body.appendChild(popup);
        
        setTimeout(() => {
            document.body.removeChild(popup);
        }, 2000);
    }

    showMessage(message) {
        if (this.elements.gameMessages) {
            this.elements.gameMessages.innerHTML = `<div class="message-item">${message}</div>`;
        }
    }

    updateBalance(newBalance) {
        if (this.elements.userBalance) {
            this.elements.userBalance.textContent = 
             + newBalance.toFixed(2);
        }
        
        // Actualizar balance en header
        const headerBalance = document.getElementById('top-balance');
        if (headerBalance) {
            headerBalance.textContent = newBalance.toFixed(2);
        }
    }

    playSound(soundId) {
        const sound = document.getElementById(`sound-${soundId}`);
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.log('Sound play failed:', e));
        }
    }
}

// Inicializar el juego cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    console.log('Inicializando Buscaminas mejorado...');
    window.minesGame = new MinesGame();
});