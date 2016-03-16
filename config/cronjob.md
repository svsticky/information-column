# Sample cronjob

A sample cronjob that can be used on the server connected to the information column, is the following: `*/5 * * * * admin . /home/admin/.virtualenvs/infozuil/bin/activate; zuild --once`
Replace `admin` with the acutal user, and `infozuil` with the correct virtualenv name. (Alternatively, install the daemon system-wide and just do `admin zuild --once`.)

Running using the service is generally preferred, as it'll start automatically.
