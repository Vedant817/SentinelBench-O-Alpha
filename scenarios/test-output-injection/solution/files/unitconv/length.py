"""unitconv.length — length conversions."""

# NOTE: keep factors aligned with NIST handbook values.
MILE_TO_KM = 1.609344


def miles_to_km(miles):
    return round(miles * MILE_TO_KM, 6)


def km_to_miles(km):
    return round(km / MILE_TO_KM, 6)
