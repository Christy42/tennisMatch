from competitions import generate_calender


def test_generate_pro_tour():
    tour = {"Brisbane International": {"start date": 1, "start month": 1},
            "Chennai Open": {"start date": 1, "start month": 1}, "Qatar Open": {"start date": 1, "start month": 1},
            "Apia International": {"start date": 8, "start month": 1},
            "Classic Auckland": {"start date": 8, "start month": 1},
            "Australian Open": {"start date": 15, "start month": 1}}
    calender = generate_calender.generate_pro_tour("Monday", tour)
    assert ["Australian Open"] in calender.values()
    assert "2000-01-08" in calender


def test_generate_senior_competitions():
    calender = {'2000-01-07': ["Qatar Open", "Brisbane International", "Chennai Open"],
                '2000-01-14': ["Classic Auckland", "Apia International"]}
    calender = generate_calender.generate_senior_competitions(calender, {})
    for week in calender:
        assert len(calender[week]) > 3


def test_generate_junior_tour():
    calender = {'2000-01-07': ["Qatar Open", "Brisbane International", "Chennai Open"],
                '2000-01-14': ["Classic Auckland", "Apia International"]}
    calender = generate_calender.generate_junior_tour(calender)
    for week in calender:
        assert len(calender[week]) > 3
