from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from utils.game_utils import GameUtils
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2005@139.180.143.70:5432/nba_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 数据模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    players = db.relationship('Player', backref='team', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    overall = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    salary = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    stats = db.Column(db.JSON)
    season_stats = db.relationship('PlayerSeasonStats', backref='player', lazy=True)

class PlayerSeasonStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    season = db.Column(db.Integer, nullable=False)
    games_played = db.Column(db.Integer, default=0)
    games_started = db.Column(db.Integer, default=0)
    minutes_per_game = db.Column(db.Float, default=0)
    points_per_game = db.Column(db.Float, default=0)
    rebounds_per_game = db.Column(db.Float, default=0)
    assists_per_game = db.Column(db.Float, default=0)
    steals_per_game = db.Column(db.Float, default=0)
    blocks_per_game = db.Column(db.Float, default=0)
    turnovers_per_game = db.Column(db.Float, default=0)
    field_goal_percentage = db.Column(db.Float, default=0)
    three_point_percentage = db.Column(db.Float, default=0)
    free_throw_percentage = db.Column(db.Float, default=0)

class DraftPick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pick_number = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    status = db.Column(db.String(20), default='pending')

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('team'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        team_id = request.form.get('team_id')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=username,
            password=generate_password_hash(password),
            team_id=team_id
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('team'))

    teams = Team.query.all()
    return render_template('register.html', teams=teams)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/team')
@login_required
def team():
    team = Team.query.get(current_user.team_id)
    return render_template('team.html', team=team)

@app.route('/draft')
@login_required
def draft():
    draft_order = DraftPick.query.order_by(DraftPick.pick_number).all()
    current_pick = DraftPick.query.filter_by(status='pending').first()
    available_players = []
    
    if current_pick and current_pick.team_id == current_user.team_id:
        # 生成可选的球员
        for _ in range(5):
            player_stats = GameUtils.generate_player_stats()
            player = Player(
                name=player_stats['name'],
                position=player_stats['position'],
                overall=player_stats['overall'],
                salary=player_stats['salary'],
                age=player_stats['age'],
                stats=player_stats['stats']
            )
            available_players.append(player)
    
    return render_template('draft.html', 
                         draft_order=draft_order,
                         current_pick=current_pick,
                         available_players=available_players)

@app.route('/trade')
@login_required
def trade():
    return render_template('trade.html')

# API路由
@app.route('/api/player/<int:player_id>/stats')
@login_required
def get_player_stats(player_id):
    player = Player.query.get_or_404(player_id)
    return jsonify(player.stats)

@app.route('/api/teams')
@login_required
def get_teams():
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'city': team.city,
        'name': team.name
    } for team in teams])

@app.route('/api/team/<int:team_id>/players')
@login_required
def get_team_players(team_id):
    players = Player.query.filter_by(team_id=team_id).all()
    return jsonify([{
        'id': player.id,
        'name': player.name,
        'position': player.position,
        'overall': player.overall
    } for player in players])

@app.route('/api/trade', methods=['POST'])
@login_required
def propose_trade():
    data = request.get_json()
    player_id = data.get('player_id')
    target_team_id = data.get('target_team_id')
    target_player_id = data.get('target_player_id')

    if not all([player_id, target_team_id, target_player_id]):
        return jsonify({'success': False, 'message': 'Missing required fields'})

    trade = Trade(
        team1_id=current_user.team_id,
        team2_id=target_team_id,
        player1_id=player_id,
        player2_id=target_player_id
    )
    db.session.add(trade)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/api/draft', methods=['POST'])
@login_required
def draft_player():
    data = request.get_json()
    player_id = data.get('player_id')
    
    current_pick = DraftPick.query.filter_by(status='pending').first()
    if not current_pick or current_pick.team_id != current_user.team_id:
        return jsonify({'success': False, 'message': 'Not your turn to draft'})

    player = Player.query.get(player_id)
    if not player:
        return jsonify({'success': False, 'message': 'Player not found'})

    player.team_id = current_user.team_id
    current_pick.player_id = player_id
    current_pick.status = 'completed'
    
    db.session.commit()
    return jsonify({'success': True})

