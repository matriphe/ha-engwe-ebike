# ENGWE E-bike for Home Assistant

Experimental custom integration for the ENGWE cloud API, based on observed traffic from an ENGWE L20 3.0 Pro. **Not yet verified against a running Home Assistant instance.** The login format and polling requests are inferred from traffic and may require additional headers or a transformed password.

## Installation

For a manual installation, copy `custom_components/engwe` to `<config>/custom_components/engwe`, restart Home Assistant, then add **ENGWE E-bike** under Settings → Devices & Services. This directory is structured for installation as a HACS custom integration after it is pushed to a suitable public GitHub repository. A local folder alone is not an installable HACS repository. No repository or marketplace listing exists yet.

Enter your ENGWE account email and password in Home Assistant, not in chat. Home Assistant stores config entries in its configuration storage; protect backups. The integration discovers the first IoT bike returned by the account and polls every 10 minutes. The integration only sends login and observed bike listing and status requests; it does not expose control actions. POST endpoints have not yet been independently verified as read-only.

## Sensors

The captured device attribute catalog reported the following codes and raw units. The integration creates the corresponding sensors; a missing value remains unknown.

| Sensor | API attribute | API unit | Conversion |
| --- | --- | --- | --- |
| Battery | `vehicleBatterySOC` | % | none |
| Battery health | `vehicleBatterySOH` | % | none |
| IoT battery | `iotBatterySOC` | % | none |
| Total ride duration | `totalRideTime` | min | none |
| Total distance | `totalMileages` | 0.1 km | multiply by 0.1 |
| Current, maximum, average speed | `currentSpeed`, `maxSpeed`, `avgSpeed` | 0.1 km/h | multiply by 0.1 |
| Current, maximum cadence | `pedallingRate`, `maxPedallingRate` | 1 RPM | none |
| Online | `networkInfo.isOnline` | boolean | none |

Each sensor exposes `api_raw_value`, `api_raw_unit`, `api_attribute_code`, and `api_scale_factor` as separate attributes. The Home Assistant state is the numeric raw value multiplied by the scale factor; its unit is set separately through `native_unit_of_measurement`. No historical values are fabricated.

The factors follow the API's reported units, but they and the semantics of maximum/average speed must still be checked against the app. These are latest device attributes, not necessarily the values for the last ride. The separate history endpoint exposes duration, distance and speed but its period, units, and request semantics are not yet verified.

A GPS device tracker is present but disabled by default. It uses the separately reported `latitude` and `longitude` numeric attributes only if both are finite and in valid ranges. The API's coordinate reference system, scale, freshness, and values have not been verified. Enable it only after confirming its behavior in Home Assistant. Location is sensitive and may be stored by Home Assistant if enabled.

The cloud API is undocumented and may change. Bluetooth-only information and certificate-pinned traffic may not be available. Authentication, token renewal, multiple bicycles, sensor conversions and behavior on a real HA installation require validation.

## Privacy and publishing

Do not commit Home Assistant `.storage`, backups, logs, proxy captures, HAR files, certificates, private keys, account credentials, tokens, device identifiers, or GPS coordinates. The `.gitignore` covers common filenames and extensions but cannot detect secrets in arbitrary files or existing Git history. Review all staged files and any existing history before publishing. Redact diagnostics and screenshots before sharing them.

This project is an independent, experimental integration and is not affiliated with ENGWE. Do not use it to send control commands: only observed login, device listing, and status endpoints are implemented, and the effects of these POST endpoints still require verification.
