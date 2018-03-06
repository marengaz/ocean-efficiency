from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import decimal

from wtforms import Form, DecimalField, validators


class LatLongForm(Form):
    latitude = DecimalField(
        'Latitude',
        places=12,
        rounding=decimal.ROUND_UP,
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=-180, max=180)
        ]
    )
    longitude = DecimalField(
        'Longitude',
        places=12,
        rounding=decimal.ROUND_UP,
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=-180, max=180)
        ]
    )

