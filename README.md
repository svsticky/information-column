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
- Requests
- APScheduler

## Future plans

- Include times (and perhaps locations) in the output when Koala outputs it in the API

## Installation
- Create a virtualenv (if not installing system-wide)
- Download the release tarball and do `pip install infozuild-x.x.x.tar.gz`. Internet connection is required for automatic downloading of dependencies.
- (Optional) Create `~/.infozuil/daemon.ini` with config overrides (example is TODO)

## Usage
- `zuil-get`: connect to Koala and output a JSON dict readable by `zuil-send`
	- Optional arguments: `--output` (`-o`): Write JSON to file, not stdout
	- `--limit`, `-l`: Limit the number of events displayed (0: only title page, -1: all)
- `zuil-send`: read a JSON dict and send it to the zuil.
	- Required arguments:
		- `--file [file]`: File to read
	- Optional argument:
		- `--output [file]`: output control string to a file
- `zuild`: Combines `zuil-get` and `zuil-send`, generally better
	- Optional arguments:
		- `--once`: update zuil immediately and exit
		- `--interval`: number of minutes to wait between updates
		- `--limit`: as `zuil-get --limit`
		- `--config`: manually specify a config file (other than `~/.infozuil/daemon.ini`)
		- `--host`: override zuil hostname
		- `--index`: override zuil controller index (which is always zero as we've only got one controller)
