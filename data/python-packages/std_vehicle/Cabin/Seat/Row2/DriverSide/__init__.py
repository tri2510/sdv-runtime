#!/usr/bin/env python3

"""DriverSide model."""

# pylint: disable=C0103,R0801,R0902,R0915,C0301,W0235


from velocitas_sdk.model import (
    DataPointBoolean,
    DataPointFloat,
    DataPointInt8,
    DataPointUint16,
    DataPointUint8,
    Model,
)

from vehicle.Cabin.Seat.Row2.DriverSide.Airbag import Airbag
from vehicle.Cabin.Seat.Row2.DriverSide.Backrest import Backrest
from vehicle.Cabin.Seat.Row2.DriverSide.Headrest import Headrest
from vehicle.Cabin.Seat.Row2.DriverSide.Occupant import Occupant
from vehicle.Cabin.Seat.Row2.DriverSide.Seating import Seating
from vehicle.Cabin.Seat.Row2.DriverSide.Switch import Switch


class DriverSide(Model):
    """DriverSide model.

    Attributes
    ----------
    Airbag: branch
        Airbag signals.

        Unit: None
    Backrest: branch
        Describes signals related to the backrest of the seat.

        Unit: None
    Headrest: branch
        Headrest settings.

        Unit: None
    Heating: actuator
        Seat cooling / heating. 0 = off. -100 = max cold. +100 = max heat.

        Value range: [-100, 100]
        Unit: percent
    HeatingCooling: actuator
        Heating or Cooling requsted for the Item. -100 = Maximum cooling, 0 = Heating/cooling deactivated, 100 = Maximum heating.

        Value range: [-100, 100]
        Unit: percent
    Height: actuator
        Seat position on vehicle z-axis. Position is relative within available movable range of the seating. 0 = Lowermost position supported.

        Value range: [0, ]
        Unit: mm
    IsBelted: sensor
        Is the belt engaged.

        Unit: None
    IsOccupied: sensor
        Does the seat have a passenger in it.

        Unit: None
    Massage: actuator
        Seat massage level. 0 = off. 100 = max massage.

        Value range: [0, 100]
        Unit: percent
    Occupant: branch
        Occupant data.

        Unit: None
    Position: actuator
        Seat position on vehicle x-axis. Position is relative to the frontmost position supported by the seat. 0 = Frontmost position supported.

        Value range: [0, ]
        Unit: mm
    SeatBeltHeight: actuator
        Seat belt position on vehicle z-axis. Position is relative within available movable range of the seat belt. 0 = Lowermost position supported.

        Unit: mm
    Seating: branch
        Describes signals related to the seat bottom of the seat.

        Seating is here considered as the part of the seat that supports the thighs. Additional cushions (if any) for support of lower legs is not covered by this branch.

        Unit: None
    Switch: branch
        Seat switch signals

        Unit: None
    Tilt: actuator
        Tilting of seat (seating and backrest) relative to vehicle x-axis. 0 = seat bottom is flat, seat bottom and vehicle x-axis are parallel. Positive degrees = seat tilted backwards, seat x-axis tilted upward, seat z-axis is tilted backward.

        In VSS it is assumed that tilting a seat affects both seating (seat bottom) and backrest, i.e. the angle between seating and backrest will not be affected when changing Tilt.

        Unit: degrees
    """

    def __init__(self, name, parent):
        """Create a new DriverSide model."""
        super().__init__(parent)
        self.name = name

        self.Airbag = Airbag("Airbag", self)
        self.Backrest = Backrest("Backrest", self)
        self.Headrest = Headrest("Headrest", self)
        self.Heating = DataPointInt8("Heating", self)
        self.HeatingCooling = DataPointInt8("HeatingCooling", self)
        self.Height = DataPointUint16("Height", self)
        self.IsBelted = DataPointBoolean("IsBelted", self)
        self.IsOccupied = DataPointBoolean("IsOccupied", self)
        self.Massage = DataPointUint8("Massage", self)
        self.Occupant = Occupant("Occupant", self)
        self.Position = DataPointUint16("Position", self)
        self.SeatBeltHeight = DataPointUint16("SeatBeltHeight", self)
        self.Seating = Seating("Seating", self)
        self.Switch = Switch("Switch", self)
        self.Tilt = DataPointFloat("Tilt", self)
