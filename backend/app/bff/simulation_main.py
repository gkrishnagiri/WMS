from app.bff.app_factory import create_bff_app
from app.bff.experience_registry import get_experience

app = create_bff_app(get_experience("simulation"))
