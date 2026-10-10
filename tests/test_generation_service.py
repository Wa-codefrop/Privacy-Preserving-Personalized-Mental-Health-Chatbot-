from app.services.generation_service import GenerationService


def test_generation_service_falls_back_gracefully_without_local_model():
    service = GenerationService(local_model_path=None)
    result = service.generate("I feel overwhelmed and need support.")

    assert isinstance(result, str)
    assert "listen" in result.lower()
    assert "support" in result.lower()
