"""Config flow for the Brunata Online integration."""

import logging
import json
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_CODE
from homeassistant.core import HomeAssistant

from brunata_online import TokenData, BrunataOnlineClient, BrunataUser, MeterApi

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CODE): str,
    }
)


class BrunataOnlineHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, token: TokenData) -> None:
        """Initialize."""
        self.token = token
        self.user_api = BrunataUser(self.token)
        self.meter_api = MeterApi(self.token)

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            self.user_api.get_user()
        except:
            return False
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    token = TokenData(**json.loads(data[CONF_CODE]))

    client = BrunataOnlineClient(token)

    user = BrunataUser(token)

    hub = BrunataOnlineHub(data[CONF_HOST])

    if not await hub.authenticate():
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "brunata_integration or some name.."}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Brunata Online."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
