import pytest

from src.drivers.drivers_registry import (
    DriverRegistry
)


@pytest.fixture
def driver_registry():
    return DriverRegistry()


# ============================================================
# REVENUE DRIVERS
# ============================================================

def test_revenue_drivers(driver_registry):

    drivers = driver_registry.get_drivers(
        "revenue"
    )

    assert drivers == [
        "customers",
        "orders_per_customer",
        "aov",
    ]


# ============================================================
# AOV SUB-DRIVERS
# ============================================================

def test_aov_sub_drivers(driver_registry):

    sub_drivers = (
        driver_registry.get_sub_drivers(
            "revenue",
            "aov"
        )
    )

    assert sub_drivers == [
        "price",
        "discounting",
        "product_mix",
        "attach_rate",
    ]


# ============================================================
# DRIVER FORMULA
# ============================================================

def test_driver_formula(driver_registry):

    formula = (
        driver_registry.get_driver_formula(
            "revenue",
            "aov"
        )
    )

    assert formula == "revenue / orders"


# ============================================================
# DRIVER CONFIGURATION
# ============================================================

def test_get_driver(driver_registry):

    driver = driver_registry.get_driver(
        "revenue",
        "aov"
    )

    assert driver["formula"] == (
        "revenue / orders"
    )

    assert "sub_drivers" in driver


# ============================================================
# DRIVER TREE
# ============================================================

def test_driver_tree(driver_registry):

    tree = driver_registry.get_driver_tree(
        "revenue"
    )

    assert "customers" in tree
    assert "orders_per_customer" in tree
    assert "aov" in tree

    assert (
        tree["aov"]["formula"]
        == "revenue / orders"
    )

    assert (
        tree["aov"]["sub_drivers"]
        == [
            "price",
            "discounting",
            "product_mix",
            "attach_rate",
        ]
    )


# ============================================================
# DRIVER EXISTENCE
# ============================================================

def test_has_driver(driver_registry):

    assert driver_registry.has_driver(
        "revenue",
        "aov"
    )

    assert driver_registry.has_driver(
        "revenue",
        "customers"
    )

    assert not driver_registry.has_driver(
        "revenue",
        "something_fake"
    )


# ============================================================
# SUB-DRIVER EXISTENCE
# ============================================================

def test_has_sub_driver(driver_registry):

    assert driver_registry.has_sub_driver(
        "revenue",
        "aov",
        "product_mix"
    )

    assert not driver_registry.has_sub_driver(
        "revenue",
        "aov",
        "something_fake"
    )


# ============================================================
# INVALID DRIVER
# ============================================================

def test_invalid_driver_raises_error(
    driver_registry
):

    with pytest.raises(KeyError):

        driver_registry.get_driver(
            "revenue",
            "not_a_driver"
        )