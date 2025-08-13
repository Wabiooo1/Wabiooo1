// blackjack.js - Implementación completa y funcional

class BlackjackGame {
    constructor() {
        this.gameState = {
            isPlaying: false,
            playerHand: [],
            dealerHand: [],
            playerScore: 0,
            dealerScore: 0,
            bet: 0,
            gameOver: false
        };
        
        this.elements = {
            dealBtn: document.getElementById('deal-btn'),
            hitBtn: document.getElementById('hit-btn'),
            standBtn: document.getElementById('stand-btn'),
            betAmount: document.getElementById('bet-amount'),
            playerHand: document.getElementById('player-hand'),
            dealerHand: document.getElementById('dealer-hand'),
            playerScore: document.getElementById('player-score'),
            dealerScore: document.getElementById('dealer-score'),
            gameMessage: document.getElementById('game-message'),
            currentBalance: document.getElementById('current-balance')
        };
        
        this.initEventListeners();
        console.log('Blackjack game initialized');
    }

    initEventListeners() {
        if (this.elements.dealBtn) {
            this.elements.dealBtn.addEventListener('click', () => this.dealCards());
        }
        if (this.elements.hitBtn) {
            this.elements.hitBtn.addEventListener('click', () => this.hit());
        }
        if (this.elements.standBtn) {
            this.elements.standBtn.addEventListener('click', () => this.stand());
        }
    }

    // Crear carta visual mejorada
    createCardElement(cardCode, isHidden = false) {
        const cardEl = document.createElement('div');
        cardEl.className = 'card';
        
        if (isHidden || cardCode === '??' || !cardCode) {
            cardEl.classList.add('card-hidden');
            cardEl.innerHTML = '<div class="card-back">🂠</div>';
        } else {
            const { suit, rank, color } = this.parseCard(cardCode);
            cardEl.innerHTML = `
                <div class="card-content ${color}">
                    <div class="card-rank">${rank}</div>
                    <div class="card-rank-bottom">${rank}</div>
                    <div class="card-suit">${suit}</div>
                </div>
            `;
        }
        
        // Animación de entrada mejorada
        cardEl.style.opacity = '0';
        cardEl.style.transform = 'translateY(-50px) rotateX(-90deg)';
        
        setTimeout(() => {
            cardEl.style.transition = 'all 0.4s ease-out';
            cardEl.style.opacity = '1';
            cardEl.style.transform = 'translateY(0) rotateX(0)';
        }, 50);
        
        return cardEl;
    }

    // Parsear código de carta mejorado
    parseCard(cardCode) {
        if (!cardCode || cardCode === '??' || cardCode === 'undefined') {
            return { suit: '🂠', rank: '?', color: 'black' };
        }
        
        // Manejar diferentes formatos de cartas
        let suit, rank;
        
        if (cardCode.length >= 2) {
            suit = cardCode.slice(-1);
            rank = cardCode.slice(0, -1);
        } else {
            return { suit: '🂠', rank: '?', color: 'black' };
        }
        
        const suitSymbols = {
            'H': '♥', 'D': '♦', 'S': '♠', 'C': '♣'
        };
        
        const suitColors = {
            'H': 'red', 'D': 'red', 'S': 'black', 'C': 'black'
        };
        
        return {
            suit: suitSymbols[suit] || '?',
            rank: rank === 'A' ? 'A' : rank,
            color: suitColors[suit] || 'black'
        };
    }

    // Actualizar puntuación en pantalla
    updateScore(isPlayer, score) {
        if (isPlayer && this.elements.playerScore) {
            this.elements.playerScore.textContent = `Puntuación: ${score}`;
        } else if (!isPlayer && this.elements.dealerScore) {
            this.elements.dealerScore.textContent = `Puntuación: ${score === '?' ? '?' : score}`;
        }
    }

    // Mostrar mensaje del juego
    showMessage(message, type = 'normal') {
        if (!this.elements.gameMessage) return;
        
        this.elements.gameMessage.textContent = message;
        
        // Colores según el tipo de mensaje
        switch(type) {
            case 'error':
                this.elements.gameMessage.style.color = '#ff6b6b';
                break;
            case 'win':
                this.elements.gameMessage.style.color = '#4CAF50';
                break;
            case 'lose':
                this.elements.gameMessage.style.color = '#f44336';
                break;
            case 'push':
                this.elements.gameMessage.style.color = '#FFC107';
                break;
            default:
                this.elements.gameMessage.style.color = '#d4af37';
        }
    }

    // Actualizar balance en la UI
    updateBalance(newBalance) {
        if (this.elements.currentBalance) {
            this.elements.currentBalance.textContent = newBalance.toFixed(2);
        }
        // También actualizar el balance del header si existe
        const headerBalance = document.getElementById('top-balance');
        if (headerBalance) {
            headerBalance.textContent = newBalance.toFixed(2);
        }
    }

