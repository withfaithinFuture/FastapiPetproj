from sqlalchemy import ForeignKey, Column, Table
from src.services.db.base_service import Base


joined_table = Table(
    'clubs_and_players', Base.metadata,
    Column('club_id', ForeignKey('clubs.id', ondelete='CASCADE')),
    Column('player_id', ForeignKey('players.id', ondelete='CASCADE')),
)
