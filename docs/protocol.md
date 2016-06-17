# Overview of the protocol, as taken from the manual and/or tested.
This document is an attempt to clarify the somewhat weird protocol for controlling the zuil, in a language-independent way.

## Opening a connection
The controller accepts connections at its IP address, `131.211.83.245` on port 23. (At the time of writing, `infozuil.svsticky.nl` is aliased to this address.)
The controller can be sent a _control string_ (see below) by opening a TCP socket to this port, receiving the header (some static connection information) and then just sending the control string. No response is given.
The controller does not accept multiple concurrent connections, and the first connection must be closed if another connection is to be made.

It is currently unknown if an open socket may be reused to send another control string (the manual seems to do it in the example, but does not explicitly state this), and if/when the connection times out.

## Control strings
A control string contains the instructions for the controller, and follows one of the formats defined in the manual.

 - ASCII control characters are used as markers for beginning and ending of values/fields/lines in the control strings. See the manual for the exact values used, this document will use the common abbreviations (SOH for 0x01, etc.).
 - Numeric values are encoded as a single ASCII character, starting at character 32 (the space). This encoding is written here as `enc(value)`. In Python: `enc(value) == chr(value + 32)`.
 - Control strings are required to start with the controller's address, which is always 0 in our case (as we've only got one display).

There are three types of control strings, described below.

### Text input
Text input control strings allow you to update the pages that the controller will cycle through on the screen. Each update will completely replace the previously stored text, there is no (known) way to get the current text or append pages. Pages are kept when the power to the zuil is lost and will appear again when the zuil is turned on again.

Text input has the following syntax (note that spaces, `# comments`, and newlines are meaningless, and only added for readability):

```
    SOH enc(address) FS		# Addressing
	'0' 'line 1' FS			# Lines of text
	'1' 'line 2' FS
	...
	'7'	'line 8' FS
	# Attributes for this page
	ESC 'A' enc(A) enc(B) enc(C) enc(D) FS 	# Duration (see below)
	ESC 'B' enc(blinkspeed) FS				# Blinkspeed, 0..4
	ESC 'Q' enc(brightness) FS				# Brightness, 1..17
	ESC 'R' enc(bool) FS					# Scrolling on/off 1/0
	ESC 'S' enc(bool) FS					# Fading on/off 1/0
	ESC 'P' enc(year) .. enc(sec) FS		# Schedular (see below)
	CR	# Required termination character
```

Notes:

- It is currently unknown if all lines of text are required to be entered (even if empty).
- Only the 'duration' attribute seems to be required, all other attributes may be omitted by completely leaving out the corresponding `ESC .. FS`-section.

#### Page duration
The duration of a page specifies how long the page should be visible before the next page is shown. The duration is specified in 'ticks' of 26.7 milliseconds.
The amount of ticks is encoded in four characters, A, B, C and D, which are encoded values from 0 up to 50.

A, B and C are multiplied by 4096, 256, and 16 respectively, see the manual (page 5, 'Readtime') for an example of how this works.

#### The schedular
The schedular is an attribute with an unknown meaning, it contains a datetime that maybe affects the pages in some way. It is currently unknown what its function is, and it does not seem to be required. The manual describes the schedular on page 6.

#### Text expansion
Some substrings are automatically replaced with something else:

 - `%M` -> current numeric month (`01` for January, etc.)
 - `%D` -> current day in month
 - `%H` -> hour on 24-hour clock
 - `%m` -> minute
 - `%S` -> second
 - `%R` -> hourglass glyph indicating the time until the page changes

There are some other values in the manual, but they either don't work or are no longer relevant.
In order to use these variables, setting the RTC is required. (Except for `%R`)

### RTC update
The controller contains a RTC (Real Time Clock), that keeps track of the time independently of the network. It is currently unknown whether the RTC can save the time across power loss, and/or whether the time keeps ticking when power is not connected.

The RTC can be updated to a new time by sending a control string following this format:

```
	SOH enc(address) FS		# Addressing, as above
	ESC 'T'
	enc(year)	# Offset from 1980, 0..95
	enc(month)  # 1..12
	' '			# enc(0), unused field
	enc(day)	# 1..31
	enc(hour)	# 0..23
	enc(minute)	# 0..59
	enc(second) # 0..59
	FS CR 		# Termination
```

### Display mode
The controller can be instructed to turn the screen on or off, and can enter a special test mode where it cycles through some predefined test pages. Note that all text is lost when the controller enters test mode. It is currently unknown whether the display mode is saved when the power is lost.

The modes are:

 0. Blanks display, no text is shown. Text that was entered earlier will be saved, and the text can be updated while the display is blanked (won't show until the display mode is changed to 1 again).
 1. Normal mode, the display turns on and the pages are shown.
 2. Test off, disables test mode. The display will blank, as the text is deleted when test mode is started. It is currently unknown whether setting mode 1 has the same effect.
 3. Pause test, toggles whether the test pages cycle. This does not work on normal pages.
 4. Test on, enables test mode. The display will cycle through some predefined pages, which will test the leds. All normal pages are lost!
 10) Toggle output, see manual. Unclear and probably unused.

The format for control strings for setting the display mode is:

```
	SOH enc(address) FS		# Addressing, as above
	ESC 'D'
	enc(mode)
	FS CR					# Termination
```
