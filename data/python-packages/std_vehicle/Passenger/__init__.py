#!/usr/bin/env python3

"""Passenger model."""

# pylint: disable=C0103,R0801,R0902,R0915,C0301,W0235


from velocitas_sdk.model import (
    DataPointFloat,
    DataPointString,
    DataPointUint8,
    Model,
)


class Passenger(Model):
    """Passenger model.

    Attributes
    ----------
    Age: sensor
        Age

        Unit: string
    Gender: sensor
        Gender

        Unit: string
    KinetosisScore: sensor
        KinetosisScore

        Unit: string
    """

    def __init__(self, name, parent):
        """Create a new Passenger model."""
        super().__init__(parent)
        self.name = name

        self.Age = DataPointUint8("Age", self)
        self.Gender = DataPointString("Gender", self)
        self.KinetosisScore = DataPointFloat("KinetosisScore", self)
