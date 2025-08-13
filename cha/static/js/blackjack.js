// blackjack.js - Lógica completa de Blackjack con animaciones y depuración

document.addEventListener('DOMContentLoaded', () => {
    const dealButton = document.getElementById('deal');
    const hitButton = document.getElementById('hit');
    const standButton = document.getElementById('stand');
    const dealerCards = document.querySelector('.dealer-hand .cards');
    const playerCards = document.querySelector('.player-hand .cards');
    const dealerHand = document.querySelector('.dealer-hand');
    const playerHand = document.querySelector('.player-hand');

    // Función para renderizar y animar una carta
    function renderCard(handElement, cardName, isBack = false, delay = 0) {
        setTimeout(() => {
            const cardDiv = document.createElement('div');
            cardDiv.classList.add('card');
            const imgPath = isBack ? '/static/img/card_back.svg' : `/static/img/cards/${cardName}.svg`;
            cardDiv.style.backgroundImage = `url(${imgPath})`;
            cardDiv.classList.add('dealing');
            handElement.appendChild(cardDiv);
            setTimeout(() => cardDiv.classList.remove('dealing'), 700);
            console.log(`Carta renderizada: ${imgPath}`);  // Depuración
        }, delay);
    }

    // Función para actualizar puntuación
    function updateScore(handElement, score) {
        const scoreElem = handElement.querySelector('.score');
        scoreElem.textContent = `Puntuación: ${score}`;
        console.log(`Puntuación actualizada: ${score}`);  // Depuración
    }

    // Función para resetear el juego
    function resetGame() {
        dealButton.disabled = false;
        hitButton.disabled = true;
        standButton.disabled = true;
        dealerCards.innerHTML = '';
        playerCards.innerHTML = '';
        updateScore(dealerHand, 0);
        updateScore(playerHand, 0);
        console.log('Juego reseteado');
    }

    // Evento para repartir
    dealButton.addEventListener('click', async () => {
        resetGame();  // Limpiar antes de nuevo deal
        try {
            const response = await fetch('/api/blackjack/deal', { method: 'POST' });
            if (!response.ok) throw new Error('Error en fetch');
            const data = await response.json();
            console.log('Datos del server:', data);  // Depuración

            // Repartir con animaciones
            renderCard(playerCards, data.player[0], false, 0);
            renderCard(dealerCards, 'back', true, 300);
            renderCard(playerCards, data.player[1], false, 600);
            renderCard(dealerCards, data.dealer[1], false, 900);

            updateScore(playerHand, data.playerScore);
            updateScore(dealerHand, data.dealerScore);

            dealButton.disabled = true;
            hitButton.disabled = false;
            standButton.disabled = false;
        } catch (error) {
            console.error('Error en deal:', error);
            alert('Error al conectar con el servidor. Usando modo demo.');
            // Fallback con cartas mock para visibilidad
            renderCard(playerCards, 'hearts-A', false, 0);
            renderCard(dealerCards, 'back', true, 300);
            renderCard(playerCards, 'diamonds-7', false, 600);
            renderCard(dealerCards, 'spades-K', false, 900);
            updateScore(playerHand, 18);
            updateScore(dealerHand, 10);
        }
    });

    // Evento para hit
    hitButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/blackjack/hit', { method: 'POST' });
            if (!response.ok) throw new Error('Error en hit');
            const data = await response.json();
            console.log('Datos de hit:', data);

            renderCard(playerCards, data.newCard, false, 0);
            updateScore(playerHand, data.playerScore);

            if (data.gameOver) {
                alert(data.result);
                resetGame();
            }
        } catch (error) {
            console.error('Error en hit:', error);
            alert('Error en hit. Usando mock.');
            renderCard(playerCards, 'clubs-5', false, 0);
            updateScore(playerHand, 23);  // Simula bust
        }
    });

    // Evento para stand
    standButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/blackjack/stand', { method: 'POST' });
            if (!response.ok) throw new Error('Error en stand');
            const data = await response.json();
            console.log('Datos de stand:', data);

            // Revelar carta oculta (reemplaza el back)
            const hiddenCard = dealerCards.querySelector('.card');
            hiddenCard.style.backgroundImage = `url(/static/img/cards/${data.dealerHidden}.svg)`;
            hiddenCard.classList.add('dealing');  // Anima el flip
            setTimeout(() => hiddenCard.classList.remove('dealing'), 700);

            // Añadir cartas adicionales del dealer
            data.dealerAdditional.forEach((card, index) => {
                renderCard(dealerCards, card, false, (index + 1) * 300);
            });

            updateScore(dealerHand, data.dealerScore);
            alert(data.result);
            resetGame();
        } catch (error) {
            console.error('Error en stand:', error);
            alert('Error en stand. Usando mock.');
            renderCard(dealerCards, 'hearts-10', false, 300);
            updateScore(dealerHand, 20);
        }
    });

    // Reset inicial
    resetGame();
});
