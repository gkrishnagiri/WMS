from app.core.config import Settings


def test_configuration_defaults_are_local_development_safe(monkeypatch):
    monkeypatch.delenv("DATABASE_HOST", raising=False)
    monkeypatch.delenv("DATABASE_PORT", raising=False)
    monkeypatch.delenv("REDIS_HOST", raising=False)
    monkeypatch.delenv("REDIS_PORT", raising=False)
    settings = Settings(_env_file=None)
    assert settings.database_host == "localhost"
    assert settings.database_port == 15432
    assert settings.redis_host == "localhost"
    assert settings.redis_port == 6379
    assert settings.app_version == "0.1.0"


def test_configuration_reads_environment(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test EOS")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://one.test, http://two.test")
    settings = Settings()
    assert settings.app_name == "Test EOS"
    assert settings.app_port == 9000
    assert settings.cors_origins == ["http://one.test", "http://two.test"]
