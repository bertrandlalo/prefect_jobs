def test_range_sums(form, form_config_all_sums):
    form_config = form_config_all_sums
    dimension1 = form_config.domains[0].dimensions[0]
    dim1_range = dimension1.get_range(form)
    dimension2 = form_config.domains[0].dimensions[1]
    dim2_range = dimension2.get_range(form)

    assert dim1_range == (0, 10)
    assert dim2_range == (2, 20)


def test_range_means(form, form_config_all_means):
    form_config = form_config_all_means
    dimension1 = form_config.domains[0].dimensions[0]
    dim1_range = dimension1.get_range(form)
    dimension2 = form_config.domains[0].dimensions[1]
    dim2_range = dimension2.get_range(form)

    assert dim1_range == (0 / 2, 10 / 2)
    assert dim2_range == (2 / 3, 20 / 3)


def test_value_sums(form, form_config_sums, response):
    form_config = form_config_sums
    dimension1 = form_config.domains[0].dimensions[0]
    value1 = dimension1.get_value(form, response)
    dimension2 = form_config.domains[0].dimensions[1]
    value2 = dimension2.get_value(form, response)

    assert value1 == (1 + 5)
    assert value2 == (2 + 0 + 5)


def test_value_sums_reversed(form, form_config_sums_reversed, response):
    form_config = form_config_sums_reversed
    dimension1 = form_config.domains[0].dimensions[0]
    value1 = dimension1.get_value(form, response)
    dimension2 = form_config.domains[0].dimensions[1]
    value2 = dimension2.get_value(form, response)

    assert value1 == (4 + 0)
    assert value2 == (10 + 4 + 1)


def test_value_means(form, form_config_means, response):
    form_config = form_config_means
    dimension1 = form_config.domains[0].dimensions[0]
    value1 = dimension1.get_value(form, response)
    dimension2 = form_config.domains[0].dimensions[1]
    value2 = dimension2.get_value(form, response)

    assert value1 == (1 + 5) / 2
    assert value2 == (2 + 0 + 5) / 3


def test_value_means_reversed(form, form_config_means_reversed, response):
    form_config = form_config_means_reversed
    dimension1 = form_config.domains[0].dimensions[0]
    value1 = dimension1.get_value(form, response)
    dimension2 = form_config.domains[0].dimensions[1]
    value2 = dimension2.get_value(form, response)

    assert value1 == (4 + 0) / 2
    assert value2 == (10 + 4 + 1) / 3
