from app import db, Team, Player, User
from utils.game_utils import GameUtils

def init_database():
    # 创建所有表
    db.create_all()

    # 检查是否已经初始化
    if Team.query.first() is not None:
        print("Database already initialized!")
        return

    # 创建30支NBA球队
    teams = [
        ('Atlanta', 'Hawks'),
        ('Boston', 'Celtics'),
        ('Brooklyn', 'Nets'),
        ('Charlotte', 'Hornets'),
        ('Chicago', 'Bulls'),
        ('Cleveland', 'Cavaliers'),
        ('Dallas', 'Mavericks'),
        ('Denver', 'Nuggets'),
        ('Detroit', 'Pistons'),
        ('Golden State', 'Warriors'),
        ('Houston', 'Rockets'),
        ('Indiana', 'Pacers'),
        ('LA', 'Clippers'),
        ('Los Angeles', 'Lakers'),
        ('Memphis', 'Grizzlies'),
        ('Miami', 'Heat'),
        ('Milwaukee', 'Bucks'),
        ('Minnesota', 'Timberwolves'),
        ('New Orleans', 'Pelicans'),
        ('New York', 'Knicks'),
        ('Oklahoma City', 'Thunder'),
        ('Orlando', 'Magic'),
        ('Philadelphia', '76ers'),
        ('Phoenix', 'Suns'),
        ('Portland', 'Trail Blazers'),
        ('Sacramento', 'Kings'),
        ('San Antonio', 'Spurs'),
        ('Toronto', 'Raptors'),
        ('Utah', 'Jazz'),
        ('Washington', 'Wizards')
    ]

    # 添加球队
    for city, name in teams:
        team = Team(city=city, name=name)
        db.session.add(team)
    db.session.commit()

    # 为每支球队生成初始球员
    for team in Team.query.all():
        # 生成15名球员
        for _ in range(15):
            player_stats = GameUtils.generate_player_stats()
            player = Player(
                name=player_stats['name'],
                position=player_stats['position'],
                overall=player_stats['overall'],
                team_id=team.id,
                salary=player_stats['salary'],
                age=player_stats['age']
            )
            db.session.add(player)
    db.session.commit()

    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database() 