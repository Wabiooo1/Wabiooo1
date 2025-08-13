document.addEventListener('DOMContentLoaded', () => {
    // --- CONSTANTS ---
    // CORRECCIÓN FINAL Y DEFINITIVA: El orden de los números ahora coincide 1:1 con tu SVG.
    const ROULETTE_NUMBERS = [
  0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,
  24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26
];
    const RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];

    // --- STATE ---
    const state = {
        selectedChip: 5,
        bets: [],
        isSpinning: false,
        totalBet: 0,
        currentRotation: 0,
    };

    // --- DOM ELEMENTS ---
    const rotor = document.getElementById('rotor');
    const ballTrack = document.getElementById('ball-track');
    const ball = document.getElementById('ball');
    const resultDisplay = document.querySelector('.roulette-result');
    const tableEl = document.querySelector('.roulette-table');
    const messageArea = document.getElementById('roulette-message');
    const totalBetDisplay = document.getElementById('total-bet');
    const clearButton = document.getElementById('clear-bets');
    const spinButton = document.getElementById('spin-wheel');
    const chips = document.querySelectorAll('.chip');

    function playSound(id) {
        const sound = document.getElementById(id);
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.log("Sound play failed:", e));
        }
    }

    function placeBet(betOption) {
        if (state.isSpinning) return;
        const betType = betOption.dataset.type;
        const betValue = betOption.dataset.value;
        const chipValue = state.selectedChip;
        const existingBet = state.bets.find(b => b.type === betType && b.value === betValue);

        if (existingBet) {
            existingBet.amount += chipValue;
            existingBet.element.querySelector('.placed-chip').textContent = '$' + existingBet.amount;
        } else {
            const chipEl = document.createElement('div');
            chipEl.className = 'placed-chip';
            chipEl.textContent = '$' + chipValue;
            betOption.appendChild(chipEl);
            state.bets.push({ type: betType, value: betValue, amount: chipValue, element: betOption });
        }
        updateTotalBet();
        playSound('chip-sound');
    }

    function updateTotalBet() {
        state.totalBet = state.bets.reduce((sum, bet) => sum + bet.amount, 0);
        totalBetDisplay.textContent = state.totalBet.toFixed(2);
    }

    function clearBets() {
        if (state.isSpinning) return;
        state.bets = [];
        document.querySelectorAll('.placed-chip').forEach(chip => chip.remove());
        updateTotalBet();
        messageArea.textContent = 'Coloca tus apuestas.';
    }

    function updateUIForSpin(isSpinning) {
        state.isSpinning = isSpinning;
        spinButton.disabled = isSpinning;
        clearButton.disabled = isSpinning;
        chips.forEach(c => c.style.pointerEvents = isSpinning ? 'none' : 'auto');
        tableEl.style.pointerEvents = isSpinning ? 'none' : 'auto';
        if (!isSpinning) {
            resultDisplay.classList.remove('visible');
        }
    }

    async function spinWheel() {
        if (state.isSpinning || state.bets.length === 0) {
            messageArea.textContent = 'Coloca una apuesta para girar.';
            return;
        }

        updateUIForSpin(true);
        messageArea.textContent = '¡Girando... Buena suerte!';
        const response = await apiPost('/api/roulette/spin', { bets: state.bets });

        if (!response.ok) {
            messageArea.textContent = response.msg;
            updateUIForSpin(false);
            return;
        }
        
        playSound('wheel-sound');

        const { winning_number, payout, saldo } = response;
        const resultIndex = ROULETTE_NUMBERS.indexOf(winning_number);

        const degreesPerNumber = 360 / ROULETTE_NUMBERS.length;
        const randomOffset = Math.random() * degreesPerNumber - (degreesPerNumber / 2);
        const finalAngle = (resultIndex * degreesPerNumber) + randomOffset;
        
        const randomSpins = Math.floor(Math.random() * 5) + 5;
        const totalRotation = (360 * randomSpins) + finalAngle;

        const ballSpins = randomSpins - 2;
        const ballRotation = -(360 * ballSpins);

        state.currentRotation += totalRotation;
        
        rotor.style.transform = `rotate(${state.currentRotation}deg)`;
        ballTrack.style.transform = `rotate(${ballRotation}deg)`;
        
        await new Promise(resolve => setTimeout(resolve, 7000));
        
        ball.classList.add('settling');
        await new Promise(resolve => setTimeout(resolve, 500));
        ball.classList.remove('settling');

        resultDisplay.textContent = winning_number;
        resultDisplay.className = 'roulette-result visible ' +
            (winning_number === 0 ? 'green' : RED_NUMBERS.includes(winning_number) ? 'red' : 'black');
        
        updateHeaderBalance(saldo);
        const profit = payout - state.totalBet;
        if (payout > 0) {
            messageArea.textContent = `¡Número ${winning_number}! Ganaste $${profit.toFixed(2)}`;
            playSound('win-sound');
        } else {
            messageArea.textContent = `Número ${winning_number}. Mejor suerte la próxima vez.`;
            playSound('lose-sound');
        }

        await new Promise(resolve => setTimeout(resolve, 3000));
        clearBets();
        updateUIForSpin(false);
        messageArea.textContent = 'Coloca tus apuestas para la siguiente ronda.';
    }

    function setupNumbersGrid() {
        const grid = document.querySelector('.numbers-grid');
        grid.innerHTML = '';
        for (let i = 1; i <= 36; i++) {
            const numberDiv = document.createElement('div');
            numberDiv.className = `bet-option number ${RED_NUMBERS.includes(i) ? 'red' : 'black'}`;
            numberDiv.setAttribute('data-type', 'number');
            numberDiv.setAttribute('data-value', i);
            numberDiv.textContent = i;
            numberDiv.style.position = 'relative';
            grid.appendChild(numberDiv);
        }
    }

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            if (state.isSpinning) return;
            chips.forEach(c => c.classList.remove('selected'));
            chip.classList.add('selected');
            state.selectedChip = parseInt(chip.dataset.value, 10);
        });
    });

    tableEl.addEventListener('click', (e) => {
        const betOption = e.target.closest('.bet-option');
        if (betOption) {
            placeBet(betOption);
        }
    });

    clearButton.addEventListener('click', clearBets);
    spinButton.addEventListener('click', spinWheel);

    setupNumbersGrid();
    document.querySelector('.chip[data-value="5"]').click();
    messageArea.textContent = 'Selecciona una ficha y haz tu apuesta.';
});