    // Controlar botones
    setButtonsState(deal, hit, stand) {
        if (this.elements.dealBtn) this.elements.dealBtn.disabled = !deal;
        if (this.elements.hitBtn) this.elements.hitBtn.disabled = !hit;
        if (this.elements.standBtn) this.elements.standBtn.disabled = !stand;
        if (this.elements.betAmount) this.elements.betAmount.disabled = !deal;
    }

    // Limpiar mesa
    clearTable() {
        if (this.elements.playerHand) this.elements.playerHand.innerHTML = '';
        if (this.elements.dealerHand) this.elements.dealerHand.innerHTML = '';
        this.updateScore(true, 0);
        this.updateScore(false, '?');
    }

    // Añadir carta con animación y delay
    addCardWithDelay(container, cardCode, isHidden = false, delay = 0) {
        return new Promise((resolve) => {
            setTimeout(() => {
                if (container) {
                    const cardEl = this.createCardElement(cardCode, isHidden);
                    container.appendChild(cardEl);
                    console.log(`Carta añadida: ${cardCode}, Hidden: ${isHidden}`);
                }
                resolve();
            }, delay);
        });
    }

    // Repartir cartas
    async dealCards() {
        const betAmount = parseFloat(this.elements.betAmount?.value || 10);
        
        if (!betAmount || betAmount <= 0) {
            this.showMessage('Por favor ingresa una apuesta válida', 'error');
            return;
        }

        console.log('Iniciando deal con apuesta:', betAmount);
        this.showMessage('Repartiendo cartas...');
        this.clearTable();
        this.setButtonsState(false, false, false);

        try {
            const response = await fetch('/api/blackjack/deal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ bet: betAmount })
            });

            const data = await response.json();
            console.log('Respuesta del servidor:', data);

            if (!data.ok) {
                this.showMessage(data.msg || 'Error al repartir cartas', 'error');
                this.setButtonsState(true, false, false);
                return;
            }

            // Guardar estado del juego
            this.gameState.isPlaying = true;
            this.gameState.playerHand = data.player_hand || [];
            this.gameState.dealerHand = data.dealer_hand || [];
            this.gameState.bet = betAmount;
            this.gameState.gameOver = data.game_over || false;

            // Secuencia de repartir cartas con animaciones
            // Carta 1 del jugador
            if (this.gameState.playerHand[0]) {
                await this.addCardWithDelay(this.elements.playerHand, this.gameState.playerHand[0], false, 0);
            }
            
            // Carta 1 del dealer (visible)
            if (this.gameState.dealerHand[0]) {
                await this.addCardWithDelay(this.elements.dealerHand, this.gameState.dealerHand[0], false, 300);
            }
            
            // Carta 2 del jugador
            if (this.gameState.playerHand[1]) {
                await this.addCardWithDelay(this.elements.playerHand, this.gameState.playerHand[1], false, 600);
            }
            
            // Carta 2 del dealer (oculta si no es game over)
            if (this.gameState.dealerHand[1]) {
                const isHidden = !data.game_over;
                await this.addCardWithDelay(this.elements.dealerHand, isHidden ? '??' : this.gameState.dealerHand[1], isHidden, 900);
            }

            // Actualizar puntuaciones
            this.updateScore(true, data.player_score || 0);
            this.updateScore(false, data.game_over ? (data.dealer_score || 0) : '?');

            // Actualizar balance
            if (typeof data.saldo !== 'undefined') {
                this.updateBalance(data.saldo);
            }

            // Verificar si el juego terminó (blackjack natural)
            if (data.game_over) {
                setTimeout(() => {
                    this.showGameResult(data);
                    this.setButtonsState(true, false, false);
                }, 1200);
            } else {
                setTimeout(() => {
                    this.showMessage('Tu turno - ¿Hit o Stand?');
                    this.setButtonsState(false, true, true);
                }, 1200);
            }

        } catch (error) {
            console.error('Error en deal:', error);
            this.showMessage('Error de conexión con el servidor', 'error');
            this.setButtonsState(true, false, false);
        }
    }

    // Hit - pedir carta
    async hit() {
        this.showMessage('Pidiendo carta...');
        this.setButtonsState(false, false, false);

        try {
            const response = await fetch('/api/blackjack/hit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            console.log('Respuesta de hit:', data);

            if (!data.ok) {
                this.showMessage(data.msg || 'Error al pedir carta', 'error');
                this.setButtonsState(false, true, true);
                return;
            }

            // Añadir nueva carta (la última del array)
            if (data.hand && data.hand.length > 0) {
                const newCard = data.hand[data.hand.length - 1];
                await this.addCardWithDelay(this.elements.playerHand, newCard, false, 0);
            }

            // Actualizar puntuación
            this.updateScore(true, data.score || 0);

            if (data.game_over) {
                // Si es bust, revelar carta del dealer y mostrar resultado
                setTimeout(() => {
                    if (data.dealer_hand && data.dealer_hand.length > 1) {
                        this.revealDealerCard(data.dealer_hand[1]);
                    }
                    this.showGameResult({
                        result: data.result,
                        dealer_score: data.dealer_score,
                        saldo: data.saldo
                    });
                    if (typeof data.saldo !== 'undefined') {
                        this.updateBalance(data.saldo);
                    }
                    this.setButtonsState(true, false, false);
                }, 500);
            } else {
                setTimeout(() => {
                    this.showMessage('¿Hit o Stand?');
                    this.setButtonsState(false, true, true);
                }, 500);
            }

        } catch (error) {
            console.error('Error en hit:', error);
            this.showMessage('Error de conexión', 'error');
            this.setButtonsState(false, true, true);
        }
    }

    // Stand - plantarse
    async stand() {
        this.showMessage('Te plantas. Dealer juega...');
        this.setButtonsState(false, false, false);

        try {
            const response = await fetch('/api/blackjack/stand', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            console.log('Respuesta de stand:', data);

            if (!data.ok) {
                this.showMessage(data.msg || 'Error al plantarse', 'error');
                this.setButtonsState(true, false, false);
                return;
            }

            // Revelar carta oculta del dealer
            if (data.dealer_hand && data.dealer_hand.length > 1) {
                this.revealDealerCard(data.dealer_hand[1]);
            }
            
            // Mostrar cartas adicionales del dealer si las hay
            if (data.dealer_hand && data.dealer_hand.length > 2) {
                for (let i = 2; i < data.dealer_hand.length; i++) {
                    await this.addCardWithDelay(this.elements.dealerHand, data.dealer_hand[i], false, (i - 1) * 500);
                }
            }

            setTimeout(() => {
                this.updateScore(false, data.dealer_score || 0);
                this.showGameResult(data);
                if (typeof data.saldo !== 'undefined') {
                    this.updateBalance(data.saldo);
                }
                this.setButtonsState(true, false, false);
            }, Math.max(500, (data.dealer_hand?.length || 2) * 300));

        } catch (error) {
            console.error('Error en stand:', error);
            this.showMessage('Error de conexión', 'error');
            this.setButtonsState(true, false, false);
        }
    }

    // Revelar carta oculta del dealer
    revealDealerCard(cardCode) {
        if (!this.elements.dealerHand) return;
        
        const dealerCards = this.elements.dealerHand.children;
        if (dealerCards.length >= 2) {
            const hiddenCard = dealerCards[1];
            if (hiddenCard.classList.contains('card-hidden')) {
                const { suit, rank, color } = this.parseCard(cardCode);
                hiddenCard.classList.remove('card-hidden');
                hiddenCard.innerHTML = `
                    <div class="card-content ${color}">
                        <div class="card-rank">${rank}</div>
                        <div class="card-rank-bottom">${rank}</div>
                        <div class="card-suit">${suit}</div>
                    </div>
                `;
                
                // Animación de flip
                hiddenCard.style.transform = 'rotateY(180deg)';
                setTimeout(() => {
                    hiddenCard.style.transition = 'transform 0.3s ease';
                    hiddenCard.style.transform = 'rotateY(0deg)';
                }, 100);
            }
        }
    }

    // Mostrar resultado del juego
    showGameResult(data) {
        const messages = {
            'blackjack': '¡BLACKJACK! ¡Ganaste!',
            'player_win': '¡Ganaste!',
            'dealer_win': 'Dealer gana',
            'dealer_bust': '¡Dealer se pasa! ¡Ganaste!',
            'bust': 'Te pasaste de 21. Dealer gana',
            'push': 'Empate'
        };

        const message = messages[data.result] || `Resultado: ${data.result}`;
        
        // Determinar tipo de mensaje para el color
        let messageType = 'normal';
        if (data.result === 'blackjack' || data.result === 'player_win' || data.result === 'dealer_bust') {
            messageType = 'win';
        } else if (data.result === 'push') {
            messageType = 'push';
        } else {
            messageType = 'lose';
        }
        
        this.showMessage(message, messageType);
        
        this.gameState.isPlaying = false;
        this.gameState.gameOver = true;
    }
}

// Inicializar el juego cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Blackjack...');
    const game = new BlackjackGame();
    
    // Verificar que todos los elementos existan
    const requiredElements = ['deal-btn', 'hit-btn', 'stand-btn', 'player-hand', 'dealer-hand'];
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    
    if (missingElements.length > 0) {
        console.error('Elementos faltantes en el DOM:', missingElements);
    } else {
        console.log('Todos los elementos encontrados, juego listo');
    }
});