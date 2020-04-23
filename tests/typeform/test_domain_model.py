def test_range_sums(form, form_config_all_sums):
    form_config = form_config_all_sums
    domain = form_config.domains[0]
    domain_range = domain.get_range(form)
    assert domain_range == (0 + 2, 10 + 20)


def test_range_means(form, form_config_all_means):
    form_config = form_config_all_means
    domain = form_config.domains[0]
    domain_range = domain.get_range(form)

    # note that the results is the mean of the mean of dimensions
    assert domain_range == ((0 / 2 + 2 / 3) / 2, (10 / 2 + 20 / 3) / 2)


def test_value_sums(form, form_config_sums, response):
    form_config = form_config_sums
    domain = form_config.domains[0]
    value = domain.get_value(form, response)

    assert value == (1 + 5 + 2 + 0 + 5)


def test_value_sums_reversed(form, form_config_sums_reversed, response):
    form_config = form_config_sums_reversed
    domain = form_config.domains[0]
    value = domain.get_value(form, response)

    assert value == (4 + 0 + 10 + 4 + 1)


def test_value_means(form, form_config_means, response):
    form_config = form_config_means
    domain = form_config.domains[0]
    value = domain.get_value(form, response)

    assert value == ((1 + 5) / 2 + (2 + 0 + 5) / 3) / 2


def test_value_means_reversed(form, form_config_means_reversed, response):
    form_config = form_config_means_reversed
    domain = form_config.domains[0]
    value = domain.get_value(form, response)

    assert value == ((4 + 0) / 2 + (10 + 4 + 1) / 3) / 2
