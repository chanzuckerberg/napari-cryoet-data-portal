# napari-cryoet-data-portal

[![License MIT](https://img.shields.io/pypi/l/napari-cryoet-data-portal.svg?color=green)](https://github.com/chanzuckerberg/napari-cryoet-data-portal/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-cryoet-data-portal.svg?color=green)](https://pypi.org/project/napari-cryoet-data-portal)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-cryoet-data-portal.svg?color=green)](https://python.org)
[![tests](https://github.com/chanzuckerberg/napari-cryoet-data-portal/workflows/tests/badge.svg)](https://github.com/chanzuckerberg/napari-cryoet-data-portal/actions)
[![codecov](https://codecov.io/gh/chanzuckerberg/napari-cryoet-data-portal/branch/main/graph/badge.svg)](https://codecov.io/gh/chanzuckerberg/napari-cryoet-data-portal)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-cryoet-data)](https://napari-hub.org/plugins/napari-cryoet-data-portal)

List and open tomograms from the [CZII cryoET data portal] in [napari].

https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/5ad75c51-61f2-4695-8a50-8f9199e63f20

## Installation

You can install the latest development version using [pip]:

    pip install git+https://github.com/chanzuckerberg/napari-cryoet-data-portal.git

## Usage

Click the *Connect* button to establish a connection to the data portal.

![Connect button and editable URI to the portal](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/96ccb89a-f926-4a8f-945b-450e65969855)

After connecting to the portal, datasets are added below as they are found.

![Datasets and tomograms in the portal shown as an interactive tree](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/9562b530-a0f8-4c99-80d2-89e26391f23d)

Datasets and tomograms can be filtered by specifying a regular expression pattern.

![Datasets and tomograms filtered by the text 26, so that only two are shown](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/a15b27b2-aa1b-4704-af24-36e66805da02)

Selecting a dataset displays its metadata, which can be similarly explored and filtered.

![Metadata of dataset 10000 shown as an interactive tree of keys and values](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/1e88f78e-47e5-4bfc-84a1-06f8c038f4a4)

Selecting a tomogram displays its metadata and also opens the lowest resolution tomogram and all of its associated point annotations in the napari viewer.

![Metadata of tomogram TS_026 shown as an interactive tree of keys and values](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/f0772092-a2b0-406e-a42f-989c513b3bf6)

Higher resolution tomograms can be loaded instead by selecting a different resolution and clicking the *Open* button.

![Open button and resolution selector showing high resolution](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/fe5c0081-1658-43c0-9cbe-0d997e207b62)

In this case, napari only loads the data that needs to be displayed in the canvas.
While this can reduce the amount of data loaded, it may also cause performance problems when initially opening and exploring the data.

In general, finding and fetching data from the portal can take a long time.
All plugin operations that fetch data from the portal try to run concurrently in order to keep interaction with napari and the plugin as responsive as possible.
These operations can also be cancelled by clicking the *Cancel* button.

![Screenshot 2023-06-07 at 2 38 41 PM](https://github.com/chanzuckerberg/napari-cryoet-data-portal/assets/2608297/3f621a8a-0962-4a25-bee0-3596cec58659)

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
