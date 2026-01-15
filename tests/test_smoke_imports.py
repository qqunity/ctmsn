def test_smoke_imports():
    import ctmsn
    from ctmsn.core.network import SemanticNetwork
    from ctmsn.forcing.engine import ForcingEngine
    assert SemanticNetwork is not None
    assert ForcingEngine is not None
