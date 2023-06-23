import enum


class DataLinks(enum.Enum):
    season_page: str = 'https://animego.org/anime/season/2023?sort=a.createdAt&direction=desc&type=animes'
    main_page: str = 'https://animego.org/'
    ongoing_page: str = 'https://animego.org/anime/filter/status-is-ongoing/apply?sort=createdAt&direction=desc&type' \
                        '=animes'