# 添加生成球员赛季统计数据的函数
def generate_player_game_stats(player):
    """根据球员能力值生成单场比赛的统计数据"""
    base_stats = {
        'minutes': random.uniform(20, 40),
        'points': random.uniform(5, 30),
        'rebounds': random.uniform(2, 15),
        'assists': random.uniform(1, 10),
        'steals': random.uniform(0, 3),
        'blocks': random.uniform(0, 3),
        'turnovers': random.uniform(0, 5),
        'fg_attempts': random.uniform(5, 20),
        'fg_made': 0,
        'three_attempts': random.uniform(0, 10),
        'three_made': 0,
        'ft_attempts': random.uniform(0, 10),
        'ft_made': 0
    }
    
    # 根据球员能力值调整统计数据
    overall_factor = player.overall / 80.0  # 假设80是平均能力值
    
    # 调整投篮命中率
    base_stats['fg_made'] = base_stats['fg_attempts'] * (0.4 + (overall_factor - 1) * 0.2)
    base_stats['three_made'] = base_stats['three_attempts'] * (0.3 + (overall_factor - 1) * 0.2)
    base_stats['ft_made'] = base_stats['ft_attempts'] * (0.7 + (overall_factor - 1) * 0.15)
    
    # 根据位置调整特定数据
    if player.position in ['PG', 'SG']:
        base_stats['assists'] *= 1.5
        base_stats['three_attempts'] *= 1.5
    elif player.position in ['PF', 'C']:
        base_stats['rebounds'] *= 1.5
        base_stats['blocks'] *= 1.5
    
    return base_stats

def update_player_season_stats(player, game_stats):
    """更新球员赛季统计数据"""
    current_season = datetime.now().year
    season_stats = PlayerSeasonStats.query.filter_by(
        player_id=player.id,
        season=current_season
    ).first()
    
    if not season_stats:
        season_stats = PlayerSeasonStats(
            player_id=player.id,
            season=current_season
        )
        db.session.add(season_stats)
    
    # 更新统计数据
    season_stats.games_played += 1
    season_stats.minutes_per_game = (season_stats.minutes_per_game * (season_stats.games_played - 1) + 
                                   game_stats['minutes']) / season_stats.games_played
    season_stats.points_per_game = (season_stats.points_per_game * (season_stats.games_played - 1) + 
                                  game_stats['points']) / season_stats.games_played
    season_stats.rebounds_per_game = (season_stats.rebounds_per_game * (season_stats.games_played - 1) + 
                                    game_stats['rebounds']) / season_stats.games_played
    season_stats.assists_per_game = (season_stats.assists_per_game * (season_stats.games_played - 1) + 
                                   game_stats['assists']) / season_stats.games_played
    season_stats.steals_per_game = (season_stats.steals_per_game * (season_stats.games_played - 1) + 
                                  game_stats['steals']) / season_stats.games_played
    season_stats.blocks_per_game = (season_stats.blocks_per_game * (season_stats.games_played - 1) + 
                                  game_stats['blocks']) / season_stats.games_played
    season_stats.turnovers_per_game = (season_stats.turnovers_per_game * (season_stats.games_played - 1) + 
                                     game_stats['turnovers']) / season_stats.games_played
    
    # 更新投篮命中率
    total_fg_attempts = season_stats.games_played * game_stats['fg_attempts']
    total_fg_made = season_stats.games_played * game_stats['fg_made']
    season_stats.field_goal_percentage = (total_fg_made / total_fg_attempts) * 100 if total_fg_attempts > 0 else 0
    
    total_three_attempts = season_stats.games_played * game_stats['three_attempts']
    total_three_made = season_stats.games_played * game_stats['three_made']
    season_stats.three_point_percentage = (total_three_made / total_three_attempts) * 100 if total_three_attempts > 0 else 0
    
    total_ft_attempts = season_stats.games_played * game_stats['ft_attempts']
    total_ft_made = season_stats.games_played * game_stats['ft_made']
    season_stats.free_throw_percentage = (total_ft_made / total_ft_attempts) * 100 if total_ft_attempts > 0 else 0
    
    db.session.commit()

# 添加新的API路由来获取球员赛季统计
@app.route('/api/player/<int:player_id>/season-stats')
@login_required
def get_player_season_stats(player_id):
    player = Player.query.get_or_404(player_id)
    current_season = datetime.now().year
    season_stats = PlayerSeasonStats.query.filter_by(
        player_id=player_id,
        season=current_season
    ).first()
    
    if not season_stats:
        return jsonify({
            'message': 'No stats available for this season',
            'stats': None
        })
    
    return jsonify({
        'stats': {
            'games_played': season_stats.games_played,
            'games_started': season_stats.games_started,
            'minutes_per_game': round(season_stats.minutes_per_game, 1),
            'points_per_game': round(season_stats.points_per_game, 1),
            'rebounds_per_game': round(season_stats.rebounds_per_game, 1),
            'assists_per_game': round(season_stats.assists_per_game, 1),
            'steals_per_game': round(season_stats.steals_per_game, 1),
            'blocks_per_game': round(season_stats.blocks_per_game, 1),
            'turnovers_per_game': round(season_stats.turnovers_per_game, 1),
            'field_goal_percentage': round(season_stats.field_goal_percentage, 1),
            'three_point_percentage': round(season_stats.three_point_percentage, 1),
            'free_throw_percentage': round(season_stats.free_throw_percentage, 1)
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 