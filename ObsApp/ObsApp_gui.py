



'''
@click.command(help=CLASS_NAME + " Get Telescope Status")
def statustelescope():
    pass


def test_statustelescope():
    assert "statustelescope"


@click.command(help=CLASS_NAME + " Move Telescope position, dra:float, ddec:float")
@click.argument("dra", type=click.FLOAT)
@click.argument("ddec", type=click.FLOAT)
def movetelescope(dra, ddec):
    pass


def test_movetelescope():
    assert "movetelescope 10 20" 
    

@click.command(help=CLASS_NAME + " Image Taking, fowlernum:int, exptime:float, repeat:int")
@click.argument("fowlernum", type=click.INT)
@click.argument("exptime", type=click.FLOAT)
@click.argument("repeat", type=click.INT)
def imagetaking(fowlernum, exptime, repeat):
    pass


def test_imagetaking():
    assert "imagetaking 1 1.63 1"
'''    