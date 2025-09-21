from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import sqlite3, os, random
from config import DB_PATH, SECRET_KEY
from werkzeug.security import generate_password_hash, check_password_hash

import json
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

def get_db_connection():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
    return conn


# ---- game state helpers (server-side) ----
def _serialize_state(s):
    try:
        return json.dumps(s)
    except Exception:
        return json.dumps({})

def _deserialize_state(s):
    try:
        return json.loads(s) if s else {}
    except Exception:
        return {}

def create_game_record(user_id, game_type, bet=0, initial_state=None):
    conn = get_db_connection()
    cur = conn.cursor()
    st = _serialize_state(initial_state or {})
    cur.execute("""INSERT INTO games (user_id, game_type, bet, state) VALUES (?, ?, ?, ?)""", (user_id, game_type, bet, st))
    conn.commit()
    return cur.lastrowid

def get_game_record(game_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM games WHERE id = ?', (game_id,))
    r = cur.fetchone()
    return dict(r) if r else None

def update_game_record(game_id, state_obj=None, game_over=None, bet=None):
    conn = get_db_connection()
    cur = conn.cursor()
    updates = []
    params = []
    if state_obj is not None:
        updates.append('state = ?'); params.append(_serialize_state(state_obj))
    if game_over is not None:
        updates.append('game_over = ?'); params.append(1 if game_over else 0)
    if bet is not None:
        updates.append('bet = ?'); params.append(bet)
    if not updates:
        return True
    updates.append("updated_at = datetime('now')")
    sql = 'UPDATE games SET ' + ', '.join(updates) + ' WHERE id = ?'
    params.append(game_id)
    cur.execute(sql, params)
    conn.commit()
    return True

# ---- end helpers ----

@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            saldo REAL DEFAULT 0.0,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cur.execute('''CREATE TABLE game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            juego TEXT,
            resultado TEXT,
            monto_apostado REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Tabla games para el estado de los juegos
        cur.execute('''CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_type TEXT,
            bet REAL DEFAULT 0.0,
            state TEXT,
            game_over INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()

with app.app_context():
    init_db()

@app.before_request
def load_current_user():
    g.user = None
    uid = session.get('user_id')
    if uid:
        conn = get_db_connection()
        g.user = conn.execute('SELECT * FROM users WHERE id = ?', (uid,)).fetchone()


# --------------------
# Rutas de UI (templates)
# --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        if not username or not email or not password:
            flash('Completa todos los campos','error')
            return redirect(url_for('register'))
        ph = generate_password_hash(password)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO users (username, email, password_hash, saldo) VALUES (?, ?, ?, ?)', (username, email, ph, 100.0))
            conn.commit()
            flash('Registro exitoso – saldo inicial: $100','success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Error: usuario o email ya existente','error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        conn = get_db_connection()
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Bienvenido, ' + user['username'],'success')
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos','error')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada','info')
    return redirect(url_for('index'))

@app.route('/perfil')
def perfil():
    if not g.user:
        flash('Debes iniciar sesión para ver tu perfil.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    history = conn.execute('SELECT * FROM game_history WHERE user_id = ? ORDER BY fecha DESC LIMIT 50', (g.user['id'],)).fetchall()
    
    # Calcular estadísticas para la plantilla
    stats = {'total_games': 0, 'fav_game': 'N/A'}
    all_history = conn.execute('SELECT juego FROM game_history WHERE user_id = ?', (g.user['id'],)).fetchall()
    if all_history:
        stats['total_games'] = len(all_history)
        game_counts = {}
        for record in all_history:
            game_counts[record['juego']] = game_counts.get(record['juego'], 0) + 1
        if game_counts:
            stats['fav_game'] = max(game_counts, key=game_counts.get).capitalize()

    return render_template('perfil.html', user=g.user, history=history, stats=stats)

@app.route('/recargar', methods=['GET','POST'])
def recargar():
    if 'user_id' not in session:
        flash('Debes iniciar sesión','error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            monto = float(request.form.get('monto', '0'))
            if monto <= 0:
                flash('Monto inválido','error')
                return redirect(url_for('recargar'))
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE users SET saldo = saldo + ? WHERE id = ?', (monto, session['user_id']))
            conn.commit()
            flash(f'Saldo recargado: ${monto:.2f}','success')
            return redirect(url_for('perfil'))
        except (ValueError, TypeError):
            flash('Error al recargar','error')
            return redirect(url_for('recargar'))
    return render_template('recargar.html')

@app.route('/buscaminas')
def buscaminas_page():
    return render_template('buscaminas.html')

@app.route('/blackjack')
def blackjack_page():
    return render_template('blackjack.html')

@app.route('/slots')
def slots_page():
    return render_template('coming_soon.html', game_name="Tragamonedas")


# --------------------
# API: balance
# --------------------
@app.route('/api/get_balance')
def api_get_balance():
    if 'user_id' not in session:
        return jsonify({'ok': False, 'msg': 'No autenticado'}), 401
    conn = get_db_connection()
    row = conn.execute('SELECT saldo FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return jsonify({'ok': True, 'saldo': row['saldo']})


# --------------------
# Blackjack: server-side, compacto en session (cartas codificadas como strings)
# --------------------
def _make_deck_codes():
    # Rango de ranks y suits (usamos códigos cortos para ahorrar espacio en session)
    ranks = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
    suits = ['S', 'H', 'D', 'C']  # Spades, Hearts, Diamonds, Clubs
    deck = [f"{r}{s}" for s in suits for r in ranks]
    random.shuffle(deck)
    return deck

def _card_value(code):
    # code ejemplos: 'AS', '10H', 'JC'
    rank = code[:-1]
    if rank in ('J','Q','K'):
        return 10
    if rank == 'A':
        return 11
    return int(rank)

def _calculate_score_from_codes(hand_codes):
    total = 0
    aces = 0
    for c in hand_codes:
        if c == '??':  # hidden placeholder
            continue
        v = _card_value(c)
        total += v
        if c[:-1] == 'A':
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def _finalize_blackjack_game(game):
    """Recibe el diccionario game {deck, player_hand, dealer_hand, bet, game_over}
       Juega por el dealer y calcula resultado y payout_return (cantidad a añadir al saldo).
       Devuelve (result_dict, payout_return).
    """
    deck = game['deck']
    player = game['player_hand']
    dealer = game['dealer_hand']
    bet = float(game.get('bet', 0))

    player_score = _calculate_score_from_codes(player)
    # Si el jugador ya está bust, no es necesario que el dealer saque cartas
    if player_score > 21:
        result = 'bust'
        payout_return = 0.0
        return {'result': result, 'player_score': player_score, 'dealer_score': _calculate_score_from_codes(dealer), 'dealer_hand': dealer}, payout_return

    # Dealer revela y juega
    dealer_score = _calculate_score_from_codes(dealer)
    while dealer_score < 17:
        if not deck:
            deck = _make_deck_codes()
        dealer.append(deck.pop())
        dealer_score = _calculate_score_from_codes(dealer)

    # Determinar resultado
    result = ''
    payout_return = 0.0
    # Natural Blackjack check
    player_natural = (len(player) == 2 and player_score == 21)
    dealer_natural = (len(dealer) == 2 and dealer_score == 21)

    if player_natural and not dealer_natural:
        result = 'blackjack'
        payout_return = bet * 2.5  # devuelve 2.5x (apuesta + 1.5x)
    elif player_natural and dealer_natural:
        result = 'push'
        payout_return = bet
    else:
        if dealer_score > 21:
            result = 'dealer_bust'
            payout_return = bet * 2
        else:
            if player_score > dealer_score:
                result = 'player_win'
                payout_return = bet * 2
            elif player_score == dealer_score:
                result = 'push'
                payout_return = bet
            else:
                result = 'dealer_win'
                payout_return = 0.0

    return ({'result': result, 'player_score': player_score, 'dealer_score': dealer_score, 'dealer_hand': dealer}, payout_return)


@app.route('/api/blackjack/deal', methods=['POST'])
def blackjack_deal():
    if not g.user:
        return jsonify({'ok': False, 'msg': 'No autenticado'}), 401

    data = request.get_json() or {}
    try:
        bet_amount = float(data.get('bet', 0))
    except Exception:
        return jsonify({'ok': False, 'msg': 'Apuesta inválida.'})

    if bet_amount <= 0:
        return jsonify({'ok': False, 'msg': 'Apuesta inválida.'})
    if g.user['saldo'] < bet_amount:
        return jsonify({'ok': False, 'msg': 'Saldo insuficiente.'})

    # Descontar apuesta ahora (se devuelve según resultado)
    conn = get_db_connection()
    conn.execute('UPDATE users SET saldo = saldo - ? WHERE id = ?', (bet_amount, g.user['id']))
    conn.commit()
    new_bal = conn.execute('SELECT saldo FROM users WHERE id = ?', (g.user['id'],)).fetchone()['saldo']

    deck = _make_deck_codes()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    session['blackjack_game'] = {
        'deck': deck,
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'bet': bet_amount,
        'game_over': False
    }
    session.modified = True

    player_score = _calculate_score_from_codes(player_hand)
    dealer_visible_score = _card_value(dealer_hand[0]) if dealer_hand[0][:-1] != 'A' else 11

    # Si blackjack natural del jugador se resuelve automáticamente
    if player_score == 21:
        game = session.get('blackjack_game')
        result_info, payout = _finalize_blackjack_game(game)
        # aplicar payout al saldo
        conn.execute('UPDATE users SET saldo = saldo + ? WHERE id = ?', (payout, g.user['id']))
        conn.execute('INSERT INTO game_history (user_id, juego, resultado, monto_apostado) VALUES (?, ?, ?, ?)',
                     (g.user['id'], 'blackjack', result_info['result'], bet_amount))
        conn.commit()
        session['blackjack_game']['game_over'] = True
        session.modified = True
        new_bal = conn.execute('SELECT saldo FROM users WHERE id = ?', (g.user['id'],)).fetchone()['saldo']
        
        return jsonify({
            'ok': True, 
            'game_over': True, 
            'player_hand': player_hand, 
            'dealer_hand': result_info['dealer_hand'],
            'player_score': result_info['player_score'], 
            'dealer_score': result_info['dealer_score'], 
            'result': result_info['result'], 
            'saldo': new_bal
        })

    return jsonify({
        'ok': True, 
        'game_over': False, 
        'player_hand': player_hand, 
        'dealer_hand': dealer_hand,
        'player_score': player_score, 
        'dealer_score': dealer_visible_score, 
        'saldo': new_bal
    })


@app.route('/api/blackjack/hit', methods=['POST'])
def blackjack_hit():
    if not g.user or 'blackjack_game' not in session:
        return jsonify({'ok': False, 'msg': 'Juego no encontrado'}), 400

    game = session['blackjack_game']
    if game.get('game_over'):
        return jsonify({'ok': False, 'msg': 'La ronda ha terminado.'}), 400

    if not game['deck']:
        game['deck'] = _make_deck_codes()

    # Dar carta al jugador
    card = game['deck'].pop()
    game['player_hand'].append(card)

    # calcular estado
    player_score = _calculate_score_from_codes(game['player_hand'])

    # si bust -> finalizar la partida
    if player_score > 21:
        result_info, payout = _finalize_blackjack_game(game)
        game['game_over'] = True
        
        conn = get_db_connection()
        conn.execute('UPDATE users SET saldo = saldo + ? WHERE id = ?', (payout, g.user['id']))
        conn.execute('INSERT INTO game_history (user_id, juego, resultado, monto_apostado) VALUES (?, ?, ?, ?)',
                     (g.user['id'], 'blackjack', result_info['result'], game.get('bet', 0)))
        conn.commit()
        new_bal = conn.execute('SELECT saldo FROM users WHERE id = ?', (g.user['id'],)).fetchone()['saldo']
        
        session['blackjack_game'] = game
        session.modified = True
        
        return jsonify({
            'ok': True, 
            'game_over': True, 
            'hand': game['player_hand'],
            'dealer_hand': result_info['dealer_hand'], 
            'score': result_info['player_score'],
            'dealer_score': result_info['dealer_score'], 
            'result': result_info['result'], 
            'saldo': new_bal
        })

    # actualizar session y devolver estado parcial
    session['blackjack_game'] = game
    session.modified = True
    
    return jsonify({
        'ok': True, 
        'game_over': False, 
        'hand': game['player_hand'], 
        'score': player_score
    })


@app.route('/api/blackjack/stand', methods=['POST'])
def blackjack_stand():
    if not g.user or 'blackjack_game' not in session:
        return jsonify({'ok': False, 'msg': 'Juego no encontrado'}), 400

    game = session['blackjack_game']
    if game.get('game_over'):
        return jsonify({'ok': False, 'msg': 'La ronda ya terminó.'}), 400

    # finalizar juego
    result_info, payout = _finalize_blackjack_game(game)
    game['game_over'] = True
    session['blackjack_game'] = game
    session.modified = True

    # aplicar payout y guardar historial
    conn = get_db_connection()
    conn.execute('UPDATE users SET saldo = saldo + ? WHERE id = ?', (payout, g.user['id']))
    conn.execute('INSERT INTO game_history (user_id, juego, resultado, monto_apostado) VALUES (?, ?, ?, ?)',
                 (g.user['id'], 'blackjack', result_info['result'], game.get('bet', 0)))
    conn.commit()
    new_bal = conn.execute('SELECT saldo FROM users WHERE id = ?', (g.user['id'],)).fetchone()['saldo']

    return jsonify({
        'ok': True, 
        'game_over': True, 
        'player_hand': game['player_hand'],
        'dealer_hand': result_info['dealer_hand'], 
        'player_score': result_info['player_score'],
        'dealer_score': result_info['dealer_score'], 
        'result': result_info['result'], 
        'saldo': new_bal
    })


# --------------------
# Buscaminas API
# --------------------
@app.route('/api/mines/start', methods=['POST'])
def mines_start():
    """Iniciar una nueva partida de buscaminas"""
    if not g.user:
        return jsonify({'ok': False, 'msg': 'No autenticado'}), 401
    
    data = request.get_json() or {}
    try:
        bet_amount = float(data.get('bet', 1.0))
        mine_count = int(data.get('mines', 3))
        grid_size = int(data.get('grid_size', 5))
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'msg': 'Parámetros inválidos'}), 400
    
    # Validaciones
    if bet_amount <= 0:
        return jsonify({'ok': False, 'msg': 'Apuesta inválida'}), 400
    
    if mine_count < 1 or mine_count >= (grid_size * grid_size):
        return jsonify({'ok': False, 'msg': 'Número de minas inválido'}), 400
    
    if g.user['saldo'] < bet_amount:
        return jsonify({'ok': False, 'msg': 'Saldo insuficiente'}), 400
    
    # Generar posiciones de minas
    import random
    total_cells = grid_size * grid_size
    mine_positions = random.sample(range(total_cells), mine_count)
    
    # Crear registro del juego
    game_state = {
        'bet': bet_amount,
        'mines': mine_count,
        'grid_size': grid_size,
        'mine_positions': mine_positions,
        'revealed_cells': [],
        'gems_found': 0,
        'multiplier': 1.0,
        'active': True
    }
    
    # Descontar apuesta
    conn = get_db_connection()
    conn.execute('UPDATE users SET saldo = saldo - ? WHERE id = ?', (bet_amount, g.user['id']))
    conn.commit()
    
    # Guardar estado en sesión
    session['mines_game'] = game_state
    session.modified = True
    
    new_balance = conn.execute('SELECT saldo FROM users WHERE id = ?', (g.user['id'],)).fetchone()['saldo']
    
    return jsonify({
        'ok': True,
        'game_id': 'mines_session',  # Usando sesión en lugar de DB
        'saldo': new_balance,
        'total_gems': total_cells - mine_count
    })

@app.route('/api/mines/reveal', methods=['POST'])
def mines_reveal():
    """Revelar una celda del buscaminas"""
    if not g.user:
        return jsonify({'ok': False, 'msg': 'No autenticado'}), 401
    
    if 'mines_game' not in session:
        return jsonify({'ok': False, 'msg': 'No hay juego activo'}), 400
    
    game = session['mines_game']
    if not game.get('active'):
        return jsonify({'ok': False, 'msg': 'Juego no activo'}), 400
    
    data = request.get_json() or {}
    try:
        cell_index = int(data.get('cell', -1))
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'msg': 'Celda inválida'}), 400
    
    total_cells = game['grid_size'] * game['grid_size']
    if cell_index < 0 or cell_index >= total_cells:
        return jsonify({'ok': False, 'msg': 'Celda fuera de rango'}), 400
    
    if cell_index in game['revealed_cells']:
        return jsonify({'ok': False, 'msg': 'Celda ya revelada'}), 400
    
    # Agregar celda a reveladas
    game['revealed_cells'].append(cell_index)
    
    # Verificar si es mina
    if cell_index in game['mine_positions']:
        # Es mina - fin del juego
        game['active'] = False
        session['mines_game'] = game
        session.modified = True
        
        # Guardar en historial
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO game_history (user_id, juego, resultado, monto_apostado) VALUES (?, ?, ?, ?)',
            (g.user['id'], 'buscaminas', 'Derrota - Mina encontrada', game['bet'])
        )
        conn.commit()
        
        return jsonify({
            'ok': True,
            'result': 'mine',
            'cell': cell_index,
            'mine_positions': game['mine_positions'],
            'game_over': True
        })
    
    else:
        # Es gema
        game['gems_found'] += 1
        
        # Calcular nuevo multiplicador
        safe_cells = total_cells - game['mines']
        remaining_safe = safe_cells - game['gems_found']
        remaining_total = total_cells - len(game['revealed_cells'])
        
        if remaining_safe > 0:
            game['multiplier'] = remaining_total / remaining_safe
        else:
            game['multiplier'] = total_cells  # Victoria total
        
        session['mines_game'] = game
        session.modified = True
        
        # Verificar victoria total
        if game['gems_found'] == safe_cells:
            game['active'] = False
            payout = game['bet'] * game['multiplier']
            
            conn = get_db_connection()
            conn.execute('UPDATE users SET saldo = saldo + ? WHERE id = ?', (payout, g.user['id']))
            conn.execute(
                'INSERT INTO game_history (user_id, juego, resultado, monto_apostado) VALUES (?, ?, ?, ?)',
                (g.user['id'], 'buscaminas', f'Victoria total - {game["gems_found"]} gemas', game['bet'])
            )
            conn.commit()
            
            new_balance = conn.execute('SELECT saldo FROM users WHERE id = ?', (g.user['id'],)).fetchone()['saldo']
            session['mines_game'] = game
            session.modified = True
            
            return jsonify({
                'ok': True,
                'result': 'gem',
                'cell': cell_index,
                'gems_found': game['gems_found'],
                'multiplier': game['multiplier'],
                'game_over': True,
                'victory': True,
                'payout': payout,
                'saldo': new_balance
            })
        
        return jsonify({
            'ok': True,
            'result': 'gem',
            'cell': cell_index,
            'gems_found': game['gems_found'],
            'multiplier': game['multiplier'],
            'game_over': False
        })

