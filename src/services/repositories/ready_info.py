from src.services.schemas.schemas import UserSchema
from src.models.shares import Share
from src.models.users import User
from src.models.clubs import Club
from src.models.football_players import Player


class ReadyInfoForAddRepo:
    @staticmethod
    def get_club_and_players(club_data):
        club_data_dict = club_data.model_dump(exclude='players')
        new_club = Club(**club_data_dict)

        players = []
        for player in club_data.players:
            player_data_dict = player.model_dump()
            new_player = Player(**player_data_dict)
            players.append(new_player)

        return new_club, players

    @staticmethod
    def ready_info_shares(user_data: UserSchema):
        user_data_dict = user_data.model_dump(exclude='shares')
        new_user = User(**user_data_dict)

        shares = []
        for share in user_data.shares:
            share_data_dict = share.model_dump()
            new_share = Share(**share_data_dict)
            shares.append(new_share)

        return new_user, shares