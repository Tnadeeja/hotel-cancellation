"""Strict request validation from the Stage 9A contract."""
from datetime import date
import re
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, model_validator

# Exact pandas-read raw vocabulary, including source exceptions such as CN.
COUNTRY_CODES = frozenset("ABW AGO AIA ALB AND ARE ARG ARM ASM ATA ATF AUS AUT AZE BDI BEL BEN BFA BGD BGR BHR BHS BIH BLR BOL BRA BRB BWA CAF CHE CHL CHN CIV CMR CN COL COM CPV CRI CUB CYM CYP CZE DEU DJI DMA DNK DOM DZA ECU EGY ESP EST ETH FIN FJI FRA FRO GAB GBR GEO GGY GHA GIB GLP GNB GRC GTM GUY HKG HND HRV HUN IDN IMN IND IRL IRN IRQ ISL ISR ITA JAM JEY JOR JPN KAZ KEN KHM KIR KNA KOR KWT LAO LBN LBY LCA LIE LKA LTU LUX LVA MAC MAR MCO MDG MDV MEX MKD MLI MLT MMR MNE MOZ MRT MUS MWI MYS MYT NAM NCL NGA NIC NLD NOR NPL NZL OMN PAK PAN PER PHL PLW POL PRI PRT PRY PYF QAT ROU RUS RWA SAU SDN SEN SGP SLE SLV SMR SRB STP SUR SVK SVN SWE SYC SYR TGO THA TJK TMP TUN TUR TWN TZA UGA UKR UMI URY USA UZB VEN VGB VNM ZAF ZMB ZWE".split())
Count = Annotated[int, Field(strict=True, ge=0)]


class BookingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hotel: Literal["City Hotel", "Resort Hotel"]
    lead_time: Count
    arrival_date: date
    stays_in_weekend_nights: Count
    stays_in_week_nights: Count
    adults: Count
    children: Count
    babies: Count
    meal: Literal["BB", "FB", "HB", "SC", "Undefined"]
    country: StrictStr | None = None
    market_segment: Literal["Aviation", "Complementary", "Corporate", "Direct", "Groups", "Offline TA/TO", "Online TA", "Undefined"]
    distribution_channel: Literal["Corporate", "Direct", "GDS", "TA/TO", "Undefined"]
    is_repeated_guest: Annotated[int, Field(strict=True, ge=0, le=1)]
    previous_cancellations: Count
    previous_bookings_not_canceled: Count
    reserved_room_type: Literal["A", "B", "C", "D", "E", "F", "G", "H", "L", "P"]
    deposit_type: Literal["No Deposit", "Non Refund", "Refundable"]
    agent: StrictStr | None = None
    days_in_waiting_list: Count
    customer_type: Literal["Contract", "Group", "Transient", "Transient-Party"]
    required_car_parking_spaces: Count
    total_of_special_requests: Count

    @field_validator("arrival_date", mode="before")
    @classmethod
    def valid_date(cls, value):
        message = "arrival_date must be a valid calendar date in YYYY-MM-DD format."
        if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
            raise ValueError(message)
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError(message) from None

    @field_validator("agent")
    @classmethod
    def valid_agent(cls, value):
        if value is not None and re.fullmatch(r"0|[1-9][0-9]*", value) is None:
            raise ValueError("agent must be a canonical non-negative integer string or null.")
        return value

    @field_validator("country")
    @classmethod
    def valid_country(cls, value):
        if value is not None and value not in COUNTRY_CODES:
            raise ValueError("country must be an approved dataset code or null when unknown.")
        return value

    @model_validator(mode="after")
    def positive_guests(self) -> Self:
        if self.adults + self.children + self.babies == 0:
            raise ValueError("adults + children + babies must be greater than 0.")
        return self


class PredictionResponse(BaseModel):
    prediction: Annotated[int, Field(strict=True, ge=0, le=1)]
    prediction_label: Literal["Not Cancelled", "Cancelled"]
    cancellation_probability: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    model_name: Literal["Random Forest"] = "Random Forest"
    strategy: Literal["General-only"] = "General-only"
