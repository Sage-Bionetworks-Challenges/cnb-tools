<div align="center">

  ![cnb-tools](https://raw.githubusercontent.com/Sage-Bionetworks-Challenges/cnb-tools/main/docs/assets/cnb-tools.png)

  <h3>
    Convenience tools/functions for challenges and benchmarking on
    <a href="https://www.synapse.org" title="Synapse.org">Synapse.org</a>
  </h3>

  <br/>

  <a href="https://pypi.org/project/cnb-tools/" title="cnb-tools on PyPI">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/cnb-tools?style=flat-square&logo=pypi&logoColor=white&color=%23679EC1">
  </a>
  <img alt="Supported Python versions" src="https://img.shields.io/badge/python-3.9 | 3.10 | 3.11 | 3.12-%23EB8231?style=flat-square&logo=python&logoColor=white">
  <a href="https://github.com/Sage-Bionetworks-Challenges/cnb-tools/blob/main/LICENSE" title="License">
    <img alt="License" src="https://img.shields.io/github/license/Sage-Bionetworks-Challenges/cnb-tools?style=flat-square&logo=github&color=%236DB56D">
  </a>

</div>

---

📖 **Documentation**: [https://sage-bionetworks-challenges.github.io/cnb-tools]

👾 **Source code**: [https://github.com/Sage-Bionetworks-Challenges/cnb-tools]

---

**cnb-tools** is a set of tools and commands that provides an interface
for managing crowd-sourced challenges hosted on Synapse.org, including
but not limited to, [DREAM Challenges].

## Requirements

- [Python 3.9+]
- [Synapse account]

To fully utilize **cnb-tools**, you must have a Synapse account and
provide your credentials to the tool.  To do so, create a `.synapseConfig`
file in your home directory, and enter the following:

```yaml
[authentication]
authtoken=<YOUR PAT>
```

Generate a new Synapse [Personal Access Token (PAT)] with all token
permissions enabled, then copy-paste it into `authtoken`. Save the file.

For security, we recommend updating its permissions so that other
users on your machine do not have read access to your credentials, e.g.

```console
chmod 600 ~/.synapseConfig
```

## Installation

For best practice, use a Python environment to install **cnb-tools**
rather than directly into your base env.  In our docs, we will be
using [miniconda], but you can use [miniforge], [venv], [pyenv], etc.

<!-- termynal -->
```console
# Create a new env and activate it
conda create -n cnb-tools python=3.12 -y
conda activate cnb-tools

# Install cnb-tools using pip
pip install cnb-tools
```

> ⓘ **NOTE**
>
> **cnb-tools** builds off of the Synapse Python Client — by
> installing **cnb-tools**, you will also be installing **synapseclient**.
>  
> → [Read its docs.]

Verify the installation with:

```console
cnb-tools
```

## Running With Docker

If you rather not install `cnb-tools` onto your machine, you may still use the
tool via Docker!  The package and list of versions are [available here].

In order to provide your Synapse credentials during each run, you must create a
file with your Synapse PAT as the `SYNAPSE_AUTH_TOKEN` environment variable:

```text
SYNAPSE_AUTH_TOKEN=<YOUR PAT>
```

The `docker run` command will look something like this:

```console
$ docker run --rm \
    --env-file .synapse-config \
    ghcr.io/sage-bionetworks-challenges/cnb-tools

 Usage: cnb-tools [OPTIONS] COMMAND [ARGS]...

 Manage challenges on Synapse.org from the CLI
 (Note: some commands will require challenge admin permissions)
 ...
```

## License

**cnb-tools** is released under the Apache 2.0 license.

[https://sage-bionetworks-challenges.github.io/cnb-tools]: https://sage-bionetworks-challenges.github.io/cnb-tools
[https://github.com/Sage-Bionetworks-Challenges/cnb-tools]: https://github.com/Sage-Bionetworks-Challenges/cnb-tools
[DREAM Challenges]: https://dreamchallenges.org/
[Python 3.9+]: https://www.python.org/downloads/
[Synapse account]: https://www.synapse.org/#!LoginPlace:0
[Personal Access Token (PAT)]: https://www.synapse.org/#!PersonalAccessTokens:
[miniconda]: https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html
[miniforge]: https://github.com/conda-forge/miniforge
[venv]: https://docs.python.org/3/library/venv.html
[pyenv]: https://github.com/pyenv/pyenv
[Read its docs.]: https://python-docs.synapse.org/
[available here]: https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pkgs/container/cnb-tools
