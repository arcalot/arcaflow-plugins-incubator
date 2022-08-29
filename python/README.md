# Python Plugins

## Automated, In-Place, PEP 8 Formatting

Install (black)[https://github.com/psf/black] as a development dependency.

```shell
pip install --user black
```

Tell `black` to edit `your_plugin.py` to make its code style conform to
`black`'s code style, a strict subset of PEP 8.

```shell
black --preview --experimental-string-processing <your_plugin.py>
```

This should perform most of the necessary style formatting. Updates to this method
are recommended.