import pytest

from ..xgui import get_surface_central_if_can

from ..gui.widgets.surface_central import SurfaceCentralWidget

def _test_gscic(arg, expected_maybe_cls):
    """Tests get_surface_central_if_can called with the given argument has the given expected class.

    Works correctly if the function produces False.

    arg : str?
    expected_maybe_cls : class as first-class value
    """
    out = get_surface_central_if_can(arg)
    act_cls_val = out.__class__ if out else out

    exp_cls_val = expected_maybe_cls.__class__ if expected_maybe_cls else expected_maybe_cls

    assert act_cls_val is exp_cls_val

def test_get_surface_central_default():
    _test_gscic(None, SurfaceCentralWidget)

def test_get_surface_central_legal_name():
    # Ideally we have a name that is different from the default
    # option. Once we have a second variant, add that in.
    _test_gscic('SurfaceCentralWidget', SurfaceCentralWidget)

def test_get_surface_central_illegal_name():
    # It is impossible for a user to accidentally create a widget with
    # those names and make this test case fail, because those names
    # are illegal.
    _test_gscic("illegal?name", False)
    _test_gscic("another/illegalname", False)
    
