# napari-cryoet-data-portal

[![tests](https://github.com/chanzuckerberg/napari-cryoet-data-portal/workflows/tests/badge.svg)](https://github.com/chanzuckerberg/napari-cryoet-data-portal/actions)
[![codecov](https://codecov.io/gh/chanzuckerberg/napari-cryoet-data-portal/branch/main/graph/badge.svg)](https://codecov.io/gh/chanzuckerberg/napari-cryoet-data-portal)

List and open tomograms from the [CZII CryoET Data Portal] in [napari].

https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/6ccbd314-fd2b-40aa-abeb-dd1afe2a61e2

## Installation

You can install the latest development version using [pip]:

    pip install git+https://github.com/chanzuckerberg/napari-cryoet-data-portal.git

## Usage

Click the *Connect* button to establish a connection to the data portal.

![Connect button and editable URI to the portal](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/1bc5ecba-daf6-4a14-83a5-332ea5625604)

After connecting to the portal, datasets are added below as they are found.

![Datasets and tomograms in the portal shown as an interactive tree](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/7af78e00-bbba-4c5b-a286-fb865ca8cff0)

Datasets and tomograms can be filtered by specifying a regular expression pattern.

![Datasets and tomograms filtered by the text 26, so that only two are shown](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/96a57f4c-290e-4932-aa2d-95d13edd2d8c)

Selecting a dataset displays its metadata, which can be similarly explored and filtered.

![Metadata of dataset 10000 shown as an interactive tree of keys and values](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/b230720a-9083-4e35-a9db-44071c979fcc)

Selecting a tomogram displays its metadata and also opens the lowest resolution tomogram and all of its associated point annotations in the napari viewer.

![Metadata of tomogram TS_026 shown as an interactive tree of keys and values](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/386b3116-ba16-4f5d-840d-4eafa3dc62b0)

Higher resolution tomograms can be loaded instead by selecting a different resolution and clicking the *Open* button.

![Open button and resolution selector showing high resolution](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/4e5ccb1c-209e-4690-8375-e87cc242abbc)

In this case, napari only loads the data that needs to be displayed in the canvas.
While this can reduce the amount of data loaded, it may also cause performance problems when initially opening and exploring the data.

In general, finding and fetching data from the portal can take a long time.
All plugin operations that fetch data from the portal try to run concurrently in order to keep interaction with napari and the plugin as responsive as possible.
These operations can also be cancelled by clicking the *Cancel* button.

![Progress bar with loading status and cancel button](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/2dc316ae-5231-4159-bc93-785548dbf6a5)

## Contributing

This is still in early development, but contributions and ideas are welcome!
Don't hesitate to [open an issue] or [open a pull request] to help improve this plugin.

This project adheres to the [Contributor Covenant code of conduct].
By participating, you are expected to uphold this code.
Please report unacceptable behavior to opensource@chanzuckerberg.com.

## Security

If you believe you have found a security issue, please see our [security policy] on how to report it.

## License

Distributed under the terms of the [MIT] license, "napari-cryoet-data-portal" is free and open source software. See the [license file] for more details.

## Acknowledgements

This plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.


[napari]: https://github.com/napari/napari
[@napari]: https://github.com/napari
[CZII CryoET Data Portal]: https://chanzuckerberg.github.io/cryoet-data-portal
[pip]: https://pypi.org/project/pip/
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[MIT]: http://opensource.org/licenses/MIT
[security policy]: /SECURITY.md
[license file]: /LICENSE
[Contributor Covenant code of conduct]: https://github.com/chanzuckerberg/.github/tree/master/CODE_OF_CONDUCT.md
[open an issue]: https://github.com/chanzuckerberg/napari-cryoet-data-portal/issues
[open a pull request]: https://github.com/chanzuckerberg/napari-cryoet-data-portal/pulls