@app.route('/api/mines/cashout', methods=['POST'])
def mines_cashout():
    """Retirar ganancias actuales del buscaminas"""
    if not g.user:
        return jsonify({'ok': False, 'msg': 'No autenticado'}), 401
    
    if 'mines_game' not in session:
        return jsonify({'ok': False, 'msg': 'No hay juego activo'}), 400
    
    game = session['mines_game']
    if not game.get('active') or game['gems_found'] == 0:
        return jsonify({'ok': False, 'msg': 'No se puede retirar'}), 400
    
    # Calcular payout
    payout = game['bet'] * game['multiplier']
    
    # Actualizar saldo
    conn = get_db_connection()
    conn.execute('UPDATE users SET saldo = saldo + ? WHERE id = ?', (payout, g.user['id']))
    conn.execute(
        'INSERT INTO game_history (user_id, juego, resultado, monto_apostado) VALUES (?, ?, ?, ?)',
        (g.user['id'], 'buscaminas', f'Cashout - {game["gems_found"]} gemas', game['bet'])
    )
    conn.commit()
    
    new_balance = conn.execute('SELECT saldo FROM users WHERE id = ?', (g.user['id'],)).fetchone()['saldo']
    
    # Finalizar juego
    game['active'] = False
    session['mines_game'] = game
    session.modified = True
    
    return jsonify({
        'ok': True,
        'payout': payout,
        'profit': payout - game['bet'],
        'saldo': new_balance,
        'gems_found': game['gems_found'],
        'multiplier': game['multiplier']
    })

if __name__ == '__main__':
    app.run(port=8080, debug=True)