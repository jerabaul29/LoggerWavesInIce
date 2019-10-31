
--------------------------------------------------------------------------------
workflow:
- First, should have parsed the data (see ../Parse)  - at this point, have the parsed data in different files for different kinds of data
- ./split_data_between_folders.py                    - at this point, the data is split between a series of folders; this will make it easier to load data into Python without overflowing RAM
- ./prepare_data_damping.py                          - at this point, () a time slice of the data has been chose () the regression between arduino timestamp and UTC has been performed () the data is saved. NOTE that at this point, the data has not been re-sampled / interpolated yet!

--------------------
At this point, the show_spectra and look_at_damping can be used
--------------------

- ./filter_resample_csvWrite_acceleration.py          - at this point, the acceleration data has been filtered, resampled, and exported as csv

--------------------
At this point, the CSV are filtered and resampled, and ready for use for analysis:
- show_spectrogram.py
- show_specter.py
--------------------

