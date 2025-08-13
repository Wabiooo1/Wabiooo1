// blackjack.js - Lógica completa de Blackjack con animaciones de cartas

// Función auxiliar para renderizar y animar una carta
function renderCard(handElement, cardName, isBack = false, delay = 0) {
    setTimeout(() => {
        const cardDiv = document.createElement('div');
        cardDiv.classList.add('card');
        const imgPath = isBack ? '/static/img/card_back.svg' : `/static/img/cards/${cardName}.svg`;
        cardDiv.style.backgroundImage = `url(${imgPath})`;
        cardDiv.classList.add('dealing');  // Trigger animación
        handElement.appendChild(cardDiv);
        setTimeout(() => cardDiv.classList.remove('dealing'), 700);  // Remover después
    }, delay);
}

// Función para actualizar puntuación (simulada, ajusta con datos del server si es necesario)
function updateScore(handElement, score) {
    let scoreElem = handElement.querySelector('.score');
    if (!scoreElem) {
        scoreElem = document.createElement('p');
        scoreElem.classList.add('score');
        handElement.appendChild(scoreElem);
    }
    scoreElem.textContent = `Puntuación: ${score}`;
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const dealButton = document.getElementById('deal');
    const hitButton = document.getElementById('hit');
    const standButton = document.getElementById('stand');
    const dealerCards = document.querySelector('.dealer-hand .cards');
    const playerCards = document.querySelector('.player-hand .cards');
    const dealerHand = document.querySelector('.dealer-hand');
    const playerHand = document.querySelector('.player-hand');

    // Evento para repartir (deal)
    dealButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/blackjack/deal', { method: 'POST' });
            if (!response.ok) throw new Error('Error al repartir');
            const data = await response.json();

            // Limpiar manos
            dealerCards.innerHTML = '';
            playerCards.innerHTML = '';

            // Repartir con delays para animación secuencial
            renderCard(playerCards, data.player[0], false, 0);
            renderCard(dealerCards, 'back', true, 300);  // Dealer oculta
            renderCard(playerCards, data.player[1], false, 600);
            renderCard(dealerCards, data.dealer[1], false, 900);

            // Actualizar puntuaciones (usa datos del server)
            updateScore(playerHand, data.playerScore);
            updateScore(dealerHand, data.dealerScore);  // Inicialmente parcial

            // Habilitar botones
            dealButton.disabled = true;
            hitButton.disabled = false;
            standButton.disabled = false;
        } catch (error) {
            console.error(error);
            alert('Error al conectar con el servidor');
        }
    });

    // Evento para hit
    hitButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/blackjack/hit', { method: 'POST' });
            if (!response.ok) throw new Error('Error en hit');
            const data = await response.json();

            // Añadir nueva carta al jugador con animación
            renderCard(playerCards, data.newCard, false, 0);

            // Actualizar puntuación
            updateScore(playerHand, data.playerScore);

            // Si bust, finalizar
            if (data.gameOver) {
                alert('¡Bust! Pierdes.');
                resetGame();
            }
        } catch (error) {
            console.error(error);
            alert('Error al conectar con el servidor');
        }
    });

    // Evento para stand
    standButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/blackjack/stand', { method: 'POST' });
            if (!response.ok) throw new Error('Error en stand');
            const data = await response.json();

            // Revelar carta oculta del dealer (simula flip removiendo back y añadiendo real)
            dealerCards.querySelector('.card').style.backgroundImage = `url(/static/img/cards/${data.dealerHidden}.svg)`;

            // Añadir cartas adicionales del dealer con animaciones
            data.dealerAdditional.forEach((card, index) => {
                renderCard(dealerCards, card, false, (index + 1) * 300);
            });

            // Actualizar puntuación
            updateScore(dealerHand, data.dealerScore);

            // Mostrar resultado
            alert(data.result);  // e.g., "¡Ganaste!" o "Empate"
            resetGame();
        } catch (error) {
            console.error(error);
            alert('Error al conectar con el servidor');
        }
    });

    // Función para resetear el juego
    function resetGame() {
        dealButton.disabled = false;
        hitButton.disabled = true;
        standButton.disabled = true;
    }
});
