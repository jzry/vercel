# imports
# import cv2 as cv

BC_WIDTH = 2200
BC_HEIGHT = 1700

CTR_WIDTH = 1700
CTR_HEIGHT = 2800

# Global dictionary containing score field coordinates for each rider
BC_TEMPLATE_FIELDS = {
    "Rider1": {
        'Rider#': (363, 321, 95, 44),
        'recovery': (361, 510, 107, 49), # (x, y, width, height)
        'hydration': (361, 555, 107, 41),
        'lesions': (361, 594, 107, 41),
        'soundness': (361, 664, 107, 49),
        'qual_movement': (361, 711, 107, 41),
        'rider_time': (307, 971, 116, 44),
        'rider_weight': (307, 1310, 119, 44)
    },
    "Rider2": {
        'Rider#': (770, 321, 95, 44),
        'recovery': (768, 510, 107, 49),
        'hydration': (768, 555, 107, 41),
        'lesions': (768, 594, 107, 41),
        'soundness': (768, 664, 107, 49),
        'qual_movement': (768, 711, 107, 41),
        'rider_time': (714, 971, 116, 44),
        'rider_weight': (714, 1310, 119, 44)
    },
    "Rider3": {
        'Rider#': (1183, 321, 95, 44),
        'recovery': (1181, 510, 107, 49),
        'hydration': (1181, 555, 107, 41),
        'lesions': (1181, 594, 107, 41),
        'soundness': (1181, 664, 107, 49),
        'qual_movement': (1181, 711, 107, 41),
        'rider_time': (1127, 971, 116, 44),
        'rider_weight': (1127, 1310, 119, 44)
    },
    "Rider4": {
        'Rider#': (1590, 321, 95, 44),
        'recovery': (1588, 510, 107, 49),
        'hydration': (1588, 555, 107, 41),
        'lesions': (1588, 594, 107, 41),
        'soundness': (1588, 664, 107, 49),
        'qual_movement': (1588, 711, 107, 41),
        'rider_time': (1534, 971, 116, 44),
        'rider_weight': (1534, 1310, 119, 44)
    },
    "Rider5": {
        'Rider#': (2003, 321, 95, 44),
        'recovery': (2001, 510, 107, 49),
        'hydration': (2001, 555, 107, 41),
        'lesions': (2001, 594, 107, 41),
        'soundness': (2001, 664, 107, 49),
        'qual_movement': (2001, 711, 107, 41),
        'rider_time': (1947, 971, 116, 44),
        'rider_weight': (1947, 1310, 119, 44)
    },
}

CTR_TEMPLATE_FIELDS = {
    "initial_pulse_before": (1384, 1110, 89, 76), # (x, y, width, height)
    "initial_pulse_after": (1384, 1202, 89, 102),
    "mucous_membrane": (1384, 1428, 89, 29),
    "capillary_refill": (1384, 1467, 89, 29),
    "skin_pinch": (1384, 1509, 89, 29),
    "jugular_vein_refill": (1384, 1548, 89, 29),
    "gut_sounds": (1384, 1589, 89, 29),
    "anal_tone": (1384, 1731, 89, 72),
    "muscle_tone": (1384, 1815, 89, 37),
    "unwillingness_to_trot": (1384, 1863, 89, 27),
    "leg_injuries": (1384, 1903, 89, 109),
    "injury_interference": (1384, 2025, 89, 46),
    "lameness_grade1": (1384, 2097, 89, 74),
    "lameness_grade2": (1384, 2182, 89, 37),
    "back_stress": (1384, 2317, 89, 54),
    "tack_area": (1384, 2404, 89, 53),
    "hold_on_trail": (1489, 2489, 86, 30),
    "time_penalty": (1489, 2531, 86, 43)
}
