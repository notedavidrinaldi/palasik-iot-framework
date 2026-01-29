from palasik.core.context import PalasikContext


def test_context_initialization():
    ctx = PalasikContext()

    assert ctx.trust is not None
    assert ctx.logger is not None
