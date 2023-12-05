![cnb-tools](assets/cnb-tools.png)

<p align="center"><em>
  Convenience tools/functions for challenges and benchmarking on
  <a href="https://www.synapse.org" title="Synapse.org">Synapse.org</a>
</em></p>

<p align="center">
  <a href="https://pypi.org/project/cnb-tools/" title="cnb-tools on PyPI">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/cnb-tools?style=flat-square&logo=pypi&logoColor=white&color=%23679EC1">
  </a>
  <img alt="Supported Python versions" src="https://img.shields.io/badge/python-3.9 | 3.10 | 3.11 | 3.12-%23EB8231?style=flat-square&logo=python&logoColor=white">
  <a href="https://github.com/Sage-Bionetworks-Challenges/cnb-tools/blob/main/LICENSE" title="License">
    <img alt="License" src="https://img.shields.io/github/license/Sage-Bionetworks-Challenges/cnb-tools?style=flat-square&logo=github&color=%236DB56D">
  </a>
</p>

---

**Documentation**: [https://sage-bionetworks-challenges.github.io/cnb-tools]

**Source code**: [https://github.com/Sage-Bionetworks-Challenges/cnb-tools]

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
authtoken = "YOUR PAT"
```

Generate a new Synapse [Personal Access Token (PAT)] with all token
permissions enabled, then copy-paste it into `authtoken`. Save the file.

For security, we recommend updating its permissions so that other
users on your machine do not have read access to your credentials, e.g.

<!-- termynal -->
```console
$ chmod 600 ~/.synapseConfig
$ ls -l ~/.synapseConfig
-rw-------@ 1 user  staff  123 Jan  1 12:00 .synapseConfig
```

## Installation

<!-- termynal -->
```console
$ pip install cnb-tools
---> 100%
Successfully installed cnb-tools
```

!!! note
    **cnb-tools** builds off of the Synapse Python Client — by
    installing **cnb-tools**, you will also be installing **synapseclient**.
    
    → [Read its docs.]

Verify the installation with:

<!-- termynal -->
```console
$ cnb-tools --version
cnb-tools v0.1.1
```

## License

**cnb-tools** is released under the Apache 2.0 license.

[https://sage-bionetworks-challenges.github.io/cnb-tools]: https://sage-bionetworks-challenges.github.io/cnb-tools
[https://github.com/Sage-Bionetworks-Challenges/cnb-tools]: https://github.com/Sage-Bionetworks-Challenges/cnb-tools
[DREAM Challenges]: https://dreamchallenges.org/
[Python 3.9+]: https://www.python.org/downloads/
[Synapse account]: https://www.synapse.org/#!LoginPlace:0
[Personal Access Token (PAT)]: https://www.synapse.org/#!PersonalAccessTokens:
[Read its docs.]: https://python-docs.synapse.org/build/html/index.html
