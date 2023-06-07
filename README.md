# napari-cryoet-data-portal

[![License MIT](https://img.shields.io/pypi/l/napari-cryoet-data-portal.svg?color=green)](https://github.com/chanzuckerberg/napari-cryoet-data-portal/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-cryoet-data-portal.svg?color=green)](https://pypi.org/project/napari-cryoet-data-portal)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-cryoet-data-portal.svg?color=green)](https://python.org)
[![tests](https://github.com/chanzuckerberg/napari-cryoet-data-portal/workflows/tests/badge.svg)](https://github.com/chanzuckerberg/napari-cryoet-data-portal/actions)
[![codecov](https://codecov.io/gh/chanzuckerberg/napari-cryoet-data-portal/branch/main/graph/badge.svg)](https://codecov.io/gh/chanzuckerberg/napari-cryoet-data-portal)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-cryoet-data)](https://napari-hub.org/plugins/napari-cryoet-data-portal)

List and open tomograms from the [CZII cryoET data portal] in [napari].

https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/1542b136-718a-490c-b907-65c1dfb6ccd9

## Installation

You can install the latest development version using [pip]:

    pip install git+https://github.com/chanzuckerberg/napari-cryoet-data-portal.git

## Usage

Click the *Connect* button to establish a connection to the data portal.

![Connect button and editable URI to the portal](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/bad1dbb7-2752-4b1a-b9d2-d0d685e4536c)

After connecting to the portal, datasets are added below as they are found.

![Datasets and tomograms in the portal shown as an interactive tree](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/47ececbd-40e6-4374-9c64-18a07ce36bf2)

Datasets and tomograms can be filtered by specifying a regular expression pattern.

![Datasets and tomograms filtered by the text 26, so that only two are shown](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/437cb5e3-ac53-4fc0-83a9-53cd4c9f67c1)

Selecting a dataset displays its metadata, which can be similarly explored and filtered.

![Metadata of dataset 10000 shown as an interactive tree of keys and values](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/f9793891-84e9-4a82-af2f-51b68bcf4287)

Selecting a tomogram displays its metadata and also opens the lowest resolution tomogram and all of its associated point annotations in the napari viewer.

![Metadata of tomogram TS_026 shown as an interactive tree of keys and values](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/1dabcaa0-c232-4b1d-adc7-b431b4a80418)

Higher resolution tomograms can be loaded instead by selecting a different resolution and clicking the *Open* button.

![Open button and resolution selector showing high resolution](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/9132c68a-dd8e-420b-b31e-746baa9fc2bd)

In this case, napari only loads the data that needs to be displayed in the canvas.
While this can reduce the amount of data loaded, it may also cause performance problems when initially opening and exploring the data.

In general, finding and fetching data from the portal can take a long time.
All plugin operations that fetch data from the portal try to run concurrently in order to keep interaction with napari and the plugin as responsive as possible.
These operations can also be cancelled by clicking the *Cancel* button.

![Progress bar with loading status and cancel button](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/b0ba4a69-5f24-4aaf-99d5-37541cfff17f)

## Contributing

Contributions and ideas are welcome!
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
[CZII cryoET data portal]: https://chanzuckerberg.github.io/cryoet-data-portal
[pip]: https://pypi.org/project/pip/
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[MIT]: http://opensource.org/licenses/MIT
[security policy]: /SECURITY.md
[license file]: /LICENSE
[Contributor Covenant code of conduct]: https://github.com/chanzuckerberg/.github/tree/master/CODE_OF_CONDUCT.md
[open an issue]: https://github.com/chanzuckerberg/napari-cryoet-data-portal/issues
[open a pull request]: https://github.com/chanzuckerberg/napari-cryoet-data-portal/pulls
