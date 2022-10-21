[![HACS Custom][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]
[![Ko-Fi][ko_fi_shield]][ko_fi]
[![PayPal.Me][paypal_me_shield]][paypal_me]


[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Custom&style=popout&color=orange&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/faq/custom_repositories

[latest_release]: https://github.com/PiotrMachowski/Home-Assistant-custom-components-MPK-Lodz/releases/latest
[releases_shield]: https://img.shields.io/github/release/PiotrMachowski/Home-Assistant-custom-components-MPK-Lodz.svg?style=popout

[releases]: https://github.com/PiotrMachowski/Home-Assistant-custom-components-MPK-Lodz/releases
[downloads_total_shield]: https://img.shields.io/github/downloads/PiotrMachowski/Home-Assistant-custom-components-MPK-Lodz/total

[ko_fi_shield]: https://img.shields.io/static/v1.svg?label=%20&message=Ko-Fi&color=F16061&logo=ko-fi&logoColor=white
[ko_fi]: https://ko-fi.com/piotrmachowski

[buy_me_a_coffee_shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy_me_a_coffee]: https://www.buymeacoffee.com/PiotrMachowski

[paypal_me_shield]: https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal
[paypal_me]: https://paypal.me/PiMachowski

# MPK Łódź sensor

This sensor uses unofficial API provided by MPK Łódź.

## Configuration options

| Key | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | `False` | `MPK Łódź` | Name of sensor |
| `stops` | `list` | `True` | - | List of stop configurations |

### Stop configuration

| Key | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `id` | `positive integer` | `False` | - | ID of a stop |
| `num` | `positive integer` | `False` | - | Number of a stop |
| `name` | `string` | `False` | id | Name of a stop |
| `lines` | `list` | `False` | all available | List of monitored lines. |
| `directions` | `list` | `False` | all available | List of monitored directions. |

One of `id` or `num` must be provided!

## Example usage

```
sensor:
  - platform: mpk_lodz
      stops:
        - id: 2427
          lines:
            - "o97A"          
        - id: 2873
          directions:
            - "DW. ŁÓDŹ KALISKA"
```

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

This integration can be added to HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories):
* URL: `https://github.com/PiotrMachowski/Home-Assistant-custom-components-MPK-Lodz`
* Category: `Integration`

After adding a custom repository you can use HACS to install this integration using user interface.

### Manual

To install this integration manually you have to download [*mpk_lodz.zip*](https://github.com/PiotrMachowski/Home-Assistant-custom-components-MPK-Lodz/releases/latest/download/mpk_lodz.zip) and extract its contents to `config/custom_components/mpk_lodz` directory:
```bash
mkdir -p custom_components/mpk_lodz
cd custom_components/mpk_lodz
wget https://github.com/PiotrMachowski/Home-Assistant-custom-components-MPK-Lodz/releases/latest/download/mpk_lodz.zip
unzip mpk_lodz.zip
rm mpk_lodz.zip
```

## Hints

* Value for `id`/`num` can be retrieved from [*ITS Łódź*](http://rozklady.lodz.pl/). After choosing a desired stop open its electronical table. There should be a number visibile in URL. If URL contains `busStopId` you should use this number as `id`. If URL contains `busStopNum` you should use this number as `num`. 

* These sensors provides attributes which can be used in [*HTML card*](https://github.com/PiotrMachowski/Home-Assistant-Lovelace-HTML-card) or [*HTML Template card*](https://github.com/PiotrMachowski/Home-Assistant-Lovelace-HTML-Template-card): `html_timetable`, `html_departures`
  * HTML card:
    ```yaml
    - type: custom:html-card
      title: 'MPK'
      content: |
        <big><center>Timetable</center></big>
        [[ sensor.mpk_lodz_2427.attributes.html_timetable ]]
        <big><center>Departures</center></big>
        [[ sensor.mpk_lodz_2873.attributes.html_departures ]]
    ```
  * HTML Template card:
    ```yaml
    - type: custom:html-template-card
      title: 'MPK'
      ignore_line_breaks: true
      content: |
        <big><center>Timetable</center></big></br>
        {{ state_attr('sensor.mpk_lodz_2427','html_timetable') }}
        </br><big><center>Departures</center></big></br>
        {{ state_attr('sensor.mpk_lodz_2873','html_departures') }}
    ```

<a href='https://ko-fi.com/piotrmachowski' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />
<a href="https://paypal.me/PiMachowski" target="_blank"><img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg" border="0" alt="PayPal Logo" style="height: auto !important;width: auto !important;"></a>
