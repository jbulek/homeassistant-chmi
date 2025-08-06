from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, STATIONS


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        options = {key: data['location'] for key, data in STATIONS.items()}

        schema = vol.Schema({
            vol.Required("station_key"): vol.In(options),
        })

        if user_input is not None:
            return self.async_create_entry(
                title=options[user_input["station_key"]],
                data={"station_key": user_input["station_key"]}
            )

        return self.async_show_form(step_id="user", data_schema=schema)
