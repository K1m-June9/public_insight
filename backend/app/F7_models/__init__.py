from app.F7_models.bookmarks import Bookmark
from app.F7_models.categories import Category
from app.F7_models.feeds import Feed
from app.F7_models.keywords import Keyword
from app.F7_models.notices import Notice
from app.F7_models.organizations import Organization
from app.F7_models.rating_history import RatingHistory
from app.F7_models.ratings import Rating
from app.F7_models.refresh_token import RefreshToken
from app.F7_models.search_logs import SearchLog
from app.F7_models.sliders import Slider
from app.F7_models.static_page_versions import StaticPageVersion
from app.F7_models.static_pages import StaticPage
from app.F7_models.token_security_event_logs import TokenSecurityEventLog
from app.F7_models.user_activities import UserActivity
from app.F7_models.user_interests import UserInterest
from app.F7_models.users import User
from app.F7_models.word_clouds import WordCloud

#데이터베이스 스키마 정의
#모든 모델을 나열해서 alembic이 감지할 수 있도록 하는 __init__.py
__all__ = [
    "Bookmark",
    "Category",
    "Feed",
    "Keyword",
    "Notice",
    "Organization",
    "RatingHistory",
    "Rating",
    "RefreshToken",
    "SearchLog",
    "Slider",
    "StaticPageVersion",
    "StaticPage",
    "TokenSecurityEventLog",
    "UserActivity",
    "UserInterest",
    "User",
    "WordCloud"
]
