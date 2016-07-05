# Information column

The **information column** is the billboard-like device standing outside Sticky's chamber. The goal is to show the upcoming events at Sticky with its start/end dates and times. It should give an easy overview for members of Sticky.

## Technical requirements

* A Linux client device with
   * A wired network interface AND
   * A wireless interface
* The information column

## Dependencies

### Client

- Python 3.4
- Virtualenvwrapper, pip
- Requests (via pip)
- APScheduler (via pip)

## Future plans

- ~~Include times (and perhaps locations) in the output when Koala outputs it in the API~~
- Show a message on the zuil itself if error occurs (no internet, no activities)

## Installation
- Ensure `pip`, `virtualenvwrapper` are installed
- Create a virtualenv (if not installing system-wide) (`mkvirtualenv -ppython3 infozuil`)
- `pip install infozuild` for the latest release, or clone the repo and do `python setup.py develop`
- (Optional) Create `~/.infozuil/daemon.ini` with config overrides (example is TODO)
- Use one of the methods documented in `config/` to set up the service.

## Console scripts usage
- `zuil-get`: connect to Koala and output a JSON string readable by `zuil-send`
	- Optional arguments:
		- `--limit NUM` (`-l`): Limit the number of events displayed (0: only title page, omitted: all)
		- `--output` (`-o`): Write JSON to file, not stdout
- `zuil-send`: read a JSON dict and send it to the zuil.
	- Optional arguments:
		- `--verbose` (`-v`): Activate debug logging
		- `--displaymode MODE`: set a display mode (see docs)
		- `--file FILE` (`-f`): File with JSON to read (stdin if omitted)
		- `--output FILE` (`-o`): output control string to a file
		- `--update-rtc`: update the RTC to the current time (overrides text update)
- `zuild`: Combines `zuil-get` and `zuil-send`, what actually runs on the zuil.
	- Optional arguments:
		- `--verbose` (`-v`): Activate debug logging
		- `--config FILE`: manually specify a config file (other than `~/.infozuil/daemon.ini`)
		- `--host HOSTNAME`: override zuil hostname
		- `--index NUM`: override zuil controller index (which should be always zero as we've only got one controller)
		- `--interval NUM`: number of minutes to wait between updates
		- `--limit NUM`: as `zuil-get --limit`
		- `--once`: update zuil immediately and exit